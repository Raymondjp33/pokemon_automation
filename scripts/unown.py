from __future__ import annotations

import argparse
from pathlib import Path
import time
import cv2
import serial
import json
import sqlite3
import redis

from services.common import *

redis_client = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)

def increment_counter(frame=None):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    stream_data_path = STREAM_DATA_PATH

    with stream_data_path.open("r") as stream_data_file:
        stream_data = json.load(stream_data_file)

    hunt_id = stream_data['switch1_hunt_id']

    # Increment the counter
    pokemon = cursor.execute("SELECT * FROM hunt_encounters WHERE hunt_id = ?", (hunt_id,)).fetchone()
    pokemon_name = pokemon[4]

    if (frame is not None):
        cursor.execute("SELECT * FROM pokemon WHERE name = ?", (pokemon_name,))
        pokemon_row = cursor.fetchone()
        cursor.execute("SELECT * FROM catches WHERE name = ?", (pokemon_name,))
        catch_rows = cursor.fetchall()
        catches = [{"caught_timestamp": ts, "encounters": enc, "encounter_method": method, "total_dens": tdens} for _, _, ts, enc, method, _, _, tdens, _ in catch_rows]
        previous_encounters = 0
        
        for catch in catches:
            previous_encounters = previous_encounters + catch["encounters"]

        count_difference = pokemon_row[2] - previous_encounters

        cursor.execute(
            "INSERT INTO catches (pokemon_id, caught_timestamp, encounters, encounter_method, switch, name, total_dens, hunt_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                pokemon[1],
                int(time.time() * 1000),
                count_difference,
                "static",
                1,
                pokemon_name,
                None,
                hunt_id
            )
        )

        cv2.imwrite(f"/Volumes/DexDrive/poke screenshots/Unown - {time.time()}.png", frame)
    
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
    
    redis_client.publish(REDIS_CHANNEL, json.dumps({"update_data":True}))
    conn.commit()
    conn.close()

      
def write_shiny_text():
    shiny_text_path = SWITCH1_SHINY_TEXT_PATH
    with shiny_text_path.open("w") as file1:
        file1.write('I got the shiny! My switch\nwill be off until I am\nback. Make sure to come\nback when/after I catch it!')


def handle_encounter(vid: cv2.VideoCapture, ser: serial.Serial):
    timeout = 0
    x_val = 960
    y_val = 660

    while timeout < 60:
        frame = getframe(vid)
        current_text = get_text(frame=frame, top_left=Point(y=584, x=115), bottom_right=Point(y=642, x=590), invert=True)
        # print(f'here and current text is ${current_text}')
        if (current_text == 'You encountered a wild Unown!'):
            print('Wild Unown!')
            break
        time.sleep(0.4)

    await_not_pixel(vid, x=x_val, y=y_val, pixel=(255, 255, 255))
    log_frame = getframe(vid)
    print(f'Unown pixel gone') 
    t0 = time.time()

    await_pixel(vid, x=x_val, y=y_val, pixel=(255, 255, 255))
    print('Go Breloom!')
    t1 = time.time()

    delay = t1 - t0
    print(f'dialog delay: {delay:.3f}s')

    if ((delay) > 0.7):
        return (True ,log_frame)
    
    # Wait until we can run
    await_pixel(vid, x=1111, y=672, pixel=(238, 127, 115))
    time.sleep(0.5)

    print('Running')
    press(ser, 'w', sleep_time=0.3)
    press(ser, 'A', sleep_time=0.3)

    await_pixel(vid, x=x_val, y=y_val, pixel=(255, 255, 255))
    await_not_pixel(vid, x=x_val, y=y_val, pixel=(255, 255, 255))

    time.sleep(2)
    print('Exited battle')

    return (False, log_frame)

def main() -> int:
    ser_str = SWITCH1_SERIAL
    vid = make_vid(SWITCH1_VID_NUM)

    start_time = time.time()
  
    with serial.Serial(ser_str, 9600) as ser, shh(ser):
        time.sleep(1)
        while True:
            start_time = time.time()

            # encountering = False
            # going_left = False

            # while not encountering:
            #     press(ser, 'a' if going_left else 'd', duration=0.3)
            #     going_left = not going_left
            #     frame = getframe(vid)
            #     if (_color_near(frame[660][960], (255, 255, 255))):
            #         print('Encounter starting!')
            #         encountering = True

            press(ser, 'X', sleep_time=0.75)
            press(ser, 'A', sleep_time=1)
            press(ser, 'A', sleep_time=0.5)
            press(ser, 's')
            press(ser, 'A')
            
            shiny_encounter = handle_encounter(vid, ser)
            if (shiny_encounter[0]):
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
                increment_counter(frame=shiny_encounter[1],)
                write_shiny_text()
                return 0

            increment_counter()

            time.sleep(1) 
            end_time = time.time()
            print(f'Full encounter took {(end_time-start_time):.3f}s')
            # return 0

    vid.release()
    cv2.destroyAllWindows()
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
