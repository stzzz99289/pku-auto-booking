from configparser import ConfigParser
from os import stat
from time import sleep

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as Chrome_Options
from selenium.webdriver.firefox.options import Options as Firefox_Options
from selenium.webdriver.firefox.service import Service
import warnings
import sys
import multiprocessing as mp
from env_check import *
from page_func import *
from notice import *

warnings.filterwarnings('ignore')

def load_config(config):
    conf = ConfigParser()
    conf.read(config, encoding='utf8')

    user_name = conf['login']['user_name']
    password = conf['login']['password']
    venue = conf['type']['venue']
    venue_num = int(conf['type']['venue_num'])
    start_time = conf['time']['start_time']
    end_time = conf['time']['end_time']
    wechat_notice = conf.getboolean('wechat', 'wechat_notice')
    sckey = conf['wechat']['SCKEY']
    username = conf['chaojiying']['username']
    pass_word = conf['chaojiying']['password']
    soft_id = conf['chaojiying']['soft_id']

    return (user_name, password, venue, venue_num, start_time, end_time, wechat_notice, sckey, username, pass_word, soft_id)


def log_status(config, start_time, log_str):
    print("记录日志")
    now = datetime.datetime.now()
    print(now)
    print('%s.log' % config.split('.')[0])
    with open('%s.log' % config.split('.')[0], 'a', encoding='utf-8') as fw:
        fw.write(str(now) + "\n")
        fw.write("%s\n" % str(start_time))
        fw.write(log_str + "\n")
    print("记录日志成功\n")


def page(config):
    # load config
    user_name, password, venue, venue_num, start_time, end_time, wechat_notice, sckey, username, pass_word, soft_id = load_config(config)

    # check if booking time is valid
    log_str = ""
    status = True
    start_time_list_new, end_time_list_new, delta_day_list, log_exceeds = judge_exceeds_days_limit(start_time, end_time)
    log_str += log_exceeds
    if len(start_time_list_new) == 0:
        log_status(config, [start_time.split('/'), end_time.split('/')], log_exceeds)
        return False
    
    # launch firefox browser
    firefox_options = Firefox_Options()
    firefox_options.add_argument("--headless")
    service = Service(executable_path='geckodriver')
    driver = webdriver.Firefox(service=service, options=firefox_options)
    print('Firefox browser launched\n')

    # login into IAAA
    if status:
        try:
            sleep(2)
            log_str += login(driver, user_name, password, retry=0)
        except:
            log_str += "Login failed\n"
            status = False

    # enter venue booking page
    if status:
        try:
            sleep(2)
            status, log_venue = go_to_venue(driver, venue)
            log_str += log_venue
        except:
            log_str += "failed to enter %s booking page\n" % venue
            print("failed to enter %s booking page\n" % venue)
            status = False

    # booking
    if status:
        try:
            sleep(2)
            status, log_book, start_time, end_time, venue_num = book(driver, start_time_list_new,
                                                                 end_time_list_new, delta_day_list, venue, venue_num)
            log_str += log_book
        except:
            log_str += "failed to click booking table\n"
            print("failed to click booking table\n")
            status = False

    # click 'agree statement'
    if status:
        try:
            log_str += click_agree(driver)
        except:
            log_str += "failed to click 'agree statement'\n"
            print("failed to click 'agree statement'\n")
            status = False

    # click submit booking
    if status:
        try:
            log_str += click_book(driver)
        except:
            log_str += "failed to click submit booking\n"
            print("failed to click submit booking\n")
            status = False

    # verify
    if status:
        try:
            log_str += verify(driver, username, pass_word, soft_id)
        except:
            log_str += "failed to verify\n"
            print("failed to verify\n")
            status = False

    # click pay
    if status:
        try:
            log_str += click_pay(driver)
        except:
            log_str += "failed to click pay\n"
            print("failed to click pay\n")
            status = False

    # send wechat notification if enabled
    if status and wechat_notice:
        try:
            log_str += wechat_notification(user_name,
                                           venue, venue_num, start_time, end_time, sckey)
        except:
            log_str += "failed to send wechat notification\n"
            print("failed to send wechat notification\n")

    # quit browser
    time.sleep(10)
    driver.quit()
    log_status(config, [start_time_list_new, end_time_list_new], log_str)
    return status


def sequence_run(lst_conf, browser="chrome"):
    print("按序预约")
    for config in lst_conf:
        print("预约 %s" % config)
        page(config, browser)


def multi_run(lst_conf, browser="chrome"):
    parameter_list = []
    for i in range(len(lst_conf)):
        parameter_list.append((lst_conf[i], browser))
    print("并行预约")
    pool = mp.Pool()
    pool.starmap_async(page, parameter_list)
    pool.close()
    pool.join()


if __name__ == '__main__':
    repeat_times = 1
    for i in range(repeat_times):
        status_main = page('config0.ini')
        if status_main:
            break
        else:
            print("failed to book venue, retrying...")
    if not status_main:
        print("failed to book venue after %d times" % repeat_times)
