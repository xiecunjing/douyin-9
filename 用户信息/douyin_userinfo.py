import requests
import json
import datetime
import pymysql
import random
import time
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
def get_fans_uid(conn,account):
    cursor = conn.cursor()
    sql = "SELECT uid,account FROM cr_dy_fans_mes WHERE account ='%s'"%account
    cursor.execute(sql)
    data = cursor.fetchone()
    return data
    pass
def my_close(conn):
    conn.close()
def get_constellation(month, date):
    dates = (21, 20, 21, 21, 22, 22, 23, 24, 24, 24, 23, 22)
    constellations = ("摩羯", "水瓶", "双鱼", "白羊", "金牛", "双子", "巨蟹", "狮子", "处女", "天秤", "天蝎", "射手", "摩羯")
    if date < dates[month-1]:
        return constellations[month-1]
    else:
        return constellations[month]
def my_insert(conn,data,table_name):
    try:
        keys_sql = ','.join(data.keys())
        values_sql = []
        for v in data.values():
            values_sql.append('"%s"' % v)
        a = ','.join(values_sql)
        sql = "INSERT INTO %s(%s) VALUES (%s)" % (table_name,keys_sql, a)
        # print(sql)
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()
    except Exception as e:
        keys_sql = ','.join(data.keys())
        values_sql = []
        for v in data.values():
            values_sql.append("'%s'" % v)
        a = ','.join(values_sql)
        # print(len(data.values()))
        # print(len(data.keys()))
        sql = 'INSERT INTO %s(%s) VALUES (%s)' % (table_name, keys_sql, a)
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()
def my_update(conn,data,table_name,cloumn):
    cursor = conn.cursor()

    sql_list = []
    for i in data:
        if i != 'uid':
            s = str(i)+'='+"'%s'"%str(data[i])
            sql_list.append(s)
    c = ','.join(sql_list)
    sql  = 'UPDATE %s set %s where %s = "%s"'%(table_name,c,cloumn,data['%s'%cloumn])
    cursor.execute(sql)
    conn.commit()
def my_select(conn,column,table_name):
    cursor = conn.cursor()
    select_sql = "SELECT %s FROM %s "%(column,table_name)
    cursor.execute(select_sql)
    datas = cursor.fetchall()
    video_ids = []
    for video_id in datas:
        video_ids.append('%s'%video_id.get('%s'%column))
    return video_ids
def my_select_account(conn,table_name):
    cursor = conn.cursor()
    sql = 'SELECT fans_uid FROM %s'%table_name
    cursor.execute(sql)
    datas = cursor.fetchall()
    return datas
def get_userinfo(conn,fans_uid):
    url = 'https://aweme-eagle.snssdk.com/aweme/v1/user/?'
    now = datetime.datetime.now()
    now_timestamp =now.timestamp()
    params_data = {
        'user_id':'%s'%fans_uid,
        'retry_type':'no_retry',
        'iid':'70543539397',
        'device_id':'60067084431',
        'ac':'wifi',
        'channel':'xiaomi',
        'aid':'1128',
        'app_name':'aweme',
        'version_code':'600',
        'version_name':'6.0.0',
        'device_platform':'android',
        'ssmix':'a',
        'device_type':'MI 6',
        'device_brand':'Xiaomi',
        'language':'zh',
        'os_api':'26',
        'os_version':'8.0.0',
        'uuid':'867391031793024',
        'openudid':'f24c369321aa71b1',
        'manifest_version_code':'600',
        'resolution':'1080*1920',
        'dpi':'480',
        'update_version_code':'6002',
        '_rticket':round(float(now_timestamp)*1000,0),
        'mcc_mnc':'46011',
        'ts':now_timestamp,
        'js_sdk_version':'1.14.5.20',
    }
    headers = {
        'accept-encoding':'gzip',
        'x-ss-req-ticket':'%s'%round(float(now_timestamp)*1000,0),
        'x-tt-token':'0072d0a393a18fef963114bbb700cb60b98ed430b2756e7bf9706c14ff82a828244546cdddfdbe21866d442c435a97d7e936',
        'sdk-version':'1',
        'user-agent':'com.ss.android.ugc.aweme/600 (Linux; U; Android 8.0.0; zh_CN; MI 6; Build/OPR1.170623.027; Cronet/58.0.2991.0)',
        'x-khronos':'%s'%now_timestamp,
        'x-pods':'',
    }
    wb_data = requests.get(url=url,params=params_data,headers=headers,verify=False)
    data = json.loads(wb_data.text)
    print(data)
    # uid_res = re.compile('user_id=(\d+)&')

    account = data.get('user').get('short_id')
    if str(account) == '0':
        account = data.get('user').get('unique_id')
    else:
        account = account
    uid = get_fans_uid(conn=conn, account=account).get('uid')
    gender = data.get('user').get('gender')
    city = data.get('user').get('city')
    province = data.get('user').get('province')
    if str(gender) == 'None':
        gender = 0
    birthday = data.get('user').get('birthday')
    now_year = datetime.datetime.now().strftime('%Y')
    if birthday:
        birthday = datetime.datetime.strptime(birthday, '%Y-%m-%d')
        birthday = birthday
        year = birthday.strftime('%Y')
        month = birthday.strftime('%m')
        day = birthday.strftime('%d')
        constellation = get_constellation(month=int(month), date=int(day))
        age = int(now_year) - int(year)


    else:
        constellation = ''
        age = 0

    cr_dyusermes_data = {
        'account': account,
        'gender': gender,
        'constellation': constellation,
        'age': age,
        'uid': uid,
        'city': city,
        'province': province,
        'fans_uid':fans_uid,
    }
    print(cr_dyusermes_data)
    table_name = 'cr_dy_fans_mes'
    column = 'account'
    ids = my_select(conn=conn, column=column, table_name=table_name)
    if cr_dyusermes_data.get('%s' % column) in ids:
        print('update')
        my_update(conn=conn, data=cr_dyusermes_data, table_name=table_name, cloumn=column)
    else:
        my_insert(conn=conn, data=cr_dyusermes_data, table_name=table_name)

if __name__ == '__main__':
    # host = 'www.muming8.com'
    # user = 'zhang'
    # passwd = 'zhang.123'
    # port = 3306
    # db = 'xuanyuan'

    host = '192.168.0.33'
    user = 'dev'
    passwd = '1q!Q3e#E5t%T'
    port = 3306
    db = 'inshoot'

    conn = my_conn(host=host, user=user, passwd=passwd, port=port, db=db)
    fans_datas = my_select_account(conn=conn, table_name='cr_dy_fans_mes')
    count = 0
    for fans_data in fans_datas:
        if str(fans_data.get('fans_uid')) != '0':
            print(fans_data.get('fans_uid'))
            #

            get_userinfo(fans_uid=fans_data.get('fans_uid'),conn=conn)
            time.sleep(random.uniform(0.5,1.5))
            count+=1
    print(count)
    my_close(conn=conn)
