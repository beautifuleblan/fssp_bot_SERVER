from parser.launch_preparations import launch_chrome, launch_firefox
from parser.search_results_handler import handle_search_results
from parser.check_modes import define_check_mode
from parser.captcha_solver import submit_captcha
from playwright.sync_api import sync_playwright
from flask_api.executor import lock
from configs.config import *
from time import sleep, time
from loguru import logger
from random import choice
from DB import DataBase

logger.remove()
# logger.add('/var/www/fssp_bot/log_file.log', encoding='utf-8', format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}")
# logger.add('log_file.log', retention='1 day', rotation='50 MB', encoding='utf-8', format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}")

db = DataBase()

def generate_response(kwargs):
    try:
        with sync_playwright() as play:
            launch_options = [launch_chrome, launch_firefox]
            if CHROME_BROWSER and not FIREFOX_BROWSER:
                page, browser = launch_chrome(playwright=play, proxy_server=kwargs['proxy'])
            elif FIREFOX_BROWSER and not CHROME_BROWSER:
                page, browser = launch_firefox(playwright=play, proxy_server=kwargs['proxy'])
            else:
                page, browser = choice(launch_options)(playwright=play, proxy_server=kwargs['proxy'])
            define_check_mode(page, kwargs)
            submit_captcha(page)
            result, params = handle_search_results(page, browser, kwargs)
            return result, params

    except Exception as ex:
        ex_message = str(ex)
        if kwargs.get('taskId'):
            with lock:
                db.update_task(kwargs['taskId'], result=None, status=2, error='"Данные не получены"')
        if 'net::ERR' in ex_message:
            if 'net::ERR_INVALID_AUTH_CREDENTIALS' in ex_message:
                logger.error(f"{kwargs['proxy']['server']} | net::ERR_INVALID_AUTH_CREDENTIALS | Неверные данные прокси!")
                with lock:
                    db.remove_banned_proxy(kwargs['proxy'])
            elif 'net::ERR_HTTP_RESPONSE_CODE_FAILURE' in ex_message:
                logger.error(f"{kwargs['proxy']['server']} | net::ERR_HTTP_RESPONSE_CODE_FAILURE")
                kwargs['repeat_amount'] += 1
                with lock:
                    db.remove_banned_proxy(kwargs['proxy'])
                return 'Banned', kwargs
            elif 'net::ERR_EMPTY_RESPONSE' in ex_message:
                logger.error(f"{kwargs['proxy']['server']} | net::ERR_EMPTY_RESPONSE | Прокси недействительны")
                with lock:
                    db.remove_banned_proxy(kwargs['proxy'])
            elif 'net::ERR_PROXY_CONNECTION_FAILED' in ex_message:
                logger.error(f"{kwargs['proxy']['server']} | net::ERR_PROXY_CONNECTION_FAILED")
                with lock:
                    db.remove_banned_proxy(kwargs['proxy'])
            elif 'net::ERR_CONNECTION_CLOSED' in ex_message:
                logger.error(f"{kwargs['proxy']['server']} | net::ERR_CONNECTION_CLOSED")
                kwargs['repeat_amount'] += 1
                with lock:
                    db.remove_banned_proxy(kwargs['proxy'])
                return 'Banned', kwargs
            elif 'NS_ERROR_PROXY_CONNECTION_REFUSED' in ex_message:
                logger.error(f"{kwargs['proxy']['server']} | NS_ERROR_PROXY_CONNECTION_REFUSED")
                kwargs['repeat_amount'] += 1
                with lock:
                    db.remove_banned_proxy(kwargs['proxy'])
                return 'Banned', kwargs
        else:
            logger.exception(f"{kwargs['proxy']['server']} |  {ex_message}")
            return 'Нет', kwargs



# if __name__ == '__main__':
    # generate_response(variant=1, lastname='Коровин', firstname='Дмитрий', birthday='11.09.1982', regionId=13)
    # generate_response(variant=2, drtrName='ООО Арарат ', regionId=80)
    # kwargs = {'proxy': {'server': 'http://45.152.116.192:56748', 'username': 'kuKP8mES', 'password': 'tLFSmfHV'}}
    # kwargs = {'proxy': {'server': 'http://dc14.ibaldr.ru:8143', 'username': '21ndo1x2bu', 'password': '45y4xlybl0'}}
    # generate_response(**kwargs)
