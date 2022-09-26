import concurrent.futures as pool
from DB import DataBase

db = DataBase()

executor = pool.ThreadPoolExecutor()