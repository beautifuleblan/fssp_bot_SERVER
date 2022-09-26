from playwright.sync_api import Playwright, Page, Browser
from time import sleep
from urllib.parse import urlencode
from playwright._impl._api_structures import ProxySettings
from pyuseragents import random as random_useragent
from configs.config import *
from parser.captcha_solver import submit_captcha
from parser.parse_results import parse_data
from parser.manual_check import individual_entity_check, legal_entity_check, ip_number_check
from loguru import logger
from flask_api.executor import db


browser_args = ['--disable-background-networking',
                '--enable-automation',
                '--disable-back-forward-cache',
                '--disable-breakpad',
                '--disable-client-side-phishing-detection',
                '--disable-component-extensions-with-background-pages',
                '--disable-popup-blocking',
                '--disable-prompt-on-repost',
                '--disable-renderer-backgrounding',
                '--disable-features=ImprovedCookieControls,'
                'LazyFrameLoading,GlobalMediaControls,'
                'DestroyProfileOnBrowserClose,'
                'MediaRouter,DialMediaRouteProvider,'
                'AcceptCHFrame,'
                'AutoExpandDetailsElement,'
                'CertificateTransparencyComponentUpdater,'
                'AvoidUnnecessaryBeforeUnloadCheckSync,'
                'Translate',
                '--disable-extensions',
                '--allow-pre-commit-input',
                '--enable-features=NetworkService,NetworkServiceInProcess',
                '--disable-field-trial-config',
                '--disable-background-timer-throttling',
                '--disable-backgrounding-occluded-windows',
                '--disable-default-apps',
                '--disable-dev-shm-usage',
                '--disable-hang-monitor',
                '--disable-ipc-flooding-protection',
                '--disable-sync',
                '--force-color-profile=srgb',
                '--metrics-recording-only',
                '--password-store=basic --use-mock-keychain',
                '--password-store=basic',
                '--use-mock-keychain',
                '--no-service-autorun',
                '--export-tagged-pdf',
                '--enable-use-zoom-for-dsf=false',
                '--proxy-bypass-list=<-loopback>']

def launch_firefox(playwright: Playwright, proxy_server: ProxySettings):
    browser = playwright.firefox.launch(headless=False, proxy={'server': 'per-context'},
                                       slow_mo=BETWEEN_ACTIONS_DELAY*1000)
    context = browser.new_context(user_agent=random_useragent(), proxy=proxy_server)
    page = context.new_page()
    page.set_default_timeout(SELECTOR_TIMEOUT*1000)
    page.evaluate("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return page, browser

def launch_chrome(playwright: Playwright, proxy_server: ProxySettings):
    browser = playwright.chromium.launch(channel="chrome", headless=False, proxy=proxy_server,
                                         slow_mo=BETWEEN_ACTIONS_DELAY * 1000, ignore_default_args=browser_args)
    page = browser.new_page(user_agent=random_useragent())
    page.set_default_timeout(SELECTOR_TIMEOUT * 1000)
    return page, browser

def grab_data(page: Page):
    pagination_is_present = page.is_visible('div[class="pagination"]')
    contents = []
    if pagination_is_present:
        contents.append(page.content())
        while page.is_visible('text=Следующая'):
            page.click('text=Следующая')
            sleep(2)
            submit_captcha(page)
            contents.append(page.content())
        data = parse_data(contents)
        print(len(data))
        return data
    else:
        content = page.content()
        contents.append(content)
        data = parse_data(contents)
        return data


def define_check_mode(page: Page, kwargs):
    if PASS_PARAMS_IN_URL:
        params = {
        "is[ip_preg]": "",
        "is[variant]": kwargs['variant'],
        "is[last_name]": kwargs['lastname'],
        "is[first_name]": kwargs['firstname'],
        "is[patronymic]": kwargs['middlename'],
        "is[date]": kwargs['birthday'],
        "is[drtr_name]": kwargs['drtrName'],
        "is[address]": kwargs['address'],
        "is[ip_number]": kwargs['ipNumber'],
        "is[id_number]": "",
        "is[id_type]": "",
        "is[id_issuer]": "",
        "is[inn]": "",
        "is[region_id][0]": str(kwargs['regionId']) if kwargs.get('regionId') else "-1"
        }
        url = 'https://fssp.gov.ru/iss/ip/?' + urlencode(params)
        page.goto(url, wait_until='commit')

    else:
        page.goto('https://fssp.gov.ru/iss/ip/', wait_until='commit')
        if kwargs['variant'] == 1:
            individual_entity_check(page, **kwargs)
        if kwargs['variant'] == 2:
            legal_entity_check(page, **kwargs)
        if kwargs['variant'] == 3:
            ip_number_check(page, **kwargs)

# def test_connection(page: Page, kwargs):
#     page.goto('https://fssp.gov.ru', wait_until='commit')


def handle_search_results(page: Page, browser: Browser, kwargs):
    sleep(2)
    task_id = kwargs.get('taskId')
    if page.is_visible('body>center>h1'):
        logger.error(
            f'{kwargs["proxy"]["server"]} Сайт лежит или проблема с прокси | {page.locator("body>center>h1").inner_text()}')
        if kwargs.get('taskId'):
            db.update_task(kwargs['taskId'], result=None, status=2, error="Данные не получены")
        return 'Нет', kwargs

    elif page.is_visible('body>div>h1'):
        logger.error(f'Сайт лежит или проблема с прокси | {page.locator("body>div>h1").inner_text()}')
        if task_id:
            db.update_task(task_id, result=None, status=2, error="Данные не получены")
        return 'Нет', kwargs

    elif page.is_visible('div[class="b-error-holder"]'):
        logger.error(__message='Сайт лежит или проблема с прокси | ' + page.locator('div[class="b-error-holder"]').inner_text())
        if kwargs.get('taskId'):
            db.update_task(kwargs['taskId'], result=None, status=2, error="Данные не получены")
        return 'Нет', kwargs

    elif page.is_visible('div[class="results"]'):
        search_message = page.locator('div[class="results"]').inner_text()
        if 'По вашему запросу ничего не найдено' in search_message:
            if task_id:
                db.update_task(task_id, result='[]', status=10, error="Долгов нет")
            return [], kwargs
        elif page.is_visible('tbody'):
            data = grab_data(page)
            print(data)
            data = str(data).replace(", ", ",").replace(": ", ":").replace("\\\\", "\\")
            if task_id:
                db.update_task(task_id, result=data, status=10, error=None)
            return data, kwargs
        elif page.is_visible('div[class="b-search-message__text"]'):
            search_message = page.locator('div[class="b-search-message__text"]').inner_text()
            if ('Ваш запрос обрабатывается' or 'Извините, что-то пошло не так') \
                    in search_message \
                    and (kwargs['repeat_amount'] <= QUERY_IN_WORK_REPEAT_AMOUNT):
                browser.close()
                kwargs['repeat_amount'] += 1
                print(f'repeat, try #{kwargs["repeat_amount"]}')
                return 'Repeat', kwargs
            else:
                logger.error(f'Данные не получены! Ответ от сайта: {search_message}')
                if task_id:
                    db.update_task(task_id, result=None, status=2, error="Данные не получены")
                return 'Нет', kwargs
        else:
            logger.error(f'Данные не получены! Ответ от сайта: {search_message}')
            if task_id:
                db.update_task(task_id, result=None, status=2, error="Данные не получены")
            return 'Нет', kwargs

    else:
        if task_id:
            db.update_task(task_id, result=None, status=2, error="Данные не получены")
        return 'Нет', kwargs