from __future__ import annotations

import argparse
from pathlib import Path
import time
import cv2
import serial
import json
import sqlite3
import redis
import numpy
import re
import pytesseract
import threading
from queue import Queue

from services.common import *

redis_client = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)
switch_num = 3

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--switch_num')
    args = parser.parse_args()

    if args.switch_num:
        global switch_num 
        switch_num = int(args.switch_num)

    ser_str = get_switch_serial(switch_num)
    vid = make_vid(get_switch_vid_num(switch_num))
  
    with serial.Serial(ser_str, 9600) as ser, shh(ser):
        time.sleep(1)

        while True:
            start_time = time.time()

            press(ser, 's', duration=1.5, sleep_time=2.5)
            press(ser, 'aB', duration=0.5)
            press(ser, 'wB', duration=0.4)

            press(ser, 'aB', dont_clear=True)
            while not numpy.array_equal(getframe(vid)[272][1079], [85, 239, 145]):
                time.sleep(0.5)
                if time.time() - start_time > 100:
                    print('Error 1')
                    press(ser, 'H', duration=1.5, sleep_time=3)
                    press(ser, 'A')
                    return

            press(ser, 'wB', duration=1.5)
            press(ser, 'dB', duration=2, sleep_time=0.5)

            if numpy.array_equal(getframe(vid)[274][342], [85, 239, 145]):
                press(ser, 'd')
            elif numpy.array_equal(getframe(vid)[277][203], [85, 238, 147]):
                press(ser, 'a')
                press(ser, 'a')

            press(ser, 'wB', duration=8)

            current_text = None

            while current_text != 'RAY scurried':
                press(ser, 'A', sleep_time=0.3)
                current_text = get_text(getframe(vid), Point(y=215, x=119), Point(y=275, x=436), invert=True)

                if time.time() - start_time > 500:
                    print('Error 2')
                    press(ser, 'H', duration=1.5, sleep_time=3)
                    press(ser, 'A')
                    return
            
            press(ser, 'B', count=18, sleep_time=0.5)
     
            end_time = time.time()
            print(f'Full script took {(end_time-start_time):.3f}s')
            # return 0

    vid.release()
    cv2.destroyAllWindows()
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
