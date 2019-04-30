# -*- coding:utf-8 -*-
from appium import webdriver
import selenium
import re
from appium.webdriver.common.touch_action import TouchAction
import time
import requests
import json
from ftplib import FTP
import datetime
import urllib
import os
from  urllib import parse
import pymysql
import sys
# root_dir = os.path.split(os.path.abspath(sys.argv[0]))[0]
#  log_name = os.path.split(os.path.abspath(sys.argv[0]))[-1].split('.')[0]
# log_format = "%(asctime)s - %(levelname)s - %(message)s" 
# DATE_FORMAT = "%m/%d/%Y %H:%M:%S" 
# logging.basicConfig(filename='%s/log/%s-%s'%(root_dir,log_name,'Project.log'),filemode='a',level=logging.INFO,format=log_format,datefmt=DATE_FORMAT)

desired_caps ={
    "platformName": "Android",#平台
    "appPackage": "com.ss.android.ugc.aweme", #安装包名称
    "noReset":'True',#是否重置app信息
    "deviceName": "MI_6", #手机型号
    "appActivity": ".main.MainActivity"#appactivity

}
#视频界面元素检测

host = '192.168.0.33'
user = 'dev'
passwd = '1q!Q3e#E5t%T'
port=3306
db = 'inshoot'



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



class image_to_text():
    def __init__(self):
        self.loadfile_path = ''
        self.httpfile_path= ''
    def load_file(self,loadfile_path):
        ftp = FTP("bxu2442410600.my3w.com")  # 设置ftp服务器地址
        ftp.login('bxu2442410600', 'zhang123')
        ftp.set_pasv(0)
        ftp.cwd('htdocs/yanzheng/')
        localfile = loadfile_path
        f = open('%s'%loadfile_path, 'rb')
        ftp.storbinary('STOR %s' % os.path.basename(localfile), f)  # 上传文件
        filename = '%s'%(loadfile_path).split('\\')[-1]
        return self.http_file(httpfile_path='http://blog.systrong.net/yanzheng/' + filename)
    def http_file(self,httpfile_path):
        headers = {
            'Authorization':'APPCODE 0ad0ed066bbc4ee8a30f72fb60f71afe',
            'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8'
        }

        data = {
        'image':'%s'%httpfile_path
        }
        # data = {
        #     'image':image
        # }
        post_data = urllib.parse.urlencode(data)
        wb_data = requests.post(url='http://imgurlocr.market.alicloudapi.com/urlimages',data=post_data,headers=headers)
        wb_json = json.loads(wb_data.text)['result']
        text_list = []
        for text in wb_json:
            text_list.append(text['words'])
        return text_list
def check_text(driver,check_text):
    driver.save_screenshot('check_img.png')
    itx = image_to_text()
    a = itx.load_file(loadfile_path='check_img.png')
    res = re.compile('[\u4e00-\u9fa5]\w')
    if '%s'%check_text in ''.join(a):
        print('正常-%s监测到'%check_text)
        return True
    else:
        print('未监测到%s,2秒后从新截图'%check_text)
        time.sleep(2)
        return False
def check_user_text(driver,check_text):
    jieshu_text_list = []
    for i in driver.find_elements_by_xpath('//*/android.widget.EditText'):
        jieshu_text_list.append(i.get_attribute('text'))
    if '%s'%check_text in ''.join(jieshu_text_list):
        return True
    else:
        return False
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

        return False
def check_monitor(conn):
    now = datetime.datetime.now()
    start_time = (now -  datetime.timedelta(minutes=3)).strftime('%Y-%m-%d %H:%M:%S')
    end_time = now.strftime('%Y-%m-%d %H:%M:%S')
    print(start_time)
    print(end_time)
    cursor = conn.cursor()
    select_sql = "SELECT * FROM `inshoot`.`cr_dyusermes` WHERE `update_time` >= '%s' AND `update_time` <= '%s' LIMIT 0, 1000"%(start_time,end_time)
    cursor.execute(select_sql)
    datas = cursor.fetchall()
    print(datas)
    if datas:
        my_close(conn=conn)
        return True
    else:
        my_close(conn=conn)
        return False
#日志文件监控
def file_monitor_mtime(file):
    s_now_min_5 = int(datetime.datetime.now().timestamp()) -60
    file_mtime = int(os.stat(file).st_mtime)

    print(os.stat(file),s_now_min_5)
    # print('aaaaa')
    if file_mtime >= s_now_min_5:
        return True
    else:
        return False
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
        pass

def get_name(driver):
    while True:
        try:
            el1 = driver.find_element_by_id('com.ss.android.ugc.aweme:id/ahj')#
            el1_text = el1.get_attribute('text')
            # qiehuan_text = el1.get_attribute('text')
            text_len = re.findall('[\u4e00-\u9fa5]\w', el1_text)
            if len(text_len) >=1:
                return True
            else:
                return False
        except:
            return False
