"""Utility functions for ews_sender."""

import mimetypes
from pathlib import Path
from typing import Union

from ews_sender.exceptions import AttachmentError


def guess_mime_type(file_path: Union[str, Path]) -> str:
    """Guess MIME type from file extension.

    Args:
        file_path: Path to the file.

    Returns:
        MIME type string (e.g., 'application/pdf').
    """
    mime_type, _ = mimetypes.guess_type(str(file_path))
    return mime_type or "application/octet-stream"


def validate_attachment_path(file_path: Union[str, Path]) -> Path:
    """Validate that an attachment file exists and is readable.

    Args:
        file_path: Path to the attachment file.

    Returns:
        Path object if valid.

    Raises:
        AttachmentError: If file doesn't exist or isn't readable.
    """
    path = Path(file_path)
    if not path.exists():
        raise AttachmentError(f"Attachment file not found: {file_path}")
    if not path.is_file():
        raise AttachmentError(f"Attachment path is not a file: {file_path}")
    if not path.stat().st_size > 0:
        raise AttachmentError(f"Attachment file is empty: {file_path}")
    return path


def get_attachment_size(file_path: Union[str, Path]) -> int:
    """Get size of an attachment file in bytes.

    Args:
        file_path: Path to the attachment file.

    Returns:
        File size in bytes.
    """
    return Path(file_path).stat().st_size
