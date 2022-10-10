import asyncio
from .launch_preparations import launch_chrome, launch_firefox
from .search_results_handler import handle_search_results
from .check_modes import define_check_mode
from .captcha_solver import submit_captcha
from playwright.async_api import async_playwright
from configs import *
from loguru import logger
from random import choice
from DB import DataBase


logger.remove()
logger.add('/var/www/fssp_bot_async/log_file.log', encoding='utf-8', format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}")
# logger.add('/Users/denysmalykhin/PycharmProjects/fssp_bot_async/log_file.log', retention='1 day', rotation='50 MB', encoding='utf-8', format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}")


async def generate_response(kwargs):
    async with DataBase() as db:
        try:
            async with async_playwright() as play:
                launch_options = [launch_chrome, launch_firefox]
                if CHROME_BROWSER and not FIREFOX_BROWSER:
                    page, browser = await launch_chrome(playwright=play, proxy_server=kwargs['proxy'])
                elif FIREFOX_BROWSER and not CHROME_BROWSER:
                    page, browser = await launch_firefox(playwright=play, proxy_server=kwargs['proxy'])
                else:
                    page, browser = await choice(launch_options)(playwright=play, proxy_server=kwargs['proxy'])
                await define_check_mode(page, kwargs)
                await submit_captcha(page)
                result, params = await handle_search_results(page, browser, db, kwargs)
                return result, params

        except Exception as ex:
            ex_message = str(ex)
            if kwargs.get('taskId'):
                await db.update_task(kwargs['taskId'], result=None, status=2, error='"Данные не получены"')
            if 'net::ERR' in ex_message:
                if 'net::ERR_INVALID_AUTH_CREDENTIALS' in ex_message:
                    logger.error(f"{kwargs['proxy']['server']} | net::ERR_INVALID_AUTH_CREDENTIALS | Неверные данные прокси!")
                    await db.remove_banned_proxy(kwargs['proxy'])
                elif 'net::ERR_HTTP_RESPONSE_CODE_FAILURE' in ex_message:
                    logger.error(f"{kwargs['proxy']['server']} | net::ERR_HTTP_RESPONSE_CODE_FAILURE")
                    kwargs['repeat_amount'] += 1
                    await db.remove_banned_proxy(kwargs['proxy'])
                    return 'Banned', kwargs
                elif 'net::ERR_EMPTY_RESPONSE' in ex_message:
                    logger.error(f"{kwargs['proxy']['server']} | net::ERR_EMPTY_RESPONSE | Прокси недействительны")
                    await db.remove_banned_proxy(kwargs['proxy'])
                elif 'net::ERR_PROXY_CONNECTION_FAILED' in ex_message:
                    logger.error(f"{kwargs['proxy']['server']} | net::ERR_PROXY_CONNECTION_FAILED")
                    await db.remove_banned_proxy(kwargs['proxy'])
                elif 'net::ERR_CONNECTION_CLOSED' in ex_message:
                    logger.error(f"{kwargs['proxy']['server']} | net::ERR_CONNECTION_CLOSED")
                    kwargs['repeat_amount'] += 1
                    await db.remove_banned_proxy(kwargs['proxy'])
                    return 'Banned', kwargs
                elif 'NS_ERROR_PROXY_CONNECTION_REFUSED' in ex_message:
                    logger.error(f"{kwargs['proxy']['server']} | NS_ERROR_PROXY_CONNECTION_REFUSED")
                    kwargs['repeat_amount'] += 1
                    await db.remove_banned_proxy(kwargs['proxy'])
                    return 'Banned', kwargs
            else:
                logger.exception(f"{kwargs['proxy']['server']} |  {ex_message}")
                return 'Нет', kwargs

