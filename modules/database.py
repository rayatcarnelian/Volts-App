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
            website TEXT,
            master_status TEXT DEFAULT 'New', -- 'New', 'Qualified', 'Client', 'Blacklisted'
            total_score INTEGER DEFAULT 0,
            fit_score INTEGER DEFAULT 0,
            engagement_score INTEGER DEFAULT 0,
            recency_penalty INTEGER DEFAULT 0,
            last_scored_at DATETIME,
            last_touched_at DATETIME,
            score_factors TEXT,
            full_address TEXT,
            lat REAL,
            lon REAL,
            created_at DATE,

            notes TEXT,
            source TEXT
        )
    ''')
    
    # Add new columns to existing table if they don't exist (migration)
    try:
        c.execute("ALTER TABLE leads ADD COLUMN fit_score INTEGER DEFAULT 0")
    except: pass
    try:
        c.execute("ALTER TABLE leads ADD COLUMN engagement_score INTEGER DEFAULT 0")
    except: pass
    try:
        c.execute("ALTER TABLE leads ADD COLUMN recency_penalty INTEGER DEFAULT 0")
    except: pass
    try:
        c.execute("ALTER TABLE leads ADD COLUMN last_scored_at DATETIME")
    except: pass
    try:
        c.execute("ALTER TABLE leads ADD COLUMN last_touched_at DATETIME")
    except: pass
    try:
        c.execute("ALTER TABLE leads ADD COLUMN score_factors TEXT")
    except: pass
    try:
        c.execute("ALTER TABLE leads ADD COLUMN source TEXT DEFAULT 'Manual'")
    except: pass
    
    try:
        c.execute("ALTER TABLE leads ADD COLUMN website TEXT")
    except: pass
    
    # --- V2 RESEARCH COLUMNS (Clay-Mode) ---
    try:
        c.execute("ALTER TABLE leads ADD COLUMN website_summary TEXT")
    except: pass
    try:
        c.execute("ALTER TABLE leads ADD COLUMN ice_breaker TEXT")
    except: pass
    try:
        c.execute("ALTER TABLE leads ADD COLUMN pain_points TEXT")
    except: pass
    try:
        c.execute("ALTER TABLE leads ADD COLUMN research_status TEXT") # 'Pending', 'Done', 'Failed'
    except: pass
    
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
    
    # 5. CAMPAIGNS (Preserve existing functionality)
    c.execute('''
        CREATE TABLE IF NOT EXISTS campaigns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME,
            source TEXT,
            search_term TEXT,
            leads_found INTEGER DEFAULT 0
        )
    ''')

    conn.commit()
    conn.close()

# --- V2 LOGIC ---

def add_lead_v2(name, phone=None, email=None, source="Manual", metadata={}, bio=None, profile_url=None, price=None, area=None, status="New", company=None, role=None, location=None, link=None):
    """
    Unified entry point for V2.
    Enhanced signature to support legacy and scraper calls.
    """
    conn = get_connection()
    c = conn.cursor()
    
    # Normalize profile_url/link
    if link and not profile_url:
        profile_url = link

    # 1. Check if Lead exists (by Email or Phone or Name or Link)
    lead_id = None
    
    # Check Link/URL if provided
    if profile_url:
        c.execute("SELECT lead_id FROM linkedin_profiles WHERE profile_url = ?", (profile_url,))
        res = c.fetchone()
        if res: lead_id = res['lead_id']

    # Check Phone
    if not lead_id and phone:
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
        # Default Coords for map visualization (KL Center + Jitter)
        import random
        d_lat = 3.147 + random.uniform(-0.05, 0.05)
        d_lon = 101.699 + random.uniform(-0.05, 0.05)
        
        c.execute('''
            INSERT INTO leads (name, primary_phone, primary_email, created_at, master_status, lat, lon, source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, phone, email, datetime.date.today(), status, d_lat, d_lon, source))
        lead_id = c.lastrowid
        created_new = True
        
    # 2. Insert into specialized table based on Source
    current_time = datetime.datetime.now()
    
    if source.startswith("LinkedIn"):
        # Check if profile exists
        c.execute("SELECT id FROM linkedin_profiles WHERE lead_id = ?", (lead_id,))
        if not c.fetchone():
            c.execute('''
                INSERT INTO linkedin_profiles (lead_id, headline, profile_url, current_company, location, scraped_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                lead_id, 
                bio if bio else role, 
                profile_url, 
                company if company else "Unknown",
                location if location else "Unknown",
                current_time
            ))
            
    elif source == "Instagram":
        c.execute("SELECT id FROM instagram_profiles WHERE lead_id = ?", (lead_id,))
        if not c.fetchone():
            c.execute('''
                INSERT INTO instagram_profiles (lead_id, username, bio_text, profile_url, scraped_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (lead_id, name, bio if bio else metadata.get('bio'), profile_url if profile_url else metadata.get('profile_url'), current_time))
            
    conn.commit()
    conn.close()
    return created_new

def get_lead_by_link(link):
    """
    Checks if a lead with the given LinkedIn profile URL already exists.
    """
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT lead_id FROM linkedin_profiles WHERE profile_url = ?", (link,))
    res = c.fetchone()
    conn.close()
    return res['lead_id'] if res else None

# --- ALIAS FOR BACKWARD COMPATIBILITY ---
def add_lead(name, phone=None, source="Manual", bio=None, email=None, profile_url=None, price=None, area=None, status="New", company=None, role=None, location=None, link=None):
    # Map legacy and custom scraper arguments to V2
    return add_lead_v2(name, phone, email, source, {}, bio, profile_url, price, area, status, company, role, location, link)
    
def get_all_leads():
    # Helper to return a flat view for the dashboard (joining tables)
    conn = get_connection()
    # Left join to get info and derive Source
    query = '''
    SELECT 
        l.id, l.name, l.primary_email as email, l.primary_phone as phone, l.master_status as status,
        COALESCE(li.headline, i.bio_text, pa.specialty_area) as bio,
        COALESCE(li.profile_url, i.profile_url, pa.profile_url) as profile_url,
        l.created_at as added_date,
        l.lat, l.lon,
        l.total_score, l.fit_score, l.engagement_score, l.recency_penalty,
        l.last_scored_at, l.last_touched_at, l.score_factors,
        l.notes,
        CASE 
            WHEN l.source IS NOT NULL AND l.source != 'Manual' THEN l.source
            WHEN li.id IS NOT NULL THEN 'LinkedIn X-Ray'
            WHEN i.id IS NOT NULL THEN 'Instagram'
            WHEN pa.id IS NOT NULL THEN pa.source_portal
            WHEN pa.id IS NOT NULL THEN pa.source_portal
            ELSE 'Manual' 
        END as source,
        l.website_summary, l.ice_breaker, l.pain_points, l.research_status
    FROM leads l
    LEFT JOIN linkedin_profiles li ON l.id = li.lead_id
    LEFT JOIN instagram_profiles i ON l.id = i.lead_id
    LEFT JOIN property_agents pa ON l.id = pa.lead_id
    '''
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def create_campaign(source, search_term):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO campaigns (timestamp, source, search_term) VALUES (?, ?, ?)", 
              (datetime.datetime.now(), source, search_term))
    conn.commit()
    cid = c.lastrowid
    conn.close()
    return cid

