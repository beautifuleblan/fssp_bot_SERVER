from playwright.async_api import Page
from parser.captcha_solver import submit_captcha
from bs4 import BeautifulSoup
import asyncio
import json

async def grab_data(page: Page):
    pagination_is_present = await page.is_visible('div[class="pagination"]')
    contents = []
    if pagination_is_present:
        contents.append(await page.content())
        while await page.is_visible('text=Следующая'):
            await page.click('text=Следующая')
            await asyncio.sleep(2)
            await submit_captcha(page)
            contents.append(await page.content())
        data = await parse_data(contents)
        return data
    else:
        content = await page.content()
        contents.append(content)
        data = await parse_data(contents)
        return data


async def parse_data(contents):
    array = []
    for content in contents:
        soup = BeautifulSoup(content, 'html.parser')
        table = soup.find('tbody')
        if not table:
            return array
        results = table.find_all('tr')
        for result in results:
            categories = result.find_all('td')
            if len(categories) > 1:
                data_dict = {}
                try:
                    data_dict['debtor'] = categories[0].text.strip() \
                        if categories[0] else None
                except:
                    data_dict['debtor'] = None
                try:
                    data_dict['enforcementProceedings'] = categories[1].text.strip().replace('/', '\/')\
                        if categories[1] else None
                except:
                    data_dict['enforcementProceedings'] = None
                try:
                    data_dict['detailsOfExecutiveDocument'] = categories[2].text.strip() \
                        if categories[2] else None
                except:
                    data_dict['detailsOfExecutiveDocument'] = None
                try:
                    data_dict['dateReasonForEndOrTerminationOfIP'] = categories[3].text.strip() \
                        if categories[3] else None
                except:
                    data_dict['dateReasonForEndOrTerminationOfIP'] = None
                try:
                    data_dict['subjectOfExecutionAmountOfOutstandingDebt'] = categories[5].text.strip() \
                        if categories[5] else "null"
                except:
                    data_dict['subjectOfExecutionAmountOfOutstandingDebt'] = None
                try:
                    data_dict['bailiffDepartment'] = categories[6].text.strip() \
                        if categories[7] else None
                except:
                    data_dict['bailiffDepartment'] = None
                try:
                    data_dict['bailiffPhone'] = categories[7].text.strip() \
                        if categories[7] else None
                except:
                    data_dict['bailiffPhone'] = None
                try:
                    data_dict['debtRest'] = categories[4].find('a').get('data-uin')
                except:
                    pass
                try:
                    data_dict['ip'] = categories[4].find('a').get('data-ip').replace('/', '\/')
                except:
                    pass
                try:
                    data_dict['uin'] = categories[4].find('a').get('data-uin')
                except:
                    pass

                array.append(data_dict)
    return json.dumps(array, ensure_ascii=False)