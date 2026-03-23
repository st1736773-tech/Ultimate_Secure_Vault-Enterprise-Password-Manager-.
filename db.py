import sqlite3
from datetime import datetime

DB_NAME = "vault.db"


# -------------------------------
# DATABASE CONNECTION
# -------------------------------
def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)


# -------------------------------
# CREATE TABLES
# -------------------------------
def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    # USERS TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        created_at TEXT
    )
    """)

    # PASSWORD VAULT TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS vault (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        site TEXT,
        username TEXT,
        password TEXT,
        created_at TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    conn.commit()
    conn.close()


# -------------------------------
# USER FUNCTIONS
# -------------------------------
def create_user(email, hashed_password):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
        INSERT INTO users (email, password, created_at)
        VALUES (?, ?, ?)
        """, (email, hashed_password, datetime.now().isoformat()))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()


def get_user(email):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE email=?", (email,))
    user = cursor.fetchone()

    conn.close()
    return user


# -------------------------------
# VAULT FUNCTIONS
# -------------------------------
def add_password(user_id, site, username, encrypted_password):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO vault (user_id, site, username, password, created_at)
    VALUES (?, ?, ?, ?, ?)
    """, (user_id, site, username, encrypted_password, datetime.now().isoformat()))

    conn.commit()
    conn.close()


def get_passwords(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, site, username, password, created_at
    FROM vault WHERE user_id=?
    """, (user_id,))

    data = cursor.fetchall()
    conn.close()
    return data


def delete_password(entry_id, user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    DELETE FROM vault WHERE id=? AND user_id=?
    """, (entry_id, user_id))

    conn.commit()
    conn.close()


# -------------------------------
# DASHBOARD STATS
# -------------------------------
def get_stats(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM vault WHERE user_id=?", (user_id,))
    total = cursor.fetchone()[0]

    cursor.execute("""
    SELECT COUNT(*) FROM vault
    WHERE user_id=? AND LENGTH(password) < 12
    """, (user_id,))
    weak = cursor.fetchone()[0]

    conn.close()
    return total, weak
