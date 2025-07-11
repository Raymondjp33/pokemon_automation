from __future__ import annotations

from pathlib import Path
import time

import cv2
import serial

import json
import sqlite3
import redis

from services.common import *
from services.config_manager import ConfigManager

redis_client = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)

def write_shiny_text():
    shiny_text_path = SWITCH1_SHINY_TEXT_PATH
    with shiny_text_path.open("w") as file1:
        file1.write("I got the target amount of\nshinies! My switch will be\noff until I'm back.")

def increment_counter(caught_index=None):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    counter_path = Path(__file__).resolve().parent / 'configs' / 'switch1-counter.txt' 
    stream_data_path = Path(__file__).resolve().parent.parent / 'backend' / 'stream_data.json'
    
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
    count += 5

    with stream_data_path.open("r") as stream_data_file:
        stream_data = json.load(stream_data_file)

    pokemon_name = stream_data['switch1_targets'][0]["name"]
    pokemon_target = stream_data['switch1_targets'][0]["target"]

    target_met = False
    if (caught_index is not None):
        cursor.execute("SELECT * FROM pokemon WHERE name = ?", (pokemon_name,))
        pokemon_row = cursor.fetchone()
        cursor.execute("SELECT * FROM catches WHERE name = ?", (pokemon_name,))
        catch_rows = cursor.fetchall()
        catches = [{"caught_timestamp": ts, "encounters": enc, "encounter_method": method, "total_dens": tdens} for _, _, ts, enc, method, _, _, tdens in catch_rows]
        previous_encounters = 0

        for catch in catches:
            previous_encounters = previous_encounters + catch["encounters"]
        count_difference = pokemon_row[2] - previous_encounters - (4 - caught_index)

        cursor.execute(
            "INSERT INTO catches (pokemon_id, caught_timestamp, encounters, encounter_method, switch, name, total_dens) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                pokemon_row[0],
                int(time.time() * 1000),
                count_difference,
                "egg",
                1,
                pokemon_name,
                None
            )
        )
        
        if len(catches) + 1 >= pokemon_target:
            target_met = True
    else:
        cursor.execute("""
            UPDATE pokemon
            SET encounters_total = encounters_total + 5
            WHERE name = ?
        """, (pokemon_name,))

    with counter_path.open("w") as file1:
        file1.write(str(count))
    
    redis_client.publish(REDIS_CHANNEL, json.dumps({"update_data":True}))
    conn.commit()
    conn.close()

    return target_met

def handle_fetch(ser: serial.Serial, vid: cv2.VideoCapture, refuse_egg = False):
    press(ser, 's', duration=0.75, sleep_time=0.2)
    press(ser, 'a', duration=0.75, sleep_time=0.2)
    press(ser, 'd', duration=0.65, sleep_time=0.2)
    press(ser, 'w', duration=0.40, sleep_time=0.2)
    time.sleep(0.5)
    press(ser, 'A', sleep_time=1)

    # Now stading in front of worker and talking to him
    frame = getframe(vid)
    oh_text = get_text(frame=frame, top_left=Point(y=583, x=292), bottom_right=Point(y=634, x=382), invert=True) == 'Oh?'

    if (oh_text):
        handle_hatch(ser, vid)
        return
    
    handle_return_from_fetch(ser, vid, refuse_egg=refuse_egg)

def handle_return_from_fetch(ser: serial.Serial, vid: cv2.VideoCapture, refuse_egg = False):
    frame = getframe(vid)
    current_text = get_text(frame=frame, top_left=Point(y=586, x=472), bottom_right=Point(y=635, x=612), invert=True)
    
    if current_text == 'Good to':
        print('Good to see you!')
        press(ser, 'A', count=3, sleep_time=1)
    elif current_text == 'We were' and not refuse_egg:
        fetched_eggs = config.get('fetched_eggs')
        config.update({'fetched_eggs': fetched_eggs + 1})
        print(f'We were! Fetching egg {fetched_eggs}')
        press(ser, 'A' , count=17, sleep_time=0.4)
    elif current_text == 'We were' and refuse_egg:
        print('Refusing egg')
        press(ser, 'B' , count=8, sleep_time=1.5)
    else:
        return

    press(ser, 's', duration=1)
    press(ser, 'a', duration=1)

def handle_hatch(ser: serial.Serial, vid: cv2.VideoCapture,):
    
    hatched_eggs = config.get('hatched_eggs')
    config.update({'hatched_eggs': hatched_eggs + 1})
   
    print(f'Hatching egg {hatched_eggs}')
    press(ser, 'A', count=3, sleep_time=1)

    time.sleep(13)
    press(ser, 'A', count=3, sleep_time=1)


    time.sleep(3)
    print(f'Done hatching')
    press(ser, 's', duration=1)
    press(ser, 'a', duration=1)

