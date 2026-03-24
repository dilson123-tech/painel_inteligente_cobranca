from __future__ import annotations

import os
import smtplib
from email.message import EmailMessage
from typing import Iterable

try:
    import streamlit as st
except Exception:  # pragma: no cover
    st = None


REQUIRED_SMTP_VARS = [
    "SMTP_HOST",
    "SMTP_PORT",
    "SMTP_USERNAME",
    "SMTP_PASSWORD",
    "SMTP_FROM_EMAIL",
]


def _get_secret(name: str, default: str = "") -> str:
    value = str(os.getenv(name, "")).strip()
    if value:
        return value

    if st is not None:
        try:
            secret_value = st.secrets.get(name, default)
            return str(secret_value).strip()
        except Exception:
            return str(default).strip()

    return str(default).strip()


def get_missing_smtp_vars() -> list[str]:
    return [name for name in REQUIRED_SMTP_VARS if not _get_secret(name)]


def smtp_is_ready() -> bool:
    return len(get_missing_smtp_vars()) == 0


def build_email_message(
    *,
    to_email: str,
    subject: str,
    body: str,
    from_email: str | None = None,
) -> EmailMessage:
    sender = from_email or _get_secret("SMTP_FROM_EMAIL")
    if not sender:
        raise ValueError("SMTP_FROM_EMAIL não configurado.")
    if not str(to_email).strip():
        raise ValueError("Destinatário de e-mail vazio.")

    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = to_email.strip()
    msg["Subject"] = subject.strip()
    msg.set_content(body)
    return msg


def send_email(
    *,
    to_email: str,
    subject: str,
    body: str,
) -> dict:
    missing = get_missing_smtp_vars()
    if missing:
        raise RuntimeError("Configuração SMTP incompleta: " + ", ".join(missing))

    smtp_host = _get_secret("SMTP_HOST")
    smtp_port = int(_get_secret("SMTP_PORT", "587"))
    smtp_username = _get_secret("SMTP_USERNAME")
    smtp_password = _get_secret("SMTP_PASSWORD")
    smtp_use_tls = _get_secret("SMTP_USE_TLS", "true").lower() in {"1", "true", "yes", "sim"}
    smtp_use_ssl = _get_secret("SMTP_USE_SSL", "false").lower() in {"1", "true", "yes", "sim"}

    msg = build_email_message(
        to_email=to_email,
        subject=subject,
        body=body,
    )

    if smtp_use_ssl:
        with smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=20) as server:
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
    else:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=20) as server:
            server.ehlo()
            if smtp_use_tls:
                server.starttls()
                server.ehlo()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)

    return {
        "ok": True,
        "to_email": to_email.strip(),
        "subject": subject.strip(),
    }


def send_bulk_emails(
    *,
    recipients: Iterable[dict],
    subject: str,
) -> list[dict]:
    results: list[dict] = []

    for item in recipients:
        nome = str(item.get("nome", "")).strip()
        to_email = str(item.get("email", "")).strip()
        body = str(item.get("mensagem", "")).strip()

        if not to_email:
            results.append(
                {
                    "ok": False,
                    "nome": nome,
                    "email": to_email,
                    "erro": "Cliente sem e-mail.",
                }
            )
            continue

        try:
            response = send_email(
                to_email=to_email,
                subject=subject,
                body=body,
            )
            results.append(
                {
                    "ok": True,
                    "nome": nome,
                    "email": to_email,
                    "subject": response["subject"],
                }
            )
        except Exception as exc:
            results.append(
                {
                    "ok": False,
                    "nome": nome,
                    "email": to_email,
                    "erro": str(exc),
                }
            )

    return results
