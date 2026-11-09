"""Notification dispatch helpers for SMS and email providers."""

import smtplib
from email.message import EmailMessage
from typing import Any

import httpx
from backend.app.core.config import settings
from backend.app.core.logging import logger


class NotificationService:
    """Dispatch notifications through configured providers with safe dev fallback."""

    @property
    def sms_enabled(self) -> bool:
        return bool(
            settings.ENABLE_REAL_NOTIFICATIONS
            and settings.TWILIO_ACCOUNT_SID
            and settings.TWILIO_AUTH_TOKEN
            and settings.TWILIO_FROM_NUMBER
        )

    @property
    def email_enabled(self) -> bool:
        return bool(
            settings.ENABLE_REAL_NOTIFICATIONS
            and settings.SMTP_HOST
            and settings.SMTP_USER
            and settings.SMTP_PASSWORD
            and "placeholder" not in settings.SMTP_PASSWORD.lower()
        )

    async def send_sms(self, to_phone: str, body: str) -> str:
        """Send one SMS. Returns SENT when real dispatch succeeds, otherwise LOGGED."""
        normalized = to_phone if to_phone.startswith("+") else f"+91{to_phone}"
        if not self.sms_enabled:
            logger.info("[SMS LOGGED] To: %s -> %s", normalized, body)
            return "LOGGED"

        url = (
            "https://api.twilio.com/2010-04-01/Accounts/"
            f"{settings.TWILIO_ACCOUNT_SID}/Messages.json"
        )
        payload = {
            "From": settings.TWILIO_FROM_NUMBER,
            "To": normalized,
            "Body": body,
        }
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                url,
                data=payload,
                auth=(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN),
            )
            response.raise_for_status()
        return "SENT"

    async def send_sos_alerts(
        self,
        contacts: list[dict[str, Any]],
        latitude: float,
        longitude: float,
        message: str | None,
    ) -> list[dict[str, Any]]:
        """Notify all emergency contacts and return contact snapshots."""
        map_link = f"https://maps.google.com/?q={latitude},{longitude}"
        alert_body = (
            "SAKHISAHAY EMERGENCY ALERT: A trusted contact needs help. "
            f"Location: {latitude:.6f},{longitude:.6f}. Map: {map_link}. "
            f"Message: {message or 'Please contact immediately.'}"
        )

        snapshots: list[dict[str, Any]] = []
        for contact in contacts:
            status = "FAILED"
            try:
                status = await self.send_sms(contact["phone"], alert_body)
            except Exception as exc:
                logger.exception(
                    "SOS SMS dispatch failed for contact %s: %s",
                    contact.get("id", contact.get("name", "unknown")),
                    exc,
                )

            snapshots.append(
                {
                    "name": contact["name"],
                    "phone": contact["phone"],
                    "relationship": contact["relationship"],
                    "dispatch_status": status,
                }
            )
        return snapshots

    async def send_password_reset_email(self, email: str, reset_url: str) -> str:
        """Send password reset email or log it in development."""
        subject = "Reset your SAKHISAHAY password"
        body = (
            "We received a request to reset your SAKHISAHAY password.\n\n"
            f"Open this link within 15 minutes:\n{reset_url}\n\n"
            "If you did not request this, you can ignore this email."
        )

        if not self.email_enabled:
            logger.info("[EMAIL LOGGED] To: %s | %s | %s", email, subject, reset_url)
            return "LOGGED"

        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = settings.EMAIL_FROM
        message["To"] = email
        message.set_content(body)

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as smtp:
            if settings.SMTP_TLS:
                smtp.starttls()
            smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            smtp.send_message(message)
        return "SENT"
