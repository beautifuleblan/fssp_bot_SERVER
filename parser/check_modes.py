from parser.manual_check import individual_entity_check, legal_entity_check, ip_number_check
from playwright.sync_api import Page
from urllib.parse import urlencode
from configs.config import *


def define_check_mode(page: Page, kwargs):
    if PASS_PARAMS_IN_URL:
        params = {
        "is[ip_preg]": "",
        "is[variant]": kwargs['variant'],
        "is[last_name]": kwargs['lastname'] if kwargs.get('lastname') else "",
        "is[first_name]": kwargs['firstname'] if kwargs.get('firstname') else "",
        "is[patronymic]": kwargs['middlename'] if kwargs.get('middlename') else "",
        "is[date]": kwargs['birthday'] if kwargs.get('birthday') else "",
        "is[drtr_name]": kwargs['drtrName'] if kwargs.get('drtrName') else "",
        "is[address]": kwargs['address'] if kwargs.get('address') else "",
        "is[ip_number]": kwargs['ipNumber'] if kwargs.get('ipNumber') else "",
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


