import pymysql
import datetime
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
def my_insert(conn,data,table_name):
    try:
        keys_sql = ','.join(data.keys())
        values_sql = []
        for v in data.values():
            values_sql.append('"%s"' % v)
        a = ','.join(values_sql)
        sql = "INSERT INTO %s(%s) VALUES (%s)" % (table_name,keys_sql, a)
        # print(sql)
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
        # print(sql)
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()

def my_select_old_data(conn,uid):
    cursor = conn.cursor()
    now = datetime.datetime.now() - datetime.timedelta(days=2)
    old_start_time = now.strftime('%Y-%m-%d 00:00:00')
    # old_start_time = now.strftime('2019-04-19 00:00:00')
    # old_end_time = now.strftime('2019-04-19 23:59:59')
    old_end_time = now.strftime('%Y-%m-%d 23:59:59')
    sql = "SELECT * FROM cr_dyvideolist WHERE `create_time` >= '%s' AND `create_time` <= '%s' AND `uid` = '%s'"%(old_start_time,old_end_time,uid)
    # print(sql)
    cursor.execute(sql)
    data = cursor.fetchone()
    return data
def my_select_fans(conn,uid):
    cursor = conn.cursor()

    sql = "SELECT * FROM `cr_dyusermes` WHERE `uid` = '%s'"%uid
    cursor.execute(sql)
    data = cursor.fetchone()
    print(data)
    return data
def my_update(conn,data,table_name,cloumn):
    cursor = conn.cursor()

    sql_list = []
    for i in data:
        if i != 'uid':
            s = str(i)+'='+"'%s'"%str(data[i])
            sql_list.append(s)
    c = ','.join(sql_list)
    print(data)
    sql  = 'UPDATE %s set %s where %s = "%s"'%(table_name,c,cloumn,data['%s'%cloumn])
    print(sql)
    cursor.execute(sql)
    conn.commit()
def my_select_now_data(conn):
    cursor = conn.cursor()
    now  = datetime.datetime.now() 
    now_start_time = now.strftime('%Y-%m-%d 00:00:00')
    # now_start_time = now.strftime('2019-04-22 00:00:00')
    now_end_time = now.strftime('%Y-%m-%d 23:59:59')
    # now_end_time = now.strftime('2019-04-22 23:59:59')
    sql = "SELECT sum(digg_count) AS digg_count,sum(comment_count) AS comment_count,sum(day_interaction_count) AS day_interaction_count,sum(share_count) as share_count,sum(forward_count) as forward_count,uid FROM cr_dyonevideolist " \
          "WHERE `create_time`>='%s' AND `create_time` <= '%s' GROUP BY uid"%(now_start_time,now_end_time)
    print(sql)
    cursor.execute(sql)
    datas = cursor.fetchall()
    for today_data in datas:
        try:
            fans = my_select_fans(conn=conn,uid=today_data.get('uid')).get('follow_count')
        except AttributeError:
            fans = 0
        if fans =='None':
            today_data['fans'] = 0
        else:
            today_data['fans'] = fans
        yesterday_data = my_select_old_data(conn=conn,uid=today_data.get('uid'))
        print(yesterday_data)
        # print(today_data)

        if str(yesterday_data) == 'None':
            today_data['digg_add_count'] = 0
            today_data['comment_add_count'] = 0
            today_data['day_interaction_add_count'] = 0
            today_data['fans_add_count'] = 0
        else:
            today_data['digg_add_count'] = int(today_data.get('digg_count')) - int(yesterday_data.get('digg_count'))
            today_data['comment_add_count'] = int(today_data.get('comment_count')) - int(yesterday_data.get('comment_count'))
            today_data['day_interaction_add_count'] = int(today_data.get('day_interaction_count')) - int(yesterday_data.get('day_interaction_count'))
            today_data['fans_add_count'] = int(today_data.get('fans')) - int(yesterday_data.get('fans'))
        # print(today_data)
        today_data['inshoot_fire'] = today_data.get('fans') / 100000
        dyusermes_data = {
            'comment_count':today_data.get('comment_count'),
            'share_count':today_data.get('share_count'),
            'forward_count':today_data.get('forward_count'),
            'uid':today_data.get('uid')
        }
        my_update(conn=conn,data=dyusermes_data,table_name='cr_dyusermes',cloumn='uid')
        my_insert(conn=conn,table_name='cr_dyvideolist',data=today_data)
        print(today_data)
if __name__ == '__main__':
#     host = 'www.muming8.com'
#     user = 'zhang'
#     passwd = 'zhang.123'
#     port = 3306
#     db = 'xuanyuan'
    host = '192.168.0.33'
    user = 'dev'
    passwd = '1q!Q3e#E5t%T'
    port = 3306
    db = 'inshoot'

    conn = my_conn(host=host, user=user, passwd=passwd, port=port, db=db)
    my_select_now_data(conn=conn)
    my_close(conn=conn)