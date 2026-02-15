from modules.scraper_maps import MapsHunter
import time
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium import webdriver

# Monkey patch _setup_driver to force headless for testing
def patched_setup_driver(self):
    print("DEBUG: Using patched headless driver...")
    options = EdgeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--remote-allow-origins=*")
    self.driver = webdriver.Edge(options=options)

MapsHunter._setup_driver = patched_setup_driver

print("Initializing MapsHunter (Headless)...")
hunter = MapsHunter(browser_type="Edge") 
# Use a small limit to test quickly
limit = 5
keyword = "Architects in Kuala Lumpur"

print(f"Scanning for '{keyword}' with limit={limit}...")
leads = hunter.scan(keyword, limit=limit)

print(f"Scan complete. Found {len(leads)} leads.")
for i, lead in enumerate(leads):
    print(f"{i+1}. {lead['Name']} - {lead['Website']}")

hunter.close()

if len(leads) > 0 and len(leads) <= int(limit * 1.5): # buffer allowed
    print("SUCCESS: Maps scraper respected the limit logic.")
else:
    print(f"FAILURE: Expected around {limit} leads, but got {len(leads)}.")
