import streamlit as st
from auth import register_user, login_user
from db import create_tables, add_password, get_passwords, delete_password, get_stats, add_to_history, toggle_favorite
from utils import check_password_strength, generate_strong_password, export_to_csv, import_from_csv, generate_encrypted_export
from crypto import encrypt_password, decrypt_password, generate_key
from email_otp import generate_otp, send_otp

st.set_page_config(page_title="Ultimate Secure Vault", layout="wide", page_icon="🔒")
generate_key()
create_tables()

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user" not in st.session_state:
    st.session_state.user = None

# ------------------------
# Sidebar Multi-Page Navigation
# ------------------------
def show_home():
    st.title("Welcome to Ultimate Secure Vault 🔒")
    st.markdown("""
    This is a production-level **Enterprise Password Manager**.
    Use the sidebar to navigate through the app.
    """)
    st.balloons()  # fun animation

def show_about():
    st.title("About Ultimate Secure Vault")
    st.markdown("""
    **Features:**
    - Multi-user authentication
    - Encrypted vault per user
    - Password strength checker
    - AI strong password generator
    - CSV import/export (Encrypted)
    - Favorites, Categories, History
    - Session management
    - Optional OTP verification
    - Premium UI with animations
    """)

def auth_page():
    st.title("Login / Register")
    menu = ["Login","Register"]
    choice = st.radio("Select Action",menu)
    if choice=="Login":
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            success,msg,user = login_user(email,password)
            if success:
                st.session_state.authenticated = True
                st.session_state.user = user
                st.success(msg)
            else:
                st.error(msg)
    else:
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        password_confirm = st.text_input("Confirm Password", type="password")
        if st.button("Register"):
            if password!=password_confirm:
                st.error("Passwords do not match")
            else:
                success,msg = register_user(email,password)
                if success:
                    st.success(msg)
                else:
                    st.error(msg)

def dashboard():
    user = st.session_state.user
    st.title(f"Welcome, {user[1]} 🔒")
    page = st.sidebar.selectbox("Menu", ["Home","Dashboard","Add Password","View Vault","About","Logout"])
    total,weak = get_stats(user[0])
    st.sidebar.markdown(f"**Total Passwords:** {total}")
    st.sidebar.markdown(f"**Weak Passwords:** {weak}")

    if page=="Home":
        show_home()
    elif page=="Dashboard":
        st.subheader("Vault Stats")
        st.metric("Total Passwords", total)
        st.metric("Weak Passwords", weak)
    elif page=="Add Password":
        st.subheader("Add New Password")
        site = st.text_input("Website / App")
        username = st.text_input("Username / Email")
        password = st.text_input("Password", type="password")
        category = st.text_input("Category")
        favorite = st.checkbox("Favorite")
        if st.button("Add"):
            enc_pass = encrypt_password(password)
            add_password(user[0], site, username, enc_pass, category, 1 if favorite else 0)
            add_to_history(user[0], site, username, enc_pass)
            st.success("Password added successfully")
            st.balloons()
    elif page=="View Vault":
        st.subheader("Your Vault")
        data = get_passwords(user[0])
        for row in data:
            decrypted = decrypt_password(row[4])
            fav = "⭐" if row[6]==1 else ""
            st.write(f"{fav} **{row[2]}** ({row[3]}) → {decrypted} [{row[5]}]")
            c1,c2 = st.columns(2)
            with c1:
                if st.button(f"Delete {row[2]}"):
                    delete_password(row[0], user[0])
                    st.success("Deleted")
            with c2:
                if st.button(f"Toggle Favorite {row[2]}"):
                    toggle_favorite(row[0], user[0])
                    st.success("Favorite Toggled")
    elif page=="About":
        show_about()
    elif page=="Logout":
        st.session_state.authenticated=False
        st.session_state.user=None
        st.success("Logged out successfully")

if not st.session_state.authenticated:
    auth_page()
else:
    dashboard()
