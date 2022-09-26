from json import dumps
import concurrent.futures as pool
from time import sleep
# a = ['xyi']
# b = False
# c = None
# result = dumps(a)
# print(a)
# print(result)
# print(type(a) is list)
# print(b is None)
# print(c is False)

executor = pool.ThreadPoolExecutor()

def func():
    sleep(10)
    return False, {'a': 2}
task = executor.submit(func)
task.cancel()
# while True:
#     if task.exception():
#         print(bool(task.result()))
#         break
print(task.result() == False)


# a = [], {'a': 2}
# b = None
# print(tuple(a[0]))
# print(bool(a))
# print(a[0] == 'Banned')
# print(type(a[0]) == list)
