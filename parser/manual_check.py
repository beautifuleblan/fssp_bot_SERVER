from playwright.sync_api import Page

def individual_entity_check(page: Page, **kwargs):
    if not kwargs['lastname'] or not kwargs['firstname'] or not kwargs['birthday']:
        raise KeyError

    page.fill('input[name="is[last_name]"]', kwargs['lastname'])
    page.fill('input[name="is[first_name]"]', kwargs['firstname'])
    if kwargs.get('middlename'):
        page.fill('input[name="is[patronymic]"]', kwargs['middlename'])
    page.fill('input[name="is[date]"]', kwargs['birthday'])
    page.click('div[class="b-select-form search_bar"]')
    if kwargs.get('regionId'):
        page.click('div[class="chosen-search"]')
        page.click(f'option[value="{kwargs["regionId"]}"]')
    page.click('input[type="submit"]')



def legal_entity_check(page: Page, **kwargs):
    if not kwargs['drtrName']:
        raise KeyError

    page.click('//form/div[9]/div[1]')
    page.click('//div[2]/label/span[1]')
    page.fill('//div[4]/div/div[1]/div/input', kwargs['drtrName'])
    if kwargs.get('address'):
        page.fill('//div[4]/div/div[2]/div/input', kwargs['address'])
    if kwargs.get('regionId'):
        page.click('select[id="region_id"]')
        page.click(f'option[value="{kwargs["regionId"]}"]')
    page.click('//div[9]/div[2]/button')


def ip_number_check(page: Page, **kwargs):
    if not kwargs['ipNumber']:
        raise KeyError

    page.click('//form/div[9]/div[1]')
    page.click('//div[3]/label/span[1]')
    page.locator('//div[5]/div/div/div/input').fill(kwargs['ipNumber'])
    page.click('//div[9]/div[2]/button')