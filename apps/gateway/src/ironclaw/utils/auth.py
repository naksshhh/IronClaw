"""Request authentication decisions for the gateway.

The OpenClaw webhook keeps its own hook token. When IRONCLAW_API_TOKEN is
set, every other route except health and docs requires it. When it is unset
the existing local UI keeps working.
"""

from __future__ import annotations

import hmac
from typing import Optional

PUBLIC_EXACT = {"/", "/health", "/docs", "/redoc", "/openapi.json"}


def is_public_path(path: str) -> bool:
    """Routes that stay reachable without the API token."""
    if path in PUBLIC_EXACT:
        return True
    if path.startswith("/docs/") or path.startswith("/redoc"):
        return True
    if path.startswith("/openapi.json"):
        return True
    # OpenClaw authenticates with OPENCLAW_HOOK_TOKEN.
    if path == "/openclaw" or path.startswith("/openclaw/"):
        return True
    return False


def access_decision(
    path: str,
    method: str,
    authorization: Optional[str],
    api_token: Optional[str],
    query_token: Optional[str] = None,
) -> Optional[tuple[int, str]]:
    """Return an HTTP error for this request, or None when it may proceed.

    An empty token leaves the route open so a checkout with the existing .env
    still serves the web UI. A configured token is required on HTTP headers
    and, for browser sockets, the ``token`` query parameter.
    """
    if method.upper() == "OPTIONS" or is_public_path(path):
        return None

    expected = (api_token or "").strip()
    if not expected:
        return None

    presented = ""
    if authorization and authorization.startswith("Bearer "):
        presented = authorization.split(" ", 1)[1]
    elif query_token:
        presented = query_token
    else:
        return 401, "Missing authorization token"

    if not hmac.compare_digest(presented, expected):
        return 403, "Invalid token"
    return None
