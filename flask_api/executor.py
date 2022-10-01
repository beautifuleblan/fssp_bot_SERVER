import concurrent.futures as pool
import multiprocessing
from threading import Lock

lock = Lock()

count = {'no_queue_success': 0,
         'no_queue_fail': 0,
         'taskid_success': 0,
         'taskid_fail': 0}

workers = multiprocessing.cpu_count() * 2
executor = pool.ThreadPoolExecutor(max_workers=workers)