from __future__ import annotations

from pathlib import Path
import time
import sys
import math

import cv2
import serial

import json
import redis
import sqlite3

from services.common import *
from services.config_manager import ConfigManager

redis_client = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)
config = ConfigManager(Path(__file__).resolve().parent / 'configs' / 'sv_egg_data.json')

def write_shiny_text():
    shiny_text_path = SWITCH2_SHINY_TEXT_PATH
    with shiny_text_path.open("w") as file1:
        file1.write("I got the target amount of\nshinies! My switch will be\noff until I'm back.")

def increment_counter(caught_index=None):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    stream_data_path = Path(__file__).resolve().parent.parent / 'backend' / 'stream_data.json'    

    with stream_data_path.open("r") as stream_data_file:
        stream_data = json.load(stream_data_file)

    hunt_id = stream_data['switch2_hunt_id']

    pokemon = cursor.execute("SELECT * FROM hunt_encounters WHERE hunt_id = ?", (hunt_id,)).fetchone()

    pokemon_name = pokemon[4]

    target_met = False
    if (caught_index is not None):
        cursor.execute("SELECT * FROM catches WHERE name = ?", (pokemon_name,))
        catch_rows = cursor.fetchall()
        catches = [{"caught_timestamp": ts, "encounters": enc, "encounter_method": method, "total_dens": tdens} for _, _, ts, enc, method, _, _, tdens, _ in catch_rows]
        previous_encounters = 0

        for catch in catches:
            previous_encounters = previous_encounters + catch["encounters"]
        count_difference = pokemon[3] - previous_encounters - (4 - caught_index)

        cursor.execute(
            "INSERT INTO catches (pokemon_id, caught_timestamp, encounters, encounter_method, switch, name, total_dens, hunt_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                pokemon[1],
                int(time.time() * 1000),
                count_difference,
                "egg",
                2,
                pokemon_name,
                None,
                hunt_id
            )
        )
        
        if len(catches) + 1 >= pokemon[6]:
            target_met = True
    else:
        cursor.execute("""
            UPDATE pokemon
            SET total_encounters = total_encounters + 5
            WHERE name = ?
        """, (pokemon_name,))

        cursor.execute("""
            UPDATE hunt_encounters
            SET encounters = encounters + 5
            WHERE pokemon_name = ? AND hunt_id = ?
        """, (pokemon_name, hunt_id,))


    
    redis_client.publish(REDIS_CHANNEL, json.dumps({"update_data":True}))
    conn.commit()
    conn.close()

    return target_met

def oh_text_showing(vid: cv2.VideoCapture):
    frame = getframe(vid)
    return get_text(frame=frame, top_left=Point(y=543, x=345), bottom_right=Point(y=593, x=438), invert=True) == 'Oh?'

def handle_process_eggs(ser: serial.Serial, vid: cv2.VideoCapture,):
    print('Processing eggs!')
    increment_counter(caught_index=None)

    press(ser, 'a', sleep_time=.5)

    line_count = 5

    target_met = False
    any_shiny = False
    # Check for any shiny
    for x in range(5):
        press(ser, 's', sleep_time=.75)
        is_shiny = check_if_shiny(vid)
        if (is_shiny):
            any_shiny = True
            open_slot = config.get('open_slot')
            boxes_to_move = 2 + int((open_slot - 1) / 30)
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
            press(ser, 'R', sleep_time=2, count=boxes_to_move)
            press(ser, 'a', sleep_time=0.5)
            press(ser, 's', count = x, sleep_time=0.5)
        else:   
            print(f'Pokemon at index {x} is not shiny')

    press(ser, 'w', count=line_count - 1, sleep_time=0.25)
    time.sleep(0.5)

    # Delete all non shiny
    for _ in range(line_count):
        delete_current_pokemon(ser)
    
    press(ser, 'd')
    press(ser, 'w')

    if target_met:
        config.update({'target_met': True})

    return any_shiny

def check_if_shiny(vid: cv2.VideoCapture):
    frame = getframe(vid)

    y1, x1, y2, x2 = 74, 1134, 83, 1142
    roi = frame[y1:y2, x1:x2]
    target_color = (252, 252, 252)

    found = any(color_near(pixel, target_color) for row in roi for pixel in row)

    if found:
        return True
    
    return False

