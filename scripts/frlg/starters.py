from __future__ import annotations

import argparse
import time
import cv2
import serial
import redis
import numpy

from services.common import shh, increment_counter, getframe, press, make_vid, get_switch_serial, get_switch_vid_num

redis_client = redis.StrictRedis(host="localhost", port=6379, decode_responses=True)
switch_num = 2


def check_if_shiny(frame):
    # print(frame[272][352])
    if switch_num == 1:
        return not numpy.array_equal(frame[101][157], [246, 176, 210])
        return not numpy.array_equal(frame[272][352], [60, 184, 125])
    if switch_num == 2:
        return not numpy.array_equal(frame[301][336], [0, 111, 195])
    if switch_num == 3:
        return not numpy.array_equal(frame[236][430], [41, 147, 255])


def reset_game(ser: serial.Serial):
    press(ser, "ABXY", sleep_time=2)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--switch_num")
    args = parser.parse_args()

    if args.switch_num:
        global switch_num
        switch_num = int(args.switch_num)

    ser_str = get_switch_serial(switch_num)
    vid = make_vid(get_switch_vid_num(switch_num))
    start_time = time.time()

    with serial.Serial(ser_str, 9600) as ser, shh(ser):
        time.sleep(1)
        while True:
            start_time = time.time()
            reset_game(ser)
            press(ser, "A", count=14, sleep_time=0.5)
            press(ser, "B", count=8, sleep_time=0.5)
            press(ser, "A", count=10, sleep_time=0.5)
            press(ser, "B", count=20, sleep_time=0.5)
            press(ser, "X", sleep_time=0.75)
            press(ser, "A", sleep_time=1.25)
            press(ser, "A", count=2, sleep_time=0.5)
            time.sleep(2)

            current_frame = getframe(vid)

            if check_if_shiny(current_frame):
                print("SHINY!!!")
                press(ser, "C", duration=2)
                press(ser, "H", duration=1)
                press(ser, "s", duration=0.25)
                press(ser, "d", duration=0.25)
                press(ser, "d", duration=0.25)
                press(ser, "d", duration=0.25)
                press(ser, "d", duration=0.25)
                press(ser, "d", duration=0.25)
                press(ser, "d", duration=0.25)
                press(ser, "A", duration=1)
                press(ser, "w", duration=1)
                press(ser, "A", duration=1)
                increment_counter(
                    switch_num=switch_num,
                    add_catch=True,
                    log_frame=current_frame,
                )
                print((getframe(vid))[272][352])
                return 0

            increment_counter(switch_num=switch_num, log_frame=current_frame)

            time.sleep(1)
            end_time = time.time()
            print(f"Full encounter took {(end_time - start_time):.3f}s")
            # return 0

    vid.release()
    cv2.destroyAllWindows()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
