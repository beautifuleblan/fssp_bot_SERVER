from DB import DataBase

async def log():
    async with DataBase() as db:
        with open('/var/www/fssp_bot_async/log_file.log', 'r', encoding='utf-8') as file:
        # with open('/Users/denysmalykhin/PycharmProjects/fssp_bot_async/log_file.log', 'r', encoding='utf-8') as file:
            log = file.read().splitlines()[::-1]
            no_queue_success, no_queue_fail, taskid_success, taskid_fail = await db.get_stats()
            result = map(lambda x: f'<br>{x}', log[:500])
            return f'<body><table>' \
                   f'NO QUEUE SUCCESS - {no_queue_success} | NO QUEUE FAIL - {no_queue_fail} | ' \
                   f'TASK ID SUCCESS - {taskid_success} | TASK ID FAIL - {taskid_fail}' \
                   f'{" ".join(list(result))}' \
                   f'</table></body>'