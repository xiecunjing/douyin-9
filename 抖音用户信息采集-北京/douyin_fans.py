# -*- coding:utf-8 -*-
from appium import webdriver
import selenium
import re
from appium.webdriver.common.touch_action import TouchAction
import time


desired_caps ={
    "platformName": "Android",#平台
    "appPackage": "com.ss.android.ugc.aweme", #安装包名称
    "noReset":'True',#是否重置app信息
    "deviceName": "MI_6", #手机型号
    "appActivity": ".main.MainActivity"#appactivity

}
#流量是否继续

def traffic_Continue(driver):
    try:
        el1 = driver.find_element_by_id('com.ss.android.ugc.aweme:id/a95') #判断继续按钮
        if el1.get_attribute('text') == '继续播放':
            el1.click()
    except Exception as e:
        print(e)
        pass

#网络超时重试判断
def network_timeout(driver):
    try:
        el1 = driver.find_element_by_xpath('//*[@resource-id="com.ss.android.ugc.aweme:id/nc"]/android.widget.TextView[3]')#重试按钮判断存在
        if el1.get_attribute('text') =='重试':
            print(el1.get_attribute('text'))
            el1.click()
    except Exception as e:
        print(e)

def get_name(driver):
    while True:
        try:
            el1 = driver.find_element_by_id('com.ss.android.ugc.aweme:id/ahj')#
            el1_text = el1.get_attribute('text')
            text_len = re.findall('[\u4e00-\u9fa5]\w', el1_text)
            if len(text_len) >=1:
                return True
            else:
                return False
        except:
            return False
def start_douyin():
    driver = webdriver.Remote('http://127.0.0.1:4723/wd/hub', desired_caps)
    time.sleep(5)

    # TouchAction(driver).tap(x=629, y=147).perform()
    timeout_count = 0
    while True:
        # 切换地区
        try:
            el2 = driver.find_element_by_id('com.ss.android.ugc.aweme:id/c9_')
            like_text = el2.get_attribute('text')
            print(like_text)
            if like_text:
                print('正常，点击下面元素%s' % like_text)
                break
            else:
                print('切换元素未出现等待一秒从新点击搜索%s' % like_text)
                time.sleep(1)
                continue
        except selenium.common.exceptions.NoSuchElementException as e:
            print(e)
            if timeout_count >= 5:
                network_timeout(driver=driver)
                timeout_count = 0

            print('元素未出现等待一秒从新获取页面')
            timeout_count += 1
            time.sleep(1)
            continue
    return driver

def douyin_search(driver,search_id):
    #点击搜索
    el1 = driver.find_element_by_id("com.ss.android.ugc.aweme:id/afo")   #搜素框，抖音更新 要换
    el1.send_keys(search_id)
    timeout_count = 0
    while True:
        try:
            search_el =driver.find_element_by_id("com.ss.android.ugc.aweme:id/afr")  #搜索按钮，抖音更新要换
            search_el_text = search_el.get_attribute('text')
            print(search_el_text)
            if search_el_text == '搜索':
                search_el.click()
                time.sleep(2)
                break
            else:
                print('切换元素未出现等待一秒从新点击位置切换%s' % search_el_text)
                time.sleep(1)
                continue
        except selenium.common.exceptions.NoSuchElementException as e:
            print(e)
            if timeout_count >= 5:
                network_timeout(driver=driver)
                timeout_count = 0
            timeout_count+=1
            time.sleep(1)

    #搜索到到用户点击
    # TouchAction(driver).tap(x=139, y=604).perform()
    TouchAction(driver).tap(x=484, y=607).perform()


    while True:
        try:
            # 界面网红作品数据信息，抖音更新要换
            zuopin_el =driver.find_element_by_xpath('//*[@resource-id="com.ss.android.ugc.aweme:id/aj4"]/android.widget.HorizontalScrollView/android.widget.FrameLayout/android.widget.LinearLayout/'
                                                    'android.widget.RelativeLayout/android.widget.TextView')
            zuopin_el_text = zuopin_el.get_attribute('text')
            if zuopin_el_text:
                # zuopin_el.click()
                print(zuopin_el_text)
                break
            else:
                print('切换元素未出现等待一秒从新获取页面%s' % zuopin_el_text)
                time.sleep(1)
                continue
        except selenium.common.exceptions.NoSuchElementException as e:
            print(e)
            if timeout_count >= 5:
                network_timeout(driver=driver)
                timeout_count = 0
            time.sleep(1)
            timeout_count+=1
    # zuopin_number = re.sub('作品 ','',zuopin_el_text)
    # zuopin_page = int(zuopin_number) / 15
    end_count = 0
    while True:
        TouchAction(driver).press(x=505, y=1397).move_to(x=584, y=425).release().perform()
        time.sleep(0.5)
        if end_count>=5:
            jieshu_text_list = []
            for i in driver.find_elements_by_xpath('//*/android.widget.TextView'):
                jieshu_text_list.append(i.get_attribute('text'))
            print(jieshu_text_list)
            if '没有'in str(jieshu_text_list):
                break
            else:
                end_count+=1
        end_count +=1
    driver.back()


def douyin_user(driver):
    pass

if __name__ == '__main__':
    driver = start_douyin()
    TouchAction(driver).tap(x=988, y=150).perform()
    douyin_ids = ['191433445','274110380','erdou','duoyuduoyu','90518269','dz0528','ShowLoGNF','717XUEJOKER','rmrbxmt']
    # douyin_ids = ['dz0528','ShowLoGNF','717XUEJOKER','rmrbxmt']
    # douyin_ids = ['']
    for douyin_id in douyin_ids:
        douyin_search(driver=driver,search_id=douyin_id)
    driver.close_app()