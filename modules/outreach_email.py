import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import random
import streamlit as st

class EmailBlaster:
    def __init__(self):
        self.user = os.getenv("GMAIL_USER")
        self.password = os.getenv("GMAIL_APP_PASS")
        self.server = None

    def connect(self):
        try:
            self.server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
            self.server.login(self.user, self.password)
            return True
        except Exception as e:
            st.error(f"SMTP Connect Error: {e}")
            return False

    def send_blast(self, email_list, subject, body_html):
        if not self.server:
            if not self.connect():
                return
        
        count = 0
        greetings = ["Hi", "Hello", "Greetings", "Hey"]
        
        progress_bar = st.progress(0)
        
        for idx, email in enumerate(email_list):
            try:
                msg = MIMEMultipart()
                msg["From"] = self.user
                msg["To"] = email
                msg["Subject"] = subject
                
                # Personalization
                greeting = random.choice(greetings)
                final_body = f"<p>{greeting},</p><br>" + body_html
                
                msg.attach(MIMEText(final_body, "html"))
                
                self.server.sendmail(self.user, email, msg.as_string())
                count += 1
                
                # Update progress
                progress_bar.progress((idx + 1) / len(email_list))
                time.sleep(random.uniform(2, 5)) # Anti-spam delay
                
            except Exception as e:
                st.warning(f"Failed to send to {email}: {e}")
                
        st.success(f"Sent {count} emails successfully.")
        
    def close(self):
        if self.server:
            self.server.quit()

    def send_single_email(self, to_email, subject, body_html):
        """Sends a single email and returns (True, Msg) or (False, Error)."""
        if not self.server:
            if not self.connect():
                return False, "SMTP Connection Failed"
        
        try:
            msg = MIMEMultipart()
            msg["From"] = self.user
            msg["To"] = to_email
            msg["Subject"] = subject
            msg.attach(MIMEText(body_html, "html"))
            
            self.server.sendmail(self.user, to_email, msg.as_string())
            return True, "Email Sent Successfully"
        except Exception as e:
            return False, str(e)
