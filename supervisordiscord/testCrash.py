import time

from datetime import datetime

if __name__ == '__main__':
    print(">>>>> STARTING ...", flush=True)
    while True:
        print("sleep now:", datetime.utcnow(), flush=True)
        time.sleep(15)
        raise Exception("Test crash.")
