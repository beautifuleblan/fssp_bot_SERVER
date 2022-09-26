from flask_restful import Resource
from flask_api.args_parser import parse_args
from flask_api.utils import json_to_text, repeat_task
# from flask_api.executor import executor
from parser.main import generate_response
from DB import DataBase
from loguru import logger
import concurrent.futures as pool


class CreateTask(Resource):
    def __init__(self):
        self.db = DataBase()

    def post(self):
        with pool.ThreadPoolExecutor() as executor:
            # proxy = {"server": "http://194.67.193.236:14178", "username": "jTmE0ofKrb", "password": "IaZYp2AfPX"}
            proxy = self.db.get_proxy()
            params = parse_args()
            if not proxy:
                logger.error('Недостаточно прокси для запуска задания')
                self.db.return_stuck_proxy()
                proxy = self.db.get_proxy()
                # return json_to_text('{"status":0,"message":"Ошибка создания задачи"}', 200)
            try:
                if params.get('message'):
                    return json_to_text(str(str(params)
                                            .replace(' ', '').replace("'", "\""))
                                        .replace('Неуказан', 'Не указан ').replace('НеверныйключAPI', 'Не верный ключ API'), 200)
                else:
                    params['proxy'] = proxy
                    params['repeat_amount'] = 0
                    task_id = self.db.create_task(params)
                    params['taskId'] = task_id
                    executor.submit(repeat_task, generate_response, params)
                    return json_to_text('{"status":1,"taskId":"' + str(task_id) + '"}', 200)
            except Exception as ex:
                logger.exception(ex)
                return json_to_text('{"status":0,"message":"Ошибка создания задачи"}', 200)