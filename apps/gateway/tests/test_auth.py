"""Gateway API authentication decisions."""

from ironclaw.utils.auth import access_decision, is_public_path


def test_health_and_openclaw_stay_public():
    assert is_public_path("/health")
    assert is_public_path("/openclaw/webhook")
    assert access_decision("/health", "GET", None, None) is None
    assert access_decision("/openclaw/webhook", "POST", None, "") is None


def test_unset_token_keeps_the_local_ui_working():
    assert access_decision("/api/chat", "POST", None, "") is None
    assert access_decision("/api/upload", "POST", None, None) is None


def test_api_rejects_missing_and_wrong_bearer():
    missing_status, _ = access_decision("/api/chat", "POST", None, "secret")
    assert missing_status == 401

    wrong_status, wrong_detail = access_decision("/api/upload", "POST", "Bearer nope", "secret")
    assert wrong_status == 403
    assert wrong_detail == "Invalid token"


def test_api_accepts_matching_bearer():
    assert access_decision("/api/v1/jobs/search-and-apply", "POST", "Bearer secret", "secret") is None


def test_socket_can_pass_the_token_as_a_query_parameter():
    assert access_decision("/api/v1/speech/ws/speech-to-text", "GET", None, "secret", "secret") is None
    status, _ = access_decision("/api/v1/speech/ws/speech-to-text", "GET", None, "secret", "nope")
    assert status == 403


def test_options_preflight_is_allowed():
    assert access_decision("/api/chat", "OPTIONS", None, "secret") is None
