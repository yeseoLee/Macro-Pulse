import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options


def get_chrome_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")  # Updated headless flag
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    chrome_options.set_capability("pageLoadStrategy", "eager")

    try:
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    except Exception as e:
        print(f"Failed to initialize Chrome Driver: {e}")
        return None

def take_finviz_screenshot(output_path="finviz_map.png"):
    """
    Takes a screenshot of the Finviz map (#canvas-wrapper).
    """
    driver = get_chrome_driver()
    if not driver:
        return None

    try:
        url = "https://finviz.com/map.ashx"
        print(f"Navigating to {url}...")
        driver.get(url)

        # Wait for the map to load
        print("Waiting for map element...")
        wait = WebDriverWait(driver, 20)
        element = wait.until(
            EC.visibility_of_element_located((By.ID, "canvas-wrapper"))
        )

        # Add delay to ensure canvas is rendered
        print("Waiting for canvas to render...")
        time.sleep(5)

        # Take screenshot of the element
        element.screenshot(output_path)
        print(f"Screenshot saved to {output_path}")
        return output_path

    except Exception as e:
        import traceback

        traceback.print_exc()
        print(f"Failed to take screenshot: {e}")
        return None
    finally:
        if "driver" in locals() and driver:
            driver.quit()

def take_kospi_screenshot(output_path="kospi_map.png"):
    """
    Takes a screenshot of the KOSPI map from kospd.com
    (div.plot-container.plotly).
    """
    driver = get_chrome_driver()
    if not driver:
        return None

    try:
        url = "https://www.kospd.com/maps/1day"
        print(f"Navigating to {url}...")
        driver.get(url)
        
        # Wait for the map to load
        print("Waiting for map element...")
        wait = WebDriverWait(driver, 20)
        # Try waiting for main-svg or plot-container
        element = wait.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "div.plot-container.plotly"))
        )
        
        # Add delay to ensure canvas/svg is rendered
        print("Waiting for chart to render...")
        time.sleep(5)
        
        # Take screenshot of the element
        element.screenshot(output_path)
        print(f"Screenshot saved to {output_path}")
        return output_path
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Failed to take KOSPI screenshot: {e}")
        return None
    finally:
        if "driver" in locals() and driver:
            driver.quit()
