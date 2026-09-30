"""
Email service: Brevo HTTPS (any inbox, Render-proof) > Gmail SMTP (local) > Resend (fallback).
Returns True on real send, False when unconfigured or failed.
"""
import json
import logging
import urllib.request
import urllib.error
import resend
import smtplib
from email.message import EmailMessage
from app.core.config import settings

log = logging.getLogger(__name__)


def _brevo_configured() -> bool:
    return bool(settings.BREVO_API_KEY and settings.BREVO_SENDER_EMAIL)


def _smtp_configured() -> bool:
    return bool(settings.SMTP_USERNAME and settings.SMTP_APP_PASSWORD)


def _resend_configured() -> bool:
    return bool(settings.RESEND_API_KEY and settings.EMAIL_FROM)


def is_email_configured() -> bool:
    return _brevo_configured() or _smtp_configured() or _resend_configured()


def _send_brevo(to_email: str, subject: str, html: str) -> bool:
    """Send via Brevo HTTPS API — any recipient, no domain, no SMTP ports."""
    payload = {
        "sender": {"name": settings.EMAIL_FROM_NAME, "email": settings.BREVO_SENDER_EMAIL},
        "to": [{"email": to_email}],
        "subject": subject,
        "htmlContent": html,
    }
    req = urllib.request.Request(
        "https://api.brevo.com/v3/smtp/email",
        data=json.dumps(payload).encode(),
        method="POST",
        headers={"accept": "application/json", "api-key": settings.BREVO_API_KEY,
                 "content-type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return 200 <= r.status < 300
    except urllib.error.HTTPError as e:
        log.error("Brevo send failed to %s: %s %s", to_email, e.code, e.read().decode()[:200])
        return False
    except Exception as e:
        log.error("Brevo send failed to %s: %s", to_email, e)
        return False


def _send_smtp(to_email: str, subject: str, html: str) -> bool:
    """Send via Gmail SMTP — works for ANY recipient, no domain needed."""
    msg = EmailMessage()
    # Gmail requires From to be the account (or a verified alias), so use SMTP_USERNAME.
    msg["From"] = f"{settings.EMAIL_FROM_NAME} <{settings.SMTP_USERNAME}>"
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content("Please view this email in an HTML-capable client.")
    msg.add_alternative(html, subtype="html")
    try:
        with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT, timeout=20) as s:
            s.login(settings.SMTP_USERNAME, settings.SMTP_APP_PASSWORD.replace(" ", ""))
            s.send_message(msg)
        return True
    except Exception as e:
        log.error("Gmail SMTP send failed to %s: %s", to_email, e)
        return False


def _send(payload: dict) -> bool:
    to = payload.get("to", [None])[0] if isinstance(payload.get("to"), list) else payload.get("to")
    subject, html = payload.get("subject", ""), payload.get("html", "")
    if _brevo_configured():
        if _send_brevo(to, subject, html):
            return True
        log.warning("Brevo failed, trying SMTP fallback for %s", to)
    if _smtp_configured():
        if _send_smtp(to, subject, html):
            return True
        log.warning("SMTP failed, trying Resend fallback for %s", to)
    if not _resend_configured():
        log.warning("Email not configured (SMTP + Resend both missing) — skipping send to %s", to)
        return False
    resend.api_key = settings.RESEND_API_KEY  # bind per-send, not at import
    try:
        resend.Emails.send(payload)
        return True
    except Exception as e:
        log.error("Resend send failed: %s", e)
        return False


def send_verification_email(to_email: str, full_name: str, token: str) -> bool:
    verify_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"
    return _send({
        "from": f"{settings.EMAIL_FROM_NAME} <{settings.EMAIL_FROM}>",
        "to": [to_email],
        "subject": "Verify your CareerLens AI account",
        "html": f"""
            <!DOCTYPE html>
            <html>
            <body style="font-family: Inter, Arial, sans-serif; background: #0f172a; color: #e2e8f0; padding: 40px;">
              <div style="max-width: 560px; margin: 0 auto; background: #1e293b; border-radius: 16px; padding: 40px;">
                <div style="text-align: center; margin-bottom: 32px;">
                  <div style="background: linear-gradient(135deg, #6366f1, #8b5cf6); display: inline-block; padding: 12px 24px; border-radius: 12px; font-size: 20px; font-weight: 700; color: white;">
                    CareerLens AI
                  </div>
                </div>
                <h1 style="font-size: 24px; font-weight: 700; color: #f8fafc; margin-bottom: 16px;">
                  Verify your email, {full_name}!
                </h1>
                <p style="color: #94a3b8; line-height: 1.6; margin-bottom: 32px;">
                  Welcome to CareerLens AI! Click the button below to verify your email address and activate your account.
                </p>
                <div style="text-align: center; margin-bottom: 32px;">
                  <a href="{verify_url}"
                     style="background: linear-gradient(135deg, #6366f1, #8b5cf6); color: white; padding: 14px 32px;
                            border-radius: 10px; text-decoration: none; font-weight: 600; font-size: 16px; display: inline-block;">
                    Verify Email Address
                  </a>
                </div>
                <p style="color: #64748b; font-size: 13px; text-align: center;">
                  This link expires in 24 hours. If you didn't create an account, ignore this email.
                </p>
              </div>
            </body>
            </html>
            """,
    })


def send_password_reset_email(to_email: str, full_name: str, token: str) -> bool:
    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
    return _send({
        "from": f"{settings.EMAIL_FROM_NAME} <{settings.EMAIL_FROM}>",
        "to": [to_email],
        "subject": "Reset your CareerLens AI password",
        "html": f"""
            <!DOCTYPE html>
            <html>
            <body style="font-family: Inter, Arial, sans-serif; background: #0f172a; color: #e2e8f0; padding: 40px;">
              <div style="max-width: 560px; margin: 0 auto; background: #1e293b; border-radius: 16px; padding: 40px;">
                <div style="text-align: center; margin-bottom: 32px;">
                  <div style="background: linear-gradient(135deg, #6366f1, #8b5cf6); display: inline-block; padding: 12px 24px; border-radius: 12px; font-size: 20px; font-weight: 700; color: white;">
                    CareerLens AI
                  </div>
                </div>
                <h1 style="font-size: 24px; font-weight: 700; color: #f8fafc; margin-bottom: 16px;">
                  Reset your password
                </h1>
                <p style="color: #94a3b8; line-height: 1.6; margin-bottom: 32px;">
                  Hi {full_name}, we received a request to reset your password. Click below — this link expires in 15 minutes.
                </p>
                <div style="text-align: center; margin-bottom: 32px;">
                  <a href="{reset_url}"
                     style="background: linear-gradient(135deg, #ef4444, #f97316); color: white; padding: 14px 32px;
                            border-radius: 10px; text-decoration: none; font-weight: 600; font-size: 16px; display: inline-block;">
                    Reset Password
                  </a>
                </div>
                <p style="color: #64748b; font-size: 13px; text-align: center;">
                  If you didn't request this, ignore this email. Your password won't change.
                </p>
              </div>
            </body>
            </html>
            """,
    })


def send_google_only_info_email(to_email: str, full_name: str) -> bool:
    """Tell a Google-signup user they have no password to reset."""
    login_url = f"{settings.FRONTEND_URL}/login"
    return _send({
        "from": f"{settings.EMAIL_FROM_NAME} <{settings.EMAIL_FROM}>",
        "to": [to_email],
        "subject": "Your CareerLens AI account uses Google sign-in",
        "html": f"""
            <!DOCTYPE html>
            <html>
            <body style="font-family: Inter, Arial, sans-serif; background: #0f172a; color: #e2e8f0; padding: 40px;">
              <div style="max-width: 560px; margin: 0 auto; background: #1e293b; border-radius: 16px; padding: 40px;">
                <div style="text-align: center; margin-bottom: 32px;">
                  <div style="background: linear-gradient(135deg, #6366f1, #8b5cf6); display: inline-block; padding: 12px 24px; border-radius: 12px; font-size: 20px; font-weight: 700; color: white;">
                    CareerLens AI
                  </div>
                </div>
                <h1 style="font-size: 24px; font-weight: 700; color: #f8fafc; margin-bottom: 16px;">
                  Hi {full_name} — no password to reset
                </h1>
                <p style="color: #94a3b8; line-height: 1.6; margin-bottom: 32px;">
                  You asked to reset your password, but your account was created with
                  <b>Google sign-in</b>, so it has no password. Just click below and
                  use the "Continue with Google" button.
                </p>
                <div style="text-align: center; margin-bottom: 32px;">
                  <a href="{login_url}"
                     style="background: linear-gradient(135deg, #6366f1, #8b5cf6); color: white; padding: 14px 32px;
                            border-radius: 10px; text-decoration: none; font-weight: 600; font-size: 16px; display: inline-block;">
                    Go to Login
                  </a>
                </div>
                <p style="color: #64748b; font-size: 13px; text-align: center;">
                  If this wasn't you, ignore this email.
                </p>
              </div>
            </body>
            </html>
            """,
    })


def send_analysis_report_email(
    to_email: str, full_name: str, report_url: str, match_score: float, ats_score: float
) -> bool:
    if not report_url:
        log.warning("Skipping report email to %s — no report_url (S3 unconfigured?)", to_email)
        return False
    return _send({
        "from": f"{settings.EMAIL_FROM_NAME} <{settings.EMAIL_FROM}>",
        "to": [to_email],
        "subject": "Your Resume Analysis Report is Ready! 🎯",
        "html": f"""
            <!DOCTYPE html>
            <html>
            <body style="font-family: Inter, Arial, sans-serif; background: #0f172a; color: #e2e8f0; padding: 40px;">
              <div style="max-width: 560px; margin: 0 auto; background: #1e293b; border-radius: 16px; padding: 40px;">
                <div style="text-align: center; margin-bottom: 32px;">
                  <div style="background: linear-gradient(135deg, #6366f1, #8b5cf6); display: inline-block; padding: 12px 24px; border-radius: 12px; font-size: 20px; font-weight: 700; color: white;">
                    CareerLens AI
                  </div>
                </div>
                <h1 style="font-size: 24px; font-weight: 700; color: #f8fafc; margin-bottom: 16px;">
                  Your analysis is ready, {full_name}! 🎉
                </h1>
                <div style="display: flex; gap: 16px; margin-bottom: 32px;">
                  <div style="flex: 1; background: #0f172a; border-radius: 12px; padding: 20px; text-align: center;">
                    <div style="font-size: 36px; font-weight: 800; color: #6366f1;">{match_score:.0f}%</div>
                    <div style="color: #64748b; font-size: 13px; margin-top: 4px;">Match Score</div>
                  </div>
                  <div style="flex: 1; background: #0f172a; border-radius: 12px; padding: 20px; text-align: center;">
                    <div style="font-size: 36px; font-weight: 800; color: #10b981;">{ats_score:.0f}%</div>
                    <div style="color: #64748b; font-size: 13px; margin-top: 4px;">ATS Score</div>
                  </div>
                </div>
                <div style="text-align: center; margin-bottom: 32px;">
                  <a href="{report_url}"
                     style="background: linear-gradient(135deg, #6366f1, #8b5cf6); color: white; padding: 14px 32px;
                            border-radius: 10px; text-decoration: none; font-weight: 600; font-size: 16px; display: inline-block;">
                    Download Your Report
                  </a>
                </div>
                <p style="color: #64748b; font-size: 13px; text-align: center;">
                  Log in to your dashboard to view your full analysis history.
                </p>
              </div>
            </body>
            </html>
            """,
    })
