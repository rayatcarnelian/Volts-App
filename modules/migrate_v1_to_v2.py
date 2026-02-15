import sqlite3
import shutil
import os
import datetime

# --- CONFIG ---
DB_FILE = "volts.db"
BACKUP_FILE = f"volts_backup_{int(datetime.datetime.now().timestamp())}.db"

def migrate():
    # FORCE RECOVERY from known good backup
    source_db = "volts_backup_1769590296.db"
    print(f"FORCING MIGRATION from {source_db}...")
    
    # 2. Connect to Old DB
    conn_old = sqlite3.connect(source_db)
    conn_old.row_factory = sqlite3.Row
    old_leads = conn_old.execute("SELECT * FROM leads").fetchall()
    conn_old.close()
    
    print(f">> Loaded {len(old_leads)} records from V1.")
    
    # 3. Destroy and Re-Init V2
    # Instead of deleting lines, we drop tables one by one to avoid file lock issues
    print(">> Dropping old tables...")
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute("DROP TABLE IF EXISTS leads")
        c.execute("DROP TABLE IF EXISTS linkedin_profiles")
        c.execute("DROP TABLE IF EXISTS instagram_profiles")
        c.execute("DROP TABLE IF EXISTS property_agents")
        conn.commit()
    except Exception as e:
        print(f"WARN: Could not drop tables: {e}")
    finally:
        conn.close()
            
    import modules.database_v2_schema as db_v2
    db_v2.init_db()
    
    print(">> V2 Schema Initialized.")
    
    # 4. Data Transformation & Loading
    count = 0
    for row in old_leads:
        # Map V1 fields to V2
        row_data = dict(row)
        
        # Determine Metadata based on Source
        meta = {}
        if row_data.get('source') == 'LinkedIn X-Ray':
            meta = {
                'bio': row_data.get('bio'),
                'profile_url': row_data.get('profile_url')
            }
        elif row_data.get('source') == 'Instagram':
             meta = {
                'username': row_data.get('name'), 
                'bio': row_data.get('bio'),
                'profile_url': row_data.get('profile_url')
            }
            
        # Insert using V2 Logic
        db_v2.add_lead_v2(
            name=row_data.get('name'),
            phone=row_data.get('phone'), 
            email=row_data.get('email'),
            source=row_data.get('source', 'Manual'),
            metadata=meta
        )
        count += 1
        
    print(f"SUCCESS: MIGRATION COMPLETE. {count} records transformed to Neural Core.")

if __name__ == "__main__":
    migrate()
