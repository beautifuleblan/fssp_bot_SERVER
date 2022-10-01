from playwright.sync_api import Page, Browser
from parser.parse_results import grab_data
from configs.config import *
from loguru import logger
from time import sleep
from DB import DataBase
from flask_api.executor import lock
db = DataBase()


def handle_search_results(page: Page, browser: Browser, kwargs):
    sleep(2)
    task_id = kwargs.get('taskId')
    if page.is_visible('body>center>h1'):
        logger.error(
            f'{kwargs["proxy"]["server"]} Сайт лежит или проблема с прокси | {page.locator("body>center>h1").inner_text()}')
        if kwargs.get('taskId'):
            with lock:
                db.update_task(task_id, result=None, status=2, error='"Данные не получены"')
        return 'Нет', kwargs

    elif page.is_visible('body>div>h1'):
        logger.error(f'Сайт лежит или проблема с прокси | {page.locator("body>div>h1").inner_text()}')
        if task_id:
            with lock:
                db.update_task(task_id, result=None, status=2, error='"Данные не получены"')
        return 'Нет', kwargs

    elif page.is_visible('div[class="b-error-holder"]'):
        logger.error(__message='Сайт лежит или проблема с прокси | ' + page.locator('div[class="b-error-holder"]').inner_text())
        if task_id:
            with lock:
                db.update_task(task_id, result=None, status=2, error='"Данные не получены"')
        return 'Нет', kwargs

    elif page.is_visible('div[class="results"]'):
        search_message = page.locator('div[class="results"]').inner_text()
        if 'По вашему запросу ничего не найдено' in search_message:
            if task_id:
                with lock:
                    db.update_task(task_id, result='[]', status=10, error='"Долгов нет"')
            return [], kwargs
        elif page.is_visible('tbody'):
            data = grab_data(page)
            print(type(data))
            data = str(data).replace(", ", ",").replace(": ", ":").replace("\\\\", "\\").replace('None', 'null')
            print(data)
            if task_id:
                with lock:
                    db.update_task(task_id, result=data, status=10, error=None)
            return data, kwargs
        elif page.is_visible('div[class="b-search-message__text"]'):
            search_message = page.locator('div[class="b-search-message__text"]').inner_text()
            if ('Ваш запрос обрабатывается' or 'Извините, что-то пошло не так' or 'Ваш запрос уже обрабатывается') \
                    in search_message \
                    and (kwargs['repeat_amount'] <= QUERY_IN_WORK_REPEAT_AMOUNT):
                browser.close()
                kwargs['repeat_amount'] += 1
                print(f'repeat, try #{kwargs["repeat_amount"]}')
                return 'Repeat', kwargs
            else:
                logger.error(f'Данные не получены! Ответ от сайта: {search_message}')
                if task_id:
                    with lock:
                        db.update_task(task_id, result=None, status=2, error='"Данные не получены"')
                return 'Нет', kwargs
        else:
            logger.error(f'Данные не получены! Ответ от сайта: {search_message}')
            if task_id:
                with lock:
                    db.update_task(task_id, result=None, status=2, error='"Данные не получены"')
            return 'Нет', kwargs

    else:
        if task_id:
            with lock:
                db.update_task(task_id, result=None, status=2, error='"Данные не получены"')
        return 'Нет', kwargs