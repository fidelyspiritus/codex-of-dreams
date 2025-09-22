# app/common/auth.py
from __future__ import annotations
from app.core.config import settings

# cache the admin set once on import
_ADMIN_SET: set[int] = set(settings.ADMIN_IDS or [])

def is_admin(user_id: int | None) -> bool:
    """Fast membership check using a cached set."""
    return user_id is not None and user_id in _ADMIN_SET
