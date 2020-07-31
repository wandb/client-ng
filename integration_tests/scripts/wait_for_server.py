import requests
import time
import sys
import os

start_time = time.time()

TIMEOUT_SECONDS = 20
# Checks if the script should timeout
def is_timeout():
    return (time.time() - start_time) > TIMEOUT_SECONDS

while not is_timeout():
    res = requests.get("http://localhost:9000/ready")
    if res.status_code == 200:
        print("Server responded with 200. Success!")
        sys.exit(os.EX_OK)
    time.sleep(0.2)

print("Server failed to respond with a 200.")
sys.exit(os.EX_OK)