def update_campaign_count(cid, count):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE campaigns SET leads_found = ? WHERE id = ?", (count, cid))
    conn.commit()
    conn.close()
    
def get_recent_campaigns(limit=5):
    conn = get_connection()
    df = pd.read_sql_query(f"SELECT * FROM campaigns ORDER BY id DESC LIMIT {limit}", conn)
    conn.close()
    return df

def update_lead_contact(lead_id, email=None, phone=None):
    """
    Updates contact info for a lead found during enrichment.
    """
    conn = get_connection()
    c = conn.cursor()
    
    if email:
        c.execute("UPDATE leads SET primary_email = ? WHERE id = ?", (email, lead_id))
    
    if phone:
        c.execute("UPDATE leads SET primary_phone = ? WHERE id = ?", (phone, lead_id))
        
    conn.commit()
    conn.close()

def update_linkedin_details(lead_id, connections=None, about=None, location=None):
    """
    Updates the extended LinkedIn profile details in the sub-table.
    """
    conn = get_connection()
    c = conn.cursor()
    
    # Check if entry exists
    c.execute("SELECT id FROM linkedin_profiles WHERE lead_id = ?", (lead_id,))
    row = c.fetchone()
    
    timestamp = datetime.datetime.now()
    
    if row:
        c.execute("""
            UPDATE linkedin_profiles 
            SET connections_count = ?, about_section = ?, location = ?, scraped_at = ?
            WHERE lead_id = ?
        """, (connections, about, location, timestamp, lead_id))
    else:
        c.execute("""
            INSERT INTO linkedin_profiles (lead_id, connections_count, about_section, location, scraped_at)
            VALUES (?, ?, ?, ?, ?)
        """, (lead_id, connections, about, location, timestamp))
        
    conn.commit()
    conn.close()

# --- LEGACY ALIAS ---
def add_lead(name, company=None, role=None, location=None, link=None, source="Manual", bio=None):
    """
    Wrapper for V2 to support legacy calls.
    Mapping: 
    scraper_fb: add_lead(title, price, f"Marketplace ({query})", location, link)
    -> name=title, company=price, role=Source, location=location, link=link
    """
    # Fix for scraper_fb passing 'Source' as 3rd arg (role)
    # We need to map it correctly if it looks like a Source string
    real_source = source
    real_role = role
    
    if role and ("Facebook" in role or "Marketplace" in role):
        real_source = role
        real_role = "Listing"
        
    print(f"DEBUG: add_lead legacy called. Name={name}, Source={real_source}")
    return add_lead_v2(name, company=company, role=real_role, location=location, link=link, source=real_source, bio=bio)
