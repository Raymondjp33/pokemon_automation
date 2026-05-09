from __future__ import annotations

import argparse
import time
import cv2
import serial
import redis
import numpy
import re
import pytesseract
import threading
from queue import Queue

from services.common import (
    getframe,
    get_switch_serial,
    get_switch_vid_num,
    get_mapped_name,
    get_text,
    shh,
    make_vid,
    press,
    color_near,
    increment_counter,
    Point,
)

redis_client = redis.StrictRedis(host="localhost", port=6379, decode_responses=True)
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


def handle_movement(ser: serial.Serial, stop_event):
    index = 0
    print("Starting to move")
    while not stop_event.is_set():
        str = f"{(index % 3) + 1}"
        # print(f'pressing {str}')
        press(ser, str, duration=0.05)
        index = index + 1

    print("Coming to a stop")


def handle_encoutner_check(vid: cv2.VideoCapture, stop_event, mon_que, delay_que, frame_que):
    x_val = 608
    y_val = 382
    frame = getframe(vid)
    while not color_near(frame[y_val][x_val], (0, 0, 0)) and not stop_event.is_set():
        time.sleep(0.1)
        frame = getframe(vid)

    start_time = time.time()
    stop_event.set()

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
            end_time = time.time()
            time.sleep(0.1)
            current_text = extract_encounter_text(vid)
            pokemon = extract_pokemon_name(current_text)
            log_frame = getframe(vid)
            print(f"{pokemon} appeared!")
            break
        time.sleep(0.1)

    delay = end_time - start_time
    pokemon = get_mapped_name(pokemon.lower()).lower()
    mon_que.put(pokemon)
    delay_que.put(delay)
    frame_que.put(log_frame)


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

    mon_que = Queue()
    delay_que = Queue()
    frame_que = Queue()

    with serial.Serial(ser_str, 9600) as ser, shh(ser):
        time.sleep(1)

        # print(extract_pokemon_name(extract_encounter_text(vid)))
        # stop_event = threading.Event()
        # handle_encoutner_check(vid, stop_event, mon_que, delay_que, frame_que)
        # return

        while True:
            start_time = time.time()
            stop_event = threading.Event()

            if not numpy.array_equal(getframe(vid)[331][640], [4, 0, 11]):
                press(ser, "4")

            worker_thread = threading.Thread(
                target=handle_movement,
                args=(
                    ser,
                    stop_event,
                ),
            )
            monitor_thread = threading.Thread(
                target=handle_encoutner_check, args=(vid, stop_event, mon_que, delay_que, frame_que)
            )

            worker_thread.start()
            monitor_thread.start()

            worker_thread.join()
            monitor_thread.join()

            pokemon = mon_que.get()
            delay = delay_que.get()
            log_frame = frame_que.get()

            print(f"dialog delay: {delay:.3f}s")

            if (delay) > 4.3:
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
                increment_counter(switch_num=switch_num, pokemon_name=pokemon, add_catch=True, log_frame=log_frame)
                return 0

            increment_counter(switch_num=switch_num, pokemon_name=pokemon)

            press(ser, "B", count=4, sleep_time=0.3)
            run_texts = []
            while "RUN" not in run_texts:
                frame = getframe(vid)
                switch3_run_text = get_text(
                    frame=frame, top_left=Point(y=598, x=944), bottom_right=Point(y=667, x=1044), invert=True
                )
                run_texts = [switch3_run_text]
                press(ser, "B", sleep_time=0.5)

            print("Running")
            press(ser, "d")
            press(ser, "s")
            press(ser, "A", count=4, sleep_time=0.5)
            time.sleep(2)

            end_time = time.time()
            print(f"Full encounter took {(end_time - start_time):.3f}s")
            # return 0

    vid.release()
    cv2.destroyAllWindows()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
