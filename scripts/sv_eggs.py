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
import argparse

from services.common import *
from services.config_manager import ConfigManager

redis_client = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)
config = ConfigManager(Path(__file__).resolve().parent / 'configs' / 'sv_egg_data.json')
config3 = ConfigManager(Path(__file__).resolve().parent / 'configs' / 'sv_egg_data3.json')

switch_num = 2

###
###     DATABASE/FILE RELATED
###
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

    hunt_id = stream_data['switch2_hunt_id' if switch_num == 2 else 'switch3_hunt_id']

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
            (pokemon[1], int(time.time() * 1000), count_difference, "egg", 2 if switch_num == 2 else 3, pokemon_name, None, hunt_id)
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
    (pokemon[0], new_hunt_id, 0, new_target['name'], 2 if switch_num == 2 else 3, new_target['target'], int(time.time() * 1000), 'egg', None)
    )

    with open(STREAM_DATA_PATH, 'r') as f:
        data = json.load(f)
    data['switch2_hunt_id' if switch_num == 2 else 'switch3_hunt_id'] = new_hunt_id
    with open(STREAM_DATA_PATH, 'w') as f:
        json.dump(data, f, indent=4)

    redis_client.publish(REDIS_CHANNEL, json.dumps({"update_data":True}))
    conn.commit()
    conn.close()

    next_pos = get_location(new_target['slot'])
    starting_pos = Position(col=1,row=0)

    safe_move_box_cursor(ser, vid, next_pos)
    # press(ser, 'Y', sleep_time=0.5)
    safe_perform_grasp(ser, vid, pickup=True)
    safe_move_box_cursor(ser, vid, starting_pos)
    # press(ser, 'A', sleep_time=0.5)
    safe_perform_grasp(ser, vid, pickup=False)

def end_program(ser: serial.Serial, failure: bool = True):
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

###
###     FRAME/VID TEXT CHECKERS
###
def oh_text_showing(vid: cv2.VideoCapture):
    frame = getframe(vid)
    return get_text(frame=frame, top_left=Point(y=543, x=345), bottom_right=Point(y=593, x=438), invert=True) == 'Oh?'

def check_if_shiny(vid: cv2.VideoCapture):
    frame = getframe(vid)

    y1, x1, y2, x2 = 74, 1134, 83, 1142
    roi = frame[y1:y2, x1:x2]
    target_color = (252, 252, 252)

    found = any(color_near(pixel, target_color) for row in roi for pixel in row)

    if found:
        return True
    
    return False

def map_on_zero(vid: cv2.VideoCapture,):
    frame = getframe(vid)
    if get_text(frame=frame, top_left=Point(y=249, x=585), bottom_right=Point(y=286, x=699), invert=True) == 'Zero Gate':
        return 1
    elif get_text(frame=frame, top_left=Point(y=395, x=718), bottom_right=Point(y=433, x=779), invert=True) == 'here':
        return 2
    
    return 0

