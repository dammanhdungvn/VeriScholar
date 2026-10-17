"""Academic Luxury HTML & Plain-Text Email Templates for VeriScholar Platform.

Complies with institutional aesthetic standards:
- Dark Slate (#0f172a / #1e293b), Amber-700 (#b45309), Terracotta (#c25e3d), Linen (#faf9f5).
- Fully responsive table-based layouts compatible with Gmail, Apple Mail, Outlook (including MSO conditionals).
- Prominent 6-digit OTP grid boxes with monospace typography.
- Bulletproof CTA action buttons.
- Academic compliance footer citing ISO 32000-1 scientific evidence preservation.
"""

from typing import Final

COLOR_BG_PAGE: Final[str] = "#faf9f5"
COLOR_BG_CARD: Final[str] = "#ffffff"
COLOR_SLATE_900: Final[str] = "#0f172a"
COLOR_SLATE_800: Final[str] = "#1e293b"
COLOR_SLATE_700: Final[str] = "#334155"
COLOR_SLATE_500: Final[str] = "#64748b"
COLOR_SLATE_400: Final[str] = "#94a3b8"
COLOR_AMBER_700: Final[str] = "#b45309"
COLOR_AMBER_50: Final[str] = "#fffbeb"
COLOR_BORDER: Final[str] = "#e7e2db"


def _generate_otp_boxes_html(code: str) -> str:
    """Generate bulletproof 6-digit table cells for OTP code display."""
    clean_code = str(code).strip()
    digits = list(clean_code) if len(clean_code) == 6 else [clean_code]

    if len(digits) != 6:
        return f"""
        <table role="presentation" border="0" cellpadding="0" cellspacing="0" align="center" style="margin: 0 auto;">
            <tr>
                <td align="center" style="background-color: {COLOR_AMBER_50}; border: 2px dashed {COLOR_AMBER_700}; border-radius: 12px; padding: 14px 28px; font-family: 'Courier New', Courier, monospace; font-size: 32px; font-weight: 700; letter-spacing: 6px; color: {COLOR_SLATE_900};">
                    {clean_code}
                </td>
            </tr>
        </table>
        """

    cells_html = []
    for i, digit in enumerate(digits):
        cells_html.append(
            f'<td align="center" valign="middle" width="46" height="54" style="width: 46px; height: 54px; background-color: {COLOR_AMBER_50}; border: 2px solid {COLOR_AMBER_700}; border-radius: 10px; font-family: \'Courier New\', Courier, monospace; font-size: 28px; font-weight: 700; color: {COLOR_SLATE_900}; line-height: 54px; text-align: center; mso-line-height-rule: exactly;">{digit}</td>'
        )
        if i < 5:
            cells_html.append(
                '<td width="8" style="width: 8px; font-size: 1px; line-height: 1px;">&nbsp;</td>'
            )

    return f"""
    <table role="presentation" border="0" cellpadding="0" cellspacing="0" align="center" style="margin: 0 auto;">
        <tr>
            {"".join(cells_html)}
        </tr>
    </table>
    """


