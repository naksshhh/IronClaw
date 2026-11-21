"""OpenClaw must not accept the token that used to be hard-coded."""

import importlib
import os

from ironclaw.services.openclaw_service import OpenClawService


def test_service_distinguishes_missing_and_invalid_tokens():
    service = OpenClawService("test-secret-token")
    assert service.auth_error(None) == "Missing authorization token"
    assert service.auth_error("test-secret-token") == "Missing authorization token"
    assert service.auth_error("Bearer wrong-token") == "Invalid token"
    assert service.auth_error("Bearer test-secret-token") is None


def test_empty_hook_token_is_not_a_published_default():
    service = OpenClawService("")
    assert service.auth_error("Bearer dev-token-change-me") == "OPENCLAW_HOOK_TOKEN is not configured"
    assert service.validate_token("Bearer dev-token-change-me") is False


def test_router_disables_webhook_when_env_is_unset(monkeypatch):
    import ironclaw.api.openclaw as openclaw

    previous = os.environ.get("OPENCLAW_HOOK_TOKEN")
    monkeypatch.delenv("OPENCLAW_HOOK_TOKEN", raising=False)
    try:
        reloaded = importlib.reload(openclaw)
        assert reloaded._get_hook_token() is None
        assert reloaded._service is None
        source = open(reloaded.__file__, encoding="utf-8").read()
        assert "dev-token-change-me" not in source
    finally:
        if previous is None:
            os.environ.pop("OPENCLAW_HOOK_TOKEN", None)
        else:
            os.environ["OPENCLAW_HOOK_TOKEN"] = previous
        importlib.reload(openclaw)
