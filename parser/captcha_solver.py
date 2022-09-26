from playwright.sync_api import Page
from requests_toolbelt.multipart.encoder import MultipartEncoder
import requests

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

def submit_captcha(page: Page):
    try:
        page.set_default_navigation_timeout(5000)
        captcha_base64 = page.locator('xpath=//*[@id="capchaVisual"]').get_attribute('src')
        captcha_code = solve_captcha(captcha_base64)
        print(captcha_code)
        page.locator('xpath=//*[@id="captcha-popup-code"]').fill(captcha_code)
        page.click('xpath=//*[@id="ncapcha-submit"]')
        captcha_popup = page.is_visible('//*[@id="captcha-popup"]')
        if captcha_popup:
            submit_captcha(page)
        return True
    except:
        return False


