from flask_restful import Resource, reqparse
from flask_api.utils import json_to_text
from configs.config import API_KEY
from loguru import logger
from DB import DataBase


class GetTask(Resource):
    def __init__(self):
        self.db = DataBase()

    def post(self):
        try:
            parser = reqparse.RequestParser(trim=True)
            parser.add_argument('API', nullable=False, location='form')
            parser.add_argument('taskId', nullable=False, type=int, location='form')
            params = parser.parse_args()
            print(params)
            if params['API'] != API_KEY:
                return json_to_text('{"status":"error","message":"Не верный ключ API"}', 200)
            if not params['taskId']:
                return json_to_text('{"status":"error","message":"Не указан taskId"}', 200)

            status, result, error = self.db.fetch_result_by_taskid(params['taskId'])
            return json_to_text('{"status":' + str(status) + ',"result":' + str(result).replace('None', 'null').replace("\\\\", "\\") + ',"error":' + str(error).replace('None', 'null') + '}', 200)
        except TypeError:
            return json_to_text('{"status":2,"result":null,"error":"Такой задачи не существует"}', 200)
        except Exception as ex:
            logger.exception(ex)
            return json_to_text('{"status":2,"result":null,"error":"Данные не получены"}', 200)