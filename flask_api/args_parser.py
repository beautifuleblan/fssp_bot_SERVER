from flask_restful import reqparse
from configs.config import API_KEY

def parse_args():
    parser = reqparse.RequestParser(trim=True)
    parser.add_argument('API', nullable=False, location='form')
    parser.add_argument('variant', nullable=False, type=int, location='form')
    parser.add_argument('drtrName', nullable=True, location='form')
    parser.add_argument('address', nullable=True, location='form')
    parser.add_argument('regionId', nullable=True, type=str, location='form')
    parser.add_argument('lastname', nullable=True, location='form')
    parser.add_argument('firstname', nullable=True, location='form')
    parser.add_argument('middlename', nullable=True, location='form')
    parser.add_argument('birthday', nullable=True, location='form')
    parser.add_argument('ipNumber', nullable=True, location='form')
    params = parser.parse_args()
    print(params)
    if params['API'] != API_KEY:
        return {'status': 'error', 'message': 'Не верный ключ API'}
    if not params['variant'] or (params['variant'] not in [1, 2, 3]):
        return {'status': 'error', 'message': 'Не указан variant'}

    if params['variant'] == 1:
        if not params['lastname']:
            return {'status': 'error', 'message': 'Не указан lastname'}
        elif not params['firstname']:
            return {'status': 'error', 'message': 'Не указан firstname'}
        elif not params['birthday']:
            return {'status': 'error', 'message': 'Не указан birthday'}
        elif not params['regionId']:
            return {'status': 'error', 'message': 'Не указан regionId'}

    if params['variant'] == 2:
        if not params['drtrName']:
            return {'status': 'error', 'message': 'Не указан drtrName'}
        if not params['address']:
            return {'status': 'error', 'message': 'Не указан address'}

    if params['variant'] == 3:
        if not params['ipNumber']:
            return {'status': 'error', 'message': 'Не указан ipNumber'}
    return params