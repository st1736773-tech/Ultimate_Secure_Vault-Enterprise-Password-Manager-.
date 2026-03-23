import csv
import io
import string
import random
from cryptography.fernet import Fernet

# -------------------------------
# PASSWORD STRENGTH CHECKER
# -------------------------------
def check_password_strength(password):
    length = len(password)
    lower = any(c.islower() for c in password)
    upper = any(c.isupper() for c in password)
    digit = any(c.isdigit() for c in password)
    special = any(c in string.punctuation for c in password)

    score = sum([lower, upper, digit, special])

    if length >= 12 and score >= 3:
        return "Strong"
    elif length >= 8 and score >= 2:
        return "Medium"
    else:
        return "Weak"

# -------------------------------
# AI STRONG PASSWORD GENERATOR
# -------------------------------
def generate_strong_password(length=16):
    all_chars = string.ascii_letters + string.digits + string.punctuation
    while True:
        pwd = ''.join(random.choice(all_chars) for _ in range(length))
        if check_password_strength(pwd) == "Strong":
            return pwd

# -------------------------------
# EXPORT TO CSV
# -------------------------------
def export_to_csv(data):
    """
    data: list of tuples (id, user_id, site, username, password, category, favorite)
    """
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Site", "Username", "Password", "Category", "Favorite"])
    for row in data:
        writer.writerow([row[2], row[3], row[4], row[5], "Yes" if row[6]==1 else "No"])
    return output.getvalue()

# -------------------------------
# IMPORT FROM CSV
# -------------------------------
def import_from_csv(uploaded_file):
    """
    uploaded_file: file object from Streamlit uploader
    Returns: list of tuples (site, username, password)
    """
    entries = []
    decoded = io.StringIO(uploaded_file.getvalue().decode("utf-8"))
    reader = csv.DictReader(decoded)
    for row in reader:
        entries.append((row["Site"], row["Username"], row["Password"]))
    return entries

# -------------------------------
# ENCRYPTED EXPORT
# -------------------------------
def generate_encrypted_export(data, key=None):
    """
    Returns CSV as bytes encrypted with Fernet key
    """
    if key is None:
        key = Fernet.generate_key()
    fernet = Fernet(key)
    csv_data = export_to_csv(data)
    encrypted = fernet.encrypt(csv_data.encode())
    return encrypted
