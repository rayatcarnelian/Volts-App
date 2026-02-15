from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium import webdriver

def test_driver_manager():
    print("Testing webdriver_manager...")
    try:
        driver_path = ChromeDriverManager().install()
        print(f"Driver downloaded to: {driver_path}")
        
        # Test if it works with standard selenium
        service = Service(driver_path)
        options = webdriver.ChromeOptions()
        # options.add_argument("--headless=new")
        driver = webdriver.Chrome(service=service, options=options)
        driver.get("https://www.google.com")
        print("Standard Selenium: Success")
        driver.quit()
        return True
    except Exception as e:
        print(f"Standard Selenium Failed: {e}")
        return False

if __name__ == "__main__":
    test_driver_manager()
