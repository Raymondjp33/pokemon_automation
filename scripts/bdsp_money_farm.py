from __future__ import annotations

import argparse
import contextlib
from pathlib import Path
import time
from collections.abc import Generator
from typing import NamedTuple

import cv2
import numpy
import serial

import functools
from typing import Protocol
import tesserocr

from services.common import *


def start_battle(ser: serial.Serial, vid: cv2.VideoCapture,):
    while True:
        frame = getframe(vid)
        
        distance_duration = 1.3
        for _ in range(8):
            press(ser, 'w', duration=distance_duration)
            press(ser, 's', duration=distance_duration)

        press(ser, '+', sleep_time=1)
        press(ser, 's', sleep_time=3)

        press(ser, 'A', sleep_time=.5, count=5)

        press(ser, 'a', sleep_time=.5)
        press(ser, 'A', sleep_time=0.5, count=3)

        for _ in range(12):
            frame = getframe(vid)
            if (color_near(frame[443][1120], (7, 7, 7))):
                return True
            time.sleep(0.5)
            
        press(ser, 'd', sleep_time=.5)
        press(ser, 'A', sleep_time=0.5, count=3)

        for _ in range(12):
            frame = getframe(vid)
            if (color_near(frame[443][1120], (7, 7, 7))):
                return True
            time.sleep(0.5)



def main() -> int:
    ser_str = SWITCH1_SERIAL
    vid = make_vid(SWITCH1_VID_NUM)


    battling = False

  
    with serial.Serial(ser_str, 9600) as ser, shh(ser):
        # go_to_change_grip(ser)
        # connect_and_go_to_game(ser)
        # return 0
        while True:
            frame = getframe(vid)

            start_battle(ser, vid)

            battling = True
            print('Starting battle')


            while battling:
                # print('in this loop')
                frame = getframe(vid)
                if (color_near(frame[443][1120], (72, 76, 232))):
                    print('Using move')
                    press(ser, 'A', sleep_time=1, count=4)
                    

                # Seeing exp points
                if ((get_text(frame=frame, top_left=Point(y=584, x=685), bottom_right=Point(y=635, x=789), invert=True)) == 'Points!'):
                    print('Exp points')
                    press(ser, 'A', sleep_time=1, count=2)
                
                # Battle over
                if ((get_text(frame=frame, top_left=Point(y=634, x=299), bottom_right=Point(y=680, x=494), invert=True)) == 'buddy here...'):
                    print('Battle over')
                    press(ser, 'A', sleep_time=1, count=7)
                    battling = False
                    
                time.sleep(3)

            # return 0


    vid.release()
    cv2.destroyAllWindows()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
