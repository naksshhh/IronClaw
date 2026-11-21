"""Safe names for files saved under the upload directory."""

from __future__ import annotations

from pathlib import Path

MAX_UPLOAD_BYTES = 16 * 1024 * 1024

ALLOWED_SUFFIXES = {
    ".pdf",
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".gif",
    ".txt",
    ".webm",
    ".wav",
    ".mp3",
    ".m4a",
}


class UploadRejected(ValueError):
    """The client filename is not safe to store or read."""


def safe_upload_name(filename: str) -> str:
    """Return a basename that cannot leave the upload directory.

    Directory pieces, null bytes, and suffixes outside the allowlist are
    rejected. The result is a single path segment.
    """
    if filename is None:
        raise UploadRejected("Filename is required")

    raw = str(filename).strip()
    if not raw:
        raise UploadRejected("Filename is required")
    # Reject instead of rewriting. A slash or a null byte is a path trick.
    if "\x00" in raw or "/" in raw or "\\" in raw:
        raise UploadRejected("Filename is not allowed")

    name = Path(raw).name
    if name in {"", ".", ".."} or name.startswith("."):
        raise UploadRejected("Filename is not allowed")
    if "/" in name or "\\" in name:
        raise UploadRejected("Filename is not allowed")

    suffix = Path(name).suffix.lower()
    if suffix not in ALLOWED_SUFFIXES:
        raise UploadRejected(f"File type '{suffix or '(none)'}' is not allowed")
    return name


def resolve_upload_path(upload_dir: Path, filename: str) -> Path:
    """Resolve filename inside upload_dir, or raise UploadRejected."""
    name = safe_upload_name(filename)
    root = upload_dir.resolve()
    candidate = (root / name).resolve()
    if candidate.parent != root:
        raise UploadRejected("Filename is not allowed")
    return candidate
