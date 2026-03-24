from __future__ import annotations

import argparse
import time
import cv2
import serial
import pytesseract
import re

from services.common import (
    getframe,
    get_switch_serial,
    get_switch_vid_num,
    shh,
    make_vid,
    press,
    color_near,
    increment_counter,
)

switch_num = 3


def extract_encounter_text(vid: cv2.VideoCapture) -> str:
    frame = getframe(vid)
    height, width = frame.shape[:2]
    y1 = int(height * 0.7)
    y2 = height
    x1 = 0
    x2 = width
    crop_box = frame[y1:y2, x1:x2]
    cropped_rgb = cv2.cvtColor(crop_box, cv2.COLOR_BGR2RGB)
    text = pytesseract.image_to_string(cropped_rgb)

    return text.strip()


def extract_pokemon_name(text):
    match = re.search(r"Wild\s+([A-Za-z\-']+)", text)
    if match:
        return match.group(1)
    return None


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

            press(ser, "A", count=13, sleep_time=0.5)
            press(ser, "B", count=5, sleep_time=0.5)

            x_val = 608
            y_val = 382
            frame = getframe(vid)

            while not color_near(frame[y_val][x_val], (0, 0, 0)):
                press(ser, "A", sleep_time=0.3)
                frame = getframe(vid)

            t0 = time.time()

            timeout = 0
            pokemon = None
            print("About to enter while statement in encounter check!")
            while True:
                frame = getframe(vid)
                current_text = extract_encounter_text(vid)
                # print(f'here and current text is {current_text}')
                timeout += 1
                if timeout > 6000:
                    print("Returning from encounter check early!")
                    return
                if "Wild" in current_text:
                    t1 = time.time()
                    time.sleep(0.1)
                    current_text = extract_encounter_text(vid)
                    pokemon = extract_pokemon_name(current_text).lower()
                    log_frame = getframe(vid)
                    print(f"{pokemon} appeared!")
                    break
                time.sleep(0.1)

            delay = t1 - t0
            print(f"dialog delay: {delay:.3f}s")

            if (delay) > 4.0:
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
                    pokemon_name=pokemon,
                    add_catch=True,
                    log_frame=log_frame,
                )
                return 0

            increment_counter(
                switch_num=switch_num,
                pokemon_name=pokemon,
                log_frame=log_frame,
            )

            end_time = time.time()
            print(f"Full encounter took {(end_time - start_time):.3f}s")
            # return 0

    vid.release()
    cv2.destroyAllWindows()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
