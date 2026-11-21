"""Upload names cannot leave the upload directory."""

from pathlib import Path

import pytest

from ironclaw.utils.uploads import UploadRejected, resolve_upload_path, safe_upload_name


def test_basename_is_kept(tmp_path: Path):
    path = resolve_upload_path(tmp_path, "notes.pdf")
    assert path == (tmp_path / "notes.pdf").resolve()
    assert safe_upload_name("photo.PNG") == "photo.PNG"


@pytest.mark.parametrize(
    "filename",
    [
        "../../.env",
        "..\\..\\secrets.yaml",
        "/etc/passwd",
        "subdir/resume.pdf",
        "notes.pdf\x00.jpg",
        ".env",
        "payload.sh",
        "no-extension",
        "",
        "..",
    ],
)
def test_traversal_and_disallowed_types_are_rejected(tmp_path: Path, filename: str):
    with pytest.raises(UploadRejected):
        resolve_upload_path(tmp_path, filename)


def test_resolved_path_stays_inside_upload_dir(tmp_path: Path):
    path = resolve_upload_path(tmp_path, "resume.pdf")
    assert path.parent == tmp_path.resolve()
