"""Authentication and user session endpoints."""

from typing import Any

from backend.app.api.deps import get_auth_service, get_current_user
from backend.app.core.config import settings
from backend.app.core.rate_limit import limiter
from backend.app.schemas.common import MessageResponse
from backend.app.schemas.user import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    TokenResponse,
    UserCreate,
    UserLogin,
    UserProfileResponse,
    UserResponse,
)
from backend.app.services.auth_service import AuthService
from fastapi import APIRouter, Cookie, Depends, Request, Response, status
from pydantic import BaseModel

router = APIRouter()


class RefreshTokenBody(BaseModel):
    refresh_token: str | None = None


def set_refresh_cookie(response: Response, refresh_token: str) -> None:
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=settings.APP_ENV == "production",
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
        path="/api/v1/auth",
    )


def clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(
        key="refresh_token",
        path="/api/v1/auth",
        httponly=True,
        samesite="lax",
    )


@router.post(
    "/signup",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
)
@limiter.limit(settings.RATE_LIMIT_AUTH)
async def signup(
    request: Request,
    response: Response,
    data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    ip = request.client.host if request.client else "0.0.0.0"
    user_agent = request.headers.get("user-agent", "unknown")
    user, access_token, raw_refresh = await auth_service.signup(
        data, ip=ip, user_agent=user_agent
    )
    set_refresh_cookie(response, raw_refresh)
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse(**user),
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Log in with email and password",
)
@limiter.limit(settings.RATE_LIMIT_AUTH)
async def login(
    request: Request,
    response: Response,
    data: UserLogin,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    ip = request.client.host if request.client else "0.0.0.0"
    user_agent = request.headers.get("user-agent", "unknown")
    user, access_token, raw_refresh = await auth_service.login(
        data, ip=ip, user_agent=user_agent
    )
    set_refresh_cookie(response, raw_refresh)
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse(**user),
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh short-lived access token",
)
async def refresh_token(
    request: Request,
    response: Response,
    body: RefreshTokenBody | None = None,
    cookie_token: str | None = Cookie(None, alias="refresh_token"),
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    raw_token = (
        body.refresh_token if body and body.refresh_token else None
    ) or cookie_token
    if not raw_token:
        from backend.app.core.exceptions import UnauthorizedException

        raise UnauthorizedException(
            "Refresh token required in cookie or body.", code="TOKEN_REQUIRED"
        )

    ip = request.client.host if request.client else "0.0.0.0"
    user_agent = request.headers.get("user-agent", "unknown")
    new_access, new_refresh = await auth_service.refresh_tokens(
        raw_token, ip=ip, user_agent=user_agent
    )
    set_refresh_cookie(response, new_refresh)
    return TokenResponse(
        access_token=new_access,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Log out and invalidate session",
)
async def logout(
    response: Response,
    cookie_token: str | None = Cookie(None, alias="refresh_token"),
    current_user: dict[str, Any] = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
) -> Response:
    await auth_service.logout(cookie_token, current_user["id"])
    clear_refresh_cookie(response)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/me",
    response_model=UserProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user profile and overview",
)
async def get_me(
    current_user: dict[str, Any] = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
) -> UserProfileResponse:
    profile = await auth_service.get_profile(current_user["id"])
    return UserProfileResponse(**profile)


@router.post(
    "/forgot-password",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Request a password reset link",
)
@limiter.limit(settings.RATE_LIMIT_AUTH)
async def forgot_password(
    request: Request,
    data: ForgotPasswordRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> MessageResponse:
    ip = request.client.host if request.client else "0.0.0.0"
    await auth_service.forgot_password(data.email, ip=ip)
    return MessageResponse(
        message="If the email exists, a password reset link has been dispatched."
    )


@router.post(
    "/reset-password",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Reset password with verification token",
)
@limiter.limit(settings.RATE_LIMIT_AUTH)
async def reset_password(
    request: Request,
    data: ResetPasswordRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> MessageResponse:
    await auth_service.reset_password(data.token, data.new_password)
    return MessageResponse(
        message="Password has been successfully reset. Please log in with your new password."
    )


@router.post(
    "/change-password",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Change password when authenticated",
)
async def change_password(
    data: ChangePasswordRequest,
    current_user: dict[str, Any] = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
) -> MessageResponse:
    await auth_service.change_password(
        current_user["id"], data.current_password, data.new_password
    )
    return MessageResponse(message="Password changed successfully.")
