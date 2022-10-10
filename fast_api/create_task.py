import asyncio
from .utils import repeat_task
from .args_parser import parse_args
from DB import DataBase
from fastapi import Body
from loguru import logger


async def create_task(kwargs = Body()):
    async with DataBase() as db:
        params = parse_args(kwargs)
        if 'message' in params:
            return params
        else:
            proxy = await db.get_proxy()
            if not proxy:
                await db.return_stuck_proxy()
                proxy = await db.get_proxy()
                if not proxy.result():
                    logger.error('Недостаточно прокси для запуска задания')
                    return '{"status":0,"message":"Ошибка создания задачи"}'
            try:
                task_id = await db.create_task(params)
                params['proxy'] = proxy
                params['repeat_amount'] = 0
                params['taskId'] = task_id
                loop = asyncio.get_running_loop()
                loop.create_task(repeat_task(params))
                return '{"status":1,"taskId":"' + str(task_id) + '"}'
            except Exception as ex:
                logger.exception(ex)
                await db.update_stats('taskid_fail')
                return '{"status":0,"message":"Ошибка создания задачи"}'
