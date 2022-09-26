"""
Время указывается в секундах

QUERY_IN_WORK_DELAY: Задержка перед повторной отправкой после получения ответа "Ваш запрос уже обрабатывается"
QUERY_IN_WORK_REPEAT_AMOUNT: Кол-во повторений
BETWEEN_ACTIONS_DELAY: Задержка между выполнением каждого действия на странице
TIMEOUT_DELAY: Максимальное время ожидания появления элемента на странице
PASS_PARAMS_IN_URL: Передача параметров в ссылке - True, ручной выбор параметров - False

"""

API_KEY = 'KCE7WWhfPq9DzqLydXSkvs40llJz4o0g'
QUERY_IN_WORK_DELAY = 30
QUERY_IN_WORK_REPEAT_AMOUNT = 2
BETWEEN_ACTIONS_DELAY = 2
CHROME_BROWSER = True
FIREFOX_BROWSER = False
SELECTOR_TIMEOUT = 15
REQUEST_TIMEOUT = 180
RUN_NO_QUEUE_TIMEOUT = 90
PASS_PARAMS_IN_URL = True
