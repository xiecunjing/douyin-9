from mitmproxy import ctx
import json
import pymysql
import datetime
import re
import os
import sys


'''
采集抖音用户信息+抖音用户视频信息

（appium需实现自动搜索用户，点击用户搜索，然后滑动用户作品界面，采集用户作品（视频）信息）

'''


# host = 'www.muming8.com'
# user = 'zhang'
# passwd = 'zhang.123'
# port = 3306
# db = 'xuanyuan'

host = '192.168.0.33'
user = 'dev'
passwd = '1q!Q3e#E5t%T'
port=3306
db = 'inshoot'

root_dir = '/Users/latte/Desktop/python_project/douyin/抖音用户信息采集-北京'


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


# def my_update(conn,data,table_name):
#     sql_list = []
#     for i in data:
#         if i != 'uid':
#             s = str(i)+'='+str(data[i])
#             sql_list.append(s)
#     c = ','.join(sql_list)
#     sql  = 'UPDATE %s set %s where uid = %s'%(table_name,c,data['uid'])
#     print(sql)
#     cursor = conn.cursor()
#     cursor.execute(sql)
#     conn.commit()
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
def my_onevideo_list_update(conn,data,table_name,cloumn):
    cursor = conn.cursor()
    now = datetime.datetime.now()
    old_start_time = now.strftime('%Y-%m-%d 00:00:00')
    # old_start_time = now.strftime('2019-04-19 00:00:00')
    # old_end_time = now.strftime('2019-04-19 23:59:59')
    old_end_time = now.strftime('%Y-%m-%d 23:59:59')
    sql_list = []
    for i in data:
        if i != 'uid':
            s = str(i) + '=' + "'%s'" % str(data[i])
            sql_list.append(s)
    c = ','.join(sql_list)
    sql = 'UPDATE %s set %s where %s = "%s"  and `create_time` >= "%s" AND `create_time` <= "%s"' % (table_name, c, cloumn, data['%s' % cloumn],old_start_time,old_end_time)
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

def my_select_video_ids(conn,column,table_name):

    cursor = conn.cursor()
    cursor = conn.cursor()
    now = datetime.datetime.now()
    start_time = now.strftime('%Y-%m-%d 00:00:00')
    end_time = now.strftime('%Y-%m-%d 23:59:59')

    select_sql = "SELECT %s FROM %s WHERE `create_time` >= '%s' AND `create_time` <= '%s' " % (column, table_name,start_time,end_time)
    cursor.execute(select_sql)
    datas = cursor.fetchall()
    video_ids = []
    for video_id in datas:
        video_ids.append('%s' % video_id.get('%s' % column))
    return video_ids
def my_select_old_data(conn,video_id):
    cursor = conn.cursor()
    now = datetime.datetime.now() - datetime.timedelta(days=2)
    old_start_time = now.strftime('%Y-%m-%d 00:00:00')
    # old_start_time = now.strftime('2019-04-19 00:00:00')
    # old_end_time = now.strftime('2019-04-19 23:59:59')
    old_end_time = now.strftime('%Y-%m-%d 23:59:59')
    sql = "SELECT * FROM cr_dyonevideolist WHERE `create_time` >= '%s' AND `create_time` <= '%s' AND `video_id` = '%s'"%(old_start_time,old_end_time,video_id)
    cursor.execute(sql)
    data = cursor.fetchone()
    return data

cr_dyusermes_list = []
cr_dy_fans_mes_list = []
print(root_dir)
f = open('%s/data.json'%root_dir,'a',encoding='utf-8')


def get_fans_uid(conn,douyin_id):
    cursor = conn.cursor()
    sql = "SELECT uid,douyin_id FROM cr_dy_fans_mes WHERE douyin_id ='%s'"%douyin_id
    cursor.execute(sql)
    data = cursor.fetchone()
    return data
    pass
def get_constellation(month, date):
    dates = (21, 20, 21, 21, 22, 22, 23, 24, 24, 24, 23, 22)
    constellations = ("摩羯", "水瓶", "双鱼", "白羊", "金牛", "双子", "巨蟹", "狮子", "处女", "天秤", "天蝎", "射手", "摩羯")
    if date < dates[month-1]:
        return constellations[month-1]
    else:
        return constellations[month]
def response(flow):
    douyin_user(flow)
    douyin_video(flow)
    # douyin_fans(flow)
    # douyin_fans_city(flow)

