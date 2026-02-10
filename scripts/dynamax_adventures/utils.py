from __future__ import annotations

import contextlib
import time
from collections.abc import Generator
from typing import NamedTuple
import tesserocr
from typing import Protocol
import functools
import numpy as np
from pathlib import Path

import cv2
import numpy
import serial
import pytesseract
import os
import json

from services.common import *

os.environ['TESSDATA_PREFIX'] = '/opt/homebrew/Cellar/tesseract/5.5.0_1/share/tessdata'
pytesseract.pytesseract.tesseract_cmd = r'/opt/homebrew/Cellar/tesseract/5.5.0_1/bin/tesseract'

def tess_text_u8(
        img: numpy.ndarray,
        *,
        tessapi: tesserocr.PyTessBaseAPI | None = None,
) -> str:
    tessapi = tessapi or tessapi()

    tessapi.SetImageBytes(
        img.tobytes(),
        width=img.shape[1],
        height=img.shape[0],
        bytes_per_pixel=1,
        bytes_per_line=img.shape[1],
    )
    return tessapi.GetUTF8Text().strip()

def extract_text(vid: cv2.VideoCapture, x1, y1, x2, y2, sortByX: bool):
    image = getframe(vid)
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower_white = np.array([0, 0, 200], dtype=np.uint8)
    upper_white = np.array([180, 50, 255], dtype=np.uint8)
    mask = cv2.inRange(hsv, lower_white, upper_white)
    
    custom_config = r'--oem 3 --psm 11'
    boxes = pytesseract.image_to_data(mask, config=custom_config, output_type=pytesseract.Output.DICT)
    
    text_data = []
    for i in range(len(boxes['text'])):
        text = boxes['text'][i].strip()
        if len(text) > 1:  # Ignore very short words (likely noise)
            x, y, w, h = (boxes['left'][i], boxes['top'][i], boxes['width'][i], boxes['height'][i])
            if x1 is None or y1 is None or x2 is None or y2 is None or (x1 <= x <= x2 and y1 <= y <= y2):
                text_data.append((x if sortByX else y, text.lower()))
    
    text_data.sort()
    sorted_text = [text for _, text in text_data]

    # with open(pokemon_data_path, 'r') as file:
    #     data = json.load(file)
    
    # sorted_text = [text for text in sorted_text if text in data['pokemon_types']]

    return sorted_text

def connect_and_go_to_game(ser: serial.Serial):
    press(ser, 'H', sleep_time=1)
    press(ser, 'H', duration=0.1)
    press(ser, 'A', duration=0.5)
    press(ser, 'H', duration=0.1)
    press(ser, 'A', sleep_time=1)
    press(ser, 'A')
    press(ser, '0')

def go_to_change_grip(ser: serial.Serial):
    press(ser, 'H')
    time.sleep(1)
    press(ser, 's')
    press(ser, 'd', count=4)
    press(ser, 'A')
    time.sleep(1)
    press(ser, 'A')
    
def reset_game(ser: serial.Serial, vid: cv2.VideoCapture,):
    press(ser, 'H', sleep_time=1)
    press(ser, 'X', sleep_time=1)
    press(ser, 'A', sleep_time=1, count=3)

    print('game reset!')