def handle_update_hunt(ser: serial.Serial,  vid: cv2.VideoCapture):
    next_pokemon = config.get('next_pokemon', default=[])
    if len(next_pokemon) == 0:
        print('No new target, aborting!')
        return True
    
    new_target = next_pokemon[0]
    next_pokemon.remove(new_target)
    config.update({'next_pokemon': next_pokemon, 'target_met': False})

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    new_hunt_id = cursor.execute("SELECT MAX(hunt_id) FROM hunt_encounters").fetchone()[0] + 1
    pokemon = cursor.execute("SELECT * FROM pokemon WHERE name = ?", (new_target['name'],)).fetchone()

    cursor.execute(
    "INSERT INTO hunt_encounters (pokemon_id, hunt_id, encounters, pokemon_name, switch, targets, started_hunt_ts, encounter_method, total_dens) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
    (pokemon[0], new_hunt_id, 0, new_target['name'], 2, new_target['target'], int(time.time() * 1000), 'egg', None)
    )

    with open(STREAM_DATA_PATH, 'r') as f:
        data = json.load(f)
    data['switch2_hunt_id'] = new_hunt_id
    with open(STREAM_DATA_PATH, 'w') as f:
        json.dump(data, f, indent=4)

    redis_client.publish(REDIS_CHANNEL, json.dumps({"update_data":True}))
    conn.commit()
    conn.close()

    next_pos = get_location(new_target['slot'])
    starting_pos = Position(col=1,row=0)

    move_position(ser, starting_pos, next_pos)
    press(ser, 'Y', sleep_time=0.5)
    move_position(ser, next_pos, starting_pos)
    press(ser, 'A', sleep_time=0.5)

# Handles from the "Oh?" text through full hatch of egg
def hatch_egg(ser: serial.Serial):
    config.update({'hatched_eggs': config.get('hatched_eggs') + 1})
    press(ser, 'A', count=3)
    time.sleep(14)
    press(ser, 'A', count=2)
    time.sleep(4)
    print('Egg Hatched!')

def delete_current_pokemon(ser: serial.Serial):
    press(ser, 'A', sleep_time=0.7)
    press(ser, 'w', count=2)
    time.sleep(0.3)
    press(ser, 'A', sleep_time=0.7)
    press(ser, 'w', sleep_time=0.7)
    press(ser, 'A', sleep_time=1.2)
    press(ser, 'A', sleep_time=.7)

# Against picnic table, goes into menu, ends once out of sandwich ui
def make_sandwich(ser: serial.Serial):
    # Open sandwich menu
    press(ser, 'A', sleep_time= 1.5)
    press(ser, 'A', sleep_time= 6)

    # Select egg 2 sandwich
    press(ser, 'd')
    press(ser, 's', count=2)
    press(ser, 'A', count=4)
    time.sleep(9)

    # Put banana pieces on sandwich
    for _ in range(3):
        press(ser, 'w', duration=.5, sleep_time=.3)
        press(ser, '@', duration=.5, sleep_time=.3)

    # Put pick down and get through first animation
    press(ser, 'A', count=8, sleep_time=0.5)
    time.sleep(7)
    press(ser, 'A', count=2, sleep_time=.5)

    time.sleep(25)

    ## Eat sandwich, should be looking at picnic table
    press(ser, 'A', sleep_time=.5)
    time.sleep(2)

def select_menu_item(ser: serial.Serial, vid: cv2.VideoCapture, menu_item: str):
    press(ser, 'X', sleep_time=1)
    frame = getframe(vid)
    current_menu_item = None

    selected_color = (0, 204, 240)

    # Make sure we are on the right side of the menu
    press(ser, 'd', sleep_time=.5)

    if color_near(frame[240][1077], selected_color):
        current_menu_item = 'Boxes'

    if color_near(frame[301][1077], selected_color):
        current_menu_item = 'Picnic'


    if current_menu_item == None:
        while not color_near(frame[240][1077], selected_color):
            press(ser, 's', sleep_time=.5)
            frame = getframe(vid)
        current_menu_item = 'Boxes'

    if menu_item == current_menu_item:
        press(ser, 'A', sleep_time=2)
        print('')
    elif current_menu_item == "Boxes":
        press(ser, 's')
        press(ser, 'A', sleep_time=2)
    else:
        press(ser, 'w')
        press(ser, 'A', sleep_time=2)

    print(f'Entering {menu_item}')

