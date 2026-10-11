"""
PROJECTIQ - Secure Project Loader

Handles ZIP upload validation and extraction. The uploaded archive is
NEVER executed - it is only read from disk as bytes/text for static
analysis. This module is the single choke point for upload safety:

  - Rejects oversized archives
  - Rejects archives with too many files ("zip bomb" style abuse)
  - Blocks path traversal (../, absolute paths, Windows drive letters)
  - Skips ignored directories (node_modules, .git, venv, etc.)
  - Skips binary / irrelevant file extensions
"""

import io
import shutil
import time
import uuid
import zipfile
from pathlib import Path
from typing import Optional

from config import (
    PROJECTS_DIR, MAX_UPLOAD_BYTES, MAX_FILES_PER_PROJECT,
    IGNORED_DIRECTORIES, IGNORED_FILE_EXTENSIONS,
)


class UploadValidationError(Exception):
    """Raised when an uploaded archive fails a safety check."""


def _is_safe_member(name: str) -> bool:
    """Reject any zip member that could escape the extraction directory."""
    if not name or name.startswith("/") or name.startswith("\\"):
        return False
    if ":" in name:  # Windows drive letter, e.g. C:\
        return False
    parts = Path(name).parts
    if ".." in parts:
        return False
    return True


def _should_skip(path_parts: tuple) -> bool:
    return any(part in IGNORED_DIRECTORIES for part in path_parts)


def validate_zip_bytes(data: bytes) -> None:
    """Run pre-extraction safety checks on raw ZIP bytes."""
    if len(data) == 0:
        raise UploadValidationError("The uploaded file is empty.")
    if len(data) > MAX_UPLOAD_BYTES:
        mb = MAX_UPLOAD_BYTES // (1024 * 1024)
        raise UploadValidationError(f"The uploaded ZIP exceeds the {mb} MB limit.")
    if not zipfile.is_zipfile(io.BytesIO(data)):
        raise UploadValidationError("The uploaded file is not a valid ZIP archive.")


def extract_project_zip(data: bytes, project_display_name: str) -> Path:
    """
    Safely extract an uploaded ZIP's contents into a fresh, isolated
    storage directory and return that directory's path.
    """
    validate_zip_bytes(data)

    slug = "".join(c if c.isalnum() else "-" for c in project_display_name.lower())[:40].strip("-") or "project"
    unique_id = f"{slug}-{uuid.uuid4().hex[:8]}"
    target_dir = PROJECTS_DIR / unique_id
    target_dir.mkdir(parents=True, exist_ok=True)

    tmp_zip = target_dir / "_upload.zip"
    tmp_zip.write_bytes(data)

    extracted_count = 0
    try:
        try:
            zf_handle = zipfile.ZipFile(tmp_zip)
        except zipfile.BadZipFile as exc:
            raise UploadValidationError("The uploaded file is not a valid ZIP archive.") from exc

        with zf_handle as zf:
            members = zf.infolist()
            if len(members) > MAX_FILES_PER_PROJECT:
                raise UploadValidationError(
                    f"The archive contains {len(members)} entries, "
                    f"which exceeds the {MAX_FILES_PER_PROJECT} file safety limit."
                )

            for member in members:
                if member.is_dir():
                    continue
                if not _is_safe_member(member.filename):
                    continue  # silently skip unsafe paths rather than aborting the whole upload

                parts = Path(member.filename).parts
                if _should_skip(parts):
                    continue

                ext = Path(member.filename).suffix.lower()
                if ext in IGNORED_FILE_EXTENSIONS:
                    continue

                dest_path = (target_dir / member.filename).resolve()
                if not str(dest_path).startswith(str(target_dir.resolve())):
                    continue  # defense in depth against path traversal

                dest_path.parent.mkdir(parents=True, exist_ok=True)
                with zf.open(member) as source, open(dest_path, "wb") as out_file:
                    shutil.copyfileobj(source, out_file, length=1024 * 1024)
                extracted_count += 1
    finally:
        tmp_zip.unlink(missing_ok=True)

    if extracted_count == 0:
        shutil.rmtree(target_dir, ignore_errors=True)
        raise UploadValidationError(
            "No readable project files were found after filtering ignored "
            "directories and binary files. Please check the archive contents."
        )

    return target_dir


def delete_project_storage(storage_path: str) -> None:
    """Remove an extracted project's files from disk."""
    path = Path(storage_path)
    if path.exists() and path.is_relative_to(PROJECTS_DIR):
        shutil.rmtree(path, ignore_errors=True)


def unique_timestamp_suffix() -> str:
    return time.strftime("%Y%m%d-%H%M%S")
