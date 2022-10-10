from fastapi import APIRouter
from .create_task import create_task
from .get_task import get_task
from .run_no_queue import run_no_queue
from .log import log
from loguru import logger
from starlette.responses import PlainTextResponse, HTMLResponse

logger.remove()
# logger.add('/Users/denysmalykhin/PycharmProjects/fssp_bot_async/log_file.log', retention='1 day', rotation='50 MB', encoding='utf-8', format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}")
logger.add('/var/www/fssp_bot_async/log_file.log', encoding='utf-8', format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}")

app = APIRouter()

app.add_api_route(path="/api/fssp-gov", endpoint=run_no_queue, methods=['POST'], status_code=200, response_class=PlainTextResponse)
app.add_api_route(path="/api/test-fssp-gov/create", endpoint=create_task, methods=['POST'], status_code=200, response_class=PlainTextResponse)
app.add_api_route(path="/api/test-fssp-gov/result", endpoint=get_task, methods=['POST'], status_code=200, response_class=PlainTextResponse)
app.add_api_route(path="/api/test-fssp-gov/log", endpoint=log, methods=['GET'], status_code=200, response_class=HTMLResponse)
