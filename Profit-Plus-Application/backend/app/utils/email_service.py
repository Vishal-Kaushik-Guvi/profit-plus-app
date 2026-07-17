import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import settings


def send_otp_email(to_email: str, otp: str, name: str = "there"):
    """
    Sends OTP via Gmail SMTP.
    In Java → like using JavaMailSender with SMTP config.
    """
    subject = "Your Profit Plus Verification Code"

    body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; background-color: #06060c; padding: 40px;">
            <div style="max-width: 400px; margin: auto; background-color: #0d0d18; 
                        border-radius: 16px; padding: 30px; border: 1px solid #1f1f33;">
                <h2 style="color: #ffffff;">Profit Plus</h2>
                <p style="color: #94a3b8;">Hi {name},</p>
                <p style="color: #94a3b8;">Your verification code is:</p>
                <div style="background-color: #1c1530; padding: 15px; border-radius: 10px; 
                            text-align: center; margin: 20px 0;">
                    <span style="font-size: 32px; font-weight: bold; color: #a78bfa; letter-spacing: 8px;">
                        {otp}
                    </span>
                </div>
                <p style="color: #64748b; font-size: 12px;">
                    This code expires in 5 minutes. If you didn't request this, please ignore this email.
                </p>
            </div>
        </body>
    </html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = settings.SMTP_EMAIL
    msg["To"] = to_email
    msg.attach(MIMEText(body, "html"))

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=3) as server:
            server.starttls()  # Secure the connection
            login_user = settings.SMTP_USERNAME or settings.SMTP_EMAIL
            server.login(login_user, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_EMAIL, to_email, msg.as_string())
        return True
    except Exception as e:
        print(f"Failed to send email (Render likely blocking port 587): {e}")
        return False

def send_bill_email(to_email: str, pdf_path: str, invoice_no: str, name: str = "Customer"):
    import os
    from email.mime.application import MIMEApplication

    subject = f"Your Invoice {invoice_no} from Profit Plus"
    body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; background-color: #f4f4f5; padding: 40px;">
            <div style="max-width: 500px; margin: auto; background-color: #ffffff; 
                        border-radius: 12px; padding: 30px; border: 1px solid #e4e4e7;">
                <h2 style="color: #18181b;">Invoice Details</h2>
                <p style="color: #52525b;">Hi {name},</p>
                <p style="color: #52525b;">Thank you for your business! Please find attached your invoice <b>{invoice_no}</b>.</p>
                <p style="color: #a1a1aa; font-size: 12px; margin-top: 30px;">
                    Powered by Profit Plus
                </p>
            </div>
        </body>
    </html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = settings.SMTP_EMAIL
    msg["To"] = to_email
    msg.attach(MIMEText(body, "html"))

    if os.path.exists(pdf_path):
        with open(pdf_path, "rb") as f:
            pdf_attachment = MIMEApplication(f.read(), _subtype="pdf")
            pdf_attachment.add_header('Content-Disposition', 'attachment', filename=os.path.basename(pdf_path))
            msg.attach(pdf_attachment)

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_EMAIL, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_EMAIL, to_email, msg.as_string())
        return True
    except Exception as e:
        print(f"Failed to send bill email: {e}")
        return False