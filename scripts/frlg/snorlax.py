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
import pytesseract
import re

from services.common import *

redis_client = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)
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

def increment_counter(pokemon_name, log_frame=None):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    stream_data_path = STREAM_DATA_PATH

    with stream_data_path.open("r") as stream_data_file:
        stream_data = json.load(stream_data_file)

    hunt_id = stream_data[f'switch{switch_num}_hunt_id']

    cursor.execute("SELECT * FROM hunt_encounters WHERE pokemon_name = ? AND hunt_id = ?", (pokemon_name, hunt_id,))
    pokemon_row = cursor.fetchone()
    if (log_frame is not None):
        cursor.execute("SELECT SUM(encounters) FROM catches WHERE name = ? AND hunt_id = ?", (pokemon_name, hunt_id,))
        result = cursor.fetchone()[0]
        previous_encounters = result if result is not None else 0
        count_difference = pokemon_row[3] - previous_encounters
        cursor.execute(
            "INSERT INTO catches (pokemon_id, caught_timestamp, encounters, encounter_method, switch, name, total_dens, hunt_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                pokemon_row[1],
                int(time.time() * 1000),
                count_difference,
                "oldwild",
                switch_num,
                pokemon_name,
                None,
                hunt_id
            )
        )

        cv2.imwrite(f"/Volumes/DexDrive/frlg/{pokemon_name}-{int(time.time() * 1000)}.png", log_frame)

    if pokemon_row:
        cursor.execute("""
            UPDATE pokemon
            SET total_encounters = total_encounters + 1
            WHERE name = ?
        """, (pokemon_name,))
        
        cursor.execute("""
                UPDATE hunt_encounters
                SET encounters = encounters + 1
                WHERE pokemon_name = ? AND hunt_id = ?
            """, (pokemon_name, hunt_id,))
    else:
        cursor.execute("""
            INSERT INTO tempmons (name, encounters, hunt_id)
            VALUES (?, 1, ?)
            ON CONFLICT(name) DO UPDATE SET
                encounters = encounters + 1
        """, (pokemon_name, hunt_id,))

    redis_client.publish(REDIS_CHANNEL, json.dumps({"update_data":True}))
    conn.commit()
    conn.close()

def check_if_shiny(vid: cv2.VideoCapture):
    frame = getframe(vid)
    # print(frame[272][352])
    if switch_num == 1:
        return not numpy.array_equal(frame[272][352], [60, 184, 125])
    if switch_num == 2:
        return not numpy.array_equal(frame[301][336], [0, 111, 195])
    if switch_num == 3:
        return not numpy.array_equal(frame[236][430], [41, 147, 255])

def reset_game(ser: serial.Serial):
    press(ser, 'ABXY', sleep_time=2)

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--switch_num')
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

            press(ser, 'A', count=13, sleep_time=0.5)
            press(ser, 'B', count=5, sleep_time=0.5)

            x_val = 608
            y_val = 382
            frame = getframe(vid)

            while not color_near(frame[y_val][x_val], (0, 0, 0)):
                frame = getframe(vid)
                press(ser, 'A', sleep_time=0.3)

            t0 = time.time()

            timeout = 0
            pokemon = None
            print('About to enter while statement in encounter check!')
            while True:
                frame = getframe(vid)
                current_text = extract_encounter_text(vid)
                # print(f'here and current text is {current_text}')
                timeout += 1
                if (timeout > 6000):
                    print('Returning from encounter check early!')
                    return
                if 'Wild' in current_text:
                    t1 = time.time()
                    time.sleep(0.1)
                    current_text = extract_encounter_text(vid)
                    pokemon = extract_pokemon_name(current_text).lower()
                    log_frame = getframe(vid)
                    print(f'{pokemon} appeared!')
                    break
                time.sleep(0.1)

            delay = t1 - t0
            print(f'dialog delay: {delay:.3f}s')
            
            if (delay) > 3.8:
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
                return 0

            increment_counter(pokemon_name=pokemon)

            end_time = time.time()
            print(f'Full encounter took {(end_time-start_time):.3f}s')
            # return 0

    vid.release()
    cv2.destroyAllWindows()
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
