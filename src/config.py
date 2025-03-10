## Hepler Function
import os

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
def find_element(driver, query, by=By.CSS_SELECTOR, timeout=10):
    """Find element by given method and value."""
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, query))
        )
        return element
    except Exception as e:
        return None


# 获取程序运行时的北京时间
import subprocess
def get_system_time():
    subprocess.run(['sudo', 'timedatectl', 'set-timezone', 'Asia/Shanghai'], check=True)
    time = subprocess.check_output(['date', '+%H:%M']).decode().strip()
    hours, minutes = map(int, time.split(':'))
    return hours, minutes

# 查找是否能够找到登录二维码
def check_logma_class(driver):
    try:
        element = find_element(driver, LOGMA_ELEMENT)
        return element is not None
    except:
        print("WARNING: Unexception reach.")
        return False

# 等待到目标时间
import time
def wait_until_target_time():
    target_times = [(8, 0), (10, 0), (14, 30), (16, 30)]
    hours, minutes = get_system_time()
    
    for target_hour, target_minute in target_times:
        if (hours, minutes) < (target_hour, target_minute):
            target_seconds = ((target_hour - hours) * 60 + (target_minute - minutes)) * 60
            print(f"当前时间 {hours:02d}:{minutes:02d}，等待到 {target_hour:02d}:{target_minute:02d}...")
            time.sleep(target_seconds)
            return
    
    print("No need to wait. Continue...")

# ========================= Environment variables =========================

COOKIE_PATH = "./data/cookies.pkl"         # cookie文件路径
LOGGER_PATH = "./logs"                      # 日志文件路径

RUNNING_START_TIME = time.time()    # 程序运行时的北京时间
MAX_WAIT_TIME = 20 * 60                     # 最大等待上课时间(单位:s)
MAX_RUNNING_TIME = 100 * 60                     # 程序最长运行时间(单位:s)

LOGMA_ELEMENT = "#support-socket > div.ma > img.logma"  # 登录二维码
IS_EXIST_LOGMA_ELEMENT = check_logma_class  # 是否能够找到登录二维码

ONLESSION_ELEMENT = "#app > div.viewContainer > div > div.onlesson"     # 上课按钮
ONLESSION_NAME_ELEMENT = ONLESSION_ELEMENT + ">" + "div > div > span.name" # 课程名称

EXCLUDE_COURSES = os.environ.get("EXCLUDE_COURSES", "").split(",") # 特殊课程
API_KEY = os.environ.get("API_KEY", "") # 通义千问 API Key


# ========================= Environment variables End =========================

