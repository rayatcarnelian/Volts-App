import undetected_chromedriver as uc
import time
from selenium.common.exceptions import SessionNotCreatedException

print("Testing Component: undetected_chromedriver")

try:
    print("Attempt 1: Standard Init...")
    driver = uc.Chrome(headless=True)
    print("SUCCESS: Standard Init worked.")
    driver.quit()
except SessionNotCreatedException as e:
    print(f"FAILURE: Standard Init failed as expected: {e}")
    
    print("\nAttempt 2: Version 144 Forced Init...")
    try:
        # Force version 144 which matches the user's browser
        driver = uc.Chrome(headless=True, version_main=144)
        print("SUCCESS: Version 144 Init worked.")
        driver.quit()
    except Exception as e2:
        print(f"FAILURE: Version 144 Init also failed: {e2}")
        
except Exception as e:
    print(f"FAILURE: Unexpected error during standard init: {e}")
