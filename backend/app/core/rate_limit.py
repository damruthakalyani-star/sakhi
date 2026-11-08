"""Rate limiting configuration using SlowAPI."""

from backend.app.core.config import settings
from slowapi import Limiter
from slowapi.util import get_remote_address

# Global limiter instance keyed by client IP
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[settings.RATE_LIMIT_DEFAULT],
)