def project_start():
    driver = webdriver.Remote('http://127.0.0.1:4723/wd/hub',desired_caps)
    time.sleep(10)
    TouchAction(driver).tap(x=629, y=147).perform()
    timeout_count = 0
    while True:
        #切换地区
            if check_qiehuan_text(driver,click=True) == True:
                break
            else:
                continue
    #地区切换
    while True:
        try:
            # el1 = driver.find_element_by_xpath("/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.RelativeLayout/android.support.v7.widget.RecyclerView/android.widget.TextView[2]")
            el1 = driver.find_element_by_xpath("//*[@text='北京']")
            el1_text = el1.get_attribute('text')
            if el1_text == '北京':
                print('正常，进行下一步操作，（选择北京）,%s'%el1_text)
                el1.click()
                break
            else:
                print('%s元素未出现等待一秒从新点击位置切换'%el1_text)
                TouchAction(driver).tap(x=629, y=147).perform()
                time.sleep(2)
                continue
    #
        except selenium.common.exceptions.NoSuchElementException as e:
            print(e)
            print('元素未出现等待一秒从新点击位置切换')
            TouchAction(driver).tap(x=629, y=147).perform()
            time.sleep(2)
            timeout_count = 0
            if timeout_count>=5:
                python = sys.executable
                os.execl(python, python, *sys.argv)

            timeout_count+=1
            time.sleep(1)
            continue
    #再次判断切换元素是否出现
    while True:
        if check_qiehuan_text(driver=driver,click=False):
            break
        else:
            continue
    while True:
        try:
            el2 = driver.find_element_by_xpath('//*[@resource-id="com.ss.android.ugc.aweme:id/o7"]/android.widget.LinearLayout[3]/android.widget.TextView')
            el2_text = re.findall('[\u4e00-\u9fa5]\w',el2.text)
            print(el2_text)
            if len(el2_text) >=1:
                print(el2.text)
                el4 = driver.find_element_by_xpath('//*[@resource-id="com.ss.android.ugc.aweme:id/o7"]/android.widget.LinearLayout[3]/android.widget.RelativeLayout/android.widget.ImageView[1]')
                el4.click()
                break
            else:
                print('寻找视频')
                time.sleep(2)
                TouchAction(driver).press(x=505, y=500).move_to(x=584, y=425).release().perform()

                continue
        except Exception as e:
            # print()
            print('寻找视频-%s'%e)
            time.sleep(2)
            TouchAction(driver).press(x=505, y=500).move_to(x=584, y=425).release().perform()
    video_count = 0
    while True:
        print('第%s个视频'%video_count)
        video_count+=1
    #开始采集视频数据
        while True:
            if check_user_text(driver=driver,check_text='喜欢就要说出来') == True:
                time.sleep(1)
                TouchAction(driver).press(x=834, y=858).move_to(x=214, y=877).release().perform()#向左划
                break
            else:
                print('未识别到-喜欢就要说出来-等待2秒')
                time.sleep(2)
                continue

        time.sleep(3)
        count = 0
        while True:
            print('第%s次'%count)
            count+=1
            conn = my_conn(host=host, user=user, passwd=passwd, port=port, db=db)
            if count >=20:
                print('超过5分钟没有更新数据-重启程序')
                python = sys.executable
                os.execl(python, python, *sys.argv)
                # exit()
            if video_count >= 6:
                check_monitor_status  = file_monitor_mtime(file='%s/data.json'%root_dir)
                print(check_monitor_status)
                if  check_monitor_status == True:
                    time.sleep(2)
                    # TouchAction(driver).press(x=214, y=858).move_to(x=834, y=877).release().perform()#向右划
                    driver.back()

                    break
                else:
                    print('a')
                    time.sleep(2)
                    continue
            elif video_count <=6:
                if check_monitor(conn=conn) == True:
                    video_count =7
                if file_monitor_mtime(file='%s/data.json'%root_dir) == True:
                    time.sleep(2)
                    TouchAction(driver).press(x=214, y=858).move_to(x=834, y=877).release().perform()  # 向右划
                    break
                else:
                    time.sleep(2)
                    continue
        xihuan_count = 0
        while True:
            if check_user_text(driver=driver,check_text='喜欢就要说出来') == True:
                time.sleep(1)
                TouchAction(driver).press(x=214, y=800).move_to(x=214, y=300).release().perform()#向上化
                break
            else:
                print('ccc')
                if xihuan_count>=10:
                    print('程序发现异常 重启程序')
                    python = sys.executable
                    os.execl(python, python, *sys.argv)



                xihuan_count += 1
                time.sleep(2)
                continue



if __name__ == '__main__':
    root_dir = os.path.split(os.path.abspath(sys.argv[0]))[0]

    project_start()
    # conn = my_conn(host=host, user=user, passwd=passwd, port=port, db=db)
    # check_monitor(conn=conn)
    # my_close(conn=conn)