def take_basket_eggs(ser: serial.Serial, vid: cv2.VideoCapture):
        # Get in front of basket
        press(ser, 'a', duration=0.4, sleep_time=0.5)
        press(ser, 'w', duration=0.6, sleep_time=0.5)
        press(ser, 'd', duration=0.4, sleep_time=0.5)
        press(ser, 's')

        fetched_eggs = config.get('fetched_eggs')
        while (fetched_eggs < 30):
            time.sleep(20)

            taking_eggs = True
            print("Checking basket")
            press(ser, 'A', count=2, sleep_time=.75)
            while taking_eggs:
                time.sleep(0.5)
                

                current_text = get_text(frame=getframe(vid), top_left=Point(y=543, x=358), bottom_right=Point(y=592, x=558), invert=True)
                if current_text == 'Doesn’t look like':
                    print('No egg')
                    press(ser, 'A')
                    taking_eggs = False
                    continue
                elif current_text == 'There’s a Pokéme':
                    print('Taking egg')
                    press(ser, 'A', count=3, sleep_time=0.5)
                    config.update({'fetched_eggs': fetched_eggs + 1})
                elif current_text == '..Qh? There’s sor':
                    print('Taking egg')
                    press(ser, 'A', count=4, sleep_time=0.5)
                    config.update({'fetched_eggs': fetched_eggs + 1})
                
                fetched_eggs = config.get('fetched_eggs')
        # Exit picnic
        time.sleep(1)
        press(ser, 'Y', sleep_time=1.5)
        press(ser, 'A', sleep_time=4, count=2)

def prepare_party(ser: serial.Serial,  vid: cv2.VideoCapture, breeding: bool = False):

    select_menu_item(ser, vid, "Boxes")
    time.sleep(2)

    press(ser, 'L', sleep_time=1.5)

    # Swap ditto and coalossal
    press(ser, 'Y', sleep_time=0.3)
    press(ser, 'a', sleep_time=.5)
    press(ser, 'A', sleep_time=0.5)

    # Either put away or move breeding pokemon respectively
    if breeding:
        press(ser, 'd', count=2, sleep_time=0.3)

        if config.get('target_met'):
            if handle_update_hunt(ser, vid):
                return True

        press(ser, 'Y', sleep_time=0.5)
        press(ser, 'a', count=2, sleep_time=0.3)
        press(ser, 's', sleep_time=0.3)
        press(ser, 'A', sleep_time=0.5)
        press(ser, 'R', sleep_time=1.5)
    else:
        press(ser, 's', sleep_time=0.3)
        press(ser, 'Y', sleep_time=0.5)
        press(ser, 'd', count=2, sleep_time=0.3)
        press(ser, 'w', sleep_time=0.3)
        press(ser, 'A', sleep_time=0.5)
        press(ser, 'a', sleep_time=0.5)
        press(ser, 'R', sleep_time=1.5)
        move_eggs_to_party(ser, vid)

    
    press(ser, 'B', sleep_time=3)
    press(ser, 'B', sleep_time=1)

def move_eggs_to_party(ser: serial.Serial,  vid: cv2.VideoCapture,):
    columns_to_move = int(math.floor(config.get("hatched_eggs", 0) / 5))

    if columns_to_move > 5:
        return

    press(ser, 'd', count=columns_to_move)
    time.sleep(0.5)
    press(ser, '-', sleep_time=0.5)
    press(ser, 's', count=4)
    press(ser, 'A', sleep_time=0.5)
    press(ser, 'a', sleep_time=0.5, count=columns_to_move + 1)
    press(ser, 's', sleep_time=0.5)
    press(ser, 'A', sleep_time=1)

def hatch_eggs(ser: serial.Serial,  vid: cv2.VideoCapture,):
    total_hatched = config.get('hatched_eggs')
    party_hatched = total_hatched % 5
    forward = True

    toggle_riding(ser, vid, get_off=False)

    while total_hatched < 30:
        while party_hatched < 5:
            if (oh_text_showing(vid)):
                print(f'Hatching egg {party_hatched}')
                party_hatched = party_hatched + 1
                hatch_egg(ser)
                forward = False
            
            if (party_hatched >= 5):
                break

            # press(ser, '{', duration=0.03, write_null_byte=False)
            # press(ser, 'q', duration=0.5, write_null_byte=False)
            # press(ser, 'w', duration=0.5, write_null_byte=False)
            # press(ser, 'e', duration=0.5, write_null_byte=False)
            # press(ser, 'd', duration=0.5, write_null_byte=False)
            # press(ser, 'c', duration=0.5, write_null_byte=False)
            # press(ser, 's', duration=0.5, write_null_byte=False)
            # press(ser, 'z', duration=0.5, write_null_byte=False)
            # press(ser, 'a', duration=0.5, write_null_byte=False)
            
                
            press(ser, 's' if not forward else 'w', duration=.5, write_null_byte=False)
            press(ser, '{', duration=0.03, write_null_byte=False)
            press(ser, 's' if not forward else 'w', duration=2)
            forward = not forward
        
        reset_position(ser, vid)
        time.sleep(1)
        select_menu_item(ser, vid, 'Boxes')
        save_needed = handle_process_eggs(ser, vid)
        move_eggs_to_party(ser, vid)
        press(ser, 'B', sleep_time=3)

        if save_needed:
            press(ser, 'R', sleep_time=1.5)
            press(ser, 'A', sleep_time=3)
            press(ser, 'B', sleep_time=1)

        press(ser, 'B', sleep_time=1)
        
        total_hatched = config.get('hatched_eggs')
        party_hatched = total_hatched % 5
    
    config.update({'fetched_eggs': 0, 'hatched_eggs': 0})
    toggle_riding(ser, vid, get_off=True)

