from configs import API_KEY
from loguru import logger
from DB import DataBase
from fastapi import Body
from urllib.parse import parse_qsl, urlsplit

async def get_task(params = Body()):
    kwargs = dict(parse_qsl(urlsplit(params.decode()).path))
    try:
        if kwargs.get('API') != API_KEY:
            return '{"status":"error","message":"Не верный ключ API"}'
        if not kwargs.get('taskId'):
            return '{"status":"error","message":"Не указан taskId"}'
        else:
            async with DataBase() as db:
                status, result, error = await db.fetch_result_by_taskid(kwargs['taskId'])
                return f'{{"status":{status},"result":{result},"error":{str(error).replace("None", "null")}}}'

    except TypeError:
        return '{"status":2,"result":null,"error":"Такой задачи не существует"}'
    except Exception as ex:
        logger.exception(ex)
        return '{"status":2,"result":null,"error":"Данные не получены"}'