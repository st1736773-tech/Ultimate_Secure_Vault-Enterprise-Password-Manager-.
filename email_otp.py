import smtplib
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import streamlit as st

# -------------------------------
# CONFIGURE GMAIL SMTP
# -------------------------------
GMAIL_USER = "your_email@gmail.com"        # Replace with your Gmail
GMAIL_PASSWORD = "your_16_char_app_password"  # Use App Password, NOT your Gmail password


# -------------------------------
# GENERATE OTP
# -------------------------------
def generate_otp(length=6):
    return ''.join([str(random.randint(0, 9)) for _ in range(length)])


# -------------------------------
# SEND OTP EMAIL
# -------------------------------
def send_otp(email, otp):
    """
    Sends an OTP to the given email.
    Returns True if successful, False otherwise.
    Shows detailed errors in Streamlit.
    """
    try:
        message = MIMEMultipart()
        message['From'] = GMAIL_USER
        message['To'] = email
        message['Subject'] = "Your OTP for Ultimate Secure Vault"

        body = f"Your OTP is: {otp}"
        message.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(GMAIL_USER, GMAIL_PASSWORD)
        server.send_message(message)
        server.quit()
        return True
    except smtplib.SMTPAuthenticationError:
        st.error("SMTP Authentication Failed! ❌ Check your Gmail & App Password.")
        return False
    except smtplib.SMTPConnectError:
        st.error("SMTP Connection Failed! ❌ Check your internet/network.")
        return False
    except Exception as e:
        st.error(f"Failed to send OTP: {e}")
        return False
