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
import csv

os.environ['TESSDATA_PREFIX'] = '/opt/homebrew/Cellar/tesseract/5.5.0/share/tessdata'
pytesseract.pytesseract.tesseract_cmd = r'/opt/homebrew/Cellar/tesseract/5.5.0/bin/tesseract'

class Color(NamedTuple):
    b: int
    g: int
    r: int

class Point(NamedTuple):
    y: int
    x: int

    def norm(self, dims: tuple[int, int, int]) -> Point:
        return type(self)(
            int(self.y / NORM.y * dims[0]),
            int(self.x / NORM.x * dims[1]),
        )

    def denorm(self, dims: tuple[int, int, int]) -> Point:
        return type(self)(
            int(self.y / dims[0] * NORM.y),
            int(self.x / dims[1] * NORM.x),
        )

NORM = Point(y=720, x=1280)

@functools.lru_cache
def _tessapi() -> tesserocr.PyTessBaseAPI:
    return tesserocr.PyTessBaseAPI(
        '/opt/homebrew/share/tessdata',
        'eng',
        psm=tesserocr.PSM.SINGLE_LINE,
    )

class Matcher(Protocol):
    def __call__(self, frame: numpy.ndarray) -> bool: ...

def tess_text_u8(
        img: numpy.ndarray,
        *,
        tessapi: tesserocr.PyTessBaseAPI | None = None,
) -> str:
    tessapi = tessapi or _tessapi()

    tessapi.SetImageBytes(
        img.tobytes(),
        width=img.shape[1],
        height=img.shape[0],
        bytes_per_pixel=1,
        bytes_per_line=img.shape[1],
    )
    return tessapi.GetUTF8Text().strip()

def get_text(
        frame: numpy.ndarray,
        top_left: Point,
        bottom_right: Point,
        *,
        invert: bool,
        tessapi: tesserocr.PyTessBaseAPI | None = None,
) -> str:
    tl_norm = top_left.norm(frame.shape)
    br_norm = bottom_right.norm(frame.shape)

    crop = frame[tl_norm.y:br_norm.y, tl_norm.x:br_norm.x]
    crop = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    _, crop = cv2.threshold(
        crop, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU,
    )
    if invert:
        crop = cv2.bitwise_not(crop)

    return tess_text_u8(crop, tessapi=tessapi)

def _press(ser: serial.Serial, s: str, duration: float = .1, count: int = 1, sleep_time = .075, write_null_byte=True, print_output=False) -> None:
    for _ in range(count):
        if (print_output):
            print(f'{s=} {duration=}')
        ser.write(s.encode())
        time.sleep(duration)
        if (write_null_byte):
            ser.write(b'0')
            time.sleep(sleep_time)

