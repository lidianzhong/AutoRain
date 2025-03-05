import time
import os
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from pyvirtualdisplay import Display
import chromedriver_autoinstaller
from .functions import setup_logger, setup_browser, load_cookies, save_cookies, find_element, check_ppt_type
from .answer import process_image
from .chatgpt import get_chatgpt_answer_from_dict
from config import *

## Close it for dev
# display = Display(visible=0, size=(1920, 1080))
# display.start()

# Auto-install chromedriver if needed
chromedriver_autoinstaller.install()

if __name__ == "__main__":
    # Init
    logger = setup_logger(LOGGER_PATH)
    browser = setup_browser(logger)

    # Try to load cookies
    load_cookies(browser, COOKIE_PATH, logger)
    browser.refresh()
    
    # Find the onlesson button
    onlesson = None
    while not onlesson:
        logger.info("Keep looking for the onlesson button")
        browser.refresh()
        time.sleep(5)
        onlesson = find_element(browser, ONLESSION_ELEMENT)
        time.sleep(10)

        # Check if the runtime has exceeded the limit
        if time.time() - RUNNING_START_TIME > MAX_WAIT_TIME:
            logger.info("There are no classes in the current time period. Exiting the program.")
            exit()
    
    # Found the onlesson button, get the lesson name
    curr_lesson_name = find_element(browser, ONLESSION_NAME_ELEMENT).text
    curr_lesson_name = curr_lesson_name.split('-')[0].strip()
    logger.info(f"Found the onlesson button, current lesson name: {curr_lesson_name}")

    # Exclude special lessons
    if any(special_lesson in curr_lesson_name for special_lesson in SPECAIL_LESSONS):
        logger.info(f"Current lesson {curr_lesson_name} is in the special lessons list, waiting for half of max runtime")
        time.sleep(MAX_RUNNING_TIME / 2)

    # Enter the lesson
    logger.info("Clicking on the onlesson button")
    onlesson.click()
    time.sleep(2)

    # Switch to the new window
    windows = browser.window_handles
    browser.switch_to.window(windows[-1])
    logger.info("Switched to the new window")

    last_index = -1

    try:
        while True:
            # Check if the runtime has exceeded the limit
            if time.time() - RUNNING_START_TIME > MAX_RUNNING_TIME:
                logger.info("End of Course, exiting the program.")
                break

            nav_bar = find_element(browser, "#app > section > section.ppt__wrapper.J_ppt > section.lesson__page > section > section > nav > section > section")
            sections = nav_bar.find_elements(By.CSS_SELECTOR, 'section[data-index]')
            data_indexs = [int(section.get_attribute('data-index')) for section in sections]
            if not data_indexs or max(data_indexs) == last_index:
                print(".", end="", flush=True)
                time.sleep(10)
                continue

            max_index = max(data_indexs)
            last_index = max_index

            # Click on the max index page
            max_index_page = nav_bar.find_element(By.CSS_SELECTOR, f'section[data-index="{max_index}"]')
            max_index_page.click()
            logger.info(f"Clicked on the max index page: {max_index}")
            time.sleep(2)

            curr_page = find_element(browser, "#app > section > section.ppt__wrapper.J_ppt > section.lesson__page > section > section > section > section.slide__info.J_container > section")

            ppt_type = check_ppt_type(curr_page, logger)
            logger.info(f"Current ppt type: {ppt_type}")

            if ppt_type == "single_choice" or ppt_type == "multiple_choice":
                countdown = curr_page.find_element(By.CSS_SELECTOR, "div.time-box > div").text

                if "倒计时" in countdown:
                    # Screenshot the page
                    logger.info("Detected quiz page, screenshotting the page")
                    screenshot_flag = curr_page.screenshot(f"./data/screenshots/{curr_lesson_name}_{max_index}.png")
                
                    if not screenshot_flag:
                        logger.error("Failed to screenshot the page")
                        raise Exception("Failed to screenshot the page")
                    
                    # Process the image
                    logger.info("Processing the image")
                    quiz_text, abcd_dict = process_image(f"./data/screenshots/{curr_lesson_name}_{max_index}.png")
                    logger.info(f"Quiz text: {quiz_text}, ABCD dict: {abcd_dict}")

                    # Answer the question
                    logger.info("Answering the question")
                    answer = get_chatgpt_answer_from_dict(quiz_text, abcd_dict)
                    logger.info(f"ChatGPT answered: {answer}")
                
                while True:
                    countdown = curr_page.find_element(By.CSS_SELECTOR, "div.time-box > div").text
                    logger.info(f"Countdown: {countdown}")
                    time.sleep(2)

                    if "倒计时" not in countdown:
                        logger.info("Countdown finished, cannot answer the question")
                        break

                    match = re.search(r"倒计时\s(\d{2}):(\d{2})", countdown)
                    if match:
                        minutes = int(match.group(1))
                        seconds = int(match.group(2))
                        total_seconds = minutes * 60 + seconds
                        if total_seconds < 10:
                            logger.info("Countdown less than 10 seconds, answering the question")
                            # Click on the answer
                            option_element = curr_page.find_element(By.CSS_SELECTOR, f'p[data-option="{answer}"]')
                            option_element.click()
                            logger.info(f"Clicked on the answer: {answer}")

                            submit_button = curr_page.find_element(By.CSS_SELECTOR, 'div.submit-btn')
                            submit_button.click()
                            logger.info("Clicked on the submit button")

                            break
            time.sleep(2)

    except Exception as e:
        logger.error(f"Program encountered an error: {str(e)}")
    finally:
        logger.info("Program ended, closing browser")
        browser.quit()
        # display.stop()
