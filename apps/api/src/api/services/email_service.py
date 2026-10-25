"""Email Delivery Service for VeriScholar Authentication & Notifications.

Supports official Resend REST API delivery, SMTP fallback, and secure audit logging.
"""

import asyncio
import os
import smtplib
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import httpx
import structlog

try:
    from api.templates.email_templates import (
        render_password_reset_email,
        render_password_reset_text,
        render_verification_email,
        render_verification_text,
    )

    HAS_EMAIL_TEMPLATES = True
except ImportError:
    HAS_EMAIL_TEMPLATES = False

from api.core.config import ROOT_DIR, settings

logger = structlog.get_logger("api.services.email")

EMAIL_LOG_PATH = ROOT_DIR / "storage" / "logs" / "auth-emails.log"


class EmailService:
    """Service handling transactional emails (verification, OTP, password reset)."""

    def __init__(self) -> None:
        self.resend_api_key = settings.RESEND_API_KEY or os.getenv("RESEND_API_KEY", "")
        self.resend_from_email = (
            settings.RESEND_FROM_EMAIL
            or os.getenv("RESEND_FROM_EMAIL", "onboarding@resend.dev")
        )
        self.smtp_host = settings.SMTP_HOST or os.getenv("SMTP_HOST", "")
        self.smtp_port = int(settings.SMTP_PORT or os.getenv("SMTP_PORT", "587"))
        self.smtp_user = settings.SMTP_USER or os.getenv("SMTP_USER", "")
        self.smtp_password = settings.SMTP_PASSWORD or os.getenv("SMTP_PASSWORD", "")
        self.from_email = (
            settings.SMTP_FROM_EMAIL
            or os.getenv("SMTP_FROM_EMAIL", "onboarding@resend.dev")
        )
        self.from_name = (
            settings.SMTP_FROM_NAME
            or os.getenv("SMTP_FROM_NAME", "VeriScholar Academic Platform")
        )
        self.app_url = (
            settings.APP_PUBLIC_URL
            or os.getenv("APP_PUBLIC_URL", "https://verischolar.duckdns.org")
        )

        EMAIL_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    def _write_email_audit_log(
        self, recipient: str, subject: str, code: str, token: str, html_body: str
    ) -> None:
        """Record dispatched email to persistent audit log."""
        timestamp = datetime.now(timezone.utc).isoformat()
        log_entry = (
            f"\n{'=' * 75}\n"
            f"TIMESTAMP: {timestamp}\n"
            f"TO:        {recipient}\n"
            f"FROM:      {self.from_name} <{self.resend_from_email or self.from_email}>\n"
            f"SUBJECT:   {subject}\n"
            f"OTP CODE:  {code}\n"
            f"JWT TOKEN: {token}\n"
            f"{'-' * 75}\n"
            f"{html_body}\n"
            f"{'=' * 75}\n"
        )
        try:
            with open(EMAIL_LOG_PATH, "a", encoding="utf-8") as f:
                f.write(log_entry)
        except Exception as exc:
            logger.warning("email_audit_log_write_failed", error=str(exc))

    async def _send_resend(
        self, recipient: str, subject: str, html_content: str, text_content: str
    ) -> bool:
        """Send email asynchronously using the official Resend REST API."""
        headers = {
            "Authorization": f"Bearer {self.resend_api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "from": f"{self.from_name} <{self.resend_from_email}>",
            "to": [recipient],
            "subject": subject,
            "html": html_content,
            "text": text_content,
        }
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    "https://api.resend.com/emails",
                    headers=headers,
                    json=payload,
                )
                if response.status_code in (200, 201):
                    res_data = response.json()
                    logger.info(
                        "resend_email_dispatched_successfully",
                        recipient=recipient,
                        resend_id=res_data.get("id"),
                    )
                    return True
                else:
                    logger.warning(
                        "resend_delivery_non_200",
                        recipient=recipient,
                        status_code=response.status_code,
                        detail=response.text,
                    )
                    return False
        except Exception as exc:
            logger.error("resend_delivery_exception", error=str(exc), recipient=recipient)
            return False

    def _send_smtp_sync(
        self, recipient: str, subject: str, html_content: str, text_content: str
    ) -> bool:
        """Send email synchronously using smtplib."""
        if not self.smtp_host or not self.smtp_user:
            logger.info(
                "smtp_not_configured_falling_back_to_log",
                recipient=recipient,
                subject=subject,
            )
            return True

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{self.from_name} <{self.from_email}>"
        msg["To"] = recipient

        msg.attach(MIMEText(text_content, "plain", "utf-8"))
        msg.attach(MIMEText(html_content, "html", "utf-8"))

        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                if self.smtp_password:
                    server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.from_email, [recipient], msg.as_string())
            logger.info("smtp_email_dispatched_successfully", recipient=recipient)
            return True
        except Exception as exc:
            logger.error("smtp_delivery_failed", error=str(exc), recipient=recipient)
            return False

    async def _dispatch_email(
        self, recipient: str, subject: str, html_content: str, text_content: str
    ) -> bool:
        """Dispatch email according to priority: Resend API -> SMTP -> Audit Log Fallback."""
        # 1. Ưu tiên 1: SMTP nếu được cấu hình đầy đủ (như Google App Password)
        if self.smtp_host and self.smtp_user:
            ok = await asyncio.to_thread(
                self._send_smtp_sync, recipient, subject, html_content, text_content
            )
            if ok:
                return True
            logger.warning(
                "smtp_delivery_failed_falling_back_to_resend",
                recipient=recipient,
            )

        # 2. Ưu tiên 2: Resend API
        if self.resend_api_key:
            ok = await self._send_resend(recipient, subject, html_content, text_content)
            if ok:
                return True
            logger.info(
                "resend_failed_or_restricted_falling_back",
                recipient=recipient,
            )

        # 3. Fallback: Ghi audit log
        logger.info(
            "smtp_and_resend_not_configured_falling_back_to_log",
            recipient=recipient,
            subject=subject,
        )
        return True

    def _render_verification(self, email: str, code: str, verify_url: str) -> tuple[str, str]:
        """Render verification email HTML and text using custom or fallback template."""
        if HAS_EMAIL_TEMPLATES:
            try:
                html = render_verification_email(
                    email=email,
                    code=code,
                    verify_url=verify_url,
                    app_url=self.app_url,
                )
                text = render_verification_text(
                    email=email,
                    code=code,
                    verify_url=verify_url,
                    app_url=self.app_url,
                )
                return html, text
            except Exception as exc:
                logger.warning("custom_template_render_failed", error=str(exc))

        # Built-in fallback template
        text = (
            f"Chào bạn,\n\n"
            f"Cảm ơn bạn đã đăng ký tài khoản tại VeriScholar ({self.app_url}).\n"
            f"Mã OTP kích hoạt tài khoản của bạn là: {code}\n"
            f"Hoặc nhấp vào liên kết sau để kích hoạt trực tiếp:\n"
            f"{verify_url}\n\n"
            f"Mã này có hiệu lực trong vòng 15 phút.\n"
            f"Trân trọng,\nĐội ngũ VeriScholar."
        )
        html = (
            f"<html><body><h2>VeriScholar</h2><p>Mã OTP: <b>{code}</b></p>"
            f'<a href="{verify_url}">Kích hoạt tài khoản</a></body></html>'
        )
        return html, text

    def _render_password_reset(self, email: str, code: str, reset_url: str) -> tuple[str, str]:
        """Render password reset email HTML and text using custom or fallback template."""
        if HAS_EMAIL_TEMPLATES:
            try:
                html = render_password_reset_email(
                    email=email,
                    code=code,
                    reset_url=reset_url,
                    app_url=self.app_url,
                )
                text = render_password_reset_text(
                    email=email,
                    code=code,
                    reset_url=reset_url,
                    app_url=self.app_url,
                )
                return html, text
            except Exception as exc:
                logger.warning("custom_password_reset_render_failed", error=str(exc))

        # Built-in fallback template
        text = (
            f"Chào bạn,\n\n"
            f"Yêu cầu đặt lại mật khẩu cho tài khoản {email} tại {self.app_url}.\n"
            f"Mã xác thực của bạn là: {code}\n"
            f"Hoặc nhấp vào liên kết sau:\n{reset_url}\n\n"
            f"Trân trọng,\nĐội ngũ VeriScholar."
        )
        html = (
            f"<html><body><h2>VeriScholar</h2><p>Mã OTP đặt lại mật khẩu: <b>{code}</b></p>"
            f'<a href="{reset_url}">Đặt lại mật khẩu mới</a></body></html>'
        )
        return html, text

    async def send_verification_email(self, email: str, code: str, token: str) -> bool:
        """Send scholarly account verification email with 6-digit OTP and 1-click link."""
        verify_url = f"{self.app_url}/verify-email?token={token}&email={email}"
        subject = f"[{code}] Xác thực tài khoản nghiên cứu VeriScholar"

        html_content, text_content = self._render_verification(email, code, verify_url)

        self._write_email_audit_log(email, subject, code, token, html_content)
        return await self._dispatch_email(email, subject, html_content, text_content)

    async def send_password_reset_email(self, email: str, code: str, token: str) -> bool:
        """Send scholarly password recovery email with 6-digit OTP and reset link."""
        reset_url = f"{self.app_url}/reset-password?token={token}&email={email}"
        subject = f"[{code}] Yêu cầu đặt lại mật khẩu VeriScholar"

        html_content, text_content = self._render_password_reset(email, code, reset_url)

        self._write_email_audit_log(email, subject, code, token, html_content)
        return await self._dispatch_email(email, subject, html_content, text_content)
