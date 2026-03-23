import random
import streamlit as st

# Gmail config (optional)
GMAIL_USER = st.secrets.get("GMAIL_USER", None)
GMAIL_PASSWORD = st.secrets.get("GMAIL_PASSWORD", None)

def generate_otp(length=6):
    return ''.join([str(random.randint(0, 9)) for _ in range(length)])

def send_otp(email, otp):
    """
    If Gmail is configured, send OTP.
    If not, skip and print a warning.
    """
    if not GMAIL_USER or not GMAIL_PASSWORD:
        st.warning("Gmail not configured — OTP skipped. Login will proceed without OTP.")
        return True  # Treat as OTP "sent" so login works
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart

        message = MIMEMultipart()
        message['From'] = GMAIL_USER
        message['To'] = email
        message['Subject'] = "Your OTP for Ultimate Secure Vault"
        message.attach(MIMEText(f"Your OTP is: {otp}", 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(GMAIL_USER, GMAIL_PASSWORD)
        server.send_message(message)
        server.quit()
        return True
    except Exception as e:
        st.warning(f"Failed to send OTP ({e}). Login will proceed without OTP.")
        return True