def get_box_cursor_position(vid: cv2.VideoCapture,):
    frame = getframe(vid)
    party_selected_color = (0, 220, 255)
    box_selected_color = (4, 224, 244)
    box_selected_color2 = (8, 224, 244)
    bottom_selected_color1 = (1, 218, 234)
    bottom_selected_color2 = (2, 224, 244)
    selection_colors = [party_selected_color, box_selected_color, box_selected_color2, bottom_selected_color1, bottom_selected_color2]
    what_doya_want_popup = (45, 40, 20)
    red_thresh = 180

    # if color_near(frame[544][484], what_doya_want_popup):
    if frame[544][484][2] > red_thresh:
        if 'Release' == get_text(frame=getframe(vid), top_left=Point(y=303, x=296), bottom_right=Point(y=339, x=390), invert=True):
            return 'realese'
        elif 'Yes' == get_text(frame=getframe(vid), top_left=Point(y=433, x=962), bottom_right=Point(y=462, x=1007), invert=True):
            return 'confirming'

    ## Current Party
    party_difference = 92
    party1_y = 150
    for x in range(6):
        y_location = party1_y + (x * party_difference)
        # if color_near(frame[y_location][35], party_selected_color):
        if frame[y_location][35][2] > red_thresh:
            return f'-1,{x}'

    ## Box locations in x,y
    diff = 87
    starting_x = 308
    starting_y = 147
    for x in range(6):
        curr_x = starting_x + (x * diff)
        for y in range(5):
            curr_y = starting_y + (y * diff)
            # if any(color_near(frame[curr_y][curr_x], certain_color) for certain_color in selection_colors):
            if frame[curr_y][curr_x][2] > red_thresh:
                return f'{x},{y}'

    # if color_near(frame[100][471], party_selected_color):
    if frame[100][471][2] > red_thresh:
        return 'top'
    
    # if color_near(frame[613][359], bottom_selected_color1):
    if frame[613][359][2] > red_thresh:
        return 'bottom1'
    
    # if color_near(frame[613][660], bottom_selected_color2):
    if frame[613][660][2] > red_thresh:
        return 'bottom2'

def moving_pokemon(vid: cv2.VideoCapture,):
    if 'Swap' == get_text(frame=getframe(vid), top_left=Point(y=681, x=676), bottom_right=Point(y=708, x=720), invert=True):
        return False
    if 'Swap' == get_text(frame=getframe(vid), top_left=Point(y=684, x=769), bottom_right=Point(y=707, x=811), invert=True):
        return False
    if 'Swap' == get_text(frame=getframe(vid), top_left=Point(y=680, x=598), bottom_right=Point(y=709, x=638), invert=True):
        return False
    
    return True

###
###     HELPER FUNCTIONS
###
# Handles from the "Oh?" text through full hatch of egg
def attempt_action(ser: serial.Serial, action, condition, *, attempts: int = 10):
    for _ in range(attempts):
        action()

        if condition():
            return
    
    end_program(ser)

def hatch_egg(ser: serial.Serial):
    config.update({'hatched_eggs': config.get('hatched_eggs') + 1})
    press(ser, 'A', count=3)
    time.sleep(14)
    press(ser, 'A', count=2)
    time.sleep(4)
    print('Egg Hatched!')

def delete_current_pokemon(ser: serial.Serial, vid: cv2.VideoCapture):
    if check_if_shiny(vid):
        print('Attempting to delete shiny, aborting!')
        end_program(ser)

    selected_color = (0, 219, 255)

    # Select pokemon, we are looking for the word 'Release' in the menu'   
    attempt_action(
        ser, 
        action = lambda: press(ser, 'A', sleep_time=1),
        condition = lambda: ('Release' == get_text(frame=getframe(vid), top_left=Point(y=303, x=296), bottom_right=Point(y=339, x=390), invert=True)),
    )

    # Pokemon menu should be open, make sure we are over 'Release'
    attempt_action(
        ser, 
        action = lambda: press(ser, 'w', sleep_time=0.3),
        condition = lambda: (color_near((getframe(vid))[320][500], selected_color)),
    )
    time.sleep(0.3)

    # Make sure we now see the word 'Yes' in the menu
    attempt_action(
        ser, 
        action = lambda: press(ser, 'A', sleep_time=1),
        condition = lambda: 'Yes' == get_text(frame=getframe(vid), top_left=Point(y=433, x=962), bottom_right=Point(y=462, x=1007), invert=True),
    )

    # Make sure we are over the word yes
    attempt_action(
        ser, 
        action = lambda: press(ser, 'w', sleep_time=1),
        condition = lambda: color_near((getframe(vid))[442][1047], selected_color),
    )

    # Make sure that yes was tapped
    attempt_action(
        ser, 
        action = lambda: press(ser, 'A'),
        condition = lambda: (not 'Yes' == get_text(frame=getframe(vid), top_left=Point(y=433, x=962), bottom_right=Point(y=462, x=1007), invert=True)),
    )
    
    # Wait until we see 'Bye-Bye' text
    attempt_action(
        ser, 
        action = lambda: time.sleep(0.5),
        condition = lambda: ('Bye-bye' == get_text(frame=getframe(vid), top_left=Point(y=593, x=361), bottom_right=Point(y=632, x=454), invert=True)),
    )
    time.sleep(0.5)

    # Make sure that 'Bye Bye' text is gone
    attempt_action(
        ser, 
        action = lambda: press(ser, 'A', sleep_time=1.75),
        condition = lambda: (not 'Bye-bye' == get_text(frame=getframe(vid), top_left=Point(y=593, x=361), bottom_right=Point(y=632, x=454), invert=True)),
    )

