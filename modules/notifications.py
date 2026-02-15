import smtplib
from email.mime.text import MIMEText
import os
import streamlit as st

class SystemAlert:
    def __init__(self):
        self.sender = os.getenv("GMAIL_USER")
        self.password = os.getenv("GMAIL_APP_PASS")
        self.recipient = os.getenv("NOTIFY_EMAIL", "hadgetruhin@gmail.com") # Default to user provided
        self.enabled = bool(self.sender and self.password)

    def send_alert(self, subject, message):
        """Sends a single email notification to the admin."""
        if not self.enabled:
            st.warning("⚠️ Email Notifications Disabled. Check GMAIL_USER/PASS in .env")
            return False

        try:
            msg = MIMEText(message)
            msg["From"] = self.sender
            msg["To"] = self.recipient
            msg["Subject"] = f"⚡ VOLTS ALERT: {subject}"

            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(self.sender, self.password)
                server.sendmail(self.sender, self.recipient, msg.as_string())
            
            return True
        except Exception as e:
            print(f"Notification Failed: {e}")
            return False
