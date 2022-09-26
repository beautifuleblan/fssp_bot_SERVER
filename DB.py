import mysql.connector
from mysql.connector import RefreshOption
import yaml
from yaml import CLoader as Loader
import time
with open('/var/www/fssp_bot/configs/config.yaml', 'r') as f:
    config = yaml.load(f, Loader=Loader)['DB']
# with open('/Users/denysmalykhin/PycharmProjects/fssp_bot/configs/config.yaml', 'r') as f:
#     config = yaml.load(f, Loader=Loader)['DB']

class DataBase():
    def __init__(self):
        self.cnx = mysql.connector.connect(**config)
        self.cursor = self.cnx.cursor()

    def fetch_result_by_taskid(self, task_id: int):
        self.cursor.execute('SELECT status, result, error FROM task WHERE id = %s', (task_id, ))
        data = self.cursor.fetchone()
        status = data[0]
        result = data[1]
        error = data[2]
        return status, result, error

    def create_task(self, params):
        timestamp = int(time.time())
        self.cursor.execute('INSERT INTO task(createdAt, updatedAt, variant, lastname, firstname, middlename,'
                            'birthday, regionId, drtrName, ipNumber, status) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                            (timestamp, 0, params['variant'], params['lastname'], params['firstname'],
                             params['middlename'], params['birthday'], params['regionId'], params['drtrName'],
                             params['ipNumber'], 1))
        data = self.cursor.lastrowid
        self.cnx.commit()
        return data

    def update_task(self, task_id: int, result, status: int, error):
        timestamp = int(time.time())
        self.cursor.execute('UPDATE task SET updatedAt = %s, result = %s, status = %s, error = %s '
                            'WHERE id = %s', (timestamp, result, status, error, task_id))
        self.cnx.commit()

    def get_proxy(self):
        self.cursor.execute('SELECT ip, port, username, password FROM proxy ORDER BY RAND() LIMIT 1')
        data = self.cursor.fetchone()
        if data:
            proxy = {}
            proxy['server'] = f'http://{data[0]}:{data[1]}'
            proxy['username'] = data[2]
            proxy['password'] = data[3]
            self.cursor.execute('DELETE FROM proxy WHERE ip = %s AND port = %s', (data[0], data[1]))
            self.cnx.commit()
            self.cursor.execute('INSERT INTO proxy_in_work(ip, port, username, password) VALUES (%s,%s,%s,%s)', (data[0], data[1], data[2], data[3]))
            self.cnx.commit()
            return proxy
        else:
            return None


    # def return_proxy(self, proxy):
    #     ip = proxy['server'].split('//')[-1].split(':')[0]
    #     port = proxy['server'].split(':')[2]
    #     username = proxy['username']
    #     password = proxy['password']
    #     self.cursor.execute('INSERT INTO proxy(ip, port, username, password) VALUES(%s,%s,%s,%s)', (ip, port, username, password))
    #     self.cnx.commit()


    def remove_banned_proxy(self, proxy):
        ip = proxy['server'].split('//')[-1].split(':')[0]
        port = proxy['server'].split(':')[2]
        username = proxy['username']
        password = proxy['password']
        self.cursor.execute('DELETE FROM proxy_in_work WHERE ip = %s AND port = %s', (ip, port))
        self.cnx.commit()
        self.cursor.execute('INSERT INTO banned_proxy(ip, port, username, password) VALUES (%s, %s, %s, %s)',
                            (ip, port, username, password))
        self.cnx.commit()

    def update_stats(self, status: str):
        match status:
            case 'no_queue_success':
                self.cursor.execute('SELECT NO_QUEUE_SUCCESS FROM stats WHERE id = 1')
                value = self.cursor.fetchone()
                print(value)
                self.cursor.execute('UPDATE stats SET NO_QUEUE_SUCCESS = %s WHERE id = 1', (value[0] + 1, ))
            case 'no_queue_fail':
                self.cursor.execute('SELECT NO_QUEUE_FAIL FROM stats WHERE id = 1')
                value = self.cursor.fetchone()
                self.cursor.execute('UPDATE stats SET NO_QUEUE_FAIL = %s WHERE id = 1', (value[0] + 1,))
            case 'taskid_success':
                self.cursor.execute('SELECT TASKID_SUCCESS FROM stats WHERE id = 1')
                value = self.cursor.fetchone()
                self.cursor.execute('UPDATE stats SET TASKID_SUCCESS = %s WHERE id = 1', (value[0] + 1,))
            case 'taskid_fail':
                self.cursor.execute('SELECT TASKID_FAIL FROM stats WHERE id = 1')
                value = self.cursor.fetchone()
                self.cursor.execute('UPDATE stats SET TASKID_FAIL = %s WHERE id = 1', (value[0] + 1,))
        self.cnx.commit()


    def get_stats(self):
        self.cursor.execute('SELECT NO_QUEUE_SUCCESS, NO_QUEUE_FAIL, TASKID_SUCCESS, TASKID_FAIL FROM stats WHERE id = 1')
        data = self.cursor.fetchone()
        return data[0], data[1], data[2], data[3]

    def set_stats_to_zero(self):
        self.cursor.execute('UPDATE stats SET NO_QUEUE_SUCCESS = 0, NO_QUEUE_FAIL = 0, TASKID_SUCCESS = 0, TASKID_FAIL = 0 WHERE id = 1')
        self.cnx.commit()

    def return_stuck_proxy(self):
        self.cursor.execute('SELECT ip, port, username, password FROM proxy_in_work')
        data = self.cursor.fetchall()
        if data:
            for proxy in data:
                self.cursor.execute('INSERT INTO proxy(ip, port, username, password) VALUES(%s,%s,%s,%s)', (proxy[0], proxy[1], proxy[2], proxy[3]))
                self.cnx.commit()
                self.cursor.execute('DELETE FROM proxy_in_work WHERE ip = %s AND port = %s', (proxy[0], proxy[1]))
                self.cnx.commit()

    # def return_banned_proxy(self):
    #     self.cnx.cmd_refresh(RefreshOption.THREADS)
    #     self.cursor.execute('SELECT ip, port, username, password FROM banned_proxy')
    #     data = self.cursor.fetchall()
    #     if data:
    #         for proxy in data:
    #             self.cursor.execute('INSERT INTO proxy(ip, port, username, password) VALUES(%s,%s,%s,%s)', (proxy[0], proxy[1], proxy[2], proxy[3]))
    #             self.cursor.execute('DELETE FROM banned_proxy WHERE ip = %s AND port = %s', (proxy[0], proxy[1]))


if __name__ == '__main__':
    database = DataBase()
    # print(database.fetch_result_by_taskid(2224183))
    # print(database.get_last_task_id())
    # print(int(time.time()))
    database.update_stats('no_queue_success')

    # print(taskid)
