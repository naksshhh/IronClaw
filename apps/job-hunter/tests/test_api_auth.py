"""Job hunter API rejects callers who do not present its token."""

from job_hunter.security import api_access_decision


def test_unset_token_keeps_the_dashboard_working():
    assert api_access_decision(None, "") is None


def test_wrong_token_is_rejected():
    status, detail = api_access_decision("Bearer nope", "secret")
    assert status == 403
    assert detail == "Invalid token"


def test_matching_token_is_allowed():
    assert api_access_decision("Bearer secret", "secret") is None


def test_flask_api_uses_the_same_decision(monkeypatch):
    monkeypatch.setenv("JOB_HUNTER_API_TOKEN", "secret")
    from job_hunter.app import app

    client = app.test_client()
    missing = client.get("/api/applications/someone")
    assert missing.status_code == 401
    wrong = client.get(
        "/api/applications/someone",
        headers={"Authorization": "Bearer nope"},
    )
    assert wrong.status_code == 403
