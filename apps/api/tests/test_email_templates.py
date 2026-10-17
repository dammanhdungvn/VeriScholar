"""Test Academic Luxury email templates generation and rendering."""

from api.templates.email_templates import (
    render_password_reset_email,
    render_password_reset_text,
    render_verification_email,
    render_verification_text,
)


def test_render_verification_email_structure() -> None:
    """Verify HTML table structure, colors, OTP grid, and ISO compliance in verification email."""
    email = "prof.smith@oxford.ac.uk"
    code = "729415"
    verify_url = "https://verischolar.duckdns.org/verify-email?token=mock_token&email=prof.smith@oxford.ac.uk"

    html = render_verification_email(email=email, code=code, verify_url=verify_url)

    # 1. Academic Luxury Palette checks
    assert "#0f172a" in html  # Slate-900
    assert "#b45309" in html  # Amber-700
    assert "#faf9f5" in html  # Luxury linen background
    assert "#ffffff" in html  # Card background

    # 2. Table-based layout checks
    assert '<table role="presentation"' in html
    assert 'class="email-container"' in html

    # 3. OTP 6-Digit Grid cells
    for digit in code:
        assert f">{digit}</td>" in html or f">{digit} </td>" in html

    # 4. CTA Button & Target URL
    assert verify_url in html
    assert "Kích hoạt tài khoản" in html
    assert "(1-Click)" not in html
    assert "Xác thực tài khoản tại đây (Verify Account)" in html

    # 5. Header and Footer Compliance
    assert "VeriScholar" in html
    assert "Nền tảng AI Nghiên cứu &amp; Phản biện Khoa học Chuẩn mực" in html
    assert "ISO 32000-1" in html
    assert email in html

    # Plain text check
    text = render_verification_text(email=email, code=code, verify_url=verify_url)
    assert code in text
    assert verify_url in text
    assert "(1-Click)" not in text
    assert "ISO 32000-1" in text


def test_render_password_reset_email_structure() -> None:
    """Verify HTML table structure, security notice, and CTA in password reset email."""
    email = "researcher@stanford.edu"
    code = "483921"
    reset_url = "https://verischolar.duckdns.org/reset-password?token=mock_reset&email=researcher@stanford.edu"

    html = render_password_reset_email(email=email, code=code, reset_url=reset_url)

    # 1. Palette & Typography
    assert "#0f172a" in html
    assert "#b45309" in html
    assert "#faf9f5" in html
    assert "BẢO MẬT &amp; KHÔI PHỤC TÀI KHOẢN" in html

    # 2. OTP Code Display
    for digit in code:
        assert f">{digit}</td>" in html or f">{digit} </td>" in html

    # 3. CTA & Links
    assert reset_url in html
    assert "Đặt lại mật khẩu mới" in html
    assert "Đặt lại mật khẩu tại đây (Reset Password)" in html
    assert email in html
    assert "ISO 32000-1" in html

    # Plain text check
    text = render_password_reset_text(email=email, code=code, reset_url=reset_url)
    assert code in text
    assert reset_url in text
    assert email in text
