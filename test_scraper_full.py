import sys
from unittest.mock import MagicMock

# AGGRESSIVE MOCKING OF STREAMLIT
mock_st = MagicMock()
sys.modules['streamlit'] = mock_st

import logging
from modules.scraper_linkedin_xray import LinkedInXRay
from modules import database as db

# Configure logging
logging.basicConfig(level=logging.INFO)

def test_scraper():
    print("Testing LinkedInXRay scraper workflow (CLI Mode)...")
    
    # Initialize DB
    db.init_db()
    
    scraper = LinkedInXRay()
    # Use a query that specifically targets profiles
    role = "CEO"
    loc = "Kuala Lumpur"
    
    print(f"\nRunning hunt_targets for {role} in {loc} (Targeting profiles)...")
    try:
        # Increase limit to give it more chance
        count = scraper.hunt_targets(role=role, location=loc, limit=10)
        print(f"\nFinal Result: Found {count} leads.")
        
        # Verify in DB
        conn = db.get_connection()
        c = conn.cursor()
        # JOIN leads with linkedin_profiles to get the name
        c.execute('''
            SELECT l.name, lp.profile_url 
            FROM leads l
            JOIN linkedin_profiles lp ON l.id = lp.lead_id
            ORDER BY lp.id DESC LIMIT 5
        ''')
        rows = c.fetchall()
        print("\nLatest Profile Entries in DB:")
        for r in rows:
            print(f"- {r[0]} | {r[1]}")
        conn.close()
        
    except Exception as e:
        print(f"\nTEST FAILED with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_scraper()
