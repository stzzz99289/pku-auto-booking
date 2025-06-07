from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from urllib.parse import quote
import time
import datetime
import warnings
from selenium.webdriver.common.action_chains import ActionChains
from chaojiying import *
import base64

warnings.filterwarnings('ignore')


def login(driver, user_name, password, retry=0):
    if retry == 3:
        return 'IAAA login failed. \n'

    print('IAAA login...')

    # visit portal and redirect to iaaa
    appID = 'portal2017'
    iaaaUrl = 'https://iaaa.pku.edu.cn/iaaa/oauth.jsp'
    appName = quote('北京大学校内信息门户新版')
    redirectUrl = 'https://portal.pku.edu.cn/portal2017/ssoLogin.do'
    driver.get('https://portal.pku.edu.cn/portal2017/')
    driver.get(f'{iaaaUrl}?appID={appID}&appName={appName}&redirectUrl={redirectUrl}')

    # enters username and password, then click login button
    time.sleep(2)
    WebDriverWait(driver, 10).until_not(
        EC.visibility_of_element_located((By.CLASS_NAME, "loading.ivu-spin.ivu-spin-large.ivu-spin-fix")))
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, 'logon_button')))
    driver.find_element(By.ID, 'user_name').send_keys(user_name)
    WebDriverWait(driver, 10).until_not(
        EC.visibility_of_element_located((By.CLASS_NAME, "loading.ivu-spin.ivu-spin-large.ivu-spin-fix")))
    time.sleep(0.2)
    driver.find_element(By.ID, 'password').send_keys(password)
    WebDriverWait(driver, 10).until_not(
        EC.visibility_of_element_located((By.CLASS_NAME, "loading.ivu-spin.ivu-spin-large.ivu-spin-fix")))
    time.sleep(0.2)
    driver.find_element(By.ID, 'logon_button').click()

    # check if login is successful by checking if the page contains element with id 'all'
    try:
        WebDriverWait(driver, 50).until(EC.visibility_of_element_located((By.ID, 'all')))
        print('IAAA login success')
        return 'IAAA login success\n'
    except:
        print('Retrying...')
        login(driver, user_name, password, retry + 1)


def go_to_venue(driver, venue, retry=0):
    if retry == 3:
        print("Enter venue %s failed" % venue)
        log_str = "Enter venue %s failed\n" % venue
        return False, log_str

    print("Entering venue %s" % venue)
    log_str = "Entering venue %s\n" % venue

    try:
        print("Step 1: Clicking 'all' button")
        butt_all = driver.find_element(By.ID, 'all')
        driver.execute_script('arguments[0].click();', butt_all)
        WebDriverWait(driver, 10).until_not(
            EC.visibility_of_element_located((By.CLASS_NAME, "loading.ivu-spin.ivu-spin-large.ivu-spin-fix")))
        
        print("Step 2: Clicking venues button and opening new window")
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, 'tag_s_venues')))
        time.sleep(0.5)
        driver.find_element(By.ID, 'tag_s_venues').click()
        while len(driver.window_handles) < 2:
            time.sleep(0.5)
        driver.switch_to.window(driver.window_handles[-1])
        WebDriverWait(driver, 10).until_not(
            EC.visibility_of_element_located((By.CLASS_NAME, "loading.ivu-spin.ivu-spin-large.ivu-spin-fix")))
        time.sleep(5)
        
        print("Step 3: Clicking venue selection")
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located(
            (By.XPATH, "/html/body/div[1]/div/div/div[2]/div[1]/div[2]/div[1]/div[2]/div[2]/div")))
        driver.find_element(By.XPATH,
                            "/html/body/div[1]/div/div/div[2]/div[1]/div[2]/div[1]/div[2]/div[2]/div").click()
        WebDriverWait(driver, 10).until_not(
            EC.visibility_of_element_located((By.CLASS_NAME, "loading.ivu-spin.ivu-spin-large.ivu-spin-fix")))
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, f"//*[contains(text(), '{venue}')]")))
        time.sleep(2)
        
        print("Step 4: Clicking specific venue with name containing %s" % venue)
        driver.find_element(By.XPATH,
                            f"//*[contains(text(), '{venue}')]").click()
        status = True
        log_str += "Enter venue %s success\n" % venue

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        print("retrying")
        status, log_str = go_to_venue(driver, venue, retry + 1)
    return status, log_str


