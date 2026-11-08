"""Health check, readiness, version, and public resources endpoints."""

from backend.app.db.mongo import db_manager
from fastapi import APIRouter, Response, status
from pydantic import BaseModel

router = APIRouter()


class HealthResponse(BaseModel):
    status: str
    service: str


class ReadyResponse(BaseModel):
    status: str
    database: str


class VersionResponse(BaseModel):
    name: str
    version: str
    build_environment: str


class HelplineItem(BaseModel):
    name: str
    number: str
    description: str
    website: str = ""


class SafetyResourcesResponse(BaseModel):
    emergency_number: str
    helplines: list[HelplineItem]
    statutory_notice: str


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Liveness check",
)
async def health_check() -> HealthResponse:
    return HealthResponse(status="ok", service="sakhisahay-backend")


@router.get(
    "/ready",
    response_model=ReadyResponse,
    status_code=status.HTTP_200_OK,
    summary="Readiness check",
)
async def readiness_check(response: Response) -> ReadyResponse:
    is_healthy = await db_manager.ping()
    if not is_healthy:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return ReadyResponse(status="degraded", database="disconnected")
    return ReadyResponse(status="ready", database="connected")


@router.get(
    "/version",
    response_model=VersionResponse,
    status_code=status.HTTP_200_OK,
    summary="Version information",
)
async def version_info() -> VersionResponse:
    from backend.app import __version__
    from backend.app.core.config import settings

    return VersionResponse(
        name=settings.APP_NAME,
        version=__version__,
        build_environment=settings.APP_ENV,
    )


@router.get(
    "/safety-resources",
    response_model=SafetyResourcesResponse,
    status_code=status.HTTP_200_OK,
    summary="Public directory of verified Indian helplines and resources",
)
async def get_safety_resources() -> SafetyResourcesResponse:
    return SafetyResourcesResponse(
        emergency_number="112",
        helplines=[
            HelplineItem(
                name="Women Helpline (MWCD)",
                number="181",
                description="24x7 toll-free helpline providing emergency and non-emergency support to women in distress.",
            ),
            HelplineItem(
                name="National Cyber Crime Reporting Helpline",
                number="1930",
                description="Dedicated helpline and portal for reporting cyber crimes, including online harassment and financial fraud.",
                website="https://cybercrime.gov.in",
            ),
            HelplineItem(
                name="National Commission for Women (NCW)",
                number="14490",
                description="24x7 helpline for women facing violence, harassment, or domestic abuse.",
                website="https://www.ncw.gov.in",
            ),
        ],
        statutory_notice="In immediate danger anywhere in India, call 112 directly. SAKHISAHAY provides guidance and contact notification but does not replace official emergency services.",
    )
