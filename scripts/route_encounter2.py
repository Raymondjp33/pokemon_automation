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
import json
import pytesseract
import os
import re
import sqlite3
import redis
import threading
from queue import Queue

from services.common import *

redis_client = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)

name_map = {
    'Nidorana' : 'NidoranM',
    'Nidoran' : 'NidoranF',
    "Mime": 'MimeJr',
}

def write_shiny_text():
    shiny_text_path = SWITCH2_SHINY_TEXT_PATH
    with shiny_text_path.open("w") as file1:
        file1.write("I got a shiny! My switch\nwill be off until I can\ncome catch it!")

def increment_counter(pokemon_name, log_frame=None):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()


    cursor.execute("SELECT * FROM pokemon WHERE name = ?", (pokemon_name,))
    pokemon_row = cursor.fetchone()
    if (log_frame is not None):
        cursor.execute("SELECT SUM(encounters) FROM catches WHERE name = ?", (pokemon_name,))
        result = cursor.fetchone()[0]
        previous_encounters = result if result is not None else 0
        count_difference = pokemon_row[2] - previous_encounters
        cursor.execute(
            "INSERT INTO catches (pokemon_id, caught_timestamp, encounters, encounter_method, switch, name, total_dens) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                pokemon_row[0],
                int(time.time() * 1000),
                count_difference,
                "route",
                2,
                pokemon_name,
                None
            )
        )

        cv2.imwrite(f"/Volumes/DexDrive/shield/{pokemon_name}-{int(time.time() * 1000)}.png", log_frame)
    else:
        if pokemon_row:
            cursor.execute("""
                UPDATE pokemon
                SET encounters_total = encounters_total + 1
                WHERE name = ?
            """, (pokemon_name,))
        else:
            cursor.execute("""
                INSERT INTO tempmons (name, encounters)
                VALUES (?, 1)
                ON CONFLICT(name) DO UPDATE SET
                    encounters = encounters + 1
            """, (pokemon_name,))

    
    increment_txt_counter(SWITCH2_COUNTER_PATH)
    redis_client.publish(REDIS_CHANNEL, json.dumps({"update_data":True}))
    conn.commit()
    conn.close()

def extract_encounter_text(vid: cv2.VideoCapture) -> str:
    frame = getframe(vid)
    height, width = frame.shape[:2]
    crop_box = frame[int(height * 0.8):height, 0:width]
    cropped_rgb = cv2.cvtColor(crop_box, cv2.COLOR_BGR2RGB)
    text = pytesseract.image_to_string(cropped_rgb)
    return text.strip()

def extract_pokemon_name(text):
    match = re.search(r"You encountered a wild (\w+)!?", text)
    if match:
        return match.group(1)
    return None

def handle_movement(ser: serial.Serial, stop_event):
    move_up = True
    should_exit = False
    print('Starting to move')
    while not should_exit:
        press(ser, 'w' if move_up else 's', write_null_byte=False)
        for _ in range(10):
            if stop_event.is_set():
                should_exit = True
                break
            time.sleep(0.1)
        move_up = not move_up

    press(ser, 'B')
    print('Coming to a stop')

def handle_encoutner_check(vid: cv2.VideoCapture, stop_event, mon_que, delay_que, frame_que):
    x_val = 1143
    y_val = 640
    frame = getframe(vid)
    while not color_near(frame[y_val][x_val], (58, 58, 58)) and not stop_event.is_set():
        frame = getframe(vid)
        time.sleep(0.1)

    timeout = 0
    pokemon = None
    print('About to entry while statement in encounter check!')
    while True:
        frame = getframe(vid)
        current_text = extract_encounter_text(vid)
        # print(f'here and current text is {current_text}')
        timeout += 1
        if (timeout > 6000):
            print('Returning from encounter check early!')
            return
        if 'You encountered' in current_text:
            stop_event.set()
            time.sleep(0.1)
            current_text = extract_encounter_text(vid)
            pokemon = extract_pokemon_name(current_text)
            break

        time.sleep(0.2)

    # Wait for encounter text to go away, noting delay
    await_pixel(vid, x=x_val, y=y_val, pixel=(58, 58, 58))
    print(f'{pokemon} appeared!')
    await_not_pixel(vid, x=x_val, y=y_val, pixel=(58, 58, 58))
    log_frame = getframe(vid)
    t0 = time.time()

    await_pixel(vid, x=x_val, y=y_val, pixel=(58, 58, 58))
    t1 = time.time()

    delay = t1 - t0

    pokemon = name_map.get(pokemon, pokemon)
    mon_que.put(pokemon)
    delay_que.put(delay)
    frame_que.put(log_frame)

def main() -> int:
    ser_str = SWITCH2_SERIAL
    vid = make_vid(SWITCH2_VID_NUM)



    start_time = time.time()

    mon_que = Queue()
    delay_que = Queue()
    frame_que = Queue()
    with serial.Serial(ser_str, 9600) as ser, shh(ser):
        time.sleep(2)
        while True:
            stop_event = threading.Event()

            worker_thread = threading.Thread(target=handle_movement, args=(ser, stop_event,))
            monitor_thread = threading.Thread(target=handle_encoutner_check, args=(vid, stop_event, mon_que, delay_que, frame_que))

            worker_thread.start()
            monitor_thread.start()

            worker_thread.join()
            monitor_thread.join()

            pokemon = mon_que.get()
            delay = delay_que.get()
            log_frame = frame_que.get()

            print(f'dialog delay: {delay:.3f}s')
            if (delay) > 0.6:
                print('SHINY!!!')
                press(ser, 'C', duration=2)
                press(ser, 'H', duration=1)
                press(ser, 's', duration=0.25)
                press(ser, 'd', duration=0.25)
                press(ser, 'd', duration=0.25)
                press(ser, 'd', duration=0.25)
                press(ser, 'd', duration=0.25)
                press(ser, 'd', duration=0.25)
                press(ser, 'd', duration=0.25)
                press(ser, 'A', duration=1)
                press(ser, 'w', duration=1)
                press(ser, 'A', duration=1)
                increment_counter(pokemon_name=pokemon, log_frame=log_frame)
                write_shiny_text()
                return 0

            increment_counter(pokemon_name=pokemon)

            frame = getframe(vid)
            current_text = get_text(frame=frame, top_left=Point(y=650, x=1054), bottom_right=Point(y=699, x=1123), invert=True)
            while current_text != 'Run':
                current_text = get_text(frame=frame, top_left=Point(y=650, x=1054), bottom_right=Point(y=699, x=1123), invert=True)
                frame = getframe(vid)
                time.sleep(1)
            
            print('Running')
            press(ser, 'w', sleep_time=.5)
            press(ser, 'A',  sleep_time= 6)

 
            end_time = time.time()
            print(f'Total runtime: {(end_time-start_time):.3f}s')
            start_time = time.time()
            # return 0

    vid.release()
    cv2.destroyAllWindows()
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