def check_menu(ser: serial.Serial, vid: cv2.VideoCapture, leave_open:bool = False):
    print(f'Checking for the menu and {"leaving it open" if leave_open else "closing it"}')

    for x in range(30):
        press(ser, 'X', sleep_time=1)
        if 'MAIN MENU' == get_text(frame=getframe(vid), top_left=Point(y=112, x=884), bottom_right=Point(y=154, x=1038), invert=True):
            break

        if x > 15:
            handle_battle_check(ser, vid, full_reset=False)

        if x > 27:
            return False

    if not leave_open:
        press(ser, 'B', sleep_time=2)

    return True

def select_menu_item(ser: serial.Serial, vid: cv2.VideoCapture, menu_item: str):
    check_menu(ser, vid, leave_open=True)
    frame = getframe(vid)
    current_menu_item = None

    selected_color = (0, 204, 240)

    # Make sure we are on the right side of the menu
    press(ser, 'd', sleep_time=1)

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
        if menu_item == 'Boxes':        
            curr = 0
            while get_box_cursor_position(vid) != '0,0':
                time.sleep(1)
                if curr > 10:
                    end_program(ser)
                curr = curr + 1

    elif current_menu_item == "Boxes":
        press(ser, 's')
        press(ser, 'A', sleep_time=2)

    else:
        press(ser, 'w')
        press(ser, 'A', sleep_time=2)

    print(f'Entering {menu_item}')

def reset_position(ser: serial.Serial, vid: cv2.VideoCapture, full_reset=False):
    # Open map
    press(ser, 'Y', sleep_time=2.5)

    # Try to get over the area zero gate fast travel
    ready_to_travel = False
    press(ser, 'A', sleep_time=1)
    if map_on_zero(vid) == 2:
        ready_to_travel = True
        print("Already on zero")
    else:
        press(ser, 'B', sleep_time=2)

    def attempt_map_move(button):
        nonlocal ready_to_travel
        if ready_to_travel:
            return
        
        press(ser, '+', sleep_time=1)
        press(ser, button, sleep_time=1, duration=0.07)
        if map_on_zero(vid) == 1:
            ready_to_travel = True
            press(ser, 'A', sleep_time=1)
            print(f"Got to zero moving with '{button}'")

    attempt_map_move('c')
    attempt_map_move('s')
    attempt_map_move('q')
    attempt_map_move('d')
    
    if not ready_to_travel:
        end_program(ser)

    # At this point we should be looking at "Fly Here"
    press(ser, 'A', sleep_time=1.5, count=2)

    if full_reset:
        toggle_riding(ser, vid)
        select_menu_item(ser, vid, 'Boxes')
        move_eggs_to_party(ser, vid, from_party=True)
        exit_menus(ser, vid)
        press(ser, 'e', duration=2, sleep_time=5)
        press(ser, 's', duration=2, sleep_time=3)
        toggle_riding(ser, vid)
        press(ser, 'w', duration=4)
        press(ser, 'd', duration=1)
        press(ser, 'a', duration=0.5)
        press(ser, 'L', sleep_time=0.5)
        select_menu_item(ser, vid, 'Boxes')
        move_eggs_to_party(ser, vid)
        exit_menus(ser, vid)
    else:
        toggle_riding(ser, vid)
        press(ser, 'L', sleep_time=0.5)
        press(ser, 'e', sleep_time=0.5)
        press(ser, 'L', sleep_time=0.5)
        press(ser, 'w', duration=2.5)
        press(ser, 'd', duration=2.2)
        press(ser, 'a', duration=0.3)
        press(ser, 'L', sleep_time=0.5)