def _getframe(vid: cv2.VideoCapture, show_frame=False) -> numpy.ndarray:
    _, frame = vid.read()
    if (show_frame):
        cv2.imshow('game', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        raise SystemExit(0)
    return frame

def _wait_and_render(vid: cv2.VideoCapture, t: float) -> None:
    end = time.time() + t
    while time.time() < end:
        _getframe(vid)

def _await_pixel(
        ser: serial.Serial,
        vid: cv2.VideoCapture,
        *,
        x: int,
        y: int,
        pixel: tuple[int, int, int],
        timeout: float = 90,
        exact_pixel: bool = True,
) -> None:
    end = time.time() + timeout
    frame = _getframe(vid)

    compare = numpy.array_equal if exact_pixel else _color_near

    while not compare(frame[y][x], pixel):
        frame = _getframe(vid)

def _await_not_pixel(
        ser: serial.Serial,
        vid: cv2.VideoCapture,
        *,
        x: int,
        y: int,
        pixel: tuple[int, int, int],
        timeout: float = 90,
        exact_pixel: bool = True,
) -> None:
    end = time.time() + timeout
    frame = _getframe(vid)
    compare = numpy.array_equal if exact_pixel else _color_near
    while compare(frame[y][x], pixel):
        frame = _getframe(vid)

def _color_near(pixel: numpy.ndarray, expected: tuple[int, int, int]) -> bool:
    total = 0
    for c1, c2 in zip(pixel, expected):
        total += (c2 - c1) * (c2 - c1)

    return total < 76

@contextlib.contextmanager
def _shh(ser: serial.Serial) -> Generator[None]:
    try:
        yield
    finally:
        ser.write(b'.')    

def connect_and_go_to_game(ser: serial.Serial):
    _press(ser, 'H', sleep_time=1)
    _press(ser, 'H', duration=0.1)
    _press(ser, 'A', duration=0.5)
    _press(ser, 'H', duration=0.1)
    _press(ser, 'A', sleep_time=1)
    _press(ser, 'A')
    _press(ser, '0')

def go_to_change_grip(ser: serial.Serial):
    _press(ser, 'H')
    time.sleep(1)
    _press(ser, 's')
    _press(ser, 'd', count=4)
    _press(ser, 'A')
    time.sleep(1)
    _press(ser, 'A')
    
def reset_game(ser: serial.Serial, vid: cv2.VideoCapture,):
    _press(ser, 'H')
    time.sleep(1)
    _press(ser, 'X')
    time.sleep(1)
    _press(ser, 'A')

    frame = _getframe(vid)
    while not _color_near(frame[50][90], (250, 250, 250)):
        _press(ser, 'A')
        _wait_and_render(vid, .15)
        frame = _getframe(vid)

    print('game loaded!')

def get_pokemon_name(vid: cv2.VideoCapture):
    frame = _getframe(vid)
    # Switch 1
    # return get_text(frame=frame, top_left=Point(y=570, x=89), bottom_right=Point(y=607, x=221), invert=True)

    # Switch 2
    return get_text(frame=frame, top_left=Point(y=571, x=67), bottom_right=Point(y=603, x=205), invert=True)

def check_if_shiny(vid: cv2.VideoCapture):
    frame = _getframe(vid)

    y1, x1, y2, x2 = 557, 527, 602, 557
    roi = frame[y1:y2, x1:x2]
    target_color = (255, 255, 255)

    found = any(_color_near(pixel, target_color) for row in roi for pixel in row)

    if found:
        return True
    
    return False

def load_pokemon_species_ids():
    name_to_species_id = {}

    with open(Path(__file__).resolve().parent / 'pokemon.csv', mode='r', encoding='utf-8') as file:
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
        _press(ser, '2' if not invert else '4', count=abs(difference))
    else:
        _press(ser, '1' if not invert else '3', count=abs(difference))

def move_to_box(ser: serial.Serial, from_box: Position, to_box: Position, from_old = True):
    if not from_old:
        temp = from_box
        from_box = to_box
        to_box = temp
    
    page_dif = to_box.boxOrPage - from_box.boxOrPage

    if (page_dif != 0):
        move_left = page_dif < 0
        _press(ser, 'L' if move_left else 'R', count=abs(page_dif), sleep_time=1.25)

    make_move(ser, from_box.row, to_box.row, move_vertical=True)
    make_move(ser, from_box.col, to_box.col, move_vertical=False)

    _press(ser, 'A', sleep_time=1)

def main() -> int:

    pokemon_map = load_pokemon_species_ids()

    with open("boxed_pokemon.json", "r") as f:
        owned_pokemon = set(json.load(f))

    with open("boxed_shiny_pokemon.json", "r") as f:
        owned_shiny_pokemon = set(json.load(f))

    from_box = get_box_location(44, False)
    from_pokemon_num = 1
    from_pokemon = get_box_location(from_pokemon_num, False)

    parser = argparse.ArgumentParser()
    parser.add_argument('--serial', default='/dev/tty.usbserial-110')
    args = parser.parse_args()

    vid = cv2.VideoCapture(2)
    vid.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    vid.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    vid.set(cv2.CAP_PROP_BUFFERSIZE, 1)
 
    start_time = time.time()
  
    with serial.Serial(args.serial, 9600) as ser, _shh(ser):
        time.sleep(1)
        while True:
            if (from_pokemon_num > 30):
                break

            pokemon_is_shiny = check_if_shiny(vid)
            dex_num = pokemon_map.get(get_pokemon_name(vid).lower())
            already_boxed =  owned_pokemon.__contains__(dex_num) if not pokemon_is_shiny else owned_shiny_pokemon.__contains__(dex_num)

            if dex_num != None:
                if not already_boxed:
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
                owned_shiny_pokemon.add(dex_num)
                with open("boxed_shiny_pokemon.json", "w") as f:
                    json.dump(sorted(list(owned_shiny_pokemon)), f)
            else:
                owned_pokemon.add(dex_num)
                with open("boxed_pokemon.json", "w") as f:
                    json.dump(sorted(list(owned_pokemon)), f)

            from_pokemon = get_box_location(from_pokemon_num, False)
            to_pokemon = get_box_location(dex_num, pokemon_is_shiny)
            to_box = get_box_location(to_pokemon.boxOrPage + 1, False)

            # Pick up pokemon
            _press(ser, 'A', sleep_time = .5)

            # Go down to box list
            make_move(ser, from_pos=from_pokemon.col, to_pos=3, move_vertical=False)
            make_move(ser, from_pos=from_pokemon.row, to_pos=5, move_vertical=True)
            _press(ser, 'A', sleep_time = 2)

            # Go to new box number
            move_to_box(ser, from_box, to_box, from_old=True)

            # Put pokemon in correct spot
            make_move(ser, from_pos=0, to_pos=to_pokemon.row, move_vertical=True)
            make_move(ser, from_pos=0, to_pos=to_pokemon.col, move_vertical=False)
            _press(ser, 'A', sleep_time = 1)

            # Go back to box list
            make_move(ser, from_pos=to_pokemon.col, to_pos=3, move_vertical=False)
            make_move(ser, from_pos=to_pokemon.row, to_pos=5, move_vertical=True)
            _press(ser, 'A', sleep_time = 2)

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
