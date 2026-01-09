"""Email sender for notification delivery.

Supports multiple email providers:
- Resend (primary)
- SendGrid (fallback)
- SMTP (local/testing)
"""

import os
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)

# Email provider configuration
EMAIL_PROVIDER = os.getenv("EMAIL_PROVIDER", "resend")  # resend, sendgrid, smtp
RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", "")
SMTP_HOST = os.getenv("SMTP_HOST", "localhost")
SMTP_PORT = int(os.getenv("SMTP_PORT", "1025"))  # MailHog default
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

# Email configuration
FROM_EMAIL = os.getenv("FROM_EMAIL", "notifications@todoapp.local")
FROM_NAME = os.getenv("FROM_NAME", "Todo App")


class EmailSender:
    """
    Email sender with support for multiple providers.

    Automatically selects provider based on environment configuration.
    """

    def __init__(self):
        self._provider = EMAIL_PROVIDER.lower()
        self._initialized = False
        self._client = None
        self._initialize_provider()

    def _initialize_provider(self):
        """Initialize the configured email provider."""
        try:
            if self._provider == "resend" and RESEND_API_KEY:
                try:
                    import resend
                    resend.api_key = RESEND_API_KEY
                    self._client = resend
                    self._initialized = True
                    logger.info("Initialized Resend email provider")
                except ImportError:
                    logger.warning("resend package not installed, falling back to SMTP")
                    self._provider = "smtp"

            elif self._provider == "sendgrid" and SENDGRID_API_KEY:
                try:
                    from sendgrid import SendGridAPIClient
                    self._client = SendGridAPIClient(SENDGRID_API_KEY)
                    self._initialized = True
                    logger.info("Initialized SendGrid email provider")
                except ImportError:
                    logger.warning("sendgrid package not installed, falling back to SMTP")
                    self._provider = "smtp"

            if self._provider == "smtp":
                # SMTP doesn't need special initialization
                self._initialized = True
                logger.info(f"Using SMTP email provider ({SMTP_HOST}:{SMTP_PORT})")

        except Exception as e:
            logger.error(f"Failed to initialize email provider: {e}")
            self._initialized = False

    def is_ready(self) -> bool:
        """Check if the email sender is ready."""
        return self._initialized

    async def send_reminder_email(
        self,
        to_email: str,
        task_title: str,
        task_description: Optional[str],
        due_at: datetime,
    ) -> bool:
        """
        Send a reminder email for a task.

        Args:
            to_email: Recipient email address
            task_title: Title of the task
            task_description: Description of the task
            due_at: Due date/time of the task

        Returns:
            True if email was sent successfully
        """
        if not self._initialized:
            logger.error("Email provider not initialized")
            return False

        subject = f"Reminder: {task_title}"
        html_content = self._build_reminder_html(
            task_title=task_title,
            task_description=task_description,
            due_at=due_at,
        )
        text_content = self._build_reminder_text(
            task_title=task_title,
            task_description=task_description,
            due_at=due_at,
        )

        try:
            if self._provider == "resend":
                return await self._send_via_resend(
                    to_email=to_email,
                    subject=subject,
                    html_content=html_content,
                    text_content=text_content,
                )
            elif self._provider == "sendgrid":
                return await self._send_via_sendgrid(
                    to_email=to_email,
                    subject=subject,
                    html_content=html_content,
                    text_content=text_content,
                )
            else:
                return await self._send_via_smtp(
                    to_email=to_email,
                    subject=subject,
                    html_content=html_content,
                    text_content=text_content,
                )
        except Exception as e:
            logger.exception(f"Failed to send email to {to_email}: {e}")
            return False

    async def _send_via_resend(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str,
    ) -> bool:
        """Send email via Resend."""
        try:
            params = {
                "from": f"{FROM_NAME} <{FROM_EMAIL}>",
                "to": [to_email],
                "subject": subject,
                "html": html_content,
                "text": text_content,
            }
            response = self._client.Emails.send(params)
            logger.info(f"Sent email via Resend: {response.get('id', 'unknown')}")
            return True
        except Exception as e:
            logger.error(f"Resend error: {e}")
            raise

    async def _send_via_sendgrid(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str,
    ) -> bool:
        """Send email via SendGrid."""
        try:
            from sendgrid.helpers.mail import Mail, Email, To, Content

            message = Mail(
                from_email=Email(FROM_EMAIL, FROM_NAME),
                to_emails=To(to_email),
                subject=subject,
                plain_text_content=Content("text/plain", text_content),
                html_content=Content("text/html", html_content),
            )
            response = self._client.send(message)
            logger.info(f"Sent email via SendGrid: {response.status_code}")
            return response.status_code in (200, 201, 202)
        except Exception as e:
            logger.error(f"SendGrid error: {e}")
            raise

    async def _send_via_smtp(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str,
    ) -> bool:
        """Send email via SMTP."""
        import asyncio
        import smtplib

        def _send_sync():
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{FROM_NAME} <{FROM_EMAIL}>"
            msg["To"] = to_email

            # Attach both text and HTML versions
            msg.attach(MIMEText(text_content, "plain"))
            msg.attach(MIMEText(html_content, "html"))

            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
                if SMTP_USER and SMTP_PASSWORD:
                    server.login(SMTP_USER, SMTP_PASSWORD)
                server.sendmail(FROM_EMAIL, [to_email], msg.as_string())

            return True

        # Run SMTP in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, _send_sync)
        logger.info(f"Sent email via SMTP to {to_email}")
        return result

    def _build_reminder_html(
        self,
        task_title: str,
        task_description: Optional[str],
        due_at: datetime,
    ) -> str:
        """Build HTML content for reminder email."""
        description_html = ""
        if task_description:
            description_html = f"""
            <p style="color: #666; margin: 16px 0;">
                {task_description}
            </p>
            """

        due_formatted = due_at.strftime("%B %d, %Y at %I:%M %p")

        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 0; background-color: #f5f5f5;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background-color: #ffffff; border-radius: 8px; padding: 32px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <div style="text-align: center; margin-bottom: 24px;">
                <h1 style="color: #333; font-size: 24px; margin: 0;">⏰ Task Reminder</h1>
            </div>

            <div style="border-left: 4px solid #3b82f6; padding-left: 16px; margin: 24px 0;">
                <h2 style="color: #333; font-size: 18px; margin: 0 0 8px 0;">
                    {task_title}
                </h2>
                {description_html}
            </div>

            <div style="background-color: #f8f9fa; border-radius: 4px; padding: 16px; margin: 24px 0;">
                <p style="margin: 0; color: #666;">
                    <strong>Due:</strong> {due_formatted}
                </p>
            </div>

            <div style="text-align: center; margin-top: 32px;">
                <a href="#" style="display: inline-block; background-color: #3b82f6; color: #ffffff; text-decoration: none; padding: 12px 24px; border-radius: 6px; font-weight: 500;">
                    View Task
                </a>
            </div>

            <hr style="border: none; border-top: 1px solid #eee; margin: 32px 0;">

            <p style="color: #999; font-size: 12px; text-align: center; margin: 0;">
                You received this email because you have reminders enabled for your tasks.
                <br>
                <a href="#" style="color: #999;">Manage notification settings</a>
            </p>
        </div>
    </div>
</body>
</html>
"""

    def _build_reminder_text(
        self,
        task_title: str,
        task_description: Optional[str],
        due_at: datetime,
    ) -> str:
        """Build plain text content for reminder email."""
        due_formatted = due_at.strftime("%B %d, %Y at %I:%M %p")

        text = f"""
Task Reminder

{task_title}
"""
        if task_description:
            text += f"""
{task_description}
"""
        text += f"""
Due: {due_formatted}

---
You received this email because you have reminders enabled for your tasks.
"""
        return text.strip()


# Singleton instance
_email_sender: Optional[EmailSender] = None


def get_email_sender() -> EmailSender:
    """Get the singleton email sender instance."""
    global _email_sender
    if _email_sender is None:
        _email_sender = EmailSender()
    return _email_sender