def toggle_riding(ser: serial.Serial,  vid: cv2.VideoCapture, get_off: bool = False):
    check_menu(ser, vid, leave_open=True)
    current_text = get_text(frame=getframe(vid), top_left=Point(y=677, x=152), bottom_right=Point(y=713, x=239), invert=True)

    if current_text == 'Get On' and not get_off:
        print('Getting on Miraidon')
        press(ser, '+', sleep_time=3)
    elif current_text == 'Get Off' and get_off:
        print('Getting off Miraidon')
        press(ser, '+', sleep_time=3)
    else:
        press(ser, 'B', sleep_time=1)

def move_eggs_to_party(ser: serial.Serial, vid: cv2.VideoCapture, from_party=False, def_columns = None):
    columns_to_move = int(math.floor(config.get("hatched_eggs", 0) / 5))

    if (columns_to_move > 5 or config.get('fetched_eggs') < 30) and def_columns == None:
        return
    
    if def_columns is not None:
        columns_to_move = def_columns

    if from_party:
        safe_move_box_cursor(ser, vid, Position(col=-1, row=1))
        time.sleep(0.5)
        attempt_action(
            ser, 
            action = lambda: press(ser, '-', sleep_time=0.5),
            condition = lambda: moving_pokemon(vid),
        )
        safe_move_box_cursor(ser, vid, Position(col=-1, row=5))
        attempt_action(
            ser, 
            action = lambda: press(ser, 'A', sleep_time=0.5),
            condition = lambda: get_box_cursor_position(vid) == '-1,1',
        )
        safe_move_box_cursor(ser, vid, Position(col=columns_to_move, row=0))
        attempt_action(
            ser, 
            action = lambda: press(ser, 'A', sleep_time=1),
            condition = lambda: (not moving_pokemon(vid)),
        )
    else:
        safe_move_box_cursor(ser, vid, Position(col=columns_to_move, row=0))
        time.sleep(0.5)
        attempt_action(
            ser, 
            action = lambda: press(ser, '-', sleep_time=0.5),
            condition = lambda: moving_pokemon(vid),
        )

        safe_move_box_cursor(ser, vid, Position(col=columns_to_move, row=4))
        attempt_action(
            ser, 
            action = lambda: press(ser, 'A', sleep_time=0.5),
            condition = lambda: get_box_cursor_position(vid) == f'{columns_to_move},0',
        )

        safe_move_box_cursor(ser, vid, Position(col=-1, row=1))
        attempt_action(
            ser, 
            action = lambda: press(ser, 'A', sleep_time=1),
            condition = lambda: (not moving_pokemon(vid)),
        )

def handle_battle_check(ser: serial.Serial,  vid: cv2.VideoCapture, full_reset = True):

    in_battle = 'Run' == get_text(frame=getframe(vid), top_left=Point(y=642, x=1048), bottom_right=Point(y=686, x=1106), invert=True)
    looking_at_pokeball = 'Check Details' == get_text(frame=getframe(vid), top_left=Point(y=669, x=601), bottom_right=Point(y=688, x=725), invert=True)

    if not in_battle and not looking_at_pokeball:
        return
    
    print('We are in battle, running and resetting')
    selected_color = (0, 206, 238)

    if looking_at_pokeball: 
        press(ser, 'B', sleep_time=1)

    frame=getframe(vid)
    while not color_near(frame[663][1116], selected_color):
        press(ser, 's', sleep_time=0.5)
        frame=getframe(vid)

    time.sleep(1)
    # Now we should be over run
    press(ser, 'A', sleep_time=7.5)
    if full_reset:
        reset_position(ser, vid, full_reset=True)

