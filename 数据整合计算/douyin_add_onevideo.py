import pymysql
import datetime

#每日抖音用户视频增量信息计算
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
def my_update(conn,data,table_name,cloumn):
    cursor = conn.cursor()

    sql_list = []
    for i in data:
        if i != 'uid':
            s = str(i)+'='+"'%s'"%str(data[i])
            sql_list.append(s)
    c = ','.join(sql_list)
    now = datetime.datetime.now()
    now_start_time = now.strftime('%Y-%m-%d 00:00:00')
    now_end_time = now.strftime('%Y-%m-%d 23:59:59')
    sql  = "UPDATE %s set %s where %s = '%s' and  `create_time` >= '%s' AND `create_time` <= '%s'"%(table_name,c,cloumn,data['%s'%cloumn],now_start_time,now_end_time,)
    cursor.execute(sql)
    conn.commit()

def my_select_old_data(conn,video_id):
    cursor = conn.cursor()
    now = datetime.datetime.now() - datetime.timedelta(days=1)
    old_start_time = now.strftime('%Y-%m-%d 00:00:00')
    # old_start_time = now.strftime('2019-04-19 00:00:00')
    # old_end_time = now.strftime('2019-04-19 23:59:59')
    old_end_time = now.strftime('%Y-%m-%d 23:59:59')
    sql = "SELECT * FROM cr_dyonevideolist WHERE `create_time` >= '%s' AND `create_time` <= '%s' AND `video_id` = '%s'"%(old_start_time,old_end_time,video_id)
    cursor.execute(sql)
    data = cursor.fetchone()
    return data
def my_select_now_data(conn):
    cursor = conn.cursor()
    now  = datetime.datetime.now()
    now_start_time = now.strftime('%Y-%m-%d 00:00:00')
    now_end_time = now.strftime('%Y-%m-%d 23:59:59')
    sql = "SELECT * FROM cr_dyonevideolist WHERE  `create_time` >= '%s' AND `create_time` <= '%s'"%(now_start_time,now_end_time)
    cursor.execute(sql)
    datas = cursor.fetchall()
    for today_data in datas:
        # print(today_data)
        yesterday_data = my_select_old_data(conn=conn,video_id=today_data.get('video_id'))
        if str(yesterday_data) == 'None':
            today_data['digg_add_count'] = 0
            today_data['comment_add_count'] = 0
            today_data['day_interaction_add_count'] = 0
        else:
            today_data['digg_add_count'] = int(today_data.get('digg_count')) - int(yesterday_data.get('digg_count'))
            today_data['comment_add_count'] = int(today_data.get('comment_count')) - int(yesterday_data.get('comment_count'))
            today_data['day_interaction_add_count'] = int(today_data.get('day_interaction_count')) - int(yesterday_data.get('day_interaction_count'))
        print(today_data)
        my_update(conn=conn,table_name='cr_dyonevideolist',data=today_data,cloumn='video_id')
if __name__ == '__main__':
    host = 'www.muming8.com'
    user = 'zhang'
    passwd = 'zhang.123'
    port = 3306
    db = 'xuanyuan'
    # host = '192.168.0.33'
    # user = 'dev'
    # passwd = '1q!Q3e#E5t%T'
    # port = 3306
    # db = 'inshoot'

    conn = my_conn(host=host, user=user, passwd=passwd, port=port, db=db)
    my_select_now_data(conn=conn)
    # my_select_old_data(conn=conn,video_id='6664441326366477576')
    my_close(conn=conn)