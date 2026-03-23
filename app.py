import streamlit as st
from db import create_tables, add_password, get_passwords, delete_password, get_stats, add_to_history, toggle_favorite
from auth import register_user, login_user
from crypto import generate_key, encrypt_password, decrypt_password
from email_otp import generate_otp, send_otp
from utils import (
    check_password_strength,
    generate_strong_password,
    export_to_csv,
    import_from_csv,
    generate_encrypted_export,
)
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
if "theme" not in st.session_state:
    st.session_state.theme = "light"
if "last_action_time" not in st.session_state:
    st.session_state.last_action_time = time.time()

# -------------------------------
# THEME SWITCHER
# -------------------------------
theme_choice = st.sidebar.selectbox("Theme", ["Light", "Dark"])
st.session_state.theme = theme_choice
bg_color = "#FFFFFF" if theme_choice == "Light" else "#1e1e2f"
text_color = "#000000" if theme_choice == "Light" else "#FFFFFF"

st.markdown(
    f"""
    <style>
    body {{
        background-color: {bg_color};
        color: {text_color};
    }}
    .header {{
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        font-size: 2rem;
        font-weight: bold;
        background-color: #f5f5f5;
    }}
    .vault-card {{
        background: #f9f9f9;
        padding: 15px;
        margin: 10px 0;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }}
    .vault-card:hover {{
        background: #eaeaea;
        transform: scale(1.02);
        transition: 0.2s;
    }}
    </style>
    <div class="header">Ultimate Secure Vault</div>
    """, unsafe_allow_html=True
)

# -------------------------------
# AUTO LOGOUT AFTER INACTIVITY (10 mins)
# -------------------------------
if st.session_state.authenticated:
    if time.time() - st.session_state.last_action_time > 600:
        st.session_state.authenticated = False
        st.session_state.user = None
        st.session_state.otp_verified = False
        st.warning("Session expired due to inactivity. Please login again.")
        st.experimental_rerun()
    else:
        st.session_state.last_action_time = time.time()

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

            # OTP Verification (Optional)
            otp = generate_otp()
            st.session_state.generated_otp = otp
            sent = send_otp(email, otp)
            if sent:
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
    st.experimental_rerun()

# -------------------------------
# DASHBOARD WITH ANALYTICS
# -------------------------------
elif choice == "Dashboard":
    st.subheader("Dashboard")
    total, weak = get_stats(st.session_state.user[0])
    st.metric("Total Passwords", total)
    st.metric("Weak Passwords", weak)

    # Analytics: passwords by category / favorites
    data = get_passwords(st.session_state.user[0])
    favorite_count = sum(1 for d in data if d[5] == 1)
    st.metric("Favorites", favorite_count)

# -------------------------------
# ADD PASSWORD WITH CATEGORY / FAVORITE
# -------------------------------
elif choice == "Add Password":
    st.subheader("Add a Password")
    site = st.text_input("Site Name")
    username = st.text_input("Username/Email")
    password = st.text_input("Password", type="password")
    category = st.text_input("Category (Work/Personal/Bank etc.)")
    favorite = st.checkbox("Mark as Favorite")
    if password:
        strength = check_password_strength(password)
        st.info(f"Password Strength: {strength}")
    if st.button("Add"):
        if site and username and password:
            enc = encrypt_password(password)
            add_password(st.session_state.user[0], site, username, enc, category, int(favorite))
            add_to_history(st.session_state.user[0], site, username, enc)
            st.success("Password added successfully!")
        else:
            st.error("Please fill all fields")

# -------------------------------
# VIEW VAULT WITH SEARCH / FILTER / COPY / FAVORITE
# -------------------------------
elif choice == "View Vault":
    st.subheader("Your Vault")
    search_term = st.text_input("Search Site or Username")
    show_favorites = st.checkbox("Show Favorites Only")
    data = get_passwords(st.session_state.user[0])
    for entry in data:
        site, uname, enc_pwd, cat, fav = entry[1], entry[2], entry[3], entry[4], entry[5]
        pwd = decrypt_password(enc_pwd)
        if (search_term.lower() in site.lower() or search_term.lower() in uname.lower()) and (not show_favorites or fav == 1):
            st.markdown(f"""
            <div class="vault-card">
            <b>Site:</b> {site}<br>
            <b>Username:</b> {uname}<br>
            <b>Password:</b> {pwd} <button onclick="navigator.clipboard.writeText('{pwd}')">Copy</button><br>
            <b>Category:</b> {cat}<br>
            <b>Favorite:</b> {"Yes" if fav==1 else "No"}
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Delete {site}", key=entry[0]):
                delete_password(entry[0], st.session_state.user[0])
                st.success(f"{site} deleted")
                st.experimental_rerun()
            if st.button(f"Toggle Favorite {site}", key=f"fav{entry[0]}"):
                toggle_favorite(entry[0], st.session_state.user[0])
                st.experimental_rerun()

# -------------------------------
# GENERATE STRONG PASSWORD
# -------------------------------
elif choice == "Generate Password":
    st.subheader("AI Strong Password Generator")
    length = st.number_input("Password Length", min_value=12, max_value=32, value=16)
    if st.button("Generate"):
        pwd = generate_strong_password(length)
        st.code(pwd)

# -------------------------------
# IMPORT / EXPORT CSV & ENCRYPTED EXPORT
# -------------------------------
elif choice == "Import/Export CSV":
    st.subheader("Import / Export Passwords")

    # Export regular CSV
    if st.button("Export Vault as CSV"):
        data = get_passwords(st.session_state.user[0])
        csv_data = export_to_csv(data)
        st.download_button("Download CSV", csv_data, file_name="vault.csv")

    # Export encrypted CSV
    if st.button("Export Vault (Encrypted)"):
        data = get_passwords(st.session_state.user[0])
        enc_data = generate_encrypted_export(data)
        st.download_button("Download Encrypted Vault", enc_data, file_name="vault_encrypted.csv")

    # Import CSV
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
    if uploaded_file is not None:
        entries = import_from_csv(uploaded_file)
        for site, username, password in entries:
            enc = encrypt_password(password)
            add_password(st.session_state.user[0], site, username, enc)
        st.success("CSV Imported Successfully!")
