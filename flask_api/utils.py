from flask import make_response
# from flask_api.executor import executor
from parser.main import generate_response
from loguru import logger
from time import sleep
from flask_api.executor import db
import concurrent.futures as pool

logger.add('/var/www/fssp_bot/log_file.log', retention='1 day', rotation='50 MB', encoding='utf-8', format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}")
def json_to_text(data, code):
    resp = make_response(str(data), code)
    return resp


def repeat_task(func, params):
    with pool.ThreadPoolExecutor() as executor:
        task = executor.submit(func, params)
        while True:
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
                    db.update_stats('taskid_fail')
                    task.cancel()
                    return
                elif type(task.result()[0]) == list:
                    array = tuple(task.result()[0])
                    if len(array) == 0:
                        db.update_stats('taskid_success')
                    elif len(array) >= 1:
                        db.update_stats('taskid_success')
                    task.cancel()
                    return

            else:
                sleep(1)