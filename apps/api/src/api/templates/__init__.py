"""Email HTML & Text templates for VeriScholar Platform."""

from api.templates.email_templates import (
    render_password_reset_email,
    render_password_reset_text,
    render_verification_email,
    render_verification_text,
)

__all__ = [
    "render_password_reset_email",
    "render_password_reset_text",
    "render_verification_email",
    "render_verification_text",
]
