"""Authentication decision for the job-hunter HTTP API."""

from __future__ import annotations

import hmac
from typing import Optional


def api_access_decision(
    authorization: Optional[str],
    api_token: Optional[str],
) -> Optional[tuple[int, str]]:
    """Return an HTTP error, or None when the request may proceed."""
    expected = (api_token or "").strip()
    # Unset token keeps the existing dashboard working. A set token is required.
    if not expected:
        return None
    if not authorization or not authorization.startswith("Bearer "):
        return 401, "Missing authorization token"
    presented = authorization.split(" ", 1)[1]
    if not hmac.compare_digest(presented, expected):
        return 403, "Invalid token"
    return None