def validate_and_extract_split(input_string: str | None):
    if input_string == None:
        return None

    try:
        parts = input_string.split(',')
        if len(parts) == 2:
            num1 = int(parts[0])
            num2 = int(parts[1])
            return (num1, num2)
    except ValueError:
        return input_string
    
    return None
    
def safe_move_box_cursor(ser: serial.Serial, vid: cv2.VideoCapture, to_pos: Position):
    current_pos = validate_and_extract_split(get_box_cursor_position(vid))

    if (current_pos == None):
        print("Dont know or invalid position!")
        end_program(ser)
        return
    
    current_pos = Position(col=current_pos[0], row=current_pos[1])
    move_position(ser, current_pos, to_pos)

    # print(current_pos)
    # print(get_box_cursor_position(vid))

    current_pos = validate_and_extract_split(get_box_cursor_position(vid))
    if current_pos[0] != to_pos.col or current_pos[1] != to_pos.row:
        safe_move_box_cursor(ser, vid, to_pos)

def safe_move_box_number(ser: serial.Serial, vid: cv2.VideoCapture, to_box: int):
    def get_current_box():
        try:
            return int(get_text(frame=getframe(vid), top_left=Point(y=82, x=543), bottom_right=Point(y=118, x=607), invert=True))
        except: 
            return None
        
    current_box = get_current_box()
    if (current_box == None):
        print("Dont know box number or invalid box num!")
        end_program(ser)
        return
    
    box_diff = to_box - current_box
    press(ser, 'L' if box_diff < 0 else 'R', sleep_time=1.5, count=abs(box_diff))

    current_box = get_current_box()
    if (current_box == None):
        print("Dont know box number or invalid box num!")
        end_program(ser)
        return
    if current_box != to_box:
        safe_move_box_cursor(ser, vid, to_box)

def safe_perform_grasp(ser: serial.Serial, vid: cv2.VideoCapture, pickup: bool):
    attempt_action(
        ser, 
        action = lambda: press(ser, 'Y' if pickup else 'A', sleep_time=1),
        condition = lambda: (moving_pokemon(vid) if pickup else (not moving_pokemon(vid))),
    ) 

def exit_menus(ser: serial.Serial, vid: cv2.VideoCapture,):
    main_menu_showing = lambda: 'MAIN MENU' == get_text(frame=getframe(vid), top_left=Point(y=112, x=884), bottom_right=Point(y=154, x=1038), invert=True)
    boxes_open = lambda: 'Back' == get_text(frame=getframe(vid), top_left=Point(y=677, x=1217), bottom_right=Point(y=707, x=1262), invert=True)

    attempt_action(
        ser, 
        action = lambda: press(ser, 'B', sleep_time=2),
        condition = lambda: (not (main_menu_showing() or boxes_open())),
    ) 
    
###
###     CORE FUNCTIONS
###
def handle_picnic_and_egg_fetching(ser: serial.Serial, vid: cv2.VideoCapture):
    if config.get('fetched_eggs') >= 30:
        return

    # Start picnic make sandwich
    toggle_riding(ser, vid, get_off=True)

    if prepare_party(ser, vid, breeding=True):
        # We have no next target, end the program
        end_program(ser, failure=False)
        return 0
    select_menu_item(ser, vid, "Picnic")
    time.sleep(12)
    press(ser, 'w', duration=.3)
    make_sandwich(ser)

    try_again = False
    # # Get eggs from basket fill up boxes
    if take_basket_eggs(ser, vid) == 'reset':
        try_again = True

    prepare_party(ser, vid)

    if try_again:
        print('Trying to get eggs again')
        reset_position(ser, vid, full_reset=True)
        return handle_picnic_and_egg_fetching(ser, vid)

