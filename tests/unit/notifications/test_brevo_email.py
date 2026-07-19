from __future__ import annotations

import json

import httpx
import pytest

from app.notifications.email import BrevoEmailSender, EmailDeliveryError, EmailMessage


def test_brevo_email_sender_posts_expected_payload() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(201, json={"messageId": "123"})

    client = httpx.Client(
        transport=httpx.MockTransport(handler),
        base_url="https://api.brevo.com",
    )
    sender = BrevoEmailSender(
        client=client,
        api_key="brevo-key",
        sender_email="no-reply@example.com",
        sender_name="BheemBhai",
    )

    sender.send(
        EmailMessage(
            to_email="admin@example.com",
            subject="Verify your account",
            html_content="<p>Hello</p>",
            text_content="Hello",
        )
    )

    assert len(requests) == 1
    request = requests[0]
    payload = json.loads(request.content.decode("utf-8"))
    assert request.url.path == "/v3/smtp/email"
    assert request.headers["api-key"] == "brevo-key"
    assert payload["sender"] == {"email": "no-reply@example.com", "name": "BheemBhai"}
    assert payload["to"] == [{"email": "admin@example.com"}]
    assert payload["subject"] == "Verify your account"
    assert payload["htmlContent"] == "<p>Hello</p>"
    assert payload["textContent"] == "Hello"


def test_brevo_email_sender_raises_on_http_error() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(401, text="unauthorized")

    client = httpx.Client(
        transport=httpx.MockTransport(handler),
        base_url="https://api.brevo.com",
    )
    sender = BrevoEmailSender(
        client=client,
        api_key="brevo-key",
        sender_email="no-reply@example.com",
        sender_name="BheemBhai",
    )

    with pytest.raises(EmailDeliveryError):
        sender.send(
            EmailMessage(
                to_email="admin@example.com",
                subject="Verify your account",
                html_content="<p>Hello</p>",
            )
        )