def douyin_user(flow_):

    flow = flow_
    response = flow.response

    user_url1 = 'https://aweme-hl.snssdk.com/aweme/v1/user?'
    user_url2 = 'https://aweme-eagle-hl.snssdk.com/aweme/v1/user'
    # 'https://aweme-eagle.snssdk.com/aweme'
    #           'https://aweme-eagle.snssdk.com/aweme/v1/user/?'
    user_url3 = 'https://aweme-eagle.snssdk.com/aweme/v1/user?'
    user_url4 = 'https://api-eagle.amemv.com/aweme/v1/user?'
    user_url5 = 'https://api-eagle-hl.amemv.com/aweme/v1/user/?'




    if flow.request.url.startswith(user_url1) or flow.request.url.startswith(user_url2) or flow.request.url.startswith(user_url3) \
            or flow.request.url.startswith(user_url4) or flow.request.url.startswith(user_url5) or '/aweme/v1/user/?' in str(flow.request.url):
        data = json.loads(response.text)
        avatar =  data.get('user').get('avatar_thumb').get('url_list')[0]
        name = data.get('user').get('nickname')
        account = data.get('user').get('short_id')
        if str(account) == '0':
            account = data.get('user').get('unique_id')
        else:
            account = account

        region = data.get('user').get('region')
        gender = data.get('user').get('gender')
        if str(gender) =='None':
            gender = 0
        birthday = data.get('user').get('birthday')
        follow_count = data.get('user').get('follower_count')
        digg_count = data.get('user').get('total_favorited')
        language = data.get('user').get('signature_language')
        description  = data.get('user').get('signature')
        following_count = data.get('user').get('following_count')
        tag = data.get('user').get('custom_verify')
        live_count = data.get('user').get('favoriting_count')
        production_num = data.get('user').get('aweme_count')
        addr = data.get('user').get('city')
        uid = data.get('user').get('uid')
        inshoot_fire = data.get('user').get('follower_count') / 100000

        # try:
        #     age = int(datetime.datetime.now().strftime('%Y'))  - int(str(birthday).split('-')[0])
        # except Exception as e:
        #     age = 0
        cr_dyusermes_data = {
            'avatar':avatar,
            'tag':tag,
            'account':account,
            'name':name,
            'region':region,
            'gender':gender,
            'birthday':birthday,
            'follow_count':follow_count,
            'digg_count':digg_count,
            'language':language,
            'production_num': production_num,
            'description':description,
            'following_count':following_count,
            'like_count':live_count,
            'uid':uid,
            'addr':addr,
            'inshoot_fire':inshoot_fire,
        }
        if int(cr_dyusermes_data.get('follow_count')) >= 10000:
            cr_dyusermes_list.append(cr_dyusermes_data)
        print(cr_dyusermes_data)
        f.write(json.dumps(cr_dyusermes_data, ensure_ascii=False))
        f.write('\n')
        f.flush()
        print(len(cr_dyusermes_list),'*'*99)
        if len(cr_dyusermes_list) >= 0:
            conn = my_conn(host=host, user=user, passwd=passwd, port=port, db=db)
            table_name = 'cr_dyusermes'
            column = 'uid'
            ids = my_select(conn=conn,column=column,table_name=table_name)
            for cr_dyusermes_item in cr_dyusermes_list:
                print(cr_dyusermes_item.get('%s'%column),ids)





                if cr_dyusermes_item.get('%s'%column) in ids:
                    print('update')
                    my_update(conn=conn, data=cr_dyusermes_item, table_name=table_name, cloumn=column)
                else:
                    my_insert(conn=conn, data=cr_dyusermes_item,table_name=table_name)

            my_close(conn=conn)
            cr_dyusermes_list.clear()