# Against picnic table, goes into menu, ends once out of sandwich ui
def make_sandwich(ser: serial.Serial):
    # Open sandwich menu
    press(ser, 'A', sleep_time= 1.5)
    press(ser, 'A', sleep_time= 6)

    # Select egg 2 sandwich
    if switch_num == 2:
        press(ser, 'd', sleep_time=0.4)
        press(ser, 's', sleep_time=0.4, count=2)
        press(ser, 'A', sleep_time=0.3, count=4)
    elif switch_num == 3:
        press(ser, 's', sleep_time=0.4, count=8, duration=0.05)
        press(ser, 'A', sleep_time=0.3, count=4)
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

def take_basket_eggs(ser: serial.Serial, vid: cv2.VideoCapture):
        # Get in front of basket
        press(ser, 'a', duration=0.4, sleep_time=0.5)
        press(ser, 'w', duration=0.6, sleep_time=0.5)
        press(ser, 'd', duration=0.4, sleep_time=0.5)
        press(ser, 's')

        loop_attempt = 0
        no_egg_count = 0
        fetched_eggs = config.get('fetched_eggs')
        while (fetched_eggs < 30):
            time.sleep(20)

            taking_eggs = True
            print("Checking basket")
            press(ser, 'A', count=2, sleep_time=1)
            start_time = time.time()
            while taking_eggs:
                time.sleep(1)
                
                current_text = get_text(frame=getframe(vid), top_left=Point(y=543, x=358), bottom_right=Point(y=592, x=558), invert=True)
                if current_text == 'Doesn’t look like' or current_text == "Doesn't look like":
                    print('No egg')
                    press(ser, 'A')
                    taking_eggs = False
                    loop_attempt = 0
                    no_egg_count = no_egg_count + 1
                elif current_text == 'There’s a Pokéme' or current_text == 'There’s a Pokémo':
                    print('Taking egg')
                    press(ser, 'A', count=3, sleep_time=0.5)
                    config.update({'fetched_eggs': fetched_eggs + 1})
                    loop_attempt = 0
                    no_egg_count = 0
                elif current_text == '..Qh? There’s sor':
                    print('Taking egg')
                    press(ser, 'A', count=4, sleep_time=0.5)
                    config.update({'fetched_eggs': fetched_eggs + 1})
                    loop_attempt = 0
                    no_egg_count = 0
                
                end_time = time.time()
                curr_time = end_time - start_time

                if curr_time > 100:
                    print('Attempting to break out of loop')
                    press(ser, 'B', sleep_time=1, count=4)
                    start_time = time.time()
                    loop_attempt = loop_attempt + 1
                
                if loop_attempt > 5 or curr_time > 2400 or no_egg_count > 10:
                    time.sleep(1)
                    press(ser, 'B', sleep_time=1, count=10)
                    press(ser, 'Y', sleep_time=1.5)
                    press(ser, 'A', sleep_time=4, count=2)
                    press(ser, 'B', count=8)
                    time.sleep(1)
                    print('Resetting picnic')
                    return 'reset'

                fetched_eggs = config.get('fetched_eggs')
        # Exit picnic
        time.sleep(1)
        press(ser, 'B', sleep_time=1, count=10)
        press(ser, 'Y', sleep_time=1.5)
        press(ser, 'A', sleep_time=4, count=2)
        press(ser, 'B', count=8)
        time.sleep(1)

