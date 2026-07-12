from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import httpx


@dataclass(frozen=True, slots=True)
class EmailMessage:
    to_email: str
    subject: str
    html_content: str
    text_content: str | None = None


class EmailSender(Protocol):
    def send(self, message: EmailMessage) -> None: ...


class EmailDeliveryError(RuntimeError):
    pass


@dataclass(slots=True)
class BrevoEmailSender:
    client: httpx.Client
    api_key: str
    sender_email: str
    sender_name: str
    base_url: str = "https://api.brevo.com"

    @classmethod
    def from_settings(cls, settings: object) -> BrevoEmailSender:
        api_key = getattr(settings, "brevo_api_key", "") or ""
        sender_email = getattr(settings, "brevo_sender_email", "") or ""
        sender_name = getattr(settings, "brevo_sender_name", "") or ""
        if not api_key or not sender_email:
            raise ValueError("Brevo email settings are required")
        return cls(
            client=httpx.Client(timeout=10.0),
            api_key=api_key,
            sender_email=sender_email,
            sender_name=sender_name or sender_email,
        )

    def send(self, message: EmailMessage) -> None:
        payload: dict[str, object] = {
            "sender": {"email": self.sender_email, "name": self.sender_name},
            "to": [{"email": message.to_email}],
            "subject": message.subject,
            "htmlContent": message.html_content,
        }
        if message.text_content is not None:
            payload["textContent"] = message.text_content

        try:
            response = self.client.post(
                f"{self.base_url.rstrip('/')}/v3/smtp/email",
                headers={
                    "api-key": self.api_key,
                    "accept": "application/json",
                    "content-type": "application/json",
                },
                json=payload,
            )
            response.raise_for_status()
        except httpx.RequestError as exc:
            raise EmailDeliveryError(f"Brevo email delivery failed: {exc}") from exc
        except httpx.HTTPStatusError as exc:
            details = exc.response.text.strip()
            if len(details) > 200:
                details = f"{details[:197]}..."
            raise EmailDeliveryError(
                f"Brevo rejected email delivery with status {exc.response.status_code}"
                + (f": {details}" if details else "")
            ) from exc
