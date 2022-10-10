from parser import generate_response
from loguru import logger
from time import time
from DB import DataBase
from configs import *


async def repeat_task(kwargs):
    async with DataBase() as db:
        params = kwargs
        start = time()
        task = await generate_response(params)
        while (time() - start) < REQUEST_TIMEOUT:
            if task[0] == 'Repeat':
                params = task[1]
                proxy = await db.get_proxy()
                params['proxy'] = proxy
                task = await generate_response(params)
            elif task[0] == 'Banned':
                params = task[1]
                proxy = await db.get_proxy()
                params['proxy'] = proxy
                task = await generate_response(params)
            elif task[0] == 'Нет':
                await db.update_stats('taskid_fail')
                return
            elif type(task[0]) == list:
                await db.update_stats('taskid_success')
                return
            elif task[0]:
                await db.update_stats('taskid_success')
                return

        else:
            logger.error(f'TASKID | TIMEOUT EXCEEDED | {REQUEST_TIMEOUT}')
            await db.update_task(params['taskId'], result=None, status=2, error='"Данные не получены"')