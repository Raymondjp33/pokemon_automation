from __future__ import annotations

from pathlib import Path
import time
from typing import NamedTuple

import cv2
import serial

import json
import csv
import bisect

from services.common import *



def get_pokemon_name(vid: cv2.VideoCapture):
    frame = getframe(vid)
    # Switch 1
    # return get_text(frame=frame, top_left=Point(y=570, x=89), bottom_right=Point(y=607, x=221), invert=True)

    # Switch 2
    return get_text(frame=frame, top_left=Point(y=571, x=67), bottom_right=Point(y=603, x=205), invert=True)

def check_if_shiny(vid: cv2.VideoCapture):
    frame = getframe(vid)

    y1, x1, y2, x2 = 557, 527, 602, 557
    roi = frame[y1:y2, x1:x2]
    target_color = (255, 255, 255)

    found = any(color_near(pixel, target_color) for row in roi for pixel in row)

    if found:
        return True
    
    return False

def load_pokemon_species_ids():
    name_to_species_id = {}

    with open(Path(__file__).resolve().parent / 'configs' / 'pokemon.csv', mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            name = row['identifier'].strip().lower()  # Normalize name
            species_id = int(row['species_id'])
            name_to_species_id[name] = species_id

    return name_to_species_id

class Position(NamedTuple):
    col: int
    row: int
    boxOrPage: int

def get_box_location(dex_num, shiny):  
    box_num = int((dex_num - 1) / 30)
    if (shiny):
        box_num = 199 - box_num
    box_pos = dex_num % 30
    if (box_pos == 0):
        box_pos = 30
    row = int((box_pos - 1)/6) 
    col = box_pos % 6
    if (col == 0):
        col = 5
    else:
        col = col - 1
    
    return Position(col=col, row=row, boxOrPage=box_num)

def make_move(ser: serial.Serial, from_pos, to_pos, move_vertical = False,):
    difference = to_pos - from_pos

    invert = True
    if (difference >= 0):
        invert = False

    if (move_vertical):
        press(ser, '2' if not invert else '4', count=abs(difference))
    else:
        press(ser, '1' if not invert else '3', count=abs(difference))

def move_to_box(ser: serial.Serial, from_box: Position, to_box: Position, from_old = True):
    if not from_old:
        temp = from_box
        from_box = to_box
        to_box = temp
    
    page_dif = to_box.boxOrPage - from_box.boxOrPage

    if (page_dif != 0):
        move_left = page_dif < 0
        press(ser, 'L' if move_left else 'R', count=abs(page_dif), sleep_time=1.25)

    make_move(ser, from_box.row, to_box.row, move_vertical=True)
    make_move(ser, from_box.col, to_box.col, move_vertical=False)

    press(ser, 'A', sleep_time=1)

boxed_pokemon_path = Path(__file__).resolve().parent / 'configs' / 'boxed_pokemon.json'

def main() -> int:
    parser = argparse.ArgumentParser(
        description='')
    parser.add_argument('--starting_box', type=int, required=True)
    args = parser.parse_args()

    ser_str = SWITCH2_SERIAL
    vid = make_vid(SWITCH2_VID_NUM)
    starting_box = args.starting_box

    pokemon_map = load_pokemon_species_ids()

    with open(boxed_pokemon_path, "r") as f:
        boxed_pokemon = json.load(f)

    owned_pokemon = boxed_pokemon['normal']
    owned_shiny_pokemon = boxed_pokemon['shiny']

    from_box = get_box_location(starting_box, False)
    from_pokemon_num = 1
    from_pokemon = get_box_location(from_pokemon_num, False)

    start_time = time.time()
  
    with serial.Serial(ser_str, 9600) as ser, shh(ser):
        time.sleep(1)
        while True:
            if (from_pokemon_num > 30):
                break

            pokemon_is_shiny = check_if_shiny(vid)
            dex_num = pokemon_map.get(get_pokemon_name(vid).lower())

            if dex_num == None:
                try:
                    user_input = input("Dex num: ")

                    if (user_input == 'exit'):
                        break
                    dex_num = int(user_input)
                    if dex_num > 1025 or dex_num < 1:
                        dex_num = None
                except ValueError:
                    print("Skipping")

            already_boxed =  owned_pokemon.__contains__(dex_num) if not pokemon_is_shiny else owned_shiny_pokemon.__contains__(dex_num)

            if dex_num != None:
                print(f'{from_pokemon_num} - {get_pokemon_name(vid)} - {dex_num} - {"Boxed" if already_boxed else "Not Boxed"} - {"Shiny" if pokemon_is_shiny else "Not Shiny"}')
            else:
                print(f"{from_pokemon_num} - Could not find pokemon, read name: {get_pokemon_name(vid)}")

            # if not already_boxed:
            #     print(f'{old_pokemon_num} needs home: {get_pokemon_name(vid).lower()}')
            

            if (dex_num == None or already_boxed ):
                from_row = from_pokemon.row
                from_col = from_pokemon.col
                from_pokemon_num += 1
                from_pokemon = get_box_location(from_pokemon_num, False)
                make_move(ser, from_pos=from_col, to_pos=from_pokemon.col, move_vertical=False)
                make_move(ser, from_pos=from_row, to_pos=from_pokemon.row, move_vertical=True)
                continue
            
            if pokemon_is_shiny:
                bisect.insort(owned_shiny_pokemon, dex_num)
            else:
                bisect.insort(owned_pokemon, dex_num)

            with open(boxed_pokemon_path, "w") as f:
                json.dump(boxed_pokemon, f)

            from_pokemon = get_box_location(from_pokemon_num, False)
            to_pokemon = get_box_location(dex_num, pokemon_is_shiny)
            to_box = get_box_location(to_pokemon.boxOrPage + 1, False)

            # Pick up pokemon
            press(ser, 'A', sleep_time = .5)

            # Go down to box list
            make_move(ser, from_pos=from_pokemon.col, to_pos=3, move_vertical=False)
            make_move(ser, from_pos=from_pokemon.row, to_pos=5, move_vertical=True)
            press(ser, 'A', sleep_time = 2)

            # Go to new box number
            move_to_box(ser, from_box, to_box, from_old=True)

            # Put pokemon in correct spot
            make_move(ser, from_pos=0, to_pos=to_pokemon.row, move_vertical=True)
            make_move(ser, from_pos=0, to_pos=to_pokemon.col, move_vertical=False)
            press(ser, 'A', sleep_time = 1)

            # Go back to box list
            make_move(ser, from_pos=to_pokemon.col, to_pos=3, move_vertical=False)
            make_move(ser, from_pos=to_pokemon.row, to_pos=5, move_vertical=True)
            press(ser, 'A', sleep_time = 2)

            # Go to old box number
            move_to_box(ser, from_box, to_box, from_old=False)

            from_pokemon_num += 1
            from_pokemon = get_box_location(from_pokemon_num, False)
            make_move(ser, from_pos=0, to_pos=from_pokemon.col, move_vertical=False)
            make_move(ser, from_pos=0, to_pos=from_pokemon.row, move_vertical=True)

            # return 0

    end_time = time.time()

    print(f'Total run took {end_time-start_time:.3f}s')

    vid.release()
    cv2.destroyAllWindows()
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
