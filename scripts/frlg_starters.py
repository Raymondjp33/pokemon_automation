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

from services.common import *

redis_client = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)
switch_num = 2

def increment_counter(shiny=False):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    stream_data_path = STREAM_DATA_PATH

    with stream_data_path.open("r") as stream_data_file:
        stream_data = json.load(stream_data_file)

    hunt_id = stream_data[get_switch_hunt_key(switch_num)]

    # Increment the counter
    pokemon = cursor.execute("SELECT * FROM hunt_encounters WHERE hunt_id = ?", (hunt_id,)).fetchone()
    pokemon_name = pokemon[4]

    if (shiny):
        cursor.execute("SELECT * FROM catches WHERE name = ? AND hunt_id = ?", (pokemon_name, hunt_id,))
        catch_rows = cursor.fetchall()
        catches = [{"caught_timestamp": ts, "encounters": enc, "encounter_method": method, "total_dens": tdens} for _, _, ts, enc, method, _, _, tdens, _ in catch_rows]
        previous_encounters = 0
        
        for catch in catches:
            previous_encounters = previous_encounters + catch["encounters"]

        count_difference = pokemon[3] - previous_encounters

        cursor.execute(
            "INSERT INTO catches (pokemon_id, caught_timestamp, encounters, encounter_method, switch, name, total_dens, hunt_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                pokemon[1],
                int(time.time() * 1000),
                count_difference,
                "oldwild",
                switch_num,
                pokemon_name,
                None,
                hunt_id
            )
        )

    
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

def check_if_shiny(vid: cv2.VideoCapture):
    frame = getframe(vid)
    # print(frame[272][352])
    if switch_num == 1:
        return not numpy.array_equal(frame[272][352], [60, 184, 125])
    if switch_num == 2:
        return not numpy.array_equal(frame[301][336], [0, 111, 195])
    if switch_num == 3:
        return not numpy.array_equal(frame[236][430], [41, 147, 255])

def reset_game(ser: serial.Serial, sleep_time = 4):
    press(ser, 'H', sleep_time=1.25)
    press(ser, 'X', sleep_time=1)
    press(ser, 'A', sleep_time=1.75)
    press(ser, 'A', count=3, sleep_time=.75)

    if (switch_num == 3):
        sleep_time = 7
    time.sleep(sleep_time)


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
        # print(check_if_shiny(vid))
        # reset_game(ser)
        # press(ser, 'A', count=10, sleep_time=0.5)
        # press(ser, 'B', count=4, sleep_time=0.5)
        # press(ser, 'A', count=10, sleep_time=0.5)
        # press(ser, 'B', count=16, sleep_time=0.5)
        # press(ser, 'X', sleep_time=0.75)
        # press(ser, 'A', sleep_time=1.25)
        # press(ser, 'A', count=2, sleep_time=0.5)
        # time.sleep(2)
        # print(check_if_shiny(vid))
        # return
        while True:
            start_time = time.time()
            reset_game(ser)
            press(ser, 'A', count=10, sleep_time=0.5)
            press(ser, 'B', count=4, sleep_time=0.5)
            press(ser, 'A', count=10, sleep_time=0.5)
            press(ser, 'B', count=20, sleep_time=0.5)
            press(ser, 'X', sleep_time=0.75)
            press(ser, 'A', sleep_time=1.25)
            press(ser, 'A', count=2, sleep_time=0.5)
            time.sleep(2)
            
            if (check_if_shiny(vid)):
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
                increment_counter(shiny=True,)
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
