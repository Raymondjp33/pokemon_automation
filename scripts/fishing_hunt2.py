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

from services.common import *

redis_client = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)

def write_shiny_text():
    shiny_text_path = SWITCH2_SHINY_TEXT_PATH
    with shiny_text_path.open("w") as file1:
        file1.write("I got the target amount of\nshinies! My switch will be\noff until I'm back.")

def increment_counter(pokemon_name, log_frame=None):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    counter_path = SWITCH2_COUNTER_PATH
    stream_data_path = STREAM_DATA_PATH
    
    # Read the existing count (default to 0 if file does not exist)
    if counter_path.exists():
        with counter_path.open("r") as file:
            try:
                count = int(file.read().strip())
            except ValueError:
                count = 0
    else:
        count = 0

    # Increment the counter
    count += 1

    with stream_data_path.open("r") as stream_data_file:
        stream_data = json.load(stream_data_file)

    if (log_frame is not None):
        cursor.execute("SELECT * FROM pokemon WHERE name = ?", (pokemon_name,))
        pokemon_row = cursor.fetchone()
        cursor.execute("SELECT * FROM catches WHERE name = ?", (pokemon_name,))
        catch_rows = cursor.fetchall()
        catches = [{"caught_timestamp": ts, "encounters": enc, "encounter_method": method, "total_dens": tdens} for _, _, ts, enc, method, _, _, tdens in catch_rows]
        previous_encounters = 0

        for catch in catches:
            previous_encounters = previous_encounters + catch["encounters"]
        count_difference = pokemon_row[2] - previous_encounters

        cursor.execute(
            "INSERT INTO catches (pokemon_id, caught_timestamp, encounters, encounter_method, switch, name, total_dens) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                pokemon_row[0],
                int(time.time() * 1000),
                count_difference,
                "fishing",
                2,
                pokemon_name,
                None
            )
        )

        cv2.imwrite(f"/Volumes/DexDrive/shield/{pokemon_name}-{int(time.time() * 1000)}.png", log_frame)
    else:
        cursor.execute("""
            UPDATE pokemon
            SET encounters_total = encounters_total + 1
            WHERE name = ?
        """, (pokemon_name,))

    with counter_path.open("w") as file1:
        file1.write(str(count))
            
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

def main() -> int:
    ser_str = SWITCH2_SERIAL
    vid = make_vid(SWITCH2_VID_NUM)

    x_val = 1143
    y_val = 640

    start_time = time.time()
    timeout = 0

    with serial.Serial(ser_str, 9600) as ser, shh(ser):
        time.sleep(2)
        while True:

            # Start fishing
            press(ser, 'A')
            time.sleep(2)

            # Wait to reel
            bad_reel = False
            frame = getframe(vid)
            while not color_near(frame[290][639], (236, 236, 236)) and timeout < 200:
                # print(frame[241][720])
                # cv2.rectangle(
                #         frame,
                #         (650, 210),
                #         (730, 290),
                #         Color(b=255, g=0, r=0),
                #         1,
                #     )
                time.sleep(0.1)
                frame = getframe(vid)
                timeout += 1
                if timeout % 5 == 0:
                    current_text = get_text(frame=frame, top_left=Point(597, 273), bottom_right=Point(636, 752), invert=True)
                    if current_text == "You reeled your line in too slow!" or current_text == 'You reeled your line in too fast!':
                        bad_reel = True
                        break
        
            if (bad_reel):
                print('Reeled too slow or fast!')
                time.sleep(1)
                press(ser, 'B')
                time.sleep(7)
                continue
            
            # Reel the pokemon
            print('Reeling!')
            press(ser, 'A')
            timeout = 0

            while timeout < 60:
                frame = getframe(vid)
                current_text = extract_encounter_text(vid)
                # print(f'here and current text is {current_text}')
                timeout += 1
                pokemon = None
                if 'You encountered' in current_text:
                    time.sleep(0.1)
                    current_text = extract_encounter_text(vid)
                    pokemon = extract_pokemon_name(current_text)
                    break
                time.sleep(0.4)

                if timeout % 5 == 0:
                    current_text = get_text(frame=frame, top_left=Point(597, 273), bottom_right=Point(636, 752), invert=True)
                    if current_text == "You reeled your line in too slow!" or current_text == 'You reeled your line in too fast!':
                        bad_reel = True
                        break
            
            if (bad_reel):
                print('Reeled too slow or fast!')
                time.sleep(1)
                press(ser, 'B')
                time.sleep(7)
                continue
            timeout = 0

            # Wait for encounter text to go away, noting delay
            await_pixel(vid, x=x_val, y=y_val, pixel=(58, 58, 58))
            print(f'{pokemon} appeared!')
            await_not_pixel(vid, x=x_val, y=y_val, pixel=(58, 58, 58))
            log_frame = getframe(vid)
            t0 = time.time()

            await_pixel(vid, x=x_val, y=y_val, pixel=(58, 58, 58))
            t1 = time.time()

            delay = t1 - t0
            print(f'dialog delay: {delay:.3f}s')

            if (delay) > 0.5:
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
            while not numpy.array_equal(frame[669][1152], (255, 255, 255)):
                frame = getframe(vid)
                time.sleep(1)
            
            press(ser, 'w', sleep_time=.5)
            press(ser, 'A',  sleep_time= 6)

 
            end_time = time.time()
            print(f'Total runtime: {(end_time-start_time):.3f}s')
            start_time = time.time()
            time.sleep(7)
            # return 0

    vid.release()
    cv2.destroyAllWindows()
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
