"""
AUTHENTICATION MODULE (PostgreSQL/Supabase Bridge)
Bridges legacy auth calls to the new Supabase-backed db_supabase module.
"""

import modules.db_supabase as db_supa

def signup(email, password):
    """Creates a new user using Supabase."""
    return db_supa.signup(email, password)

def login(email, password):
    """Authenticates a user using Supabase."""
    return db_supa.login(email, password)

def get_user_credits(user_id):
    """Refreshes credit count from Supabase."""
    return db_supa.get_user_credits(user_id)

def deduct_credit(user_id, usage_type="image"):
    """Deducts 1 credit from the user (Placeholder for V2)."""
    return db_supa.deduct_credit(user_id, usage_type)

def upgrade_user(user_id, new_tier):
    # Dummy pass for cloud migration
    pass

def upgrade_user_by_email(email, new_tier):
    # Dummy pass for cloud migration
    return False

def get_call_credits(user_id):
    """Get call minute usage and limits."""
    return db_supa.get_call_credits(user_id)

def can_make_call(user_id):
    """Check if user has call minutes remaining."""
    return db_supa.can_make_call(user_id)

def deduct_call_minutes(user_id, minutes_used):
    """Deduct call minutes after a call ends."""
    return db_supa.update_call_minutes(user_id, minutes_used)

# --- PASSWORD RESET FLOW (Disabled safely for V2) ---
def generate_reset_token(email):
    return False, "Password resets are temporarily disabled during cloud migration."

def verify_reset_token(email, token):
    return False, "Disabled."

def reset_password_with_token(email, token, new_password):
    return False, "Disabled."
