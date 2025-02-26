from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver

import logging
import os
import time
from datetime import datetime
import pickle

from .upload import upload_image


def setup_logger(log_dir):
    # Create logs directory (if it doesn't exist)
    os.makedirs(log_dir, exist_ok=True)
    # Create log file name (using current date)
    log_file = os.path.join(log_dir, f'autorain_{datetime.now().strftime("%Y%m%d")}.log')
    # Configure log format
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    # Configure file handler
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(formatter)
    # Configure console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    # Get logger instance
    logger = logging.getLogger('AutoRain')
    logger.setLevel(logging.INFO)
    # Add handlers
    if not logger.hasHandlers():
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    return logger


def setup_browser(logger):
    # Set Chrome options
    chrome_options = Options()
    chrome_options.add_argument('--window-size=1920, 1080') # Set window size
    chrome_options.add_argument('--start-maximized')  # Maximize window
    chrome_options.add_argument('--disable-gpu')  # Disable GPU acceleration
    chrome_options.add_argument('--no-sandbox')  # Disable sandbox mode
    chrome_options.add_argument('--ignore-certificate-errors')  # Disable shared memory
    chrome_options.add_argument('--headless')  # Run in headless mode
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    logger.info("Initializing Chrome browser...")
    # Create Chrome browser instance
    driver = webdriver.Chrome(options=chrome_options)
    
    # Open Changjiang Yuketang
    try:
        driver.set_page_load_timeout(60)
        url = "https://changjiang.yuketang.cn/v2/web/index"
        logger.info(f"Opening Changjiang Yuketang website: {url}")
        driver.get(url)
    except Exception as e:
        logger.info(f"30 seconds timeout, trying to stop the page loading...")
        driver.execute_script('window.stop()')

    return driver


def save_cookies(driver, path, logger):
    """Save cookies to a file."""
    with open(path, 'wb') as filehandler:
        pickle.dump(driver.get_cookies(), filehandler)
    logger.info("Cookies saved successfully")


def load_cookies(driver, cookie_path, logger):
    """Load cookies from a file."""

    if not os.path.exists(cookie_path):
        logger.info(f"No cookies.pkl file found in {cookie_path} directory")
        logger.info("Trying waiting 30 seconds for user to login...")
        time.sleep(20)

        # Wait for user to login
        driver.save_screenshot('./data/login_page.png')
        logger.info("Screenshot of login page saved as login_page.png")

        # Upload screenshot to get url
        logger.info("Uploading screenshot to get URL...")
        image_url = upload_image('./data/login_page.png')
        logger.info(f"Please click on the following link to login: {image_url}")
        time.sleep(40)

        # Save cookies
        save_cookies(driver, cookie_path, logger)
        logger.info("Cookies saved successfully")
        return
        
    with open(cookie_path, 'rb') as cookiesfile:
        cookies = pickle.load(cookiesfile)
        for cookie in cookies:
            driver.add_cookie(cookie)
        logger.info("Cookies loaded successfully")
    
    return driver


def find_element(driver, query, by=By.CSS_SELECTOR, timeout=10):

    """Find element by given method and value."""

    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, query))
        )
        return element
    except Exception as e:
        return None
    

def check_ppt_type(curr_page, logger):
    """Check the type of the current PPT page."""
    
    if curr_page is None:
        logger.error(f"Check PPT type failed, cannot find element with selector: {curr_page}")
        raise Exception("Check PPT type failed")    
    if "lesson__ppt" in curr_page.get_attribute("class"):
        return "normal"
    elif "page-exercise" in curr_page.get_attribute("class"):
        # Check if the topic is single choice or multiple choice
        single_choice_flag = curr_page.find_elements(By.XPATH, ".//*[contains(@class, 'MultipleChoice')]")
        if single_choice_flag:
            return "single_choice"
        return "multiple_choice"
    else:
        raise Exception("Unknown PPT type")

