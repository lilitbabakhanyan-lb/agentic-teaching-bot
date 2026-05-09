import os
import smtplib
from email.mime.text import MIMEText


def send_email(to_email: str, subject: str, body: str) -> str:
    host = os.getenv("SMTP_HOST")
    port = int(os.getenv("SMTP_PORT", "587"))
    user = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASSWORD")
    sender = os.getenv("SENDER_EMAIL", user)
    if not all([host, user, password, sender, to_email]):
        return "Email not sent: missing SMTP configuration or recipient email."

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = to_email

    with smtplib.SMTP(host, port) as server:
        server.starttls()
        server.login(user, password)
        server.send_message(msg)
    return "Email sent successfully."
