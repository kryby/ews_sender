"""Custom exceptions for ews_sender."""


class EWSSenderError(Exception):
    """Base exception for ews_sender module."""

    pass


class AuthenticationError(EWSSenderError):
    """Raised when authentication with Exchange Online fails."""

    pass


class MessageSendError(EWSSenderError):
    """Raised when sending an email message fails."""

    pass


class AttachmentError(EWSSenderError):
    """Raised when handling attachments fails."""

    pass


class ConfigurationError(EWSSenderError):
    """Raised when configuration is invalid or missing."""

    pass
