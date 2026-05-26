from __future__ import annotations

import argparse
import time
import cv2
import serial
import redis

from services.common import (
    Point,
    shh,
    increment_counter,
    getframe,
    press,
    make_vid,
    get_switch_serial,
    get_switch_vid_num,
    color_near,
    get_text,
    await_pixel,
    await_not_pixel,
)

redis_client = redis.StrictRedis(host="localhost", port=6379, decode_responses=True)
switch_num = 1


def reset_game(ser: serial.Serial, vid: cv2.VideoCapture):
    press(ser, "H", sleep_time=1)
    press(ser, "X", sleep_time=1)
    press(ser, "A", sleep_time=1)

    frame = getframe(vid)
    while not color_near(frame[50][90], (250, 250, 250)):
        press(ser, "A", sleep_time=0.15)
        frame = getframe(vid)

    print("game loaded!")


def get_stop_text_showing(vid: cv2.VideoCapture):

    frame = getframe(vid)

    if get_text(frame=frame, top_left=Point(y=585, x=295), bottom_right=Point(y=635, x=427), invert=True) == "Will you":
        return True
    elif get_text(frame=frame, top_left=Point(y=587, x=302), bottom_right=Point(y=629, x=395), invert=True) == "Which":
        return True
    elif get_text(frame=frame, top_left=Point(y=585, x=297), bottom_right=Point(y=630, x=383), invert=True) == "Look!":
        return True

    return False


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
            reset_game(ser, vid)

            press(ser, "w", duration=0.5)

            stop_text_showing = get_stop_text_showing(vid)
            while not stop_text_showing:
                press(ser, "A", sleep_time=0.15)
                stop_text_showing = get_stop_text_showing(vid)

            time.sleep(0.5)
            # Select Chimchar
            press(ser, "A", sleep_time=0.3)
            press(ser, "B", count=3, sleep_time=0.3)
            press(ser, "d", sleep_time=0.3)
            press(ser, "A", sleep_time=1)
            press(ser, "w", sleep_time=0.25)
            press(ser, "A", sleep_time=0.25)

            x_val = 960
            y_val = 660

            await_pixel(vid, x=x_val, y=y_val, pixel=(255, 255, 255))
            print("started battle!")
            time.sleep(1)
            await_not_pixel(vid, x=x_val, y=y_val, pixel=(255, 255, 255), exact_pixel=False)
            print("starting pixel gone")
            time.sleep(4)

            frame = getframe(vid)
            while not color_near(frame[y_val][x_val], (255, 255, 255)):
                print(frame[y_val][x_val])
                time.sleep(0.1)
                frame = getframe(vid)

            time.sleep(0.25)
            print("You encountered a starly!")
            await_not_pixel(vid, x=x_val, y=y_val, pixel=(255, 255, 255))
            print("starly pixel gone")

            await_pixel(vid, x=x_val, y=y_val, pixel=(255, 255, 255))
            print("Go Chimchar!")
            await_not_pixel(vid, x=x_val, y=y_val, pixel=(255, 255, 255))

            print("dialog ended")
            t0 = time.time()

            await_pixel(vid, x=35, y=630, pixel=(250, 250, 250), exact_pixel=False)

            t1 = time.time()

            delay = t1 - t0
            print(f"dialog delay: {delay:.3f}s")
            current_frame = getframe(vid)

            if delay > 1:
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
                    pokemon_name="chimchar",
                    add_catch=True,
                    log_frame=current_frame,
                )
                return 0

            increment_counter(switch_num=switch_num, pokemon_name="chimchar", log_frame=current_frame)

            time.sleep(1)
            end_time = time.time()
            print(f"Full encounter took {(end_time - start_time):.3f}s")
            # return 0

    vid.release()
    cv2.destroyAllWindows()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
