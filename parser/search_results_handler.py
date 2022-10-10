from playwright.async_api import Page, Browser
from .parse_results import grab_data
from configs.config import *
from loguru import logger
import asyncio
from DB import DataBase


async def handle_search_results(page: Page, browser: Browser, db: DataBase, kwargs):
    await asyncio.sleep(2)
    task_id = kwargs.get('taskId')
    if await page.is_visible('body>center>h1'):
        logger.error(
            f'{kwargs["proxy"]["server"]} Сайт лежит или проблема с прокси | {await page.locator("body>center>h1").inner_text()}')
        if kwargs.get('taskId'):
            await db.update_task(task_id, result=None, status=2, error='"Данные не получены"')
        return 'Нет', kwargs

    elif await page.is_visible('body>div>h1'):
        logger.error(f'Сайт лежит или проблема с прокси | {await page.locator("body>div>h1").inner_text()}')
        if task_id:
            await db.update_task(task_id, result=None, status=2, error='"Данные не получены"')
        return 'Нет', kwargs

    elif await page.is_visible('div[class="b-error-holder"]'):
        logger.error(__message='Сайт лежит или проблема с прокси | ' + await page.locator('div[class="b-error-holder"]').inner_text())
        if task_id:
            await db.update_task(task_id, result=None, status=2, error='"Данные не получены"')
        return 'Нет', kwargs

    elif await page.is_visible('div[class="results"]'):
        search_message = await page.locator('div[class="results"]').inner_text()
        if 'По вашему запросу ничего не найдено' in search_message:
            if task_id:
                await db.update_task(task_id, result='[]', status=10, error='"Долгов нет"')
            return [], kwargs
        elif page.is_visible('tbody'):
            data = await grab_data(page)
            data = str(data).replace(", ", ",").replace(": ", ":").replace("\\\\", "\\").replace('None', 'null')
            if task_id:
                await db.update_task(task_id, result=data, status=10, error=None)
            return data, kwargs
        elif await page.is_visible('div[class="b-search-message__text"]'):
            search_message = await page.locator('div[class="b-search-message__text"]').inner_text()
            if ('Ваш запрос обрабатывается' or 'Извините, что-то пошло не так' or 'Ваш запрос уже обрабатывается') \
                    in search_message \
                    and (kwargs['repeat_amount'] <= QUERY_IN_WORK_REPEAT_AMOUNT):
                await browser.close()
                kwargs['repeat_amount'] += 1
                return 'Repeat', kwargs
            else:
                logger.error(f'Данные не получены! Ответ от сайта: {search_message}')
                if task_id:
                    await db.update_task(task_id, result=None, status=2, error='"Данные не получены"')
                return 'Нет', kwargs
        else:
            logger.error(f'Данные не получены! Ответ от сайта: {search_message}')
            if task_id:
                await db.update_task(task_id, result=None, status=2, error='"Данные не получены"')
            return 'Нет', kwargs

    else:
        if task_id:
            await db.update_task(task_id, result=None, status=2, error='"Данные не получены"')
        return 'Нет', kwargs