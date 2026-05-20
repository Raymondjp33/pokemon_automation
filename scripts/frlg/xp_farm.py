from __future__ import annotations

import argparse
import time
import cv2
import serial

from services.common import Point, get_text, shh, getframe, press, make_vid, get_switch_serial, get_switch_vid_num

switch_num = 3


def do_heal_route(ser: serial.Serial):
    print("Going into the heal springs!")
    # press(ser, "a", count=11, sleep_time=0.2)
    # return

    # Get into the mountain
    press(ser, "wB", duration=1.75)
    press(ser, "d", duration=0.3)
    press(ser, "w", duration=0.3, sleep_time=2)

    # Get into the spring water
    press(ser, "wB", duration=2.75)
    press(ser, "dB", duration=1.5)
    press(ser, "wB", duration=2)
    press(ser, "dB", duration=0.3)
    press(ser, "sB", duration=0.3, sleep_time=0.5)
    press(ser, "a", count=11, sleep_time=0.2)
    press(ser, "sB", duration=1, sleep_time=1)

    # Get out of the spring water and then out of the mountain
    press(ser, "A", count=4, sleep_time=0.5)
    press(ser, "wB", duration=0.75)
    press(ser, "dB", duration=1.5)
    press(ser, "sB", duration=0.3, sleep_time=0.5)
    press(ser, "a", count=3, sleep_time=0.2)
    press(ser, "sB", duration=2, sleep_time=0.5)
    press(ser, "a", count=9, sleep_time=0.25)
    press(ser, "sB", duration=3, sleep_time=2)

    # Get into position to use vs Seeker
    press(ser, "a", count=2, sleep_time=0.2)
    press(ser, "sB", duration=3, sleep_time=0.5)


def handle_battle(ser: serial.Serial, vid: cv2.VideoCapture):
    defeated_text = get_text(
        frame=getframe(vid), top_left=Point(y=537, x=159), bottom_right=Point(y=595, x=553), invert=True
    )

    while defeated_text != "Player defeated":
        press(ser, "A", sleep_time=0.5)
        defeated_text = get_text(
            frame=getframe(vid), top_left=Point(y=537, x=159), bottom_right=Point(y=595, x=553), invert=True
        )

    press(ser, "A", count=6, sleep_time=0.5)
    time.sleep(3)
    print("Battle done!")


def attempt_battle1(ser: serial.Serial, vid: cv2.VideoCapture):
    press(ser, "dB", duration=0.3, sleep_time=0.5)
    press(ser, "w", count=2, sleep_time=0.2)
    press(ser, "A", sleep_time=1)

    print("Trying to start battle 1")
    battle_started = (
        get_text(frame=getframe(vid), top_left=Point(y=525, x=177), bottom_right=Point(y=599, x=500), invert=True)
        == "Every morning"
    )

    if not battle_started:
        print("Battler 1 not ready :(")
        time.sleep(2)
        press(ser, "A", sleep_time=1)
        return

    print("Battling trainer 1!")
    handle_battle(ser, vid)


def attempt_battle2(ser: serial.Serial, vid: cv2.VideoCapture):
    press(ser, "aB", duration=1)
    press(ser, "sB", duration=1)
    press(ser, "aB", duration=0.5)
    press(ser, "A", sleep_time=1)

    print("Trying to start battle 2")
    battle_started = (
        get_text(frame=getframe(vid), top_left=Point(y=525, x=307), bottom_right=Point(y=593, x=471), invert=True)
        == "My big"
    )

    if not battle_started:
        print("Battler 2 not ready :(")
        time.sleep(2)
        press(ser, "A", sleep_time=1)
        return

    print("Battling trainer 2!")
    handle_battle(ser, vid)


def attempt_battle3(ser: serial.Serial, vid: cv2.VideoCapture):
    press(ser, "dB", duration=0.5, sleep_time=0.5)
    press(ser, "w", count=8, sleep_time=0.2)
    press(ser, "a", count=2, sleep_time=0.2)
    press(ser, "sB", duration=0.75)
    press(ser, "A", sleep_time=1)

    print("Trying to start battle 3")
    battle_started = (
        get_text(frame=getframe(vid), top_left=Point(y=593, x=180), bottom_right=Point(y=655, x=426), invert=True)
        == "Lose that"
    )

    if not battle_started:
        print("Battler 3 not ready :(")
        time.sleep(2)
        press(ser, "A", sleep_time=1)
        return

    print("Battling trainer 3!")
    handle_battle(ser, vid)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--switch_num")
    args = parser.parse_args()

    if args.switch_num:
        global switch_num
        switch_num = int(args.switch_num)

    ser_str = get_switch_serial(switch_num)
    vid = make_vid(get_switch_vid_num(switch_num))

    with serial.Serial(ser_str, 9600) as ser, shh(ser):
        time.sleep(1)
        # handle_battle(ser, vid)
        # return 0
        while True:
            start_time = time.time()

            do_heal_route(ser)

            # Use vs Seeker
            press(ser, "-", sleep_time=4)
            press(ser, "A", count=2, sleep_time=0.5)

            attempt_battle1(ser, vid)
            attempt_battle2(ser, vid)
            attempt_battle3(ser, vid)

            # Get back to starting location
            press(ser, "w", count=2, sleep_time=0.2)
            press(ser, "dB", duration=0.75)

            time.sleep(1)
            end_time = time.time()
            print(f"Full battle loop took {(end_time - start_time):.3f}s")
            # break

    vid.release()
    cv2.destroyAllWindows()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
