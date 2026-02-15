import sqlite3
import datetime
import pandas as pd

DB_FILE = "volts.db"

def get_connection():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    c = conn.cursor()
    
    # 1. CORE LEADS TABLE (The "Golden Record")
    c.execute('''
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            primary_email TEXT,
            primary_phone TEXT,
            master_status TEXT DEFAULT 'New', -- 'New', 'Qualified', 'Client', 'Blacklisted'
            total_score INTEGER DEFAULT 0,
            full_address TEXT,
            lat REAL,
            lon REAL,
            created_at DATE,
            notes TEXT
        )
    ''')
    
    # 2. SOURCE: LINKEDIN
    c.execute('''
        CREATE TABLE IF NOT EXISTS linkedin_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lead_id INTEGER,
            profile_url TEXT,
            headline TEXT,
            current_company TEXT,
            location TEXT,
            connections_count TEXT,
            about_section TEXT,
            scraped_at DATETIME,
            FOREIGN KEY(lead_id) REFERENCES leads(id)
        )
    ''')
    
    # 3. SOURCE: INSTAGRAM
    c.execute('''
        CREATE TABLE IF NOT EXISTS instagram_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lead_id INTEGER,
            username TEXT,
            profile_url TEXT,
            follower_count INTEGER,
            following_count INTEGER,
            bio_text TEXT,
            is_business_account BOOLEAN,
            visual_style_tags TEXT, -- JSON or comma-sep
            scraped_at DATETIME,
            FOREIGN KEY(lead_id) REFERENCES leads(id)
        )
    ''')
    
    # 4. SOURCE: PROPERTY PORTALS (PropGuru/iProperty)
    c.execute('''
        CREATE TABLE IF NOT EXISTS property_agents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lead_id INTEGER,
            source_portal TEXT, -- 'PropertyGuru', 'iProperty'
            agent_license TEXT,
            active_listings_count INTEGER,
            specialty_area TEXT,
            profile_url TEXT,
            scraped_at DATETIME,
            FOREIGN KEY(lead_id) REFERENCES leads(id)
        )
    ''')

    conn.commit()
    conn.close()

# --- MIGRATION UTILS ---
# We will keep the old 'add_lead' function momentarily to avoid breaking the app,
# but internally it should route to the new tables.

def add_lead_v2(name, phone=None, email=None, source="Manual", metadata={}):
    """
    Unified entry point for V2.
    metadata: dict containing platform specific fields (e.g. {'linkedin': {...}})
    """
    conn = get_connection()
    c = conn.cursor()
    
    # 1. Check if Lead exists (by Email or Phone or Name)
    # Simple dedupe for now
    lead_id = None
    
    # Check Phone
    if phone:
        c.execute("SELECT id FROM leads WHERE primary_phone = ?", (phone,))
        res = c.fetchone()
        if res: lead_id = res['id']
            
    # Check Name (Fallback)
    if not lead_id and name:
         c.execute("SELECT id FROM leads WHERE name = ?", (name,))
         res = c.fetchone()
         if res: lead_id = res['id']
    
    created_new = False
    if not lead_id:
        c.execute('''
            INSERT INTO leads (name, primary_phone, primary_email, created_at)
            VALUES (?, ?, ?, ?)
        ''', (name, phone, email, datetime.date.today()))
        lead_id = c.lastrowid
        created_new = True
        
    # 2. Insert into specialized table based on Source
    if source == "LinkedIn X-Ray":
        # Check if profile exists
        c.execute("SELECT id FROM linkedin_profiles WHERE lead_id = ?", (lead_id,))
        if not c.fetchone():
            c.execute('''
                INSERT INTO linkedin_profiles (lead_id, headline, profile_url, scraped_at)
                VALUES (?, ?, ?, ?)
            ''', (lead_id, metadata.get('bio'), metadata.get('profile_url'), datetime.datetime.now()))
            
    elif source == "Instagram":
        c.execute("SELECT id FROM instagram_profiles WHERE lead_id = ?", (lead_id,))
        if not c.fetchone():
            c.execute('''
                INSERT INTO instagram_profiles (lead_id, username, bio_text, profile_url, scraped_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (lead_id, metadata.get('username'), metadata.get('bio'), metadata.get('profile_url'), datetime.datetime.now()))
            
    # ... handle others ...

    conn.commit()
    conn.close()
    return created_new
