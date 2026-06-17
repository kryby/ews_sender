"""ews_sender - Module for sending emails via EWS/Exchange Online."""

from ews_sender.client import EWSClient
from ews_sender.exceptions import (
    AttachmentError,
    AuthenticationError,
    ConfigurationError,
    EWSSenderError,
    MessageSendError,
)
from ews_sender.message import Attachment, BodyType, EmailMessage, Importance

__all__ = [
    "EWSClient",
    "EWSSenderError",
    "AuthenticationError",
    "MessageSendError",
    "AttachmentError",
    "ConfigurationError",
    "EmailMessage",
    "Attachment",
    "Importance",
    "BodyType",
]

__version__ = "0.1.0"
