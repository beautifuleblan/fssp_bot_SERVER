import aiomysql
import yaml
from yaml import CLoader as Loader
import time

with open('/var/www/fssp_bot_async/configs/config.yaml', 'r') as f:
    config = yaml.load(f, Loader=Loader)['DB']
# with open('/Users/denysmalykhin/PycharmProjects/fssp_bot_async/configs/config.yaml', 'r') as f:
#     config = yaml.load(f, Loader=Loader)['DB']

class DataBase:
    async def __aenter__(self):
        self.connector = await aiomysql.connect(**config, autocommit=True)
        self.cursor = await self.connector.cursor()
        return self

    async def fetch_result_by_taskid(self, task_id: int):
        await self.cursor.execute('SELECT status, result, error FROM task WHERE id = %s', (task_id, ))
        data = await self.cursor.fetchone()
        status = data[0]
        result = data[1]
        error = data[2]
        return status, result, error

    async def create_task(self, params):
        timestamp = int(time.time())
        await self.cursor.execute('INSERT INTO task(createdAt, updatedAt, variant, lastname, firstname, middlename,'
                            'birthday, regionId, drtrName, ipNumber, status) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                            (timestamp, 0, params['variant'], params['lastname'], params['firstname'],
                             params['middlename'], params['birthday'], params['regionId'], params['drtrName'],
                             params['ipNumber'], 1))
        data = self.cursor.lastrowid
        return data

    async def update_task(self, task_id: int, result, status: int, error):
        timestamp = int(time.time())
        await self.cursor.execute(f'UPDATE task SET updatedAt = %s, result = %s, status = %s, error = %s WHERE id = %s', (timestamp, result, status, error, task_id))

    async def get_proxy(self):
        await self.cursor.execute('SELECT ip, port, username, password FROM proxy ORDER BY RAND() LIMIT 1')
        data = await self.cursor.fetchone()
        if data:
            proxy = {}
            proxy['server'] = f'http://{data[0]}:{data[1]}'
            proxy['username'] = data[2]
            proxy['password'] = data[3]
            await self.cursor.execute('DELETE FROM proxy WHERE ip = %s AND port = %s', (data[0], data[1]))
            await self.cursor.execute('INSERT INTO proxy_in_work(ip, port, username, password) VALUES (%s,%s,%s,%s)', (data[0], data[1], data[2], data[3]))
            return proxy
        else:
            return None

    async def remove_banned_proxy(self, proxy):
        ip = proxy['server'].split('//')[-1].split(':')[0]
        port = proxy['server'].split(':')[2]
        username = proxy['username']
        password = proxy['password']
        await self.cursor.execute('DELETE FROM proxy_in_work WHERE ip = %s AND port = %s', (ip, port))
        await self.cursor.execute('INSERT INTO banned_proxy(ip, port, username, password) VALUES (%s, %s, %s, %s)',
                            (ip, port, username, password))

    async def update_stats(self, status: str):
        match status:
            case 'no_queue_success':
                await self.cursor.execute('SELECT NO_QUEUE_SUCCESS FROM stats WHERE id = 1')
                value = await self.cursor.fetchone()
                print(value)
                await self.cursor.execute('UPDATE stats SET NO_QUEUE_SUCCESS = %s WHERE id = 1', (value[0] + 1, ))
            case 'no_queue_fail':
                await self.cursor.execute('SELECT NO_QUEUE_FAIL FROM stats WHERE id = 1')
                value = await self.cursor.fetchone()
                await self.cursor.execute('UPDATE stats SET NO_QUEUE_FAIL = %s WHERE id = 1', (value[0] + 1,))
            case 'taskid_success':
                await self.cursor.execute('SELECT TASKID_SUCCESS FROM stats WHERE id = 1')
                value = await self.cursor.fetchone()
                await self.cursor.execute('UPDATE stats SET TASKID_SUCCESS = %s WHERE id = 1', (value[0] + 1,))
            case 'taskid_fail':
                await self.cursor.execute('SELECT TASKID_FAIL FROM stats WHERE id = 1')
                value = await self.cursor.fetchone()
                await self.cursor.execute('UPDATE stats SET TASKID_FAIL = %s WHERE id = 1', (value[0] + 1,))

    async def get_stats(self):
        await self.cursor.execute('SELECT NO_QUEUE_SUCCESS, NO_QUEUE_FAIL, TASKID_SUCCESS, TASKID_FAIL FROM stats WHERE id = 1')
        data = await self.cursor.fetchone()
        return data[0], data[1], data[2], data[3]

    async def set_stats_to_zero(self):
        await self.cursor.execute('UPDATE stats SET NO_QUEUE_SUCCESS = 0, NO_QUEUE_FAIL = 0, TASKID_SUCCESS = 0, TASKID_FAIL = 0 WHERE id = 1')

    async def return_stuck_proxy(self):
        await self.cursor.execute('SELECT ip, port, username, password FROM proxy_in_work')
        data = await self.cursor.fetchall()
        if data:
            await self.cursor.executemany('INSERT INTO proxy(ip, port, username, password) VALUES(%s,%s,%s,%s)', data)
            await self.cursor.executemany('DELETE FROM proxy_in_work WHERE ip = %s '
                                          'AND port = %s '
                                          'AND username = %s '
                                          'AND PASSWORD = %s', data)

    async def __aexit__(self, exc_type=None, exc_val=None, exc_tb=None):
        self.connector.close()