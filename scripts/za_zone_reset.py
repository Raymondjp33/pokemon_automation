from __future__ import annotations

import time

import cv2
import serial
import re
import os

import redis

from services.common import *

def increment_reset_counter(file_path):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return None
    
    try:
        with open(file_path, 'r') as file:
            content = file.read()
        
        match = re.search(r'Current resets: (\d+)', content)
        if not match:
            print("Could not find 'Current resets: X' pattern in the file")
            return None
        
        current_value = int(match.group(1))
        new_value = current_value + 1
        
        new_content = re.sub(r'Current resets: \d+', f'Current resets: {new_value}', content)
        
        with open(file_path, 'w') as file:
            file.write(new_content)
        
        return new_value
        
    except Exception as e:
        print(f"Error processing file: {e}")
        return None

def main() -> int:
    ser_str = SWITCH3_SERIAL
    # vid = make_vid(SWITCH3_VID_NUM)


    with serial.Serial(ser_str, 9600) as ser, shh(ser):
        time.sleep(2)


        
        while True:

            ## Walk in then tp, zone 2
            # press(ser, 'A', sleep_time=2)
            # press(ser, 'w', duration=2.5)
            # press(ser, 'B', sleep_time=1)
            # press(ser, 'A')
            # press(ser, '+', sleep_time=1.25)
            # press(ser, 'A', sleep_time=0.5, count=4)
            # time.sleep(5)

            ## Battles
            # press(ser, 'l', duration=0.5, write_null_byte=False)
            # press(ser, 'A', sleep_time=0.5, count=3)

            ## Bench
            # press(ser, 'a', duration=0.75)
            # press(ser, 'd', duration=0.5)
            press(ser, 'w', duration=2)
            press(ser, 's', duration=2.3)
            # press(ser, 's')
            press(ser, 'A', sleep_time=0.5, count=7)
            time.sleep(20)

            ## Teleporter
            # press(ser, 'A', sleep_time=4)
           
            ## Zone 20 charmander specific
            # press(ser, 'q', duration=0.2, write_null_byte=False)
            # press(ser, 'B', duration=0.03, write_null_byte=False)
            # press(ser, 'q', duration=6, write_null_byte=False)
            # press(ser, 'B')
            # press(ser, '+', sleep_time=1.25)
            # press(ser, 'd', duration=0.05)
            # press(ser, 'A', sleep_time=0.5, count=4)
            # press(ser, 'd')
            # press(ser, 'A', sleep_time=0.5, count=4)
            # time.sleep(3.5)

            ## Walk into zone then TP
            # press(ser, 'w', duration=1.5)
            # press(ser, 'B')
            # # press(ser, 'A', sleep_time=3)
            # press(ser, '+', sleep_time=1.25)
            # press(ser, 'a')
            # press(ser, 'A', sleep_time=0.5, count=4)
            # time.sleep(4)

            ## Zone tp (7)
            # press(ser, '+', sleep_time=1.25)
            # press(ser, 'a')
            # press(ser, 'A', sleep_time=0.5, count=4)
            # press(ser, 'B')
            # time.sleep(4)

            ## Zone 3
            # press(ser, 's', duration=1, sleep_time=3)

            ## Unspecific
            increment_reset_counter('/Users/raymondprice/Desktop/other/test_coding/pokemon_scripts/pokemon_automation/scripts/configs/bench_counter.txt')
            # end_time = time.time()
            # print(f'Full run took {(end_time-start_time):.3f}s')

    # vid.release()
    # cv2.destroyAllWindows()
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
