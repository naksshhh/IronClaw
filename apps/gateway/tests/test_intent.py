"""Chat routing should not treat compliments as job applications."""

from ironclaw.utils.intent import is_job_intent


def test_compliment_is_not_a_job_search():
    assert is_job_intent("good job") is False
    assert is_job_intent("nice job on the wallpaper") is False
    assert is_job_intent("my job is done") is False


def test_job_search_phrases_match():
    assert is_job_intent("find me a job") is True
    assert is_job_intent("Apply for jobs") is True
    assert is_job_intent("parse this resume") is True
    assert is_job_intent("I need a job") is True


def test_unrelated_apply_is_not_job_hunting():
    assert is_job_intent("apply this wallpaper") is False
    assert is_job_intent("apply it") is False
