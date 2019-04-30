# -*- coding:utf-8 -*-
from appium import webdriver
import selenium
import re
from appium.webdriver.common.touch_action import TouchAction
import time

import random
import pymysql
desired_caps ={
    "platformName": "Android",#平台
    "appPackage": "com.ss.android.ugc.aweme", #安装包名称
    "noReset":'True',#是否重置app信息
    "deviceName": "MI_6", #手机型号
    "appActivity": ".main.MainActivity"#appactivity

}

def my_conn(host,user,passwd,port,db):
    conn = pymysql.connect(
        host=host,
        user=user,
        passwd=passwd,
        port=port,
        db=db,
        charset='utf8mb4',
        cursorclass = pymysql.cursors.DictCursor
    )
    return conn
def my_close(conn):
    conn.close()

#流量是否继续
def check_qiehuan_text(driver,click):
    try:
        # el2 = driver.find_element_by_xpath('/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.FrameLayout/android.support.v4.view.ViewPager/android.widget.FrameLayout/android.support.v4.view.ViewPager/android.widget.TabHost/android.widget.FrameLayout/android.widget.FrameLayout[1]/android.widget.FrameLayout/android.view.ViewGroup/android.widget.FrameLayout/android.support.v4.view.ViewPager/android.widget.FrameLayout/android.view.ViewGroup/android.support.v7.widget.RecyclerView/android.widget.FrameLayout/android.widget.RelativeLayout/android.widget.RelativeLayout[1]/android.widget.TextView[3]')
        el2 = driver.find_element_by_xpath("//*[@text='切换']")
        qiehuan_text = el2.get_attribute('text')
        print(qiehuan_text)

        if qiehuan_text == '切换':
            print('正常，获取到切换元素')
            time.sleep(2)
            if click == True:
                print('点击切换')
                el2.click()
            else:
                pass
            return True
        else:
            print('切换元素未出现等待一秒从新点击位置切换%s' % qiehuan_text)
            time.sleep(1)
            return False
    except selenium.common.exceptions.NoSuchElementException as e:
        print('元素未出现等待一秒从新点击位置切换')
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
    #
    TouchAction(driver).tap(x=629, y=147).perform()
    timeout_count = 0



    while True:
        #切换地区
            if check_qiehuan_text(driver,click=False) == True:
                return driver
            else:
                continue

def douyin_search(driver,search_id,fans):
    #点击搜索
    el1 = driver.find_element_by_id("com.ss.android.ugc.aweme:id/agq")   #搜素框，抖音更新 要换
    el1.send_keys(search_id)
    timeout_count = 0
    while True:
        try:
            search_el =driver.find_elements_by_xpath("//*[@text='搜索']")  #搜索按钮，抖音更新要换
            search_el_text = search_el[0].get_attribute('text')
            print(search_el_text)
            if search_el_text == '搜索':
                search_el[0].click()
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
    TouchAction(driver).tap(x=484, y=607).perform()
    if fans == False:
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
    else:
        end_count = 0
        while True:
            # TouchAction(driver).press(x=505, y=1397).move_to(x=584, y=425).release().perform()
            time.sleep(0.5)
            jieshu_text_list = []
            for i in driver.find_elements_by_xpath('//*/android.widget.TextView'):
                jieshu_text_list.append(i.get_attribute('text'))
            print(jieshu_text_list)
            if '作品' in str(jieshu_text_list):
                break
            else:
                print('未加载到用户界面，等待2-3秒')
                time.sleep(random.uniform(2, 3))
                end_count += 1
    driver.back()


def douyin_fans(driver,search_id):
    el1 = driver.find_element_by_id("com.ss.android.ugc.aweme:id/agq")  # 搜素框，抖音更新 要换
    el1.send_keys(search_id)
    timeout_count = 0
    while True:
        try:
            search_el = driver.find_elements_by_xpath("//*[@text='搜索']")  # 搜索按钮，抖音更新要换
            search_el_text = search_el[0].get_attribute('text')
            print(search_el_text)
            if search_el_text == '搜索':
                search_el[0].click()
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
            timeout_count += 1
            time.sleep(1)

    # 搜索到到用户点击
    TouchAction(driver).tap(x=484, y=607).perform()
    end_count = 0
    while True:
        # TouchAction(driver).press(x=505, y=1397).move_to(x=584, y=425).release().perform()
        time.sleep(0.5)
        jieshu_text_list = []
        for i in driver.find_elements_by_xpath('//*/android.widget.TextView'):
            jieshu_text_list.append(i.get_attribute('text'))
        print(jieshu_text_list)
        if '作品' in str(jieshu_text_list):
            break
        else:
            print('未加载到用户界面，等待2-3秒')
            time.sleep(random.uniform(2,3))
            end_count += 1
    jiazai_count = 0
    while True:
        el1 = driver.find_elements_by_xpath('//*[@resource-id="com.ss.android.ugc.aweme:id/ak3"]')
        if len(el1) >=1:
            el1[0].click()
            break
        else:
            print('未加载到用户界面，等待2-3秒')
            time.sleep(random.uniform(2, 3))
            jiazai_count+=1
            if jiazai_count>=20:
                break
    if jiazai_count<=20:
        for i in range(0,100):
            TouchAction(driver).press(x=505, y=1397).move_to(x=584, y=425).release().perform()
            print('第%s页粉丝'%i)
            time.sleep(random.uniform(2,3))
        driver.back()
    driver.back()
def my_select_account(conn,table_name):
    cursor = conn.cursor()
    sql = 'SELECT account FROM %s'%table_name
    cursor.execute(sql)
    datas = cursor.fetchall()
    return datas

if __name__ == '__main__':
    host = '192.168.0.33'
    user = 'dev'
    passwd = '1q!Q3e#E5t%T'
    port = 3306
    db = 'inshoot'
    conn = my_conn(host=host, user=user, passwd=passwd, port=port, db=db)
    driver = start_douyin()
    el1 = driver.find_element_by_accessibility_id("搜索")
    el1.click()

    # douyin_ids = ['191433445','']
    count = 0
    douyin_ids =my_select_account(conn=conn,table_name='cr_dyusermes')
    #用户信息
    for douyin_id in douyin_ids:
        if str(douyin_id.get('account')) !='0':
            if str(douyin_id.get('account')) !='rmrbxmt':
                douyin_search(driver=driver,search_id=douyin_id.get('account'),fans=False)
            count+=1
            if count>=50:
                break
    #粉丝信息
    douyin_ids =my_select_account(conn=conn,table_name='cr_dyusermes')
    for douyin_id in douyin_ids:
        if str(douyin_id.get('account')) !='0':
            if str(douyin_id.get('account')) !='rmrbxmt':
                print(douyin_id)
                douyin_fans(driver=driver,search_id=douyin_id.get('account'))
                count+=1
                if count>=50:
                    break
    my_close(conn=conn)

    driver.close_app()