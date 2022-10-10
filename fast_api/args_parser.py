from configs import API_KEY
from fastapi import Body
from urllib.parse import parse_qsl, urlsplit


def parse_args(params = Body()):
    params = dict(parse_qsl(urlsplit(params.decode()).path))

    if params.get('API') != API_KEY:
        return '{"status":"error","message":"Не верный ключ API"}'
    if not params.get('variant') or (params.get('variant') not in ['1', '2', '3']):
        return '{"status":"error","message":"Не указан variant"}'

    if params.get('variant') == '1':
        if not params.get('lastname'):
            return '{"status":"error","message":"Не указан lastname"}'
        elif not params.get('firstname'):
            return '{"status":"error","message":"Не указан firstname"}'
        elif not params.get('birthday'):
            return '{"status":"error","message":"Не указан birthday"}'
        elif not params.get('regionId'):
            return '{"status":"error","message":"Не указан regionId"}'

    if params.get('variant') == '2':
        if not params.get('drtrName'):
            return '{"status":"error","message":"Не указан drtrName"}'

    if params.get('variant') == '3':
        if not params.get('ipNumber'):
            return '{"status":"error","message":"Не указан ipNumber"}'

    if not params.get('lastname'):
        params['lastname'] = None
    if not params.get('firstname'):
        params['firstname'] = None
    if not params.get('middlename'):
        params['middlename'] = None
    if not params.get('birthday'):
        params['birthday'] = None
    if not params.get('ipNumber'):
        params['ipNumber'] = None
    if not params.get('drtrName'):
        params['drtrName'] = None
    if not params.get('address'):
        params['address'] = None
    if not params.get('regionId'):
        params['regionId'] = None

    return params