def prepare_party(ser: serial.Serial,  vid: cv2.VideoCapture, breeding: bool = False):
    select_menu_item(ser, vid, "Boxes")
    time.sleep(2)

    press(ser, 'L', sleep_time=1.5)
    safe_move_box_number(ser, vid, 4)

    # Swap ditto and coalossal
    # press(ser, 'Y', sleep_time=0.3)
    safe_perform_grasp(ser, vid, pickup=True)
    safe_move_box_cursor(ser, vid, Position(col=-1, row=0))
    # press(ser, 'A', sleep_time=0.5)
    safe_perform_grasp(ser, vid, pickup=False)

    # Either put away or move breeding pokemon respectively
    if breeding:
        safe_move_box_cursor(ser, vid, Position(col=1, row=0))

        if config.get('target_met'):
            if handle_update_hunt(ser, vid):
                return True

        # press(ser, 'Y', sleep_time=0.5)
        safe_perform_grasp(ser, vid, pickup=True)
        safe_move_box_cursor(ser, vid, Position(col=-1, row=1))
        # press(ser, 'A', sleep_time=0.5)
        safe_perform_grasp(ser, vid, pickup=False)
        safe_move_box_number(ser, vid, 5)
    else:
        # press(ser, 's', sleep_time=0.3)
        safe_move_box_cursor(ser, vid, Position(col=-1, row=1))
        # press(ser, 'Y', sleep_time=0.5)
        safe_perform_grasp(ser, vid, pickup=True)
        safe_move_box_cursor(ser, vid, Position(col=1, row=0))
        # press(ser, 'A', sleep_time=0.5)
        safe_perform_grasp(ser, vid, pickup=False)
        safe_move_box_cursor(ser, vid, Position(col=0, row=0))
        # press(ser, 'R', sleep_time=1.5)
        safe_move_box_number(ser, vid, 5)
        move_eggs_to_party(ser, vid)

    exit_menus(ser, vid)

def hatch_eggs(ser: serial.Serial,  vid: cv2.VideoCapture, extra = None):
    if extra is not None:
        config.update({'hatched_eggs': 0})
    elif config.get('fetched_eggs') < 30:
        return

    total_hatched = config.get('hatched_eggs')
    party_hatched = total_hatched % 5
    forward = True

    toggle_riding(ser, vid, get_off=False)

    while total_hatched < 30:
        start_time = time.time()
        while party_hatched < 5:
            if oh_text_showing(vid):
                print(f'Hatching egg {party_hatched}')
                party_hatched = party_hatched + 1
                hatch_egg(ser)
                forward = not forward

            if (party_hatched >= 5):
                break
            

            handle_battle_check(ser, vid)
            end_time = time.time()
            current_time = end_time - start_time
            if current_time > 1000:
                end_program(ser)

            # press(ser, '{', duration=0.03, write_null_byte=False)
            # press(ser, 'q', duration=0.5, write_null_byte=False)
            # press(ser, 'w', duration=0.5, write_null_byte=False)
            # press(ser, 'e', duration=0.5, write_null_byte=False)
            # press(ser, 'd', duration=0.5, write_null_byte=False)
            # press(ser, 'c', duration=0.5, write_null_byte=False)
            # press(ser, 's', duration=0.5, write_null_byte=False)
            # press(ser, 'z', duration=0.5, write_null_byte=False)
            # press(ser, 'a', duration=0.5, write_null_byte=False)
            
                
            # press(ser, 's' if not forward else 'w', duration=.5, write_null_byte=False)
            # press(ser, '{', duration=0.03, write_null_byte=False)
            press(ser, 's' if not forward else 'w', duration=2)
            forward = not forward

        if extra == 'party':
            return
        
        time.sleep(1)
        handle_battle_check(ser, vid)
        select_menu_item(ser, vid, 'Boxes')
        save_needed = False
        if extra == 'box':
            curr_cols = int(math.floor(config.get("hatched_eggs", 0) / 5)) 
            move_eggs_to_party(ser, vid, from_party=True, def_columns=curr_cols - 1)
            move_eggs_to_party(ser, vid, def_columns=curr_cols)
        else:
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
    
    if extra is not None:
        return
    
    config.update({'fetched_eggs': 0, 'hatched_eggs': 0})
    toggle_riding(ser, vid, get_off=True)

