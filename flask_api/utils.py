from flask import make_response
from flask_api.executor import executor
from parser.main import generate_response
from loguru import logger
from time import time
from DB import DataBase
from configs.config import *
from flask_api.executor import lock

db = DataBase()

# logger.add('/var/www/fssp_bot/log_file.log', retention='1 day', rotation='50 MB', encoding='utf-8', format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}")
def json_to_text(data, code):
    resp = make_response(str(data), code)
    return resp


def repeat_task(func, params):
    start = time()
    task = executor.submit(func, params)
    while (time() - start) < REQUEST_TIMEOUT:
        if task.result():
            if task.result()[0] == 'Repeat':
                kwargs = task.result()[1]
                proxy = db.get_proxy()
                kwargs['proxy'] = proxy
                task = executor.submit(generate_response, kwargs)
            elif task.result()[0] == 'Banned':
                kwargs = task.result()[1]
                proxy = db.get_proxy()
                kwargs['proxy'] = proxy
                task = executor.submit(generate_response, kwargs)
            elif task.result()[0] == 'Нет':
                with lock:
                    db.update_stats('taskid_fail')
                return
            elif type(task.result()[0]) == list:
                with lock:
                    db.update_stats('taskid_success')
                return
            elif task.result()[0]:
                with lock:
                    db.update_stats('taskid_success')
                return

    else:
        logger.error(f'TASKID | TIMEOUT EXCEEDED | {REQUEST_TIMEOUT}')
        with lock:
            db.update_task(params['taskId'], result=None, status=2, error='"Данные не получены"')