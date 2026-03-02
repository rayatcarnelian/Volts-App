"""
AUTHENTICATION MODULE
Handles User Login, Signup, and Session Management.
Uses bcrypt for secure password hashing.
"""

import sqlite3
import datetime
import os
import bcrypt
import streamlit as st
from modules.database_v2_schema import get_connection

# --- ACCESS CONTROL ---
def _get_allowed_emails():
    """Returns list of allowed emails from env var, or None if unrestricted."""
    raw = os.getenv("ALLOWED_EMAILS", "")
    if not raw.strip():
        return None  # No restriction
    return [e.strip().lower() for e in raw.split(",") if e.strip()]

def _is_email_allowed(email):
    """Check if email is on the allowlist. Returns True if no allowlist is set."""
    allowed = _get_allowed_emails()
    if allowed is None:
        return True  # No restriction
    return email.strip().lower() in allowed

def hash_password(password):
    """Hashes a password using bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def check_password(password, hashed):
    """Checks a password against a hash."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed)

def signup(email, password):
    """Creates a new user with FREE tier. Blocked if email not on allowlist."""
    # Access control check
    if not _is_email_allowed(email):
        return False, "Registration is by invitation only. Contact admin for access."
    
    conn = get_connection()
    c = conn.cursor()
    
    try:
        hashed = hash_password(password)
        c.execute('''
            INSERT INTO users (email, password_hash, tier, credits_image, created_at, last_login)
            VALUES (?, ?, 'FREE', 5, ?, ?)
        ''', (email, hashed, datetime.datetime.now(), datetime.datetime.now()))
        conn.commit()
        return True, "User created successfully."
    except sqlite3.IntegrityError:
        return False, "Email already exists."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def login(email, password):
    """Authenticates a user and returns their data. Blocked if email not on allowlist."""
    # Access control check
    if not _is_email_allowed(email):
        return None
    
    conn = get_connection()
    c = conn.cursor()
    
    c.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = c.fetchone()
    conn.close()
    
    if user and check_password(password, user['password_hash']):
        # Update last login
        conn = get_connection()
        c = conn.cursor()
        c.execute("UPDATE users SET last_login = ? WHERE id = ?", (datetime.datetime.now(), user['id']))
        conn.commit()
        conn.close()
        return dict(user)
    
    return None

def get_user_credits(user_id):
    """Refreshes credit count from DB."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT tier, credits_image, credits_video, call_minutes_used, call_minutes_limit FROM users WHERE id = ?", (user_id,))
    res = c.fetchone()
    conn.close()
    return dict(res) if res else None

def deduct_credit(user_id, usage_type="image"):
    """Deducts 1 credit from the user."""
    conn = get_connection()
    c = conn.cursor()
    
    col = "credits_image" if usage_type == "image" else "credits_video"
    
    # Check if > 0 (handled in UI, but double check here)
    c.execute(f"UPDATE users SET {col} = {col} - 1 WHERE id = ? AND {col} > 0", (user_id,))
    conn.commit()
    conn.close()

def upgrade_user(user_id, new_tier):
    """Upgrades user tier and refills credits."""
    conn = get_connection()
    c = conn.cursor()
    
    img_limit = 500 if new_tier in ["PRO", "AGENCY"] else 5
    vid_limit = 100 if new_tier == "AGENCY" else (20 if new_tier == "PRO" else 0)
    call_limit = 100.0 if new_tier == "PRO" else (300.0 if new_tier == "AGENCY" else 2.0)
    
    c.execute('''
        UPDATE users 
        SET tier = ?, credits_image = ?, credits_video = ?,
            call_minutes_used = 0.0, call_minutes_limit = ?
        WHERE id = ?
    ''', (new_tier, img_limit, vid_limit, call_limit, user_id))
    
    conn.commit()
    conn.close()


def get_call_credits(user_id):
    """Get call minute usage and limits."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT call_minutes_used, call_minutes_limit FROM users WHERE id = ?", (user_id,))
    res = c.fetchone()
    conn.close()
    if res:
        used = res["call_minutes_used"] or 0.0
        limit = res["call_minutes_limit"] or 2.0
        return {"used": round(used, 1), "limit": round(limit, 1), "remaining": round(limit - used, 1)}
    return {"used": 0, "limit": 2, "remaining": 2}


def can_make_call(user_id):
    """Check if user has call minutes remaining."""
    credits = get_call_credits(user_id)
    return credits["remaining"] > 0


def deduct_call_minutes(user_id, minutes_used):
    """Deduct call minutes after a call ends."""
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "UPDATE users SET call_minutes_used = call_minutes_used + ? WHERE id = ?",
        (round(minutes_used, 2), user_id)
    )
    conn.commit()
    conn.close()

def upgrade_user_by_email(email, new_tier):
    """Upgrades user tier by email (useful for Stripe webhooks)."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE email = ?", (email,))
    user = c.fetchone()
    conn.close()
    
    if user:
        upgrade_user(user['id'], new_tier)
        return True
    return False

# --- PASSWORD RESET FLOW ---
def generate_reset_token(email):
    """Generates a 6-digit token and saves to DB."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE email = ?", (email,))
    user = c.fetchone()
    
    if not user:
        conn.close()
        return False, "Email not found."
        
    import random
    token = str(random.randint(100000, 999999))
    expiry = datetime.datetime.now() + datetime.timedelta(minutes=15)
    
    c.execute("UPDATE users SET reset_token = ?, reset_token_expiry = ? WHERE id = ?", (token, expiry, user['id']))
    conn.commit()
    conn.close()
    return True, token

def verify_reset_token(email, token):
    """Checks if token is valid and not expired."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT reset_token, reset_token_expiry FROM users WHERE email = ?", (email,))
    res = c.fetchone()
    conn.close()
    
    if not res:
        return False, "User not found."
        
    db_token = res['reset_token']
    db_expiry = res['reset_token_expiry']
    
    if not db_token or db_token != token:
        return False, "Invalid token."
        
    try:
        # SQLite might return string, need parsing if not auto-converted
        if isinstance(db_expiry, str):
            # Attempt basic parsing "Yz-m-d H:M:S.f"
            # Just try to compare ISO strings if format matches, otherwise datetime
            expiry_dt = datetime.datetime.fromisoformat(db_expiry)
        else:
            expiry_dt = db_expiry
            
        if datetime.datetime.now() > expiry_dt:
            return False, "Token expired."
    except:
        pass # Date parsing error, fail safe
        
    return True, "Valid"

def reset_password_with_token(email, token, new_password):
    """Resets password if token checks out."""
    valid, msg = verify_reset_token(email, token)
    if not valid:
        return False, msg
        
    hashed = hash_password(new_password)
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE users SET password_hash = ?, reset_token = NULL, reset_token_expiry = NULL WHERE email = ?", (hashed, email))
    conn.commit()
    conn.close()
    return True, "Password reset successfully."
