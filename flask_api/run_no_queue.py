from flask_restful import Resource
# from flask_api.executor import executor
from flask_api.utils import json_to_text
from flask_api.args_parser import parse_args
from parser.main import generate_response
from loguru import logger
from time import time, sleep
from configs.config import *
from DB import DataBase
import concurrent.futures as pool


class RunNoQueue(Resource):
    def __init__(self):
        self.db = DataBase()

    def post(self):
        with pool.ThreadPoolExecutor() as executor:
            proxy = self.db.get_proxy()
            if not proxy:
                logger.error('Недостаточно прокси для запуска задания')
                self.db.return_stuck_proxy()
                proxy = self.db.get_proxy()
                # return json_to_text('{"status":0,"message":"Ошибка создания задачи"}', 200)
            params = parse_args()
            print(params)
            if params.get('message'):
                return json_to_text(str(params).replace(' ', '')
                                    .replace("'", "\"").replace('Неуказан', 'Не указан ')
                                    .replace('НеверныйключAPI', 'Не верный ключ API'), 200)
            else:
                start = time()
                params['proxy'] = proxy
                params['repeat_amount'] = 0
                task = executor.submit(generate_response, params)
                while (time() - start) < RUN_NO_QUEUE_TIMEOUT:
                    try:
                        if task.result():
                            if task.result()[0] == 'Repeat':
                                kwargs = task.result()[1]
                                proxy = self.db.get_proxy()
                                kwargs['proxy'] = proxy
                                sleep(QUERY_IN_WORK_DELAY)
                                task = executor.submit(generate_response, kwargs)

                            elif task.result()[0] == 'Banned':
                                kwargs = task.result()[1]
                                proxy = self.db.get_proxy()
                                kwargs['proxy'] = proxy
                                task = executor.submit(generate_response, kwargs)

                            elif task.result()[0] == 'Нет':
                                self.db.update_stats('no_queue_fail')
                                task.cancel()
                                return json_to_text('{"status":2,"result":null,"error":"Данные не получены"}', 200)

                            elif type(task.result()[0]) == list:
                                array = tuple(task.result()[0])
                                if len(array) >= 1:
                                    self.db.update_stats('no_queue_success')
                                    task.cancel()
                                    return json_to_text('{"status":10,"results":' + str(array)
                                                        .replace('None', 'null').replace("\\\\", "\\")
                                                        .replace('(', '[').replace(')', ']') + '}', 200)
                                elif len(array) == 0:
                                    self.db.update_stats('no_queue_success')
                                    task.cancel()
                                    return json_to_text('{"status":10,"result":[],"error":"Долгов нет"}', 200)
                        else:
                            sleep(1)

                    except Exception as ex:
                        logger.error(ex)
                        task.cancel()
                        self.db.update_stats('no_queue_fail')
                        return json_to_text('{"status":0,"message":"Ошибка создания задачи"}', 200)
                else:
                    logger.error(f'RUN_NO_QUEUE | TIMEOUT EXCEEDED | {RUN_NO_QUEUE_TIMEOUT} seconds')
                    self.db.update_stats('no_queue_fail')
                    task.cancel()
                    return json_to_text('{"status":2,"result":null,"error":"Данные не получены"}', 200)



