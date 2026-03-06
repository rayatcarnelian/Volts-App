import os
import psycopg2
import csv
import json
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# We will read this from the environment later, 
# for now, using the one provided for the migration script.
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
OFFLINE_CSV = os.path.join(os.path.dirname(os.path.dirname(__file__)), "leads_offline.csv")

def get_connection():
    """Establish a connection to the Supabase PostgreSQL database with a timeout."""
    try:
        if not SUPABASE_URL:
            print("WARNING: SUPABASE_URL not found in environment.")
            return None
        
        # connect_timeout=5 prevents the app from hanging forever if Supabase is paused
        conn = psycopg2.connect(SUPABASE_URL, sslmode='require', connect_timeout=5)
        return conn
    except psycopg2.OperationalError as e:
        print(f"Supabase connection TIMEOUT (project may be paused): {e}")
        return None
    except Exception as e:
        print(f"Error connecting to Supabase: {e}")
        return None

def _save_lead_offline(name, phone, email, status, source, user_id, notes, link, location):
    """Fallback: saves lead to a local CSV file when Supabase is unreachable."""
    file_exists = os.path.exists(OFFLINE_CSV)
    try:
        with open(OFFLINE_CSV, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(['name','phone','email','status','source','user_id','notes','link','location','saved_at'])
            writer.writerow([name, phone, email, status, source, user_id, notes, link, location, datetime.now().isoformat()])
        return True
    except Exception as e:
        print(f"Offline save failed: {e}")
        return False

def init_db():
    """
    Initialize the PostgreSQL tables required for Volts App.
    This replaces the SQLite schema initialization.
    """
    conn = get_connection()
    if not conn:
        print("Failed to initialize database connection.")
        return
        
    try:
        cursor = conn.cursor()
        
        # 1. Users Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                name TEXT NOT NULL,
                company TEXT,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                tier TEXT DEFAULT 'FREE'
            )
        ''')
        
        # 2. Leads Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS leads (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                name TEXT NOT NULL,
                phone TEXT,
                email TEXT,
                company TEXT,
                website TEXT,
                score INTEGER DEFAULT 0,
                status TEXT DEFAULT 'New',
                source TEXT DEFAULT 'Manual Input',
                notes TEXT,
                bio TEXT,
                pain_points TEXT,
                ice_breaker TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 3. Call Logs Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS call_logs (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                lead_id INTEGER REFERENCES leads(id) ON DELETE SET NULL,
                call_id TEXT NOT NULL,
                target_number TEXT,
                date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                duration INTEGER DEFAULT 0,
                cost REAL DEFAULT 0.0,
                status TEXT,
                recording_url TEXT,
                transcript TEXT,
                summary TEXT
            )
        ''')
        
        # 4. Content Studio Assets
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS studio_assets (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                type TEXT NOT NULL,
                prompt TEXT,
                url TEXT NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 5. Campaigns
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS campaigns (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                status TEXT DEFAULT 'Draft',
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 6. Campaign Leads (Join Table)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS campaign_leads (
                campaign_id INTEGER REFERENCES campaigns(id) ON DELETE CASCADE,
                lead_id INTEGER REFERENCES leads(id) ON DELETE CASCADE,
                status TEXT DEFAULT 'Pending',
                PRIMARY KEY (campaign_id, lead_id)
            )
        ''')
        
        # 7. User Settings (BYOK Architecture)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_settings (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                setting_key TEXT NOT NULL,
                setting_value TEXT NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, setting_key)
            )
        ''')

        conn.commit()
        print("Supabase PostgreSQL Database successfully initialized!")
        
    except Exception as e:
        print(f"Error initializing generic database tables: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            cursor.close()
            conn.close()

# --- V2 LOGIC (POSTGRESQL PORT) ---

def add_lead_v2(name, phone=None, email=None, source="Manual", metadata={}, bio=None, profile_url=None, price=None, area=None, status="New", company=None, role=None, location=None, link=None, user_id=None):
    """Unified entry point for V2. Postgres compatible with offline fallback."""
    conn = get_connection()
    
    # Resolve the website URL from any available source
    website = profile_url or link or ''
    # Use company or location as company field
    company_val = company or location or ''
    # Bio/notes content
    notes_val = bio or role or ''

    # FALLBACK: If Supabase is down/paused, save to local CSV so data is never lost
    if not conn:
        print(f"[OFFLINE MODE] Supabase unreachable. Saving lead '{name}' to local CSV.")
        return _save_lead_offline(name, phone, email, status, source, user_id, notes_val, website, company_val)
    
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    lead_id = None
    
    # 1. Deduplication (By Phone or Website)
    try:
        if phone:
            cursor.execute("SELECT id FROM leads WHERE phone = %s AND user_id = %s", (phone, user_id))
            res = cursor.fetchone()
            if res: lead_id = res['id']
            
        if not lead_id and website:
            cursor.execute("SELECT id FROM leads WHERE website = %s AND user_id = %s", (website, user_id))
            res = cursor.fetchone()
            if res: lead_id = res['id']
            
        created_new = False
        if not lead_id:
            # INSERT using the ACTUAL schema columns: 
            # id, user_id, name, phone, email, company, website, score, status, source, notes, bio, pain_points, ice_breaker, created_at
            cursor.execute('''
                INSERT INTO leads (name, phone, email, status, source, user_id, notes, website, company, bio)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            ''', (name, phone, email, status, source, user_id, notes_val, website, company_val, notes_val))
            lead_id = cursor.fetchone()['id']
            created_new = True
            
        conn.commit()
    except Exception as e:
        print(f"Error adding lead: {e}")
        conn.rollback()
        # If cloud insert failed, save offline as safety net
        _save_lead_offline(name, phone, email, status, source, user_id, notes_val, website, company_val)
        created_new = False
    finally:
        cursor.close()
        conn.close()
        
    return created_new

def get_lead_by_link(link, user_id=None):
    """Checks if a lead with this exact URL already exists."""
    conn = get_connection()
    if not conn: return False
    try:
        c = conn.cursor(cursor_factory=RealDictCursor)
        if user_id:
            c.execute("SELECT id FROM leads WHERE website = %s AND user_id = %s", (link, user_id))
        else:
            c.execute("SELECT id FROM leads WHERE website = %s", (link,))
        return c.fetchone() is not None
    except Exception as e:
        print(f"Error checking link: {e}")
        return False
    finally:
        if conn:
            conn.close()

def get_all_leads(user_id=None):
    """Returns a flat view of leads filtered by user_id."""
    import pandas as pd
    conn = get_connection()
    if not conn: return pd.DataFrame()
    
    try:
        c = conn.cursor(cursor_factory=RealDictCursor)
        if user_id:
            c.execute("SELECT * FROM leads WHERE user_id = %s ORDER BY id DESC", (user_id,))
        else:
            c.execute("SELECT * FROM leads ORDER BY id DESC")
        data = c.fetchall()
        df = pd.DataFrame(data)
        
        # Ensure minimum required UI columns exist, fill with defaults if missing
        required_cols = ['id', 'name', 'email', 'phone', 'company', 'website', 'status', 'source', 'notes', 'bio', 'ice_breaker', 'pain_points', 'score', 'created_at']
        for col in required_cols:
            if col not in df.columns:
                df[col] = '' if col not in ['score', 'id'] else 0
    except Exception as e:
        print(f"Error fetching leads: {e}")
        df = pd.DataFrame()
    finally:
        if conn:
            conn.close()
        
    return df

# --- STUDIO ASSETS LOGIC ---

def save_studio_asset(user_id, asset_type, asset_url, prompt):
    """Save an image or video URL generated by the Studio into the cloud gallery."""
    conn = get_connection()
    if not conn: return
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO studio_assets (user_id, type, url, prompt) VALUES (%s, %s, %s, %s)", 
                  (user_id, asset_type, asset_url, prompt))
        conn.commit()
    except Exception as e:
        print(f"Error saving asset: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def get_user_assets(user_id, asset_type=None):
    """Retrieve all saved media for a specific user, ordered by newest first."""
    import pandas as pd
    conn = get_connection()
    if not conn: return pd.DataFrame()
    
    query = "SELECT * FROM studio_assets WHERE user_id = %s "
    params = [user_id]
    
    if asset_type:
         query += "AND type = %s "
         params.append(asset_type)
         
    query += "ORDER BY created_at DESC"
    
    try:
        df = pd.read_sql_query(query, conn, params=params)
    except Exception as e:
        print(f"Error fetching assets: {e}")
        df = pd.DataFrame()
    finally:
        conn.close()
        
    return df

# --- CAMPAIGNS LOGIC ---

def create_campaign(source, search_term, user_id=None):
    conn = get_connection()
    if not conn: return None
    cursor = conn.cursor()
    cid = None
    try:
        cursor.execute("INSERT INTO campaigns (user_id, source, search_term) VALUES (%s, %s, %s) RETURNING id", 
                  (user_id, source, search_term))
        cid = cursor.fetchone()[0]
        conn.commit()
    except Exception as e:
        print(f"Error creating campaign: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
    return cid

def update_campaign_count(cid, count):
    conn = get_connection()
    if not conn: return
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE campaigns SET leads_found = %s WHERE id = %s", (count, cid))
        conn.commit()
    except Exception as e:
        print(f"Error updating campaign: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
        
def get_recent_campaigns(limit=5):
    import pandas as pd
    conn = get_connection()
    if not conn: return pd.DataFrame()
    try:
        c = conn.cursor(cursor_factory=RealDictCursor)
        c.execute(f"SELECT * FROM campaigns ORDER BY id DESC LIMIT {limit}")
        data = c.fetchall()
        df = pd.DataFrame(data)
    except Exception as e:
        print(f"Error fetching campaigns: {e}")
        df = pd.DataFrame()
    finally:
        if conn:
            conn.close()
    return df

# --- LEGACY ALIAS ---
def add_lead(name, company=None, role=None, location=None, link=None, source="Manual", bio=None, user_id=None):
    """Wrapper for V2 to support legacy calls."""
    real_source = source
    real_role = role
    
    if role and ("Facebook" in role or "Marketplace" in role):
        real_source = role
        real_role = "Listing"
        
    return add_lead_v2(name, company=company, role=real_role, location=location, link=link, source=real_source, bio=bio, user_id=user_id)

# --- AUTHENTICATION & USERS ---

def signup(email, password):
    """Creates a new user with FREE tier."""
    import bcrypt
    conn = get_connection()
    if not conn: return False, "Database connection failed"
    cursor = conn.cursor()
    
    try:
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cursor.execute('''
            INSERT INTO users (name, email, password, tier)
            VALUES (%s, %s, %s, 'FREE')
        ''', (email.split('@')[0], email, hashed))
        conn.commit()
        return True, "User created successfully."
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        return False, "Email already exists."
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        cursor.close()
        conn.close()

def login(email, password):
    """Authenticates a user and returns their data."""
    import bcrypt
    conn = get_connection()
    if not conn: return None
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            return dict(user)
        return None
    except Exception as e:
        print(f"Login error: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

def get_user_credits(user_id):
    """Refreshes credit count from DB."""
    conn = get_connection()
    if not conn: return None
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    try:
        # Note: Postgres users table doesn't have credits_image by default in the schema above, 
        # but we query what's there. Returning dummy data if missing columns for now to prevent crashes.
        cursor.execute("SELECT tier FROM users WHERE id = %s", (user_id,))
        res = cursor.fetchone()
        if res:
            return {"tier": res["tier"], "credits_image": 100, "credits_video": 100, "call_minutes_used": 0.0, "call_minutes_limit": 100.0}
        return None
    except Exception as e:
        print(f"Credit fetch error: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

def deduct_credit(user_id, usage_type="image"):
    """Deduct credit (No-op in V2 cloud migration for now, managed by Stripe later)."""
    return True

def can_make_call(user_id):
    """Check if user has remaining minutes (Always true for now in migration)."""
    return True

def get_call_credits(user_id):
    """Returns call limits."""
    return {"used": 0.0, "limit": 100.0, "remaining": 100.0}

def update_call_minutes(user_id, used_minutes):
    """Updates the used minutes parameter."""
    return True

# --- USER SETTINGS (BYOK) ---

def save_user_setting(user_id, key, value):
    """Saves or updates a user-specific API key/setting."""
    if not user_id:
        return False
        
    conn = get_connection()
    if not conn: return False
    
    try:
        c = conn.cursor()
        c.execute("""
            INSERT INTO user_settings (user_id, setting_key, setting_value)
            VALUES (%s, %s, %s)
            ON CONFLICT (user_id, setting_key) 
            DO UPDATE SET setting_value = EXCLUDED.setting_value
        """, (user_id, key, value))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error saving user setting {key}: {e}")
        return False
    finally:
        if conn: conn.close()

def get_user_setting(user_id, key, default=""):
    """Fetches a specific setting for a user."""
    if not user_id:
        return default
        
    conn = get_connection()
    if not conn: return default
    
    try:
        c = conn.cursor(cursor_factory=RealDictCursor)
        c.execute("SELECT setting_value FROM user_settings WHERE user_id = %s AND setting_key = %s", (user_id, key))
        result = c.fetchone()
        if result:
            return result['setting_value']
        return default
    except Exception as e:
        print(f"Error fetching user setting {key}: {e}")
        return default
    finally:
        if conn: conn.close()
        
def get_all_user_settings(user_id):
    """Fetches all settings for a user as a dictionary."""
    if not user_id:
        return {}
        
    conn = get_connection()
    if not conn: return {}
    
    try:
        c = conn.cursor(cursor_factory=RealDictCursor)
        c.execute("SELECT setting_key, setting_value FROM user_settings WHERE user_id = %s", (user_id,))
        results = c.fetchall()
        return {row['setting_key']: row['setting_value'] for row in results}
    except Exception as e:
        print(f"Error fetching all user settings: {e}")
        return {}
    finally:
        if conn: conn.close()

def save_studio_asset(user_id, asset_type, url, prompt):
    """Saves a generated image or video to the user's gallery."""
    conn = get_connection()
    if not conn: return False
    try:
        c = conn.cursor()
        c.execute('''
            INSERT INTO studio_assets (user_id, type, url, prompt)
            VALUES (%s, %s, %s, %s)
        ''', (user_id, asset_type, url, prompt))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error saving studio asset: {e}")
        conn.rollback()
        return False
    finally:
        if conn: conn.close()

def get_user_assets(user_id):
    """Retrieves all generated assets for a user as a pandas DataFrame."""
    import pandas as pd
    conn = get_connection()
    if not conn: return pd.DataFrame()
    try:
        query = "SELECT * FROM studio_assets WHERE user_id = %s ORDER BY created_at DESC"
        df = pd.read_sql_query(query, conn, params=(user_id,))
        return df
    except Exception as e:
        print(f"Error fetching studio assets: {e}")
        return pd.DataFrame()
    finally:
        if conn: conn.close()

if __name__ == "__main__":
    init_db()
