import streamlit as st
from db import create_tables, add_password, get_passwords, delete_password, get_stats
from auth import register_user, login_user
from crypto import generate_key, encrypt_password, decrypt_password
from email_otp import generate_otp, send_otp
from utils import check_password_strength, generate_strong_password, export_to_csv, import_from_csv
import time

# -------------------------------
# INITIAL SETUP
# -------------------------------
st.set_page_config(page_title="Ultimate Secure Vault", page_icon="🔐", layout="wide")
create_tables()
generate_key()

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user" not in st.session_state:
    st.session_state.user = None
if "otp_verified" not in st.session_state:
    st.session_state.otp_verified = False

# -------------------------------
# SIDEBAR NAVIGATION
# -------------------------------
if st.session_state.authenticated and st.session_state.otp_verified:
    menu = ["Dashboard", "Add Password", "View Vault", "Generate Password", "Import/Export CSV", "Logout"]
else:
    menu = ["Login", "Register"]

choice = st.sidebar.selectbox("Menu", menu)

# -------------------------------
# REGISTER
# -------------------------------
if choice == "Register":
    st.subheader("Register")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    confirm = st.text_input("Confirm Password", type="password")
    if st.button("Register"):
        if password != confirm:
            st.error("Passwords do not match")
        elif len(password) < 8:
            st.error("Password too short")
        else:
            success, msg = register_user(email, password)
            if success:
                st.success(msg)
                st.info("Please login now")
            else:
                st.error(msg)

# -------------------------------
# LOGIN
# -------------------------------
elif choice == "Login":
    st.subheader("Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        success, msg, user = login_user(email, password)
        if success:
            st.session_state.user = user
            st.session_state.authenticated = True

            # -------------------------------
            # OTP Verification (Optional)
            # -------------------------------
            otp = generate_otp()
            st.session_state.generated_otp = otp
            sent = send_otp(email, otp)

            if sent:
                # If Gmail configured, ask OTP
                if st.secrets.get("GMAIL_USER", None) and st.secrets.get("GMAIL_PASSWORD", None):
                    st.info("OTP sent to your email")
                    entered_otp = st.text_input("Enter OTP")
                    if st.button("Verify OTP"):
                        if entered_otp == st.session_state.generated_otp:
                            st.success("OTP Verified! Access granted.")
                            st.session_state.otp_verified = True
                        else:
                            st.error("Invalid OTP")
                else:
                    # Gmail not configured → skip OTP
                    st.session_state.otp_verified = True
                    st.success("Login successful (OTP skipped).")
            else:
                st.session_state.otp_verified = True
                st.warning("OTP skipped due to email configuration.")

        else:
            st.error(msg)

# -------------------------------
# LOGOUT
# -------------------------------
elif choice == "Logout":
    st.session_state.authenticated = False
    st.session_state.user = None
    st.session_state.otp_verified = False
    st.success("Logged out successfully")
    time.sleep(1)
    st.experimental_rerun()

# -------------------------------
# DASHBOARD
# -------------------------------
elif choice == "Dashboard":
    st.subheader("Dashboard")
    total, weak = get_stats(st.session_state.user[0])
    st.metric("Total Passwords", total)
    st.metric("Weak Passwords", weak)

# -------------------------------
# ADD PASSWORD
# -------------------------------
elif choice == "Add Password":
    st.subheader("Add a Password")
    site = st.text_input("Site Name")
    username = st.text_input("Username/Email")
    password = st.text_input("Password", type="password")
    if password:
        strength = check_password_strength(password)
        st.info(f"Password Strength: {strength}")
    if st.button("Add"):
        if site and username and password:
            enc = encrypt_password(password)
            add_password(st.session_state.user[0], site, username, enc)
            st.success("Password added successfully!")
        else:
            st.error("Please fill all fields")

# -------------------------------
# VIEW VAULT
# -------------------------------
elif choice == "View Vault":
    st.subheader("Your Vault")
    data = get_passwords(st.session_state.user[0])
    for entry in data:
        pwd = decrypt_password(entry[3])
        st.write(f"**Site:** {entry[1]} | **Username:** {entry[2]} | **Password:** {pwd}")
        if st.button(f"Delete {entry[1]}", key=entry[0]):
            delete_password(entry[0], st.session_state.user[0])
            st.success(f"{entry[1]} deleted")
            st.experimental_rerun()

# -------------------------------
# GENERATE PASSWORD
# -------------------------------
elif choice == "Generate Password":
    st.subheader("AI Strong Password Generator")
    length = st.number_input("Password Length", min_value=12, max_value=32, value=16)
    if st.button("Generate"):
        pwd = generate_strong_password(length)
        st.code(pwd)

# -------------------------------
# IMPORT / EXPORT CSV
# -------------------------------
elif choice == "Import/Export CSV":
    st.subheader("Import / Export Passwords")

    # Export
    if st.button("Export Vault as CSV"):
        data = get_passwords(st.session_state.user[0])
        csv_data = export_to_csv(data)
        st.download_button("Download CSV", csv_data, file_name="vault.csv")

    # Import
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
    if uploaded_file is not None:
        entries = import_from_csv(uploaded_file)
        for site, username, password in entries:
            enc = encrypt_password(password)
            add_password(st.session_state.user[0], site, username, enc)
        st.success("CSV Imported Successfully!")