def handle_process_eggs(ser: serial.Serial, vid: cv2.VideoCapture,):
    print('Processing eggs!')
    increment_counter(caught_index=None)

    # press(ser, 'a', sleep_time=.5)
    safe_move_box_cursor(ser, vid, Position(col=-1, row=0))

    line_count = 5

    target_met = False
    any_shiny = False
    # Check for any shiny
    for x in range(5):
        # press(ser, 's', sleep_time=.75)
        safe_move_box_cursor(ser, vid, Position(col=-1, row=x+1))
        is_shiny = check_if_shiny(vid)
        if (is_shiny):
            any_shiny = True
            open_slot = config.get('open_slot')
            # boxes_to_move = 2 + int((open_slot - 1) / 30)
            box_to_move_to = 3 - int((open_slot - 1) / 30)
            print(f'We have a shiny at index {x}!')
            target_met = increment_counter(caught_index=x)
            line_count = line_count - 1
            # Pick shiny up 
            print('Picking shiny up')
            # press(ser, 'Y')
            safe_perform_grasp(ser, vid, pickup=True)
            time.sleep(1.5)
            # Put in open spot
            print('Putting in open spot')
            # press(ser, 'L', sleep_time=2, count=boxes_to_move)
            safe_move_box_number(ser, vid, box_to_move_to)
            move_location = get_location(open_slot)
            starting_location = Position(col=0, row=0)
            config.update({'open_slot': config.get('open_slot') + 1})

            safe_move_box_cursor(ser, vid, move_location)
            # press(ser, 'A', sleep_time=1.5)
            safe_perform_grasp(ser, vid, pickup=False)

            # Come back
            safe_move_box_cursor(ser, vid, starting_location)
            safe_move_box_number(ser, vid, 5)
            safe_move_box_cursor(ser, vid, Position(col=-1, row=x))
        else:   
            print(f'Pokemon at index {x} is not shiny')

    # press(ser, 'w', count=line_count - 1, sleep_time=0.25)
    safe_move_box_cursor(ser, vid, Position(col=-1, row=1))
    time.sleep(0.5)

    # Delete all non shiny
    for _ in range(line_count):
        delete_current_pokemon(ser, vid)
    
    press(ser, 'd')
    press(ser, 'w')

    if target_met:
        config.update({'target_met': True})

    return any_shiny

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--switch_num')
    args = parser.parse_args()

    if args.switch_num:
        global switch_num 
        switch_num = int(args.switch_num)

    if switch_num == 3:
        global config
        config = config3

    

    ser_str = get_switch_serial(switch_num)
    vid = make_vid(get_switch_vid_num(switch_num))
    start_time = time.time()
    # current_text = get_text(frame=getframe(vid), top_left=Point(y=543, x=358), bottom_right=Point(y=592, x=558), invert=True)

    # print(check_if_shiny(vid))
    # return

    with serial.Serial(ser_str, 9600) as ser, shh(ser):
        time.sleep(2)

        # handle_process_eggs(ser, vid)
        # delete_current_pokemon(ser, vid)
        # move_eggs_to_party(ser, vid, from_party=False)
        # safe_move_box_number(ser, vid, 3)
        # exit_menus(ser, vid)
        # reset_position(ser, vid, full_reset=True)
        # prepare_party(ser, vid, breeding=False)
        # hatch_eggs(ser, vid, extra='box')
        # handle_battle_check(ser, vid)
        # return 
    
        while True:

            # print(validate_and_extract_split(get_box_cursor_position(vid)))
            # print(color_near((getframe(vid))[540][482], (45, 40, 20)))
            # print(get_text(frame=getframe(vid), top_left=Point(y=681, x=676), bottom_right=Point(y=708, x=720), invert=True))
            # print(moving_pokemon(vid))
            # time.sleep(1)
            # continue

            reset_position(ser, vid, full_reset=True)
            handle_picnic_and_egg_fetching(ser, vid)
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
