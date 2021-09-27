from server import get_data
import time

count = 0

while True:
    time.sleep(1)
    get_data(count)
    count += 1
