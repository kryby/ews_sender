"""Tests for ews_sender package."""

import pytest
from unittest.mock import MagicMock, patch

from ews_sender import (
    EWSClient,
    EmailMessage,
    Attachment,
    Importance,
    BodyType,
    ConfigurationError,
    AuthenticationError,
    MessageSendError,
    AttachmentError,
)


class TestEmailMessage:
    """Tests for EmailMessage class."""

    def test_valid_email_message(self):
        """Test creating a valid email message."""
        msg = EmailMessage(
            to=["test@example.com"],
            subject="Test Subject",
            body="Test body",
        )
        assert msg.to == ["test@example.com"]
        assert msg.subject == "Test Subject"
        assert msg.body == "Test body"
        assert msg.cc == []
        assert msg.bcc == []
        assert msg.attachments == []
        assert msg.importance == Importance.NORMAL
        assert msg.body_type == BodyType.HTML

    def test_email_message_with_all_fields(self):
        """Test creating email message with all fields."""
        msg = EmailMessage(
            to=["to@example.com"],
            cc=["cc@example.com"],
            bcc=["bcc@example.com"],
            subject="Subject",
            body="Body",
            importance=Importance.HIGH,
            body_type=BodyType.PLAIN,
        )
        assert msg.to == ["to@example.com"]
        assert msg.cc == ["cc@example.com"]
        assert msg.bcc == ["bcc@example.com"]
        assert msg.importance == Importance.HIGH
        assert msg.body_type == BodyType.PLAIN

    def test_email_message_requires_recipient(self):
        """Test that at least one recipient is required."""
        with pytest.raises(ConfigurationError):
            EmailMessage(to=[], subject="Test", body="Body")

    def test_email_message_requires_subject(self):
        """Test that subject cannot be empty."""
        with pytest.raises(ConfigurationError):
            EmailMessage(to=["test@example.com"], subject="", body="Body")

    def test_email_message_invalid_email_format(self):
        """Test that invalid email format raises error."""
        with pytest.raises(ConfigurationError):
            EmailMessage(to=["invalid-email"], subject="Test", body="Body")

    def test_all_recipients(self):
        """Test all_recipients property."""
        msg = EmailMessage(
            to=["to1@example.com", "to2@example.com"],
            cc=["cc@example.com"],
            bcc=["bcc@example.com"],
            subject="Test",
            body="Body",
        )
        assert msg.all_recipients == [
            "to1@example.com",
            "to2@example.com",
            "cc@example.com",
            "bcc@example.com",
        ]

    def test_has_attachments_false(self):
        """Test has_attachments returns False when no attachments."""
        msg = EmailMessage(to=["test@example.com"], subject="Test", body="Body")
        assert msg.has_attachments is False


class TestAttachment:
    """Tests for Attachment class."""

    @patch("ews_sender.message.validate_attachment_path")
    def test_attachment_creation(self, mock_validate):
        """Test creating an attachment."""
        mock_path = MagicMock()
        mock_path.name = "test.pdf"
        mock_path.stat.return_value.st_size = 1024
        mock_validate.return_value = mock_path

        attachment = Attachment(path="test.pdf")
        assert attachment.name == "test.pdf"
        assert attachment.path == mock_path

    @patch("ews_sender.message.validate_attachment_path")
    def test_attachment_custom_name(self, mock_validate):
        """Test attachment with custom name."""
        mock_path = MagicMock()
        mock_path.name = "original.pdf"
        mock_path.stat.return_value.st_size = 1024
        mock_validate.return_value = mock_path

        attachment = Attachment(path="original.pdf", name="custom_name.pdf")
        assert attachment.name == "custom_name.pdf"


class TestEWSClient:
    """Tests for EWSClient class."""

    def test_client_initialization(self):
        """Test client initialization with parameters."""
        client = EWSClient(
            tenant_id="test-tenant",
            client_id="test-client",
            client_secret="test-secret",
            account_email="sender@example.com",
        )
        assert client.tenant_id == "test-tenant"
        assert client.client_id == "test-client"
        assert client.client_secret == "test-secret"
        assert client.account_email == "sender@example.com"
        assert client.is_connected is False

    def test_client_not_connected_raises(self):
        """Test that send raises when not connected."""
        client = EWSClient(
            tenant_id="test-tenant",
            client_id="test-client",
            client_secret="test-secret",
            account_email="sender@example.com",
        )
        msg = EmailMessage(to=["test@example.com"], subject="Test", body="Body")
        with pytest.raises(AuthenticationError):
            client.send(msg)

    @patch("ews_sender.client.Account")
    @patch("ews_sender.client.Configuration")
    def test_client_connect_success(self, mock_config, mock_account):
        """Test successful connection."""
        mock_account_instance = MagicMock()
        mock_account.return_value = mock_account_instance

        client = EWSClient(
            tenant_id="test-tenant",
            client_id="test-client",
            client_secret="test-secret",
            account_email="sender@example.com",
        )
        client.connect()
        assert client.is_connected is True
        mock_account.assert_called_once()

    def test_client_close(self):
        """Test closing client connection."""
        client = EWSClient(
            tenant_id="test-tenant",
            client_id="test-client",
            client_secret="test-secret",
            account_email="sender@example.com",
        )
        with patch("ews_sender.client.Account"):
            client.connect()
        assert client.is_connected is True
        client.close()
        assert client.is_connected is False


class TestImportanceEnum:
    """Tests for Importance enum."""

    def test_importance_values(self):
        """Test Importance enum values."""
        assert Importance.LOW.value == "Low"
        assert Importance.NORMAL.value == "Normal"
        assert Importance.HIGH.value == "High"


class TestBodyTypeEnum:
    """Tests for BodyType enum."""

    def test_body_type_values(self):
        """Test BodyType enum values."""
        assert BodyType.PLAIN.value == "Plain"
        assert BodyType.HTML.value == "HTML"
