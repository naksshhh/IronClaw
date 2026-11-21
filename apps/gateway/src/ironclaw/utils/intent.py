"""Chat intent checks.

Bare substrings such as "job" or "apply" used to hijack unrelated messages
("good job", "apply this wallpaper"). These checks look for a job-seeking
phrase instead.
"""

from __future__ import annotations

import re

_COMPLIMENT_JOB = re.compile(r"\b(?:good|nice|great|excellent|awesome)\s+job\b", re.IGNORECASE)
_RESUME_WORD = re.compile(r"\b(?:resume|career|employment)\b", re.IGNORECASE)
_APPLY_WORD = re.compile(r"\b(?:apply|applying|application)\b", re.IGNORECASE)
_ROLE_WORD = re.compile(r"\b(?:job|jobs|role|position|career)\b", re.IGNORECASE)
_JOB_WORD = re.compile(r"\bjobs?\b", re.IGNORECASE)
_SEEKING_WORD = re.compile(
    r"\b(?:find|search|hunt|hunting|opening|posting|hiring|looking|need|wanted)\b",
    re.IGNORECASE,
)


def is_greeting(message: str) -> bool:
    return message.lower().strip() in {"hi", "hello", "hey"}


def is_organize_tabs(message: str) -> bool:
    text = message.lower()
    return "organize" in text and ("tab" in text or "chrome" in text)


def is_close_old_tabs(message: str) -> bool:
    text = message.lower()
    return (
        ("close" in text or "delete" in text)
        and "tab" in text
        and ("old" in text or "older" in text)
    )


def is_list_tabs(message: str) -> bool:
    text = message.lower()
    return "list" in text and "tab" in text


def is_job_intent(message: str) -> bool:
    """True when the message is asking to search or apply for work."""
    text = _COMPLIMENT_JOB.sub(" ", message)
    if _RESUME_WORD.search(text):
        return True
    if _APPLY_WORD.search(text) and _ROLE_WORD.search(text):
        return True
    if _JOB_WORD.search(text) and _SEEKING_WORD.search(text):
        return True
    return False
