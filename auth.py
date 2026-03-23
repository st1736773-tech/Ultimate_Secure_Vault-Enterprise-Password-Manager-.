import bcrypt
from db import create_user, get_user


# -------------------------------
# HASH PASSWORD
# -------------------------------
def hash_password(password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode(), salt)
    return hashed.decode()


# -------------------------------
# VERIFY PASSWORD
# -------------------------------
def verify_password(password, hashed_password):
    return bcrypt.checkpw(password.encode(), hashed_password.encode())


# -------------------------------
# REGISTER USER
# -------------------------------
def register_user(email, password):
    # Check if user exists
    if get_user(email):
        return False, "User already exists"

    hashed = hash_password(password)
    success = create_user(email, hashed)

    if success:
        return True, "User registered successfully"
    else:
        return False, "Registration failed"


# -------------------------------
# LOGIN USER
# -------------------------------
def login_user(email, password):
    user = get_user(email)

    if not user:
        return False, "User not found", None

    stored_password = user[2]

    if verify_password(password, stored_password):
        return True, "Login successful", user
    else:
        return False, "Invalid password", None
