from __future__ import annotations

import argparse
import time

import cv2
import numpy as np
import serial

import json

from services.common import *

SWITCH_NUM = 3

def get_pokemon_spots(box_num, vid: cv2.VideoCapture,):
    template = cv2.imread('templates/home_empty_spot.png', cv2.IMREAD_COLOR)
    threshold = 0.9
    num_cols = 6
    cell_width = 50   # Adjust to your grid cell width
    cell_height = 50 

    frame = getframe(vid)
    # Run template matching
    result = cv2.matchTemplate(frame, template, cv2.TM_CCOEFF_NORMED)
    locations = np.where(result >= threshold)
    points = list(zip(*locations[::-1]))  # x, y pairs

    if not points:
        matched_indices = []
    else:
        min_x = 70
        min_y = 140

        cell_width = 90
        cell_height = 75

        num_cols = 6  

        matched_indices = []

        for (x, y) in points:
            col = round((x - min_x) / cell_width)
            row = round((y - min_y) / cell_height)

            index = row * num_cols + col + 1 + ((box_num - 1) * 30)
            if index not in matched_indices:
                matched_indices.append(index)

    #         cv2.putText(marked_frame, str(index), (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    #         top_left = (x, y)
    #         bottom_right = (x + w, y + h)
    #         cv2.rectangle(marked_frame, top_left, bottom_right, (0, 255, 0), 2)

    # print(sorted(matched_indices))
    # cv2.imshow('Matches', marked_frame)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    current_range = box_num * 30
    for x in range(current_range - 29, current_range + 1):
        if matched_indices.__contains__(x):
            matched_indices.remove(x)
        else:
            matched_indices.append(x)

    return matched_indices

boxed_pokemon_path = Path(__file__).resolve().parent / 'configs' / 'boxed_pokemon.json'

def main() -> int:
    ser_str = get_switch_serial(SWITCH_NUM)
    vid = make_vid(get_switch_vid_num(SWITCH_NUM))

    owned_pokemon = set()
    shiny_census = False

    box_num = 1

    with open(boxed_pokemon_path, "r") as f:
        boxed_pokemon = json.load(f)

    start_time = time.time()

    with serial.Serial(ser_str, 9600) as ser, shh(ser):
        time.sleep(1)
        while box_num <= 35:
            pokemon = get_pokemon_spots(box_num, vid)
            owned_pokemon.update(pokemon)
        
            press(ser, 'L' if shiny_census else 'R', sleep_time=2)
            box_num += 1


    with open(boxed_pokemon_path, "w") as f:
        if shiny_census:
            boxed_pokemon['shiny'] = sorted(list(owned_pokemon))
        else:
            boxed_pokemon['normal'] = sorted(list(owned_pokemon))
        json.dump(boxed_pokemon, f)

    end_time = time.time()

    print(f'Total run took {end_time-start_time:.3f}s')

    vid.release()
    cv2.destroyAllWindows()
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