def render_verification_email(
    email: str,
    code: str,
    verify_url: str,
    app_url: str = "https://verischolar.duckdns.org",
) -> str:
    """Render Academic Luxury HTML email for Scholar Registration & OTP Verification."""
    otp_grid = _generate_otp_boxes_html(code)

    return f"""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="vi">
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="x-apple-disable-message-reformatting" />
    <title>[{code}] Xác thực tài khoản nghiên cứu VeriScholar</title>
    <style type="text/css">
        body, table, td, p, a, li, blockquote {{
            -ms-text-size-adjust: 100%;
            -webkit-text-size-adjust: 100%;
        }}
        table, td {{
            mso-table-lspace: 0pt;
            mso-table-rspace: 0pt;
        }}
        img {{
            -ms-interpolation-mode: bicubic;
            border: 0;
            outline: none;
            text-decoration: none;
        }}
        @media screen and (max-width: 600px) {{
            .email-container {{
                width: 100% !important;
                max-width: 100% !important;
                border-radius: 0 !important;
            }}
            .content-padding {{
                padding: 24px 18px !important;
            }}
            .header-padding {{
                padding: 28px 18px 24px 18px !important;
            }}
        }}
    </style>
</head>
<body style="margin: 0; padding: 0; background-color: {COLOR_BG_PAGE}; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; -webkit-font-smoothing: antialiased;">
    <div style="display: none; font-size: 1px; color: #ffffff; line-height: 1px; max-height: 0px; max-width: 0px; opacity: 0; overflow: hidden;">
        Mã xác thực tài khoản VeriScholar của bạn là {code}. Nhấp để kích hoạt tài khoản nghiên cứu.
    </div>

    <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: {COLOR_BG_PAGE};">
        <tr>
            <td align="center" style="padding: 40px 12px;">
                <!--[if (gte mso 9)|(IE)]>
                <table role="presentation" align="center" border="0" cellspacing="0" cellpadding="0" width="600">
                <tr>
                <td align="center" valign="top" width="600">
                <![endif]-->
                <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%" class="email-container" style="max-width: 600px; background-color: {COLOR_BG_CARD}; border-radius: 16px; border: 1px solid {COLOR_BORDER}; box-shadow: 0 10px 25px rgba(15, 23, 42, 0.06); overflow: hidden;">
                    <!-- 1. Header with Academic Luxury Banner -->
                    <tr>
                        <td align="center" class="header-padding" style="background: linear-gradient(135deg, {COLOR_SLATE_900} 0%, {COLOR_SLATE_800} 100%); padding: 36px 32px 30px 32px; border-bottom: 3px solid {COLOR_AMBER_700};">
                            <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%">
                                <tr>
                                    <td align="center">
                                        <table role="presentation" border="0" cellpadding="0" cellspacing="0" style="margin-bottom: 14px;">
                                            <tr>
                                                <td align="center" style="background-color: rgba(217, 119, 6, 0.2); border: 1px solid rgba(217, 119, 6, 0.4); border-radius: 20px; padding: 4px 14px;">
                                                    <span style="font-size: 11px; font-weight: 700; color: #fbbf24; text-transform: uppercase; letter-spacing: 1.5px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">HỆ THỐNG XÁC THỰC HỌC THUẬT</span>
                                                </td>
                                            </tr>
                                        </table>
                                        <h1 style="margin: 0; color: #ffffff; font-family: 'Georgia', Garamond, 'Times New Roman', serif; font-size: 30px; font-weight: 700; letter-spacing: -0.5px;">
                                            VeriScholar
                                        </h1>
                                        <p style="margin: 8px 0 0 0; color: {COLOR_SLATE_400}; font-size: 13px; font-weight: 400; letter-spacing: 0.3px;">
                                            Nền tảng AI Nghiên cứu &amp; Phản biện Khoa học Chuẩn mực
                                        </p>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>

                    <!-- 2. Content Body -->
                    <tr>
                        <td class="content-padding" style="padding: 38px 36px 32px 36px;">
                            <h2 style="margin: 0 0 14px 0; color: {COLOR_SLATE_900}; font-size: 21px; font-weight: 700; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; letter-spacing: -0.3px;">
                                Xác thực tài khoản nghiên cứu
                            </h2>
                            <p style="margin: 0 0 20px 0; color: {COLOR_SLATE_700}; font-size: 14px; line-height: 1.65;">
                                Kính chào Quý học giả, để đảm bảo tính toàn vẹn và thẩm quyền của cộng đồng nghiên cứu khoa học, vui lòng sử dụng mã xác thực OTP 6 chữ số dưới đây để kích hoạt tài khoản liên kết với địa chỉ <strong style="color: {COLOR_SLATE_900};">{email}</strong>:
                            </p>

                            <!-- OTP 6-Digit Grid Box -->
                            <div style="margin: 28px 0 16px 0; text-align: center;">
                                {otp_grid}
                            </div>
                            <p style="margin: 0 0 28px 0; text-align: center; color: {COLOR_SLATE_500}; font-size: 12px; font-family: monospace;">
                                Mã OTP: <strong style="color: {COLOR_SLATE_900}; letter-spacing: 2px;">{code}</strong> (nhấp đúp để sao chép)
                            </p>

                            <!-- Bulletproof CTA Button -->
                            <table role="presentation" border="0" cellpadding="0" cellspacing="0" align="center" style="margin: 0 auto 30px auto;">
                                <tr>
                                    <td align="center" style="border-radius: 12px; background-color: {COLOR_AMBER_700}; box-shadow: 0 6px 18px rgba(180, 83, 9, 0.35);">
                                        <a href="{verify_url}" target="_blank" style="display: inline-block; padding: 15px 36px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 15px; font-weight: 700; color: #ffffff; text-decoration: none; border-radius: 12px; background-color: {COLOR_AMBER_700}; border: 1px solid #92400e; letter-spacing: 0.3px;">
                                            Kích hoạt tài khoản &rarr;
                                        </a>
                                    </td>
                                </tr>
                            </table>

                            <!-- Security & Expiration Card -->
                            <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #fdfbf7; border: 1px solid #f3ece1; border-radius: 10px; margin-bottom: 24px;">
                                <tr>
                                    <td style="padding: 16px 18px;">
                                        <p style="margin: 0 0 8px 0; color: {COLOR_AMBER_700}; font-size: 12px; font-weight: 700;">
                                            &#9201; LƯU Ý BẢO MẬT HỌC THUẬT:
                                        </p>
                                        <p style="margin: 0; color: #78716c; font-size: 12px; line-height: 1.55;">
                                            &bull; Mã OTP và liên kết kích hoạt này có hiệu lực trong vòng <strong>15 phút</strong>.<br />
                                            &bull; Tuyệt đối không chia sẻ mã này cho bất kỳ ai để bảo vệ quyền tác giả và dữ liệu nghiên cứu.<br />
                                            &bull; Nếu Quý học giả không thực hiện yêu cầu đăng ký này, vui lòng bỏ qua bức thư.
                                        </p>
                                    </td>
                                </tr>
                            </table>

                            <!-- Fallback Link Section -->
                            <div style="border-top: 1px solid #f1ece4; padding-top: 20px; text-align: center;">
                                <p style="margin: 0 0 8px 0; color: {COLOR_SLATE_500}; font-size: 12px; line-height: 1.5;">
                                    Nếu nút bấm phía trên không phản hồi trong ứng dụng email của bạn:
                                </p>
                                <p style="margin: 0;">
                                    <a href="{verify_url}" target="_blank" style="display: inline-block; color: {COLOR_AMBER_700}; font-size: 13px; font-weight: 600; text-decoration: underline;">
                                        &#128279; Xác thực tài khoản tại đây (Verify Account) &rarr;
                                    </a>
                                </p>
                            </div>
                        </td>
                    </tr>

                    <!-- 3. Academic Compliance Footer -->
                    <tr>
                        <td align="center" style="background-color: #f8fafc; border-top: 1px solid #e2e8f0; padding: 26px 32px; text-align: center;">
                            <p style="margin: 0 0 6px 0; color: {COLOR_SLATE_700}; font-size: 12px; font-weight: 600;">
                                Chuẩn bảo mật chứng cứ khoa học ISO 32000-1 &bull; Đối soát trích dẫn phân tán
                            </p>
                            <p style="margin: 0 0 10px 0; color: {COLOR_SLATE_500}; font-size: 11px; line-height: 1.4;">
                                Thư điện tử tự động phát hành bởi VeriScholar Verification Service.<br />
                                Cổng truy cập trực tiếp: <a href="{app_url}" target="_blank" style="color: {COLOR_AMBER_700}; text-decoration: none;">{app_url}</a>
                            </p>
                            <p style="margin: 0; color: {COLOR_SLATE_400}; font-size: 11px;">
                                &copy; 2026 VeriScholar Platform. All rights reserved.
                            </p>
                        </td>
                    </tr>
                </table>
                <!--[if (gte mso 9)|(IE)]>
                </td>
                </tr>
                </table>
                <![endif]-->
            </td>
        </tr>
    </table>
</body>
</html>"""


