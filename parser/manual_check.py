from playwright.async_api import Page

async def individual_entity_check(page: Page, **kwargs):
    if not kwargs['lastname'] or not kwargs['firstname'] or not kwargs['birthday']:
        raise KeyError

    await page.fill('input[name="is[last_name]"]', kwargs['lastname'])
    await page.fill('input[name="is[first_name]"]', kwargs['firstname'])
    if kwargs.get('middlename'):
        await page.fill('input[name="is[patronymic]"]', kwargs['middlename'])
    await page.fill('input[name="is[date]"]', kwargs['birthday'])
    await page.click('div[class="b-select-form search_bar"]')
    if kwargs.get('regionId'):
        await page.click('div[class="chosen-search"]')
        await page.click(f'option[value="{kwargs["regionId"]}"]')
    await page.click('input[type="submit"]')



async def legal_entity_check(page: Page, **kwargs):
    if not kwargs['drtrName']:
        raise KeyError

    await page.click('//form/div[9]/div[1]')
    await page.click('//div[2]/label/span[1]')
    await page.fill('//div[4]/div/div[1]/div/input', kwargs['drtrName'])
    if kwargs.get('address'):
        await page.fill('//div[4]/div/div[2]/div/input', kwargs['address'])
    if kwargs.get('regionId'):
        await page.click('select[id="region_id"]')
        await page.click(f'option[value="{kwargs["regionId"]}"]')
    await page.click('//div[9]/div[2]/button')


async def ip_number_check(page: Page, **kwargs):
    if not kwargs['ipNumber']:
        raise KeyError

    await page.click('//form/div[9]/div[1]')
    await page.click('//div[3]/label/span[1]')
    await page.locator('//div[5]/div/div/div/input').fill(kwargs['ipNumber'])
    await page.click('//div[9]/div[2]/button')