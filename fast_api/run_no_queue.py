import asyncio
from fastapi import Body
from .args_parser import parse_args
from parser import generate_response
from loguru import logger
from time import time, sleep
from configs import *
from DB import DataBase


async def run_no_queue(kwargs = Body()):
    async with DataBase() as db:
        params = parse_args(kwargs)

        if 'message' in params:
            return params
        else:
            proxy = await db.get_proxy()
            if not proxy:
                await db.return_stuck_proxy()
                proxy = await db.get_proxy()
                if not proxy:
                    logger.error('Недостаточно прокси для запуска задания')
                    return '{"status":0,"message":"Ошибка создания задачи"}'

            start = time()
            params['proxy'] = proxy
            params['repeat_amount'] = 0
            task = await generate_response(params)
            while (time() - start) < RUN_NO_QUEUE_TIMEOUT:
                try:
                    if task[0] == 'Repeat':
                        params = task[1]
                        proxy = await db.get_proxy()
                        params['proxy'] = proxy
                        await asyncio.sleep(QUERY_IN_WORK_DELAY)
                        task = await generate_response(params)

                    elif task[0] == 'Banned':
                        params = task[1]
                        proxy = await db.get_proxy()
                        params['proxy'] = proxy
                        task = await generate_response(params)

                    elif task[0] == 'Нет':
                        await db.update_stats('no_queue_fail')
                        return '{"status":2,"result":null,"error":"Данные не получены"}'

                    elif type(task[0]) == list:
                        await db.update_stats('no_queue_success')
                        return '{"status":10,"result":[],"error":"Долгов нет"}'

                    elif task[0]:
                        await db.update_stats('no_queue_success')
                        return f'{{"status":10,"results":{task[0]}}}'

                    else:
                        await asyncio.sleep(1)


                except Exception as ex:
                    logger.exception(ex)
                    await db.update_stats('no_queue_fail')
                    return '{"status":0,"message":"Ошибка создания задачи"}'
            else:
                logger.error(f'RUN_NO_QUEUE | TIMEOUT EXCEEDED | {RUN_NO_QUEUE_TIMEOUT} seconds')
                await db.update_stats('no_queue_fail')
                return '{"status":2,"result":null,"error":"Данные не получены"}'




