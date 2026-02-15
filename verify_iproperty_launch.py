from modules.scraper_iproperty import IPropertyHunter
import time

print("Testing IPropertyHunter Driver Initialization...")
try:
    hunter = IPropertyHunter()
    hunter._setup_driver()
    print("SUCCESS: Driver initialized successfully.")
    
    # Optional: Check version
    capabilities = hunter.driver.capabilities
    print(f"Browser Version: {capabilities.get('browserVersion')}")
    
    hunter.close()
except Exception as e:
    print(f"FAILURE: Driver initialization failed: {e}")
