from flask_api.create_task import CreateTask
from flask_api.run_no_queue import RunNoQueue
from flask_api.get_task import GetTask
from flask import Flask
from flask_restful import Api
from loguru import logger
from DB import DataBase

db = DataBase()
db.set_stats_to_zero()
logger.remove()
# logger.add('log_file.log', retention='1 day', rotation='50 MB', encoding='utf-8', format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}")
# logger.add('/var/www/fssp_bot/log_file.log', encoding='utf-8', format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}")

app = Flask(__name__)
api = Api(app)

#
# @app.route('/api/test-fssp-gov/log')
# def log():
#     with open('/var/www/fssp_bot/log_file.log', 'r', encoding='utf-8') as file:
#         log = file.read().splitlines()[::-1]
#         no_queue_success, no_queue_fail, taskid_success, taskid_fail = db.get_stats()
#         result = map(lambda x: f'<br>{x}', log[:500])
#         return f'<body><table>' \
#                f'NO QUEUE SUCCESS - {no_queue_success} | NO QUEUE FAIL - {no_queue_fail} | ' \
#                f'TASK ID SUCCESS - {taskid_success} | TASK ID FAIL - {taskid_fail}' \
#                f'{" ".join(list(result))}' \
#                f'</table></body>'


api.add_resource(RunNoQueue, "/api/fssp-gov")
api.add_resource(CreateTask, "/api/test-fssp-gov/create")
api.add_resource(GetTask, "/api/test-fssp-gov/result")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)


