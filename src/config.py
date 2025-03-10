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
    hours, minutes = 17, 15

    # 找到最近的目标时间
    closest_target = min(target_times, key=lambda t: abs(t[0] * 60 + t[1] - (hours * 60 + minutes)))

    target_hours, target_minutes = closest_target

    # 计算当前时间和目标时间的分钟数
    current_time_minutes = hours * 60 + minutes
    target_time_minutes = target_hours * 60 + target_minutes

    if current_time_minutes >= target_time_minutes:
        print(f"当前时间 {hours}:{minutes:02d} 已经过了目标时间 {target_hours}:{target_minutes:02d}，直接返回")
        return
    else:
        wait_time = target_time_minutes - current_time_minutes
        print(f"当前时间 {hours}:{minutes:02d} 未到目标时间 {target_hours}:{target_minutes:02d}，等待 {wait_time} 分钟...")
        time.sleep(wait_time * 60)  # 模拟等待
        print(f"时间到 {hours}:{minutes + wait_time:02d}，返回")
    
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