def render_password_reset_email(
    email: str,
    code: str,
    reset_url: str,
    app_url: str = "https://verischolar.duckdns.org",
) -> str:
    """Render Academic Luxury HTML email for Password Reset & Credential Recovery."""
    otp_grid = _generate_otp_boxes_html(code)

    return f"""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="vi">
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="x-apple-disable-message-reformatting" />
    <title>[{code}] Yêu cầu đặt lại mật khẩu VeriScholar</title>
    <style type="text/css">
        body, table, td, p, a, li, blockquote {{
            -ms-text-size-adjust: 100%;
            -webkit-text-size-adjust: 100%;
        }}
        table, td {{
            mso-table-lspace: 0pt;
            mso-table-rspace: 0pt;
        }}
        img {{
            -ms-interpolation-mode: bicubic;
            border: 0;
            outline: none;
            text-decoration: none;
        }}
        @media screen and (max-width: 600px) {{
            .email-container {{
                width: 100% !important;
                max-width: 100% !important;
                border-radius: 0 !important;
            }}
            .content-padding {{
                padding: 24px 18px !important;
            }}
            .header-padding {{
                padding: 28px 18px 24px 18px !important;
            }}
        }}
    </style>
</head>
<body style="margin: 0; padding: 0; background-color: {COLOR_BG_PAGE}; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; -webkit-font-smoothing: antialiased;">
    <div style="display: none; font-size: 1px; color: #ffffff; line-height: 1px; max-height: 0px; max-width: 0px; opacity: 0; overflow: hidden;">
        Mã khôi phục mật khẩu tài khoản VeriScholar của bạn là {code}.
    </div>

    <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: {COLOR_BG_PAGE};">
        <tr>
            <td align="center" style="padding: 40px 12px;">
                <!--[if (gte mso 9)|(IE)]>
                <table role="presentation" align="center" border="0" cellspacing="0" cellpadding="0" width="600">
                <tr>
                <td align="center" valign="top" width="600">
                <![endif]-->
                <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%" class="email-container" style="max-width: 600px; background-color: {COLOR_BG_CARD}; border-radius: 16px; border: 1px solid {COLOR_BORDER}; box-shadow: 0 10px 25px rgba(15, 23, 42, 0.06); overflow: hidden;">
                    <!-- 1. Header with Academic Luxury Banner -->
                    <tr>
                        <td align="center" class="header-padding" style="background: linear-gradient(135deg, {COLOR_SLATE_900} 0%, {COLOR_SLATE_800} 100%); padding: 36px 32px 30px 32px; border-bottom: 3px solid {COLOR_AMBER_700};">
                            <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%">
                                <tr>
                                    <td align="center">
                                        <table role="presentation" border="0" cellpadding="0" cellspacing="0" style="margin-bottom: 14px;">
                                            <tr>
                                                <td align="center" style="background-color: rgba(217, 119, 6, 0.2); border: 1px solid rgba(217, 119, 6, 0.4); border-radius: 20px; padding: 4px 14px;">
                                                    <span style="font-size: 11px; font-weight: 700; color: #fbbf24; text-transform: uppercase; letter-spacing: 1.5px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">BẢO MẬT &amp; KHÔI PHỤC TÀI KHOẢN</span>
                                                </td>
                                            </tr>
                                        </table>
                                        <h1 style="margin: 0; color: #ffffff; font-family: 'Georgia', Garamond, 'Times New Roman', serif; font-size: 30px; font-weight: 700; letter-spacing: -0.5px;">
                                            VeriScholar
                                        </h1>
                                        <p style="margin: 8px 0 0 0; color: {COLOR_SLATE_400}; font-size: 13px; font-weight: 400; letter-spacing: 0.3px;">
                                            Hệ thống Quản trị Danh tính &amp; Nghiên cứu Khoa học
                                        </p>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>

                    <!-- 2. Content Body -->
                    <tr>
                        <td class="content-padding" style="padding: 38px 36px 32px 36px;">
                            <h2 style="margin: 0 0 14px 0; color: {COLOR_SLATE_900}; font-size: 21px; font-weight: 700; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; letter-spacing: -0.3px;">
                                Yêu cầu đặt lại mật khẩu
                            </h2>
                            <p style="margin: 0 0 20px 0; color: {COLOR_SLATE_700}; font-size: 14px; line-height: 1.65;">
                                Kính chào Quý học giả, hệ thống vừa ghi nhận yêu cầu khôi phục mật khẩu truy cập cho tài khoản <strong style="color: {COLOR_SLATE_900};">{email}</strong>. Vui lòng sử dụng mã bảo mật 6 số bên dưới hoặc nhấp vào nút hành động để khởi tạo mật khẩu mới:
                            </p>

                            <!-- OTP 6-Digit Grid Box -->
                            <div style="margin: 28px 0 16px 0; text-align: center;">
                                {otp_grid}
                            </div>
                            <p style="margin: 0 0 28px 0; text-align: center; color: {COLOR_SLATE_500}; font-size: 12px; font-family: monospace;">
                                Mã bảo mật: <strong style="color: {COLOR_SLATE_900}; letter-spacing: 2px;">{code}</strong> (nhấp đúp để sao chép)
                            </p>

                            <!-- Bulletproof CTA Button -->
                            <table role="presentation" border="0" cellpadding="0" cellspacing="0" align="center" style="margin: 0 auto 30px auto;">
                                <tr>
                                    <td align="center" style="border-radius: 12px; background-color: {COLOR_AMBER_700}; box-shadow: 0 6px 18px rgba(180, 83, 9, 0.35);">
                                        <a href="{reset_url}" target="_blank" style="display: inline-block; padding: 15px 36px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 15px; font-weight: 700; color: #ffffff; text-decoration: none; border-radius: 12px; background-color: {COLOR_AMBER_700}; border: 1px solid #92400e; letter-spacing: 0.3px;">
                                            Đặt lại mật khẩu mới &rarr;
                                        </a>
                                    </td>
                                </tr>
                            </table>

                            <!-- Security Notice Card -->
                            <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #fdfbf7; border: 1px solid #f3ece1; border-radius: 10px; margin-bottom: 24px;">
                                <tr>
                                    <td style="padding: 16px 18px;">
                                        <p style="margin: 0 0 8px 0; color: {COLOR_AMBER_700}; font-size: 12px; font-weight: 700;">
                                            &#128274; CHÍNH SÁCH BẢO VỆ TÀI KHOẢN:
                                        </p>
                                        <p style="margin: 0; color: #78716c; font-size: 12px; line-height: 1.55;">
                                            &bull; Liên kết và mã bảo mật này có hiệu lực trong vòng <strong>15 phút</strong>.<br />
                                            &bull; Nếu Quý học giả không gửi yêu cầu đặt lại mật khẩu, tài khoản vẫn được bảo vệ an toàn và bạn có thể an tâm bỏ qua thông báo này.
                                        </p>
                                    </td>
                                </tr>
                            </table>

                            <!-- Fallback Link Section -->
                            <div style="border-top: 1px solid #f1ece4; padding-top: 20px; text-align: center;">
                                <p style="margin: 0 0 8px 0; color: {COLOR_SLATE_500}; font-size: 12px; line-height: 1.5;">
                                    Nếu nút bấm phía trên không phản hồi trong ứng dụng email của bạn:
                                </p>
                                <p style="margin: 0;">
                                    <a href="{reset_url}" target="_blank" style="display: inline-block; color: {COLOR_AMBER_700}; font-size: 13px; font-weight: 600; text-decoration: underline;">
                                        &#128279; Đặt lại mật khẩu tại đây (Reset Password) &rarr;
                                    </a>
                                </p>
                            </div>
                        </td>
                    </tr>

                    <!-- 3. Academic Compliance Footer -->
                    <tr>
                        <td align="center" style="background-color: #f8fafc; border-top: 1px solid #e2e8f0; padding: 26px 32px; text-align: center;">
                            <p style="margin: 0 0 6px 0; color: {COLOR_SLATE_700}; font-size: 12px; font-weight: 600;">
                                Chuẩn bảo mật chứng cứ khoa học ISO 32000-1 &bull; Mã hóa dữ liệu mật khẩu chuẩn PBKDF2-SHA256
                            </p>
                            <p style="margin: 0 0 10px 0; color: {COLOR_SLATE_500}; font-size: 11px; line-height: 1.4;">
                                Thư điện tử tự động phát hành bởi VeriScholar Security Protocol.<br />
                                Cổng xác thực: <a href="{app_url}" target="_blank" style="color: {COLOR_AMBER_700}; text-decoration: none;">{app_url}</a>
                            </p>
                            <p style="margin: 0; color: {COLOR_SLATE_400}; font-size: 11px;">
                                &copy; 2026 VeriScholar Platform. All rights reserved.
                            </p>
                        </td>
                    </tr>
                </table>
                <!--[if (gte mso 9)|(IE)]>
                </td>
                </tr>
                </table>
                <![endif]-->
            </td>
        </tr>
    </table>
</body>
</html>"""


