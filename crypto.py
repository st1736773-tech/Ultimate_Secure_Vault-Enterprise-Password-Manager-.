from cryptography.fernet import Fernet
import os

KEY_FILE = "secret.key"

def generate_key():
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE,"wb") as f:
            f.write(key)

def load_key():
    with open(KEY_FILE,"rb") as f:
        key = f.read()
    return key

def encrypt_password(password):
    f = Fernet(load_key())
    return f.encrypt(password.encode()).decode()

def decrypt_password(enc_password):
    f = Fernet(load_key())
    return f.decrypt(enc_password.encode()).decode()