def map_on_zero(vid: cv2.VideoCapture,):
    frame = getframe(vid)
    if get_text(frame=frame, top_left=Point(y=249, x=585), bottom_right=Point(y=286, x=699), invert=True) == 'Zero Gate':
        return 1
    elif get_text(frame=frame, top_left=Point(y=395, x=718), bottom_right=Point(y=433, x=779), invert=True) == 'here':
        return 2
    
    return 0

def reset_position(ser: serial.Serial, vid: cv2.VideoCapture,):
    # Open map
    press(ser, 'Y', sleep_time=2.5)

    # Try to get over the area zero gate fast travel
    ready_to_travel = False
    press(ser, 'c', sleep_time=1)
    if map_on_zero(vid) == 1:
        print("Got to zero moving with 'c'")
        ready_to_travel = True
        press(ser, 'A', sleep_time=1)
    
    if not ready_to_travel:
        press(ser, '+', sleep_time=1)
        press(ser, 's', sleep_time=1)

        if map_on_zero(vid) == 1:
            print("Got to zero moving with 's'")
            ready_to_travel = True
            press(ser, 'A', sleep_time=1)

    if not ready_to_travel:
        press(ser, '+', sleep_time=1)
        press(ser, 'A', sleep_time=1)
        print("Already on zero")

        if map_on_zero(vid) != 2:
            end_program(ser, failure=True)

    # At this point we should be looking at "Fly Here"
    press(ser, 'A', sleep_time=1.5, count=2)
    time.sleep(5)

    press(ser, '+', sleep_time=1)
    press(ser, 'L', sleep_time=0.5)
    press(ser, 'e', sleep_time=0.5)
    press(ser, 'L', sleep_time=0.5)
    press(ser, 'w', duration=3.5)
    press(ser, 'd', duration=2.2)
    press(ser, 'a', duration=0.3)
    press(ser, 'L', sleep_time=0.5)

def toggle_riding(ser: serial.Serial,  vid: cv2.VideoCapture, get_off: bool = False):
    press(ser, 'X', sleep_time=1)
    current_text = get_text(frame=getframe(vid), top_left=Point(y=677, x=152), bottom_right=Point(y=713, x=239), invert=True)

    if current_text == 'Get On' and not get_off:
        print('Getting on Miraidon')
        press(ser, '+', sleep_time=3)
    elif current_text == 'Get Off' and get_off:
        print('Getting off Miraidon')
        press(ser, '+', sleep_time=3)
    else:
        press(ser, 'B', sleep_time=1)

def end_program(ser: serial.Serial, failure: bool = False):
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
    if not failure:
        write_shiny_text()
    else:
        sys.exit(1)

def main() -> int:
    ser_str = SWITCH2_SERIAL
    vid = make_vid(SWITCH2_VID_NUM)

    start_time = time.time()
    # current_text = get_text(frame=getframe(vid), top_left=Point(y=543, x=358), bottom_right=Point(y=592, x=558), invert=True)

    # print(current_text)
    # return

    with serial.Serial(ser_str, 9600) as ser, shh(ser):
        time.sleep(2)
        # toggle_riding(ser, vid, get_off=True)
        # prepare_party(ser, vid)
        # handle_update_hunt(ser, vid)
        # handle_process_eggs(ser, vid)
        # delete_current_pokemon(ser)
        # move_eggs_to_party(ser, vid)
        # hatch_eggs(ser, vid)
        # handle_process_eggs(ser, vid)
        # return
    
        while True:
            
            reset_position(ser, vid)
            # Start picnic make sandwich
            toggle_riding(ser, vid, get_off=True)

            if config.get('fetched_eggs') < 30:
                if prepare_party(ser, vid, breeding=True):
                    # We have no next target, end the program
                    end_program(ser)
                    return 0
                select_menu_item(ser, vid, "Picnic")
                time.sleep(7)
                press(ser, 'w', duration=.3)
                make_sandwich(ser)

                # # Get eggs from basket fill up boxes
                take_basket_eggs(ser, vid)
                prepare_party(ser, vid)

            # Hatch all eggs 
            hatch_eggs(ser, vid)

            end_time = time.time()
            print(f'Full egg run took {(end_time-start_time):.3f}s')
            start_time = time.time()
            time.sleep(2)


    vid.release()
    cv2.destroyAllWindows()
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
