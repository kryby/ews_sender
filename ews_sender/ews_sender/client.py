"""EWS Client for sending emails via Exchange Online."""

import logging
from typing import List, Optional

import exchangelib
from exchangelib import Account, Body, Configuration, FileAttachment, HTMLBody, Mailbox, Message
from exchangelib import DELEGATE, IMPERSONATION
from exchangelib.credentials import OAuth2Credentials

from ews_sender.exceptions import AuthenticationError, MessageSendError
from ews_sender.message import BodyType, EmailMessage, Importance


logger = logging.getLogger(__name__)


class EWSClient:
    """Client for sending emails via Exchange Web Services (EWS).

    Supports OAuth2 authentication with Azure AD application registration.

    Args:
        tenant_id: Azure AD tenant ID.
        client_id: Azure AD application (client) ID.
        client_secret: Azure AD application client secret.
        account_email: Email address of the sender account.
    """

    def __init__(
        self,
        tenant_id: str,
        client_id: str,
        client_secret: str,
        account_email: str,
    ):
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.account_email = account_email
        self._account: Optional[Account] = None

    def _get_oauth2_credentials(self) -> OAuth2Credentials:
        """Build OAuth2 credentials for authentication.

        Returns:
            OAuth2Credentials object for client credentials flow.
        """
        return OAuth2Credentials(
            client_id=self.client_id,
            client_secret=self.client_secret,
            tenant_id=self.tenant_id,
        )

    def _build_configuration(self) -> Configuration:
        """Build EWS configuration with OAuth2 credentials.

        Returns:
            Configuration object for exchangelib.
        """
        credentials = self._get_oauth2_credentials()
        return Configuration(
            credentials=credentials,
        )

    def connect(self) -> None:
        """Establish connection to Exchange Online.

        Raises:
            AuthenticationError: If connection fails.
        """
        try:
            config = self._build_configuration()
            self._account = Account(
                primary_smtp_address=self.account_email,
                config=config,
                autodiscover=True,
                access_type=IMPERSONATION,
            )
            logger.info("Successfully connected to Exchange Online as %s", self.account_email)
        except Exception as e:
            raise AuthenticationError(f"Failed to connect to Exchange Online: {e}") from e

    def _map_importance(self, importance: Importance) -> str:
        """Map our Importance enum to exchangelib importance.

        Args:
            importance: Our Importance enum value.

        Returns:
            exchangelib importance string.
        """
        mapping = {
            Importance.LOW: "Low",
            Importance.NORMAL: "Normal",
            Importance.HIGH: "High",
        }
        return mapping.get(importance, "Normal")

    def send(self, message: EmailMessage) -> None:
        """Send an email message via EWS.

        Args:
            message: EmailMessage object to send.

        Raises:
            AuthenticationError: If not connected or authentication fails.
            MessageSendError: If sending the message fails.
        """
        if self._account is None:
            raise AuthenticationError("Not connected. Call connect() first.")

        try:
            if message.body_type == BodyType.HTML:
                body = HTMLBody(message.body)
            else:
                body = Body(message.body)

            email = Message(
                account=self._account,
                subject=message.subject,
                body=body,
                to_recipients=[Mailbox(email_address=addr) for addr in message.to],
                cc_recipients=[Mailbox(email_address=addr) for addr in message.cc],
                bcc_recipients=[Mailbox(email_address=addr) for addr in message.bcc],
                importance=self._map_importance(message.importance),
            )

            for attachment in message.attachments:
                email.attach(
                    FileAttachment(
                        name=attachment.name,
                        content=attachment.path.read_bytes(),
                        content_id=attachment.content_id,
                    )
                )

            email.send_and_save()
            logger.info("Email sent successfully to %s", message.to)

        except Exception as e:
            raise MessageSendError(f"Failed to send email: {e}") from e

    def send_raw(self, subject: str, body: str, to: List[str], **kwargs) -> None:
        """Send a simple email without building EmailMessage object.

        Args:
            subject: Email subject.
            body: Email body.
            to: List of recipient addresses.
            **kwargs: Additional arguments passed to EmailMessage.
        """
        message = EmailMessage(to=to, subject=subject, body=body, **kwargs)
        self.send(message)

    @property
    def is_connected(self) -> bool:
        """Check if client is connected to Exchange Online."""
        return self._account is not None

    def close(self) -> None:
        """Close the connection to Exchange Online."""
        self._account = None
        logger.info("Connection closed")
