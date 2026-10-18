"""
Real-time Email OTP Delivery Service for Visionlytics.

Sends 6-digit verification codes via:
1. Gmail SMTP (primary) - configure SMTP_EMAIL + SMTP_APP_PASSWORD env vars
2. Supabase Auth OTP (if Supabase is configured)
3. Dev mode fallback (OTP returned in API response for local testing)

Setup for Gmail SMTP:
1. Go to https://myaccount.google.com/apppasswords
2. Generate an app password for "Mail" on "Other (Custom name)"
3. Set SMTP_EMAIL and SMTP_APP_PASSWORD environment variables
"""

import logging
import os
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

logger = logging.getLogger(__name__)

# Gmail SMTP Configuration
SMTP_EMAIL = os.environ.get("SMTP_EMAIL", "").strip()
SMTP_APP_PASSWORD = os.environ.get("SMTP_APP_PASSWORD", "").strip()
SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com").strip()
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))

# Whether real email sending is available
EMAIL_CONFIGURED = bool(SMTP_EMAIL and SMTP_APP_PASSWORD)


def send_otp_email(recipient_email: str, otp_code: str) -> bool:
    """
    Send a beautifully formatted OTP verification email.
    Returns True if sent successfully, False otherwise.
    """
    if not EMAIL_CONFIGURED:
        logger.info(f"[DEV MODE] OTP for {recipient_email}: {otp_code} (SMTP not configured)")
        return False

    subject = f"Visionlytics — Your Verification Code: {otp_code}"

    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin:0;padding:0;background-color:#F1F5F9;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;">
        <table width="100%" cellpadding="0" cellspacing="0" style="padding:40px 20px;">
            <tr>
                <td align="center">
                    <table width="480" cellpadding="0" cellspacing="0" style="background:#FFFFFF;border-radius:12px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,0.08);">
                        <!-- Header -->
                        <tr>
                            <td style="background:linear-gradient(135deg,#0F172A 0%,#1E293B 100%);padding:32px 32px 24px;text-align:center;">
                                <h1 style="margin:0;color:#FFFFFF;font-size:22px;font-weight:800;letter-spacing:-0.02em;">
                                    Visionlytics
                                </h1>
                                <p style="margin:6px 0 0;color:#94A3B8;font-size:13px;">
                                    Computer Vision &amp; Crowd Intelligence Platform
                                </p>
                            </td>
                        </tr>
                        <!-- Body -->
                        <tr>
                            <td style="padding:32px;">
                                <h2 style="margin:0 0 12px;color:#0F172A;font-size:18px;font-weight:700;">
                                    Verification Code
                                </h2>
                                <p style="margin:0 0 24px;color:#64748B;font-size:14px;line-height:1.6;">
                                    Use the code below to verify your identity. This code expires in <strong>10 minutes</strong>.
                                </p>
                                <!-- OTP Code -->
                                <div style="background:#F8FAFC;border:2px dashed #CBD5E1;border-radius:8px;padding:20px;text-align:center;margin:0 0 24px;">
                                    <span style="font-size:36px;font-weight:800;letter-spacing:8px;color:#0F172A;font-family:monospace;">
                                        {otp_code}
                                    </span>
                                </div>
                                <p style="margin:0;color:#94A3B8;font-size:12px;line-height:1.5;">
                                    If you didn't request this code, you can safely ignore this email.
                                    Never share this code with anyone.
                                </p>
                            </td>
                        </tr>
                        <!-- Footer -->
                        <tr>
                            <td style="background:#F8FAFC;padding:16px 32px;border-top:1px solid #E2E8F0;">
                                <p style="margin:0;color:#94A3B8;font-size:11px;text-align:center;">
                                    &copy; 2026 Visionlytics. Sent to {recipient_email}.
                                </p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """

    plain_body = f"""
Visionlytics — Verification Code

Your verification code is: {otp_code}

This code expires in 10 minutes. Do not share it with anyone.

If you didn't request this code, please ignore this email.
"""

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"Visionlytics <{SMTP_EMAIL}>"
        msg["To"] = recipient_email

        msg.attach(MIMEText(plain_body, "plain"))
        msg.attach(MIMEText(html_body, "html"))

        context = ssl.create_default_context()
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login(SMTP_EMAIL, SMTP_APP_PASSWORD)
            server.sendmail(SMTP_EMAIL, recipient_email, msg.as_string())

        logger.info(f"OTP email sent successfully to {recipient_email}")
        return True

    except Exception as exc:
        logger.error(f"Failed to send OTP email to {recipient_email}: {exc}")
        return False


def send_otp_sms(phone_number: str, otp_code: str) -> bool:
    """
    Send OTP via SMS. Requires Twilio configuration.
    Currently logs the code for dev/demo mode.
    """
    # SMS via Twilio would go here when configured
    twilio_sid = os.environ.get("TWILIO_ACCOUNT_SID", "").strip()
    twilio_token = os.environ.get("TWILIO_AUTH_TOKEN", "").strip()
    twilio_from = os.environ.get("TWILIO_PHONE_NUMBER", "").strip()

    if twilio_sid and twilio_token and twilio_from:
        try:
            from twilio.rest import Client  # type: ignore
            client = Client(twilio_sid, twilio_token)
            client.messages.create(
                body=f"Your Visionlytics verification code is: {otp_code}. Valid for 10 minutes.",
                from_=twilio_from,
                to=phone_number,
            )
            logger.info(f"OTP SMS sent to {phone_number}")
            return True
        except Exception as exc:
            logger.error(f"Failed to send SMS to {phone_number}: {exc}")
            return False

    logger.info(f"[DEV MODE] OTP for {phone_number}: {otp_code} (Twilio not configured)")
    return False
