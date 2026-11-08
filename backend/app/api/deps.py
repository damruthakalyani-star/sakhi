"""API dependency providers for authentication, authorization, and services."""

from collections.abc import Callable
from typing import Any

import jwt
from backend.app.core.exceptions import ForbiddenException, UnauthorizedException
from backend.app.core.security import decode_access_token
from backend.app.db.mongo import get_database
from backend.app.repositories.audit_repo import AuditRepository
from backend.app.repositories.contact_repo import ContactRepository
from backend.app.repositories.location_repo import LocationRepository
from backend.app.repositories.report_repo import ReportRepository
from backend.app.repositories.sos_repo import SOSRepository
from backend.app.repositories.token_repo import TokenRepository
from backend.app.repositories.user_repo import UserRepository
from backend.app.services.auth_service import AuthService
from backend.app.services.contact_service import ContactService
from backend.app.services.location_service import LocationService
from backend.app.services.report_service import ReportService
from backend.app.services.sos_service import SOSService
from fastapi import Cookie, Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

security_bearer = HTTPBearer(auto_error=False)


# Service Dependency Factories
def get_user_repo() -> UserRepository:
    return UserRepository(get_database())


def get_token_repo() -> TokenRepository:
    return TokenRepository(get_database())


def get_contact_repo() -> ContactRepository:
    return ContactRepository(get_database())


def get_sos_repo() -> SOSRepository:
    return SOSRepository(get_database())


def get_location_repo() -> LocationRepository:
    return LocationRepository(get_database())


def get_report_repo() -> ReportRepository:
    return ReportRepository(get_database())


def get_audit_repo() -> AuditRepository:
    return AuditRepository(get_database())


def get_auth_service(
    user_repo: UserRepository = Depends(get_user_repo),
    token_repo: TokenRepository = Depends(get_token_repo),
    contact_repo: ContactRepository = Depends(get_contact_repo),
    sos_repo: SOSRepository = Depends(get_sos_repo),
    audit_repo: AuditRepository = Depends(get_audit_repo),
) -> AuthService:
    return AuthService(user_repo, token_repo, contact_repo, sos_repo, audit_repo)


def get_contact_service(
    contact_repo: ContactRepository = Depends(get_contact_repo),
    audit_repo: AuditRepository = Depends(get_audit_repo),
) -> ContactService:
    return ContactService(contact_repo, audit_repo)


def get_sos_service(
    sos_repo: SOSRepository = Depends(get_sos_repo),
    contact_repo: ContactRepository = Depends(get_contact_repo),
    audit_repo: AuditRepository = Depends(get_audit_repo),
) -> SOSService:
    return SOSService(sos_repo, contact_repo, audit_repo)


def get_location_service(
    location_repo: LocationRepository = Depends(get_location_repo),
    user_repo: UserRepository = Depends(get_user_repo),
    audit_repo: AuditRepository = Depends(get_audit_repo),
) -> LocationService:
    return LocationService(location_repo, user_repo, audit_repo)


def get_report_service(
    report_repo: ReportRepository = Depends(get_report_repo),
    audit_repo: AuditRepository = Depends(get_audit_repo),
) -> ReportService:
    return ReportService(report_repo, audit_repo)


async def get_current_user(
    request: Request,
    bearer: HTTPAuthorizationCredentials | None = Depends(security_bearer),
    access_token_cookie: str | None = Cookie(None, alias="access_token"),
    user_repo: UserRepository = Depends(get_user_repo),
) -> dict[str, Any]:
    """
    Extracts access token from Authorization header or httpOnly cookie.
    Validates token signature and loads active user.
    """
    token = None
    if bearer and bearer.credentials:
        token = bearer.credentials
    elif access_token_cookie:
        token = access_token_cookie

    if not token:
        raise UnauthorizedException(
            "Authentication token required.", code="TOKEN_MISSING"
        )

    try:
        payload = decode_access_token(token)
    except jwt.ExpiredSignatureError:
        raise UnauthorizedException(
            "Access token has expired. Please refresh your session.",
            code="TOKEN_EXPIRED",
        ) from None
    except Exception:
        raise UnauthorizedException(
            "Invalid access token.", code="TOKEN_INVALID"
        ) from None

    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedException("Invalid token payload.", code="TOKEN_MALFORMED")

    user = await user_repo.get_by_id(user_id)
    if not user:
        raise UnauthorizedException("User account not found.", code="USER_NOT_FOUND")
    if not user.get("is_active", True):
        raise ForbiddenException("Account is disabled.", code="ACCOUNT_DISABLED")

    request.state.user_id = user["id"]
    return user


async def get_optional_user(
    bearer: HTTPAuthorizationCredentials | None = Depends(security_bearer),
    access_token_cookie: str | None = Cookie(None, alias="access_token"),
    user_repo: UserRepository = Depends(get_user_repo),
) -> dict[str, Any] | None:
    """Optional user resolution for endpoints supporting unauthenticated access."""
    token = bearer.credentials if bearer else access_token_cookie
    if not token:
        return None
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if user_id:
            return await user_repo.get_by_id(user_id)
    except Exception:
        return None
    return None


def require_role(allowed_roles: list[str]) -> Callable:
    """Dependency factory checking user has at least one of allowed_roles."""

    async def role_checker(
        current_user: dict[str, Any] = Depends(get_current_user),
    ) -> dict[str, Any]:
        user_role = current_user.get("role", "user")
        if user_role not in allowed_roles:
            raise ForbiddenException(
                f"Action requires one of the following roles: {', '.join(allowed_roles)}.",
                code="INSUFFICIENT_PERMISSIONS",
            )
        return current_user

    return role_checker
