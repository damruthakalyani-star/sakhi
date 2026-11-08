"""FastAPI Application Factory, Lifespan, and Middleware Pipeline."""

import time
import uuid
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from backend.app.api.v1.router import api_v1_router
from backend.app.core.config import settings
from backend.app.core.exceptions import (
    AppException,
    app_exception_handler,
    http_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from backend.app.core.logging import logger, setup_logging
from backend.app.core.rate_limit import limiter
from backend.app.db.indexes import create_indexes
from backend.app.db.mongo import db_manager
from backend.app.db.seed import seed_admin, seed_dev_data
from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from starlette.exceptions import HTTPException as StarletteHTTPException


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifecycle manager."""
    setup_logging(settings.LOG_LEVEL)
    logger.info(f"Starting {settings.APP_NAME} in [{settings.APP_ENV}] mode...")

    # Connect to MongoDB
    if not db_manager.client:
        await db_manager.connect()
    db = db_manager.get_db()

    # Ensure all database indexes exist
    await create_indexes(db)

    # Seed admin user and initial dev data (if enabled)
    try:
        await seed_admin(db)
        if settings.APP_ENV != "production":
            await seed_dev_data(db)
    except Exception as e:
        logger.warning(f"Initial seeding encountered notice: {e}")

    logger.info(
        f"{settings.APP_NAME} initialization complete. Ready to serve requests."
    )
    yield

    # Shutdown
    logger.info("Shutting down application...")
    await db_manager.disconnect()
    logger.info("Application shutdown complete.")


def create_application() -> FastAPI:
    """Builds and configures the FastAPI application instance."""
    docs_url = "/docs" if settings.APP_ENV != "production" else None
    redoc_url = "/redoc" if settings.APP_ENV != "production" else None
    openapi_url = (
        f"{settings.API_V1_PREFIX}/openapi.json"
        if settings.APP_ENV != "production"
        else None
    )

    app = FastAPI(
        title=settings.APP_NAME,
        version="1.0.0",
        description="RESTful API for the SAKHISAHAY Women's Safety Platform",
        docs_url=docs_url,
        redoc_url=redoc_url,
        openapi_url=openapi_url,
        lifespan=lifespan,
    )

    # Attach Rate Limiter state
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # Global Exception Handlers
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)

    # ---------------------------------------------------------
    # Middleware Pipeline (Executed in reverse order of addition)
    # ---------------------------------------------------------

    # 1. GZip Compression
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # 2. CORS Headers
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID"],
    )

    # 3. Custom Request Tracking & Security Headers Middleware
    @app.middleware("http")
    async def request_context_middleware(request: Request, call_next) -> Response:
        # Request Correlation ID
        req_id = request.headers.get("X-Request-ID") or f"req-{uuid.uuid4()}"
        request.state.request_id = req_id

        start_time = time.perf_counter()
        response: Response = await call_next(request)
        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

        # Inject Security Headers (OWASP Recommended)
        response.headers["X-Request-ID"] = req_id
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = (
            "geolocation=(self), camera=(), microphone=()"
        )

        if settings.APP_ENV == "production":
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains; preload"
            )

        # Structured Log
        logger.info(
            f"{request.method} {request.url.path} -> {response.status_code} ({latency_ms}ms)",
            extra={
                "request_id": req_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "latency_ms": latency_ms,
                "client_ip": request.client.host if request.client else "unknown",
            },
        )
        return response

    # Mount API v1 Router
    app.include_router(api_v1_router, prefix=settings.API_V1_PREFIX)

    # Top-level root info endpoint
    @app.get("/", tags=["Root"])
    async def root_index() -> dict:
        return {
            "name": settings.APP_NAME,
            "environment": settings.APP_ENV,
            "api_version": "v1",
            "health": f"{settings.API_V1_PREFIX}/health",
            "ready": f"{settings.API_V1_PREFIX}/ready",
            "docs": (
                "/docs"
                if settings.APP_ENV != "production"
                else "disabled in production"
            ),
        }

    return app


app = create_application()