def render_verification_text(
    email: str,
    code: str,
    verify_url: str,
    app_url: str = "https://verischolar.duckdns.org",
) -> str:
    """Generate clean plain-text fallback for email verification."""
    return (
        f"Kính chào Quý học giả,\n\n"
        f"Cảm ơn bạn đã tham gia nền tảng VeriScholar ({app_url}).\n"
        f"Mã OTP kích hoạt tài khoản {email} của bạn là: {code}\n\n"
        f"Hoặc nhấp vào liên kết sau để kích hoạt tài khoản:\n"
        f"{verify_url}\n\n"
        f"Mã xác thực có hiệu lực trong vòng 15 phút.\n"
        f"Chuẩn bảo mật chứng cứ khoa học ISO 32000-1.\n\n"
        f"Trân trọng,\n"
        f"VeriScholar Academic Platform."
    )


def render_password_reset_text(
    email: str,
    code: str,
    reset_url: str,
    app_url: str = "https://verischolar.duckdns.org",
) -> str:
    """Generate clean plain-text fallback for password reset."""
    return (
        f"Kính chào Quý học giả,\n\n"
        f"Hệ thống VeriScholar nhận được yêu cầu đặt lại mật khẩu cho tài khoản {email} tại {app_url}.\n"
        f"Mã bảo mật khôi phục của bạn là: {code}\n\n"
        f"Hoặc nhấp vào liên kết sau để đặt lại mật khẩu mới:\n"
        f"{reset_url}\n\n"
        f"Liên kết và mã có hiệu lực trong vòng 15 phút.\n"
        f"Nếu bạn không thực hiện yêu cầu này, tài khoản của bạn vẫn an toàn.\n\n"
        f"Trân trọng,\n"
        f"VeriScholar Academic Platform."
    )
