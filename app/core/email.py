import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings

def send_email(to_email: str, subject: str, body: str):
    msg = MIMEMultipart()
    msg["From"] = settings.EMAIL_USERNAME
    msg["To"] = to_email
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "html"))

    try:
        server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
        server.starttls()
        server.login(settings.EMAIL_USERNAME, settings.EMAIL_PASSWORD)
        server.sendmail(settings.EMAIL_USERNAME, to_email, msg.as_string())
        server.quit()
        print(f"[EMAIL SENT] to {to_email}")
    except Exception as e:
        print(f"[EMAIL ERROR] {str(e)}")