def handle_process_eggs(ser: serial.Serial, vid: cv2.VideoCapture,):
    print('Processing eggs!')
    increment_counter(caught_index=None)
    config.update({'fetched_eggs': 0, 'hatched_eggs': 0})
    press(ser, 'X', sleep_time=1.5)
    press(ser, 'A', sleep_time=1.5)
    press(ser, 'R', sleep_time=2)

    press(ser, 'a', sleep_time=.5)

    line_count = 5

    target_met = False
    # Check for any shiny
    for x in range(5):
        press(ser, 's', sleep_time=.75)
        is_shiny = check_if_shiny(vid)
        if (is_shiny):
            open_slot = config.get('open_slot')
            boxes_to_move = 1 + int((open_slot - 1) / 30)
            print(f'We have a shiny at index {x}!')
            target_met = increment_counter(caught_index=x)
            line_count = line_count - 1
            # Pick shiny up 
            print('Picking shiny up')
            press(ser, 'A', sleep_time=0.75, count=2)
            time.sleep(1)
            # Put in open spot
            print('Putting in open spot')
            press(ser, 'w', count = x + 1, sleep_time=0.5)
            press(ser, 'd', sleep_time=0.5)
            press(ser, 'L', sleep_time=2, count=boxes_to_move)
            move_location = get_location(open_slot)
            config.update({'open_slot': config.get('open_slot') + 1})

            make_move(ser, from_pos=0, to_pos=move_location.row, move_vertical=True)
            make_move(ser, from_pos=0, to_pos=move_location.col, move_vertical=False)
            press(ser, 'A', sleep_time=1.5)

            # Come back
            make_move(ser, from_pos=move_location.row, to_pos=0, move_vertical=True)
            make_move(ser, from_pos=move_location.col, to_pos=0, move_vertical=False)
            press(ser, 'a', sleep_time=0.5)
            press(ser, 's', count = x, sleep_time=0.5)
            press(ser, 'R', sleep_time=2, count=boxes_to_move)
        else:   
            print(f'Pokemon at index {x} is not shiny')

    press(ser, 'w', count=line_count - 1, sleep_time=0.25)

    # Delete all non shiny
    for _ in range(line_count):
        press(ser, 'A', sleep_time=.75)
        press(ser, 'w', count=2, sleep_time=0.25)
        press(ser, 'A', sleep_time=.75)
        press(ser, 'w', sleep_time=0.25)
        press(ser, 'A', count=2, sleep_time=.75)

    # Bring over next batch
    press(ser, 'd', sleep_time=.5)
    press(ser, 'w', sleep_time=.5)
    press(ser, 'Y', count=2, sleep_time=0.25)
    press(ser, 'A', sleep_time=0.3)
    press(ser, 's', count=4, sleep_time=0.25)
    press(ser, 'A', sleep_time=0.3)
    press(ser, 'a', sleep_time=0.3)
    press(ser, 's', sleep_time=0.3)
    press(ser, 'A', sleep_time=.5)

    print('Exiting eggs')
    press(ser, 'B', count=3, sleep_time=3)
    time.sleep(1)
    press(ser, 's', duration=1)
    press(ser, 'a', duration=1)

    return target_met

def check_if_shiny(vid: cv2.VideoCapture):
    frame = getframe(vid)

    y1, x1, y2, x2 = 112, 1185, 151, 1253
    roi = frame[y1:y2, x1:x2]
    target_color = (64, 63, 255)

    found = any(color_near(pixel, target_color) for row in roi for pixel in row)

    if found:
        return True
    
    return False