def douyin_video(flow_):
    #视频信息
    # 视频包含地址
    video_url1 = 'https://aweme.snssdk.com/aweme/v1/aweme/post/?'
    video_url2 = 'https://api.amemv.com/aweme/v1/aweme/post/?'
    video_url3 = 'https://api-hl.amemv.com/aweme/v1/aweme/post/?'
    video_url4 = 'https://aweme-hl.snssdk.com/aweme/v1/aweme/post/?'
    flow = flow_
    response = flow.response

    cr_dyvideo_list = []
    cr_dyonevideolist_list = []
    if flow.request.url.startswith(video_url1) or flow.request.url.startswith(video_url2) or flow.request.url.startswith(video_url3)\
            or flow.request.url.startswith(video_url4)  or '/aweme/v1/aweme/post/?' in str(flow.request.url):
        data = json.loads(response.text)
        for item in data.get('aweme_list'):
            uid = item.get('author').get('uid')
            video_id = item.get('statistics').get('aweme_id')

            try:
                video_cover = item.get('video').get('origin_cover').get('url_list')[0]
            except Exception as e:
                video_cover ='None'
            try:
                video_play_url = item.get('video').get('play_addr_lowbr').get('url_list')[0]
            except Exception as e:
                video_play_url = 'None'

            video_url = item.get('video').get('play_addr_lowbr').get('uri')
            put_time = item.get('create_time')
            put_time = datetime.datetime.fromtimestamp(put_time).strftime('%Y-%m-%d %H:%M:%S')
            share_count = item.get('statistics').get('share_count')
            forward_count = item.get('statistics').get('forward_count')
            comment_count = item.get('statistics').get('comment_count')
            digg_count = item.get('statistics').get('digg_count')
            play_count = item.get('statistics').get('play_count')
            title = item.get('desc')
            share_url = item.get('share_info').get('share_url')
            try:
                music = item.get('music').get('play_url').get('uri')
            except Exception as e:
                music =''
            #增量
            digg_add_count = 0 #点赞增量
            comment_add_count = 0 #评论增量
            day_interaction_add_count = 0  #日互动增量
            duration = int(item.get('video').get('duration'))/1000


            cr_dyvideo_data = {
                'uid':uid,
                'video_id':video_id,
                'video_cover':video_cover,
                'video_play_url':video_play_url,
                'videourl':video_url,
                'put_time':put_time,
                'share_count':share_count,
                'forward_count':forward_count,
                'share_url': share_url,
                'comment_count':comment_count,
                'digg_count':digg_count,
                'play_count':play_count,
                'title':title,
                'music':music,
                'duration':duration,
            }
            cr_dyonevideolist_data = {
                'uid':uid,
                'digg_count':digg_count,
                'play_count':play_count,
                'video_id':video_id,
                'share_count': share_count,
                'comment_count':comment_count,
                'forward_count':forward_count,
                'day_interaction_count':int(digg_count) + int(comment_count),
                'digg_add_count':digg_add_count,
                'comment_add_count':comment_add_count,
                'day_interaction_add_count':day_interaction_add_count,

            }


            # print(cr_dyvideo_data)
            # print(cr_dyonevideolist_data)
            cr_dyvideo_list.append(cr_dyvideo_data)
            cr_dyonevideolist_list.append(cr_dyonevideolist_data)

            # if len(cr_dyonevideolist_list) >=0 or len(cr_dyvideo_list) >=0:
        table_name = 'cr_dyvideo'
        column = 'video_id'
        conn = my_conn(host=host, user=user, passwd=passwd, port=port, db=db)
        ids = my_select(conn=conn, column=column,table_name=table_name)
        for cr_dyvideo_item in cr_dyvideo_list:
            print(cr_dyvideo_item)
            if cr_dyvideo_item['%s'%column] in ids:
                my_update(conn=conn,data=cr_dyvideo_item,table_name=table_name,cloumn=column)

            else:
                my_insert(conn=conn,data=cr_dyvideo_item,table_name=table_name)
        #cr_dyonevideolist 表
        table_name = 'cr_dyonevideolist'
        column = 'video_id'
        conn = my_conn(host=host, user=user, passwd=passwd, port=port, db=db)
        ids = my_select_video_ids(conn=conn,column=column,table_name=table_name)
        for cr_dyonevideolist_item in cr_dyonevideolist_list:
            yesterday_data = my_select_old_data(conn=conn, video_id=cr_dyonevideolist_item.get('video_id'))
            if str(yesterday_data) == 'None':
                cr_dyonevideolist_item['digg_add_count'] = 0
                cr_dyonevideolist_item['comment_add_count'] = 0
                cr_dyonevideolist_item['day_interaction_add_count'] = 0
            else:
                cr_dyonevideolist_item['digg_add_count'] = int(cr_dyonevideolist_item.get('digg_count')) - int(yesterday_data.get('digg_count'))
                cr_dyonevideolist_item['comment_add_count'] = int(cr_dyonevideolist_item.get('comment_count')) - int(yesterday_data.get('comment_count'))
                cr_dyonevideolist_item['day_interaction_add_count'] = int(cr_dyonevideolist_item.get('day_interaction_count')) - int(yesterday_data.get('day_interaction_count'))
            if cr_dyonevideolist_item.get('%s'%column) in ids:
                print('update')
                my_onevideo_list_update(conn=conn, data=cr_dyonevideolist_item, table_name=table_name, cloumn=column)
            else:
                my_insert(conn=conn, data=cr_dyonevideolist_item, table_name=table_name)
            print(cr_dyonevideolist_item)

        my_close(conn=conn)
        cr_dyonevideolist_list.clear()
        cr_dyvideo_list.clear()

        pass