def increment_counter(file_prefix, frames=None, caught_legend=False, shiny_legend = False):
    total_dens_counter_path = Path(f'total-dens-counter.txt')
    counter_path = Path(f'current-counter.txt')
    data_path = Path(__file__).resolve().parent.parent.parent.parent / 'backend' / 'switch2_data.json'
    
    # Read the existing count (default to 0 if file does not exist)
    if counter_path.exists():
        with counter_path.open("r") as file:
            try:
                count = int(file.read().strip())
            except ValueError:
                count = 0
    else:
        count = 0

    if total_dens_counter_path.exists():
        with total_dens_counter_path.open("r") as file:
            try:
                total_dens_count = int(file.read().strip())
            except ValueError:
                total_dens_count = 0
    else:
        total_dens_count = 0

    total_dens_count += 1

    # Increment the counter
    if caught_legend:
        count += 1

    with data_path.open("r") as data_file:
        data = json.load(data_file)

    current_pokemon = None

    for entry in data["pokemon"]:
        if entry["pokemon"] == file_prefix:
            current_pokemon = entry
            break
    if current_pokemon != None:
        current_pokemon['extra_data']['total_dens'] = current_pokemon['extra_data']['total_dens'] + 1
        if (caught_legend):
            current_pokemon['encounters'] = current_pokemon['encounters'] + 1
        if (shiny_legend):
            current_pokemon['caught_timestamp'] = int(time.time() * 1000)
    # timestamp  = time.strftime('%Y-%m-%d %H:%M:%S')
    # star = '* ' if delay > 0.53 or delay < 0.47 else ''
    # log_data = f'{star}Count: {count} - Delay: {delay} - Timestamp {timestamp}'

    # Write the updated count back to the file
    with counter_path.open("w") as file1, total_dens_counter_path.open("w") as file2:
        file1.write(str(count))
        file2.write(str(total_dens_count))
        # file2.write(log_data + '\n')
    with open(data_path, 'w') as data_file:
        json.dump(data, data_file, indent=4)
    
    if frames is not None:
        for x in range(frames.__len__()):
            cv2.imwrite(f"/Volumes/DexDrive/dynamax/{total_dens_count}-{f'{file_prefix}-{count}' if x == 3 else x}.png", frames[x])
  
def write_shiny_text():
    shiny_text_path = Path(f"shiny_text.txt")
    with shiny_text_path.open("w") as file1:
        file1.write('I got the shiny! My switch\nwill be off until I am\nback. Make sure to come\nback when/after I catch it!')



def get_screen(vid: cv2.VideoCapture):
    frame = getframe(vid)

    if (get_text(frame=frame, top_left=Point(y=502, x=1056), bottom_right=Point(y=539, x=1133), invert=True) == 'Fight'):
        return 'Fight'
    
    if (get_text(frame=frame, top_left=Point(y=46, x=26), bottom_right=Point(y=86, x=298), invert=True) == "One Trainer can choose"):
        return 'Swapping'
    
    if (get_text(frame=frame, top_left=Point(y=163, x=691), bottom_right=Point(y=198, x=1223), invert=True) == "Choose the one Pokémon you'd like to keep!"):
        return 'Choosing'
    
    if (get_text(frame=frame, top_left=Point(y=609, x=1091), bottom_right=Point(y=643, x=1205), invert=True) == 'Catch'):
        return 'Catching'
    
    if (get_text(frame=frame, top_left=Point(y=46, x=21), bottom_right=Point(y=85, x=238), invert=True) == 'Everyone will take'):
        return 'Selecting'
    
    if (get_text(frame=frame, top_left=Point(y=500, x=1053), bottom_right=Point(y=541, x=1182), invert=True) == 'Cheer On'):
        return 'Cheer On'
    
    if (get_text(frame=frame, top_left=Point(y=590, x=565), bottom_right=Point(y=642, x=689), invert=True) == 'letdown'):
        return 'Let down'
    
    if (get_text(frame=frame, top_left=Point(y=587, x=356), bottom_right=Point(y=626, x=493), invert=True) == 'Which path'):
        return 'Pathing'
    
    if (get_text(frame=frame, top_left=Point(y=51, x=344), bottom_right=Point(y=105, x=454), invert=True) == 'hold one'):
        return 'Items'
    
    if (get_text(frame=frame, top_left=Point(y=626, x=600), bottom_right=Point(y=667, x=674), invert=True) == 'rental'):
        return 'Rental'
    
    if (get_text(frame=frame, top_left=Point(y=242, x=245), bottom_right=Point(y=294, x=562), invert=True) == 'Play is being suspended.'):
        return 'Sus'