def click_agree(driver):
    print("clicking 'agree statement'")
    log_str = "clicking 'agree statement'\n"
    driver.switch_to.window(driver.window_handles[-1])
    WebDriverWait(driver, 10).until_not(
        EC.visibility_of_element_located((By.CLASS_NAME, "loading.ivu-spin.ivu-spin-large.ivu-spin-fix")))
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CLASS_NAME, 'ivu-checkbox-wrapper')))
    driver.find_element(By.CLASS_NAME, 'ivu-checkbox-wrapper').click()
    print("clicking 'agree statement' success\n")
    log_str += "clicking 'agree statement' success\n"
    return log_str


def judge_exceeds_days_limit(start_time, end_time):
    start_time_list = start_time.split('/')
    end_time_list = end_time.split('/')
    print("time range list: ", list(zip(start_time_list, end_time_list)))

    now = datetime.datetime.today()
    today = datetime.datetime.strptime(str(now)[:10], "%Y-%m-%d")
    time_hour = datetime.datetime.strptime(
        str(now).split()[1][:-7], "%H:%M:%S")
    time_11_55 = datetime.datetime.strptime(
        "11:55:00", "%H:%M:%S")
    # time_11_55 = datetime.datetime.strptime(
    #     str(now).split()[1][:-7], "%H:%M:%S")

    start_time_list_new = []
    end_time_list_new = []
    delta_day_list = []
    log_str = ""
    for k in range(len(start_time_list)):
        start_time = start_time_list[k]
        end_time = end_time_list[k]
        if len(start_time) > 8:
            date = datetime.datetime.strptime(
                start_time.split('-')[0], "%Y%m%d")
            delta_day = (date - today).days
        else:
            delta_day = (int(start_time[0]) + 6 - today.weekday()) % 7
            date = today + datetime.timedelta(days=delta_day)
        # print("current date:", str(date).split()[0])

        if delta_day > 3 or (delta_day == 3 and (time_hour < time_11_55)):
            print("You can only book venues within 3 days after 11:55 AM")
            log_str = "You can only book venues within 3 days after 11:55 AM\n"
            break
        else:
            start_time_list_new.append(start_time)
            end_time_list_new.append(end_time)
            delta_day_list.append(delta_day)
            print("delta day: %d and time range: %s ~ %s is valid" % (delta_day, start_time, end_time))
            log_str = "delta day: %d and time range: %s ~ %s is valid\n" % (delta_day, start_time, end_time)
    return start_time_list_new, end_time_list_new, delta_day_list, log_str


