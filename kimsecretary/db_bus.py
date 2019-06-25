import pymysql.cursors

connection = pymysql.connect(
    host='localhost',
    user='root',
    password='',
    db='kimsecretary',
    charset='utf8',
    cursorclass=pymysql.cursors.DictCursor
)


def bus_go_input(chat_id, go_station_id, go_route_id, go_station_order):
    try:
        curs = connection.cursor()
        sql = f'INSERT INTO bus_table(chat_id, go_station_id, go_station_order) ' \
            f'VALUE({chat_id}, {go_station_id}, {go_route_id}, {go_station_order})'
        curs.execute(sql)
        connection.commit()
    finally:
        connection.close()
