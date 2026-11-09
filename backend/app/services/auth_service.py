"""Authentication and user management business logic service."""

from datetime import UTC, datetime
from typing import Any

from backend.app.core.exceptions import (
    ConflictException,
    ForbiddenException,
    NotFoundException,
    UnauthorizedException,
    ValidationException,
)
from backend.app.core.logging import logger
from backend.app.core.security import (
    create_access_token,
    create_refresh_token,
    generate_secure_token,
    hash_password,
    hash_token,
    verify_password,
)
from backend.app.repositories.audit_repo import AuditRepository
from backend.app.repositories.contact_repo import ContactRepository
from backend.app.repositories.sos_repo import SOSRepository
from backend.app.repositories.token_repo import TokenRepository
from backend.app.repositories.user_repo import UserRepository
from backend.app.schemas.user import UserCreate, UserLogin


class AuthService:
    def __init__(
        self,
        user_repo: UserRepository,
        token_repo: TokenRepository,
        contact_repo: ContactRepository,
        sos_repo: SOSRepository,
        audit_repo: AuditRepository,
    ) -> None:
        self.user_repo = user_repo
        self.token_repo = token_repo
        self.contact_repo = contact_repo
        self.sos_repo = sos_repo
        self.audit_repo = audit_repo

    async def signup(
        self, data: UserCreate, ip: str | None = None, user_agent: str | None = None
    ) -> tuple[dict[str, Any], str, str]:
        normalized_email = data.email.strip().lower()
        existing = await self.user_repo.get_by_email(normalized_email)
        if existing:
            raise ConflictException(
                f"An account with email '{normalized_email}' already exists.",
                code="EMAIL_ALREADY_EXISTS",
            )

        pwd_hash = hash_password(data.password)
        user_dict = {
            "email": normalized_email,
            "full_name": data.full_name.strip(),
            "phone_number": data.phone_number,
            "password_hash": pwd_hash,
            "role": "user",
            "is_active": True,
            "is_verified": False,
            "avatar_url": None,
            "failed_login_attempts": 0,
            "locked_until": None,
            "last_login_at": None,
        }
        user = await self.user_repo.create(user_dict)
        user_id = user["id"]

        access_token = create_access_token(user_id, role="user")
        raw_refresh, family_id, expires_at = create_refresh_token(user_id)
        await self.token_repo.save_refresh_token(
            user_id=user_id,
            token_hash=hash_token(raw_refresh),
            family_id=family_id,
            expires_at=expires_at,
            user_agent=user_agent,
            ip=ip,
        )

        await self.audit_repo.log_action(
            action="AUTH_SIGNUP",
            resource="users",
            actor_id=user_id,
            resource_id=user_id,
            ip=ip,
            user_agent=user_agent,
        )
        return user, access_token, raw_refresh

    async def login(
        self, data: UserLogin, ip: str | None = None, user_agent: str | None = None
    ) -> tuple[dict[str, Any], str, str]:
        normalized_email = data.email.strip().lower()
        user = await self.user_repo.get_by_email(normalized_email)

        # Constant-time prevention against account enumeration
        if not user:
            # Dummy hash comparison to mitigate timing attacks
            verify_password(
                "dummy-password",
                "$2b$12$e8YJq5N0V1aZ9r1c7yq9re3gV4j5l6m7n8o9p0q1r2s3t4u5v6w7x",
            )
            raise UnauthorizedException(
                "Invalid email or password.", code="INVALID_CREDENTIALS"
            )

        # Check account lockout
        locked_until = user.get("locked_until")
        now = datetime.now(UTC)
        if locked_until:
            if locked_until.tzinfo is None:
                locked_until = locked_until.replace(tzinfo=UTC)
            if locked_until > now:
                remaining_mins = max(1, int((locked_until - now).total_seconds() / 60))
                raise ForbiddenException(
                    f"Account temporarily locked due to multiple failed login attempts. Try again in {remaining_mins} minutes.",
                    code="ACCOUNT_LOCKED",
                )

        if not verify_password(data.password, user["password_hash"]):
            updated = await self.user_repo.increment_failed_login(
                user["id"], lock_threshold=5, lock_minutes=15
            )
            await self.audit_repo.log_action(
                action="AUTH_LOGIN_FAILED",
                resource="users",
                actor_id=user["id"],
                ip=ip,
                user_agent=user_agent,
            )
            updated_locked = updated.get("locked_until")
            if updated_locked:
                if updated_locked.tzinfo is None:
                    updated_locked = updated_locked.replace(tzinfo=UTC)
                if updated_locked > now:
                    raise ForbiddenException(
                        "Account temporarily locked due to multiple failed attempts. Try again in 15 minutes.",
                        code="ACCOUNT_LOCKED",
                    )
            raise UnauthorizedException(
                "Invalid email or password.", code="INVALID_CREDENTIALS"
            )

        if not user.get("is_active", True):
            raise ForbiddenException(
                "Account is disabled. Please contact support.", code="ACCOUNT_DISABLED"
            )

        # Reset failed attempts and update last login
        user_id = user["id"]
        await self.user_repo.reset_failed_login(user_id)

        access_token = create_access_token(user_id, role=user.get("role", "user"))
        raw_refresh, family_id, expires_at = create_refresh_token(user_id)
        await self.token_repo.save_refresh_token(
            user_id=user_id,
            token_hash=hash_token(raw_refresh),
            family_id=family_id,
            expires_at=expires_at,
            user_agent=user_agent,
            ip=ip,
        )

        await self.audit_repo.log_action(
            action="AUTH_LOGIN_SUCCESS",
            resource="users",
            actor_id=user_id,
            ip=ip,
            user_agent=user_agent,
        )
        return user, access_token, raw_refresh

    async def refresh_tokens(
        self,
        raw_refresh_token: str,
        ip: str | None = None,
        user_agent: str | None = None,
    ) -> tuple[str, str]:
        t_hash = hash_token(raw_refresh_token)
        stored_token = await self.token_repo.get_refresh_token(t_hash)
        if not stored_token:
            raise UnauthorizedException("Invalid refresh token.", code="TOKEN_INVALID")

        family_id = stored_token["family_id"]
        # Check token reuse: if token is already revoked, revoke entire family!
        if stored_token.get("revoked", False):
            await self.token_repo.revoke_token_family(family_id)
            logger.warning(
                f"Detected refresh token reuse for family {family_id}. Revoked all tokens in family."
            )
            raise UnauthorizedException(
                "Refresh token reuse detected. Please log in again.",
                code="TOKEN_REUSE_DETECTED",
            )

        # Check expiration
        expires_at = stored_token["expires_at"]
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=UTC)
        if expires_at <= datetime.now(UTC):
            raise UnauthorizedException(
                "Refresh token expired. Please log in again.", code="TOKEN_EXPIRED"
            )

        user_id = stored_token["user_id"]
        user = await self.user_repo.get_by_id(user_id)
        if not user or not user.get("is_active", True):
            raise UnauthorizedException(
                "User account inactive or not found.", code="USER_INACTIVE"
            )

        # Revoke the used refresh token (single-use rotation)
        await self.token_repo.revoke_refresh_token(t_hash)

        # Issue new token pair
        new_access = create_access_token(user_id, role=user.get("role", "user"))
        new_raw_refresh, _, new_expires = create_refresh_token(
            user_id, family_id=family_id
        )
        await self.token_repo.save_refresh_token(
            user_id=user_id,
            token_hash=hash_token(new_raw_refresh),
            family_id=family_id,
            expires_at=new_expires,
            user_agent=user_agent,
            ip=ip,
        )
        return new_access, new_raw_refresh

    async def logout(self, raw_refresh_token: str | None, user_id: str) -> None:
        if raw_refresh_token:
            t_hash = hash_token(raw_refresh_token)
            await self.token_repo.revoke_refresh_token(t_hash)
        await self.audit_repo.log_action(
            action="AUTH_LOGOUT", resource="users", actor_id=user_id
        )

    async def get_profile(self, user_id: str) -> dict[str, Any]:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User profile not found.", code="USER_NOT_FOUND")

        contacts_count = await self.contact_repo.count_by_user(user_id)
        active_sos = await self.sos_repo.get_active_by_user(user_id)

        user["emergency_contacts_count"] = contacts_count
        user["has_active_sos"] = active_sos is not None
        return user

    async def forgot_password(self, email: str, ip: str | None = None) -> None:
        normalized = email.strip().lower()
        user = await self.user_repo.get_by_email(normalized)
        if not user:
            # Prevent email harvesting: return silently
            return

        raw_reset_token = generate_secure_token(32)
        r_hash = hash_token(raw_reset_token)
        now = datetime.now(UTC)
        from datetime import timedelta

        expires_at = now + timedelta(minutes=15)

        await self.token_repo.save_password_reset(user["id"], r_hash, expires_at)
        logger.info(
            f"[DEV CONSOLE EMAIL] Password reset token for {normalized}: {raw_reset_token}"
        )
        await self.audit_repo.log_action(
            action="AUTH_FORGOT_PASSWORD_REQUEST",
            resource="users",
            actor_id=user["id"],
            ip=ip,
        )

    async def reset_password(self, token: str, new_password: str) -> None:
        r_hash = hash_token(token)
        reset_doc = await self.token_repo.get_valid_password_reset(r_hash)
        if not reset_doc:
            raise ValidationException(
                "Invalid or expired password reset token.", code="INVALID_RESET_TOKEN"
            )

        user_id = reset_doc["user_id"]
        pwd_hash = hash_password(new_password)
        await self.user_repo.update_password(user_id, pwd_hash)
        await self.token_repo.mark_password_reset_used(r_hash)
        await self.audit_repo.log_action(
            action="AUTH_PASSWORD_RESET_SUCCESS", resource="users", actor_id=user_id
        )

    async def change_password(
        self, user_id: str, current_pwd: str, new_pwd: str
    ) -> None:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("User not found.")

        if not verify_password(current_pwd, user["password_hash"]):
            raise ValidationException(
                "Current password does not match.", code="INCORRECT_CURRENT_PASSWORD"
            )

        pwd_hash = hash_password(new_pwd)
        await self.user_repo.update_password(user_id, pwd_hash)
        await self.audit_repo.log_action(
            action="AUTH_PASSWORD_CHANGED", resource="users", actor_id=user_id
        )
