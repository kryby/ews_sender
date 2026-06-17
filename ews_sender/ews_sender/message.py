"""Email message models for ews_sender."""

import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import List, Optional, Union

from ews_sender.exceptions import ConfigurationError
from ews_sender.utils import validate_attachment_path


class Importance(Enum):
    """Email importance levels."""

    LOW = "Low"
    NORMAL = "Normal"
    HIGH = "High"


class BodyType(Enum):
    """Email body content types."""

    PLAIN = "Plain"
    HTML = "HTML"


@dataclass
class Attachment:
    """Represents an email attachment.

    Attributes:
        path: Path to the file to attach.
        name: Optional custom name for the attachment.
        content_id: Optional Content-ID for inline attachments.
    """

    path: Union[str, Path]
    name: Optional[str] = None
    content_id: Optional[str] = None

    def __post_init__(self):
        """Validate and normalize attachment after initialization."""
        self.path = validate_attachment_path(self.path)
        if self.name is None:
            self.name = self.path.name

    @property
    def size(self) -> int:
        """Return the attachment file size in bytes."""
        return self.path.stat().st_size


@dataclass
class EmailMessage:
    """Represents an email message to be sent via EWS.

    Attributes:
        to: List of recipient email addresses.
        subject: Email subject line.
        body: Email body content.
        cc: Optional list of CC recipient addresses.
        bcc: Optional list of BCC recipient addresses.
        attachments: Optional list of Attachment objects.
        importance: Email importance level.
        body_type: Body content type (plain or HTML).
    """

    to: List[str]
    subject: str
    body: str
    cc: List[str] = field(default_factory=list)
    bcc: List[str] = field(default_factory=list)
    attachments: List[Attachment] = field(default_factory=list)
    importance: Importance = Importance.NORMAL
    body_type: BodyType = BodyType.HTML

    def __post_init__(self):
        """Validate email addresses and required fields after initialization."""
        if not self.to:
            raise ConfigurationError("At least one recipient is required")
        if not self.subject or not self.subject.strip():
            raise ConfigurationError("Subject cannot be empty")
        for addr in self.to:
            self._validate_email(addr)
        for addr in self.cc:
            self._validate_email(addr)
        for addr in self.bcc:
            self._validate_email(addr)

    @staticmethod
    def _validate_email(email: str) -> None:
        """Validate a single email address format.

        Args:
            email: Email address to validate.

        Raises:
            ConfigurationError: If email format is invalid.
        """
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(pattern, email):
            raise ConfigurationError(f"Invalid email address format: {email}")

    @property
    def all_recipients(self) -> List[str]:
        """Return all recipient email addresses (to, cc, bcc combined)."""
        return self.to + self.cc + self.bcc

    @property
    def has_attachments(self) -> bool:
        """Check if the message has any attachments."""
        return len(self.attachments) > 0
