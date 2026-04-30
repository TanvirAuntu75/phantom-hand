import time
import os

last_timestamp = 0
for _ in range(10):
    timestamp = int(time.perf_counter() * 1000)
    print(timestamp)
    if timestamp <= last_timestamp:
        print("Timestamp is not monotonically increasing!")
    last_timestamp = timestamp