def book(driver, start_time_list, end_time_list, delta_day_list, venue, venue_num=-1):
    print("finding free court...")
    log_str = "finding free court...\n"

    def judge_close_to_time_12():
        now = datetime.datetime.today()
        time_hour = datetime.datetime.strptime(
            str(now).split()[1][:-7], "%H:%M:%S")
        time_11_55 = datetime.datetime.strptime(
            "11:55:00", "%H:%M:%S")
        time_12 = datetime.datetime.strptime(
            "12:00:00", "%H:%M:%S")
        if time_hour < time_11_55:
            return 0
        elif time_11_55 < time_hour < time_12:
            return 1
        elif time_hour > time_12:
            return 2

    def judge_in_time_range(start_time, end_time, venue_time_range):
        vt = venue_time_range.split('-')
        vt_start_time = datetime.datetime.strptime(vt[0], "%H:%M")
        vt_end_time = datetime.datetime.strptime(vt[1], "%H:%M")
        # print(vt_start_time)
        # print(start_time)
        if start_time <= vt_start_time and vt_end_time <= end_time:
            return True
        else:
            return False

    def move_to_date(delta_day):
        # for i in range(delta_day):
        WebDriverWait(driver, 10).until_not(
            EC.visibility_of_element_located((By.CLASS_NAME, "loading.ivu-spin.ivu-spin-large.ivu-spin-fix")))
        driver.find_element(By.XPATH,
                            f'/html/body/div[1]/div/div/div[3]/div[2]/div/div[1]/div[2]/div[1]/div[2]/div[{delta_day + 1}]').click()
        print("moved to date %d" % (delta_day + 1))
        # time.sleep(0.2)

    def next_page():
        # 如果第一页没有，就往后翻，直到不存在下一页
        WebDriverWait(driver, 10).until_not(
            EC.visibility_of_element_located((By.CLASS_NAME, "loading.ivu-spin.ivu-spin-large.ivu-spin-fix")))
        # time.sleep(0.1)
        driver.find_element(By.XPATH,
                            '//*[@id="scrollTable"]/table/tbody/tr[last()]/td[last()]/div/i').click()

    def page_num(venue, start_time):
        start = str(start_time).split()[1]
        list_num = int(start[:2])
        if venue == "羽毛球场":
            lst = [0, 0, 0, 0, 0, 0, 0, 0, [0, 1], [0, 2], [0, 3], [0, 4], [0, 5], [1, 1], [1, 2], [1, 3], [1, 4], [1, 5], [2, 1], [2, 2], [2, 3], [2, 4], [2, 5]]
            return lst[list_num][0], lst[list_num][1]
        if venue == "羽毛球馆":
            lst = [0, 0, 0, 0, 0, 0, 0, [0, 1], [0, 2], [0, 3], [0, 4], [0, 5], [1, 1], [1, 2], [1, 3], [1, 4], [1, 5], [2, 1], [2, 2], [2, 3], [2, 4], [2, 5], [3, 1]]
            return lst[list_num][0], lst[list_num][1]
        return 0, 0

    def click_free(venue_num_click, time_num):
        WebDriverWait(driver, 5).until_not(
            EC.visibility_of_element_located((By.CLASS_NAME, "loading.ivu-spin.ivu-spin-large.ivu-spin-fix")))
        trs = driver.find_elements(By.TAG_NAME, 'tr')
        trs = (driver.find_elements(By.TAG_NAME, 'tbody'))
        trs = trs[1].find_elements(By.TAG_NAME, 'tr')
        trs_list = []
        for i in range(0, len(trs) - 1):
            trs_list.append(trs[i].find_elements(By.TAG_NAME, 'td'))
        # print(len(trs_list))
        if len(trs_list) == 0:
            return False, -1, 0
        # print(len(trs_list[0]))
        # print(len(trs_list[1]))
        # print(len(trs_list[2]))
        # print(venue_num_click, time_num)
        if venue_num_click != -1:
            class_name = trs_list[venue_num_click - 1][time_num].find_element(By.TAG_NAME,
                                                                              'div').get_attribute("class")
            print(class_name)
            if class_name.split()[2] == 'free':
                trs_list[venue_num_click - 1][time_num].find_element(By.TAG_NAME, 'div').click()
                return True, venue_num_click

        else:
            # 随机点一列free的，防止每次都点第一列
            for i in range(len(trs_list) - 1):
                class_name = trs_list[i][time_num].find_element(By.TAG_NAME,
                                                                'div').get_attribute("class")
                print(class_name)
                if class_name.split()[2] == 'free':
                    venue_num_click = i
                    trs_list[i][time_num].find_element(By.TAG_NAME, 'div').click()
                    return True, venue_num_click

        return False, venue_num_click

    # switch to the newest window which should be the venue booking page
    driver.switch_to.window(driver.window_handles[-1])
    WebDriverWait(driver, 10).until_not(
        EC.visibility_of_element_located((By.CLASS_NAME, "loading.ivu-spin.ivu-spin-large.ivu-spin-fix")))
    
    # check if current time is between 11:55 and 12:00
    flag = judge_close_to_time_12()

    # if current time is between 11:55 and 12:00, stay on this page, waiting for 12:00 to book venue
    if flag == 1:
        while True:
            # every 0.5 seconds, check if current time is after 12:00
            flag = judge_close_to_time_12()
            if flag == 2:
                break
            else:
                time.sleep(0.5)

        # once pass 12:00, refresh the page
        driver.refresh()
        WebDriverWait(driver, 5).until_not(
            EC.visibility_of_element_located((By.CLASS_NAME, "loading.ivu-spin.ivu-spin-large.ivu-spin-fix")))
    
    # find free court by specified time
    status = False
    for k in range(len(start_time_list)):
        # find court by specified time
        start_time = start_time_list[k]
        end_time = end_time_list[k]
        delta_day = delta_day_list[k]
        if k != 0:
            driver.refresh()
            time.sleep(0.5)
        move_to_date(delta_day)
        start_time = datetime.datetime.strptime(
            start_time.split('-')[1], "%H%M")
        end_time = datetime.datetime.strptime(end_time.split('-')[1], "%H%M")
        print("booking court %s ~ %s" % (str(start_time).split()[1], str(end_time).split()[1]))
        page, time_num = page_num(venue, start_time)
        print("page: %d, time_num: %d" % (page, time_num))
        for _ in range(page):
            next_page()

        # try to click court
        status, venue_num = click_free(venue_num, time_num)
        if status:
            log_str += "found free court, court number: %d\n" % venue_num
            print("found free court, court number: %d\n" % venue_num)
            now = datetime.datetime.now()
            today = datetime.datetime.strptime(str(now)[:10], "%Y-%m-%d")
            date = today + datetime.timedelta(days=delta_day)
            return status, log_str, str(date)[:10] + str(start_time)[10:], str(date)[:10] + str(end_time)[10:], venue_num
        else:
            log_str += "no free court\n"
            print("no free court\n")
    return status, log_str, None, None, None