def handle_target_met(ser: serial.Serial, vid: cv2.VideoCapture,):

    next_pokemon = config.get('next_pokemon', default=[])
    if len(next_pokemon) == 0:
        print('No new target, aborting!')
        return True
    
    new_target = next_pokemon[0]

    # Get rid of last egg so that new pokemon can be given
    handle_fetch(ser, vid, refuse_egg=True)

    # Get into the nursery and talk to lady
    press(ser, 'd', duration=0.45)
    press(ser, 'w', duration=1)
    time.sleep(3.5)
    press(ser, 'w', duration=1, sleep_time=0.5)
    press(ser, 'A', sleep_time=1.5)

    frame = getframe(vid)
    current_text = get_text(frame=frame, top_left=Point(y=585, x=733), bottom_right=Point(y=637, x=907), invert=True)
    if current_text != 'Now, about':
        print('Unknown location, aborting!')
        return True
    
    # Take back pokemon
    press(ser, 'A', count=3, sleep_time=0.7)
    press(ser, 's', sleep_time=0.7)
    press(ser, 'A', sleep_time=1)
    press(ser, 'B', count=11, sleep_time=0.5)

    # Put old pokemon in correct box spot
    press(ser, 'X', sleep_time=1.5)
    press(ser, 'A', sleep_time=1.5)
    press(ser, 'R', sleep_time=2)
    press(ser, 'A', count=2, sleep_time=1)
    press(ser, 'R', count=2, sleep_time=2)

    move_location = get_location(config.get('take_back_slot'))
    config.update({'take_back_slot': config.get('take_back_slot') + 1})
    make_move(ser, from_pos=0, to_pos=move_location.row, move_vertical=True)
    make_move(ser, from_pos=0, to_pos=move_location.col, move_vertical=False)

    press(ser, 'A', sleep_time=2)
    press(ser, 'B', count=3, sleep_time=3)
    time.sleep(1)

    # Give new pokemon
    print('Giving new pokemon')
    press(ser, 'A', count=5, sleep_time=1)
    time.sleep(2)

    move_location = get_location(new_target['slot'])
    make_move(ser, from_pos=0, to_pos=move_location.row, move_vertical=True)
    make_move(ser, from_pos=0, to_pos=move_location.col, move_vertical=False)

    press(ser, 'A', count=5, sleep_time=1.5)
    press(ser, 'B', count=3, sleep_time=0.5)

    press(ser, 'X', sleep_time=1.5)
    press(ser, 'A', sleep_time=1.5)
    press(ser, 'R', sleep_time=2)
    press(ser, 'L', count=2, sleep_time=2)
    press(ser, 'B', count=3, sleep_time=3)

    # Leave nursery, get on bike
    press(ser, 's', duration=1)
    time.sleep(4)
    press(ser, '+', sleep_time=1)
    press(ser, 'd', sleep_time=1)
    press(ser, 's', duration=1)
    press(ser, 'a', duration=1)
    return False
    
def handle_update_target():
    next_pokemon = config.get('next_pokemon', default=[])
    if len(next_pokemon) == 0:
        print('No new target, aborting!')
        return
    
    new_target = next_pokemon[0]
    next_pokemon.remove(new_target)

    config.update({'next_pokemon': next_pokemon})

    switch1_targets = [{ "name": new_target['name'], "target": new_target['target'], "dexNum": new_target['dexNum'] }]
    with open(STREAM_DATA_PATH, 'r') as f:
        data = json.load(f)
    data['switch1_targets'] = switch1_targets
    with open(STREAM_DATA_PATH, 'w') as f:
        json.dump(data, f, indent=4)

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT 1 FROM pokemon WHERE name = ?", (new_target['name'],))
    if cursor.fetchone() is None:
        cursor.execute(
        "INSERT INTO pokemon (name, encounters_total, started_hunt_ts) VALUES (?, ?, ?)",
        (new_target['name'], 0, int(time.time() * 1000))
        )

    redis_client.publish(REDIS_CHANNEL, json.dumps({"update_data":True}))
    conn.commit()
    conn.close()

config = ConfigManager(Path(__file__).resolve().parent / 'configs' / 'egg_data1.json')

def main() -> int:
    ser_str = SWITCH1_SERIAL
    vid = make_vid(SWITCH1_VID_NUM)


    start_time = time.time()
    with serial.Serial(ser_str, 9600) as ser, shh(ser):
        time.sleep(1)
        # handle_process_eggs(ser, vid)
        # print(check_if_shiny(vid))
        # handle_target_met(ser, vid)
        # return 0
        while True:

            # Handle movement while checking for egg hatch
            for _ in range (14):
                frame = getframe(vid)
                oh_text = get_text(frame=frame, top_left=Point(y=583, x=292), bottom_right=Point(y=634, x=382), invert=True) == 'Oh?'
                if (oh_text):
                    handle_hatch(ser, vid)
                    break
                press(ser, 'q', duration=0.27, write_null_byte=False)
                press(ser, 'e', duration=0.1, write_null_byte=False)
                press(ser, 'c', duration=0.25, write_null_byte=False)
                press(ser, 'z', duration=0.12, write_null_byte=False)

            handle_return_from_fetch(ser, vid)
          
            # If we havent fetched enough, continue fetching
            if (config.get('fetched_eggs') < 5):
                handle_fetch(ser, vid)

            if (config.get('fetched_eggs') > 4 and config.get('hatched_eggs') < 5):
                continue

            if (config.get('fetched_eggs') > 4 and config.get('hatched_eggs') > 4):
                ser.write(b'0')
                time.sleep(0.5)

                target_met = handle_process_eggs(ser, vid)
                end_program = False

                if config.get('target_updated'):
                    handle_update_target()
                    config.update({'target_updated': False})

                if target_met:
                    end_program = handle_target_met(ser, vid)

                if target_met and not end_program:
                    config.update({'target_updated': True})

                if end_program:
                    # We have reached our target for the current pokemon
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
                    write_shiny_text()
                    return 0

                end_time = time.time()
                print(f'Full egg run took {(end_time-start_time):.3f}s')
                start_time = time.time()
                time.sleep(2)

            
            

            # return 0

    vid.release()
    cv2.destroyAllWindows()
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
