"""
Quick SMTP Email Test Script
Tests sending an email via the credentials in backend/.env to your own inbox.

Usage:
    cd backend
    python test_email.py [recipient_email]
"""
import sys
import smtplib
from email.message import EmailMessage
from app.core.config import settings

def test_smtp():
    recipient = sys.argv[1] if len(sys.argv) > 1 else settings.SMTP_USERNAME
    if not settings.SMTP_USERNAME or not settings.SMTP_APP_PASSWORD:
        print("❌ Error: SMTP_USERNAME or SMTP_APP_PASSWORD not set in backend/.env")
        print("   Please check backend/.env and add your Gmail and App Password.")
        return False

    print(f"📧 Sending test email from {settings.SMTP_USERNAME} to {recipient}...")
    print(f"   Server: {settings.SMTP_HOST}:{settings.SMTP_PORT}")

    clean_pw = settings.SMTP_APP_PASSWORD.replace(" ", "").strip()
    msg = EmailMessage()
    msg["From"] = f"{settings.EMAIL_FROM_NAME} <{settings.SMTP_USERNAME}>"
    msg["To"] = recipient
    msg["Subject"] = "⚡ CareerLens AI — SMTP Connection Test"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <body style="font-family: Arial, sans-serif; background: #0f172a; color: #e2e8f0; padding: 30px;">
      <div style="max-width: 500px; margin: 0 auto; background: #1e293b; border-radius: 12px; padding: 30px; border: 1px solid rgba(255,255,255,0.1);">
        <h2 style="color: #6366f1; margin-top: 0;">⚡ CareerLens AI Email Test</h2>
        <p style="color: #94a3b8; font-size: 15px; line-height: 1.6;">
          Congratulations! Your Gmail SMTP integration is working successfully.
        </p>
        <div style="background: rgba(16,185,129,0.1); border: 1px solid rgba(16,185,129,0.3); border-radius: 8px; padding: 12px; color: #34d399; font-size: 14px; margin: 20px 0;">
          ✅ Password reset emails and analysis report delivery are fully active.
        </div>
        <p style="color: #64748b; font-size: 12px;">Sent from CareerLens AI Backend.</p>
      </div>
    </body>
    </html>
    """
    msg.set_content("Congratulations! Your Gmail SMTP integration is working successfully.")
    msg.add_alternative(html_content, subtype="html")

    try:
        if settings.SMTP_PORT == 465:
            with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT, timeout=20) as s:
                s.login(settings.SMTP_USERNAME.strip(), clean_pw)
                s.send_message(msg)
        else:
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=20) as s:
                s.starttls()
                s.login(settings.SMTP_USERNAME.strip(), clean_pw)
                s.send_message(msg)
        print("🎉 SUCCESS! Test email was successfully sent.")
        print(f"📬 Please check the inbox of: {recipient} (and check spam folder if not in primary).")
        return True
    except Exception as e:
        print(f"❌ SMTP Send Failed: {e}")
        return False

if __name__ == "__main__":
    test_smtp()