def click_book(driver):
    print("clicking 'submit booking'")
    log_str = "clicking 'submit booking'\n"
    driver.switch_to.window(driver.window_handles[-1])
    WebDriverWait(driver, 10).until_not(
        EC.visibility_of_element_located((By.CLASS_NAME, "loading.ivu-spin.ivu-spin-large.ivu-spin-fix")))
    # WebDriverWait(driver, 10).until(
    #     EC.visibility_of_element_located(
    #         (By.XPATH, '/html/body/div[1]/div/div/div[3]/div[2]/div/div[2]/div[5]/div/div[2]')))
    driver.find_element(By.XPATH,
                        '/html/body/div[1]/div/div/div[3]/div[2]/div/div[1]/div[2]/div[5]/div[2]/div[1]').click()
    print("clicking 'submit booking' success\n")
    log_str += "clicking 'submit booking' success\n"
    return log_str


def click_submit_order(driver):
    print("提交订单")
    log_str = "提交订单\n"
    driver.switch_to.window(driver.window_handles[-1])
    WebDriverWait(driver, 10).until_not(
        EC.visibility_of_element_located((By.CLASS_NAME, "loading.ivu-spin.ivu-spin-large.ivu-spin-fix")))
    time.sleep(3)
    driver.find_element(By.XPATH,
                        '/html/body/div[1]/div/div/div[3]/div[2]/div/div[2]/div[2]/div[1]').click()
    # result = EC.alert_is_present()(driver)
    print("提交订单成功")
    log_str += "提交订单成功\n"
    return log_str


def verify(driver, username, pass_word, soft_id):
    print("entering verification captcha")
    log_str = "entering verification captcha\n"

    # get target image and letters order to click
    target_element = driver.find_element(By.XPATH,
                                         "/html/body/div[1]/div/div/div[3]/div[2]/div/div[1]/div[2]/div[4]/div[3]/div/div[2]/div/div[1]/div/img")
    order = driver.find_element(By.XPATH,
                                "/html/body/div[1]/div/div/div[3]/div[2]/div/div[1]/div[2]/div[4]/div[3]/div/div[2]/div/div[2]/span")
    image_uri = target_element.get_attribute("src")
    order_str = order.text
    order_words = order_str[-6:-1].split(",")
    print("letters to click in order: ", order_words)

    # use chaojiying api to get answer
    data_start = image_uri.find(",") + 1
    image_base64 = image_uri[data_start:]
    image_content = base64.b64decode(image_base64)
    chaojiying = Chaojiying_Client(username, pass_word, soft_id)
    ans_str = chaojiying.PostPic(image_content, 9501)
    words = ans_str['pic_str'].split('|')
    words_loc = []
    for i in range(len(words)):
        words_loc.append(words[i].split(','))
    print("detected letters and their locations: ", words_loc)

    # perform actions to click letters in order
    actions = ActionChains(driver)
    for i in range(3):
        for j in range(len(words_loc)):
            if order_words[i] == words_loc[j][0]:
                # print(words_loc[j][0], int(words_loc[j][1]), int(words_loc[j][2]))
                actions.move_to_element_with_offset(target_element, int(words_loc[j][1]) - 160,
                                                    int(words_loc[j][2]) - 72).click().perform()
    print("entering verification captcha success\n")
    log_str += "entering verification captcha success\n"
    return log_str


def click_pay(driver):
    print("付款（校园卡）")
    log_str = "付款（校园卡）\n"
    time.sleep(30)
    print("需要用户自行付款")
    log_str += "需要用户自行付款\n"
    return log_str


if __name__ == '__main__':
    pass
