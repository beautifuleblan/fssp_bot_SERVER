from playwright.async_api import Page
import requests
from requests_toolbelt import MultipartEncoder
from loguru import logger

decode_dict = {"b": "б", "v": "в", "g": "г", "d": "д", "j": "ж", "k": "к", "l": "л",
                "m": "м", "n": "н", "p": "п", "r": "р", "s": "с", "t": "т"}

def solve_captcha(base_64_img: str):
    mp_encoder = MultipartEncoder(fields={'file': base_64_img.replace('data:image/jpeg;base64,', '')})
    request = requests.request('POST', 'http://92.63.103.189:5000/predict',
                               data=mp_encoder,
                               headers={'Content-Type': mp_encoder.content_type})
    captcha_code = []
    for char in request.text:
        if char in decode_dict.keys():
            captcha_code.append(decode_dict[char])
        else:
            captcha_code.append(char)
    return "".join(captcha_code)

async def submit_captcha(page: Page):
    try:
        captcha_base64 = await page.locator('xpath=//*[@id="capchaVisual"]').get_attribute('src')
        captcha_code = solve_captcha(captcha_base64)
        await page.locator('xpath=//*[@id="captcha-popup-code"]').fill(captcha_code)
        await page.click('xpath=//*[@id="ncapcha-submit"]')
        captcha_popup = await page.is_visible('//*[@id="captcha-popup"]')
        if captcha_popup:
            await submit_captcha(page)
        return True
    except Exception as ex:
        logger.exception(ex)
        return False


