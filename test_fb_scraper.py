from modules.scraper_fb import FacebookHunter
import time

def test_marketplace():
    print("Testing Marketplace...")
    
    # Cleanup old test data
    import sqlite3
    conn = sqlite3.connect("volts.db")
    conn.execute("DELETE FROM leads WHERE source LIKE 'Facebook%' OR source LIKE 'Marketplace%'")
    conn.commit()
    conn.close()
    
    hunter = FacebookHunter()
    # Test with a generic query, no city URL (global search)
    try:
        count = hunter.hunt_marketplace("", "Laptop", limit=3)
        print(f"Marketplace Count: {count}")
    except Exception as e:
        print(f"Marketplace Error: {e}")
    finally:
        hunter.close()
        
    # Verify DB
    import sqlite3
    conn = sqlite3.connect("volts.db")
    c = conn.cursor()
    leads = c.execute("SELECT * FROM leads WHERE source LIKE 'Facebook Marketplace%' ORDER BY id DESC LIMIT 5").fetchall()
    print(f"\n[VERIFICATION] Database Start Check:")
    if leads:
        for l in leads:
            print(f"- Found: {l[1]} ({l[7]})") # Name, Source
    else:
        print("- No leads found in DB!")
    conn.close()

if __name__ == "__main__":
    test_marketplace()