def douyin_fans(flow_):
    flow = flow_
    follower_url = '/aweme/v1/user/follower/list/?'
    response = flow.response
    now_year = datetime.datetime.now().strftime('%Y')
    if follower_url in str(flow.request.url):
        data = json.loads(response.text)
        uid_res = re.compile('user_id=(\d+)&')
        url = flow.request.url
        uid = ''.join(re.findall(uid_res,str(flow.request.url)))
        now_year = datetime.datetime.now().strftime('%Y')
        cr_dy_fans_mes_list = []
        for follower in data.get('followers'):
            gender = follower.get('gender')
            birthday = follower.get('birthday')
            account = follower.get('short_id')
            fans_uid = follower.get('uid')
            if account == '0':
                account = follower.get('unique_id')
            if birthday:
                birthday = datetime.datetime.strptime(birthday,'%Y-%m-%d')
                birthday = birthday
                year = birthday.strftime('%Y')
                month = birthday.strftime('%m')
                day = birthday.strftime('%d')
                constellation = get_constellation(month=int(month),date=int(day))
                age = int(now_year) - int(year)


            else:
                constellation = ''
                age = 0

            cr_dy_fans_mes_data = {
                'uid':uid,
                'gender':gender,
                'age':age,
                'constellation':constellation,
                'account':account,
                'fans_uid':fans_uid,
            }
            print(cr_dy_fans_mes_data)
            cr_dy_fans_mes_list.append(cr_dy_fans_mes_data)
        table_name = 'cr_dy_fans_mes'
        column = 'account'
        conn = my_conn(host=host, user=user, passwd=passwd, port=port, db=db)
        ids = my_select(conn=conn, column=column,table_name=table_name)

        for cr_dy_fans_mes_item in cr_dy_fans_mes_list:
            if cr_dy_fans_mes_item['%s'%column] in ids:
                my_update(conn=conn,data=cr_dy_fans_mes_item,table_name=table_name,cloumn=column)
            else:
                my_insert(conn=conn,data=cr_dy_fans_mes_item,table_name=table_name)


def douyin_fans_city(flow_):

    flow = flow_
    response = flow.response

    user_url1 = 'https://aweme-hl.snssdk.com/aweme/v1/user?'
    user_url2 = 'https://aweme-eagle-hl.snssdk.com/aweme/v1/user'
    # 'https://aweme-eagle.snssdk.com/aweme'
    #           'https://aweme-eagle.snssdk.com/aweme/v1/user/?'
    user_url3 = 'https://aweme-eagle.snssdk.com/aweme/v1/user?'
    user_url4 = 'https://api-eagle.amemv.com/aweme/v1/user?'
    user_url5 = 'https://api-eagle-hl.amemv.com/aweme/v1/user/?'




    if flow.request.url.startswith(user_url1) or flow.request.url.startswith(user_url2) or flow.request.url.startswith(user_url3) \
            or flow.request.url.startswith(user_url4) or flow.request.url.startswith(user_url5):
        conn = my_conn(host=host, user=user, passwd=passwd, port=port, db=db)
        data = json.loads(response.text)
        # uid_res = re.compile('user_id=(\d+)&')

        douyin_id = data.get('user').get('short_id')
        if str(douyin_id) == '0':
            douyin_id = data.get('user').get('unique_id')
        else:
            douyin_id = douyin_id
        uid = get_fans_uid(conn=conn,douyin_id=douyin_id).get('uid')
        gender = data.get('user').get('gender')
        city =  data.get('user').get('city')
        province = data.get('user').get('province')
        if str(gender) =='None':
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
            'douyin_id':douyin_id,
            'gender':gender,
            # 'birthday':birthday,
            'constellation':constellation,
            'age':age,
            'uid':uid,
            'city':city,
            'province':province,

        }
        cr_dyusermes_list.append(cr_dyusermes_data)
        print(cr_dyusermes_data)
        # if len(cr_dyusermes_list) >= 0:
        table_name = 'cr_dy_fans_mes'
        column = 'douyin_id'
        ids = my_select(conn=conn,column=column,table_name=table_name)
        for cr_dyusermes_item in cr_dyusermes_list:
            if cr_dyusermes_item.get('%s'%column) in ids:
                print('update')
                my_update(conn=conn, data=cr_dyusermes_item, table_name=table_name, cloumn=column)
            else:
                my_insert(conn=conn, data=cr_dyusermes_item,table_name=table_name)

        my_close(conn=conn)
        cr_dyusermes_list.clear()




