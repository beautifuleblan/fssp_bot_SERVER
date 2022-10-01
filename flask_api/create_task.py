from flask_api.utils import json_to_text, repeat_task
from flask_api.args_parser import parse_args
from flask_api.executor import executor, lock
from parser.main import generate_response
from flask_restful import Resource
from loguru import logger
from DB import DataBase


class CreateTask(Resource):
    def __init__(self):
        self.db = DataBase()

    def post(self):
        # proxy = {"server": "http://194.67.193.236:14178", "username": "jTmE0ofKrb", "password": "IaZYp2AfPX"}
        params = parse_args()
        if params.get('message'):
            return json_to_text(str(str(params).replace(' ', '').replace("'", "\""))
                                .replace('Неуказан', 'Не указан ').replace('НеверныйключAPI', 'Не верный ключ API'), 200)
        else:
            proxy = self.db.get_proxy()
            if not proxy:
                with lock:
                    self.db.return_stuck_proxy()
                proxy = self.db.get_proxy()
                if not proxy:
                    logger.error('Недостаточно прокси для запуска задания')
                    return json_to_text('{"status":0,"message":"Ошибка создания задачи"}', 200)
            try:
                params['proxy'] = proxy
                params['repeat_amount'] = 0
                with lock:
                    task_id = self.db.create_task(params)
                params['taskId'] = task_id
                executor.submit(repeat_task, generate_response, params)
                return json_to_text('{"status":1,"taskId":"' + str(task_id) + '"}', 200)
            except Exception as ex:
                logger.exception(ex)
                self.db.update_stats('taskid_fail')
                return json_to_text('{"status":0,"message":"Ошибка создания задачи"}', 200)