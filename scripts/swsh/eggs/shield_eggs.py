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

from config_manager import ConfigManager

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

def _press(ser: serial.Serial, s: str, duration: float = .1, count: int = 1, sleep_time = .075, write_null_byte=True) -> None:
    for _ in range(count):
        # print(f'{s=} {duration=}')
        ser.write(s.encode())
        time.sleep(duration)
        if (write_null_byte):
            ser.write(b'0')
            time.sleep(sleep_time)

def _getframe(vid: cv2.VideoCapture) -> numpy.ndarray:
    _, frame = vid.read()
    # cv2.imshow('game', frame)
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

def increment_counter(caught_index=None):
    counter_path = Path(f'switch1-counter.txt')
    data_path = Path(__file__).resolve().parent.parent.parent / 'backend' / 'switch1_data.json'
    stream_data_path = Path(__file__).resolve().parent.parent.parent / 'backend' / 'stream_data.json'
    
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

 

    with data_path.open("r") as data_file:
        data = json.load(data_file)
    
    with stream_data_path.open("r") as stream_data_file:
        stream_data = json.load(stream_data_file)

    current_pokemon = data["pokemon"][0]

    for entry in data["pokemon"]:
        if entry["pokemon"] == stream_data['switch1_currently_hunting']:
            current_pokemon = entry
            break
         
    
    if (caught_index is not None):
        catches = current_pokemon["catches"]
        previous_encounters = 0

        for catch in catches:
            previous_encounters = previous_encounters + catch["encounters"]
        count_difference = current_pokemon["encounters"] - previous_encounters

        catches.append(  {
                    "caught_timestamp": int(time.time() * 1000),
                    "encounters": count_difference
                })
    else:
        current_pokemon["encounters"] = entry["encounters"] + 5
        with counter_path.open("w") as file1:
            file1.write(str(count))
            
    with open(data_path, 'w') as data_file:
        json.dump(data, data_file, indent=4)

class Position(NamedTuple):
    col: int
    row: int

def get_location(num):  
    box_pos = num % 30
    if (box_pos == 0):
        box_pos = 30
    row = int((box_pos - 1)/6) 
    col = box_pos % 6
    if (col == 0):
        col = 5
    else:
        col = col - 1
    
    return Position(col=col, row=row)

def make_move(ser: serial.Serial, from_pos, to_pos, move_vertical = False,):
    difference = to_pos - from_pos

    invert = True
    if (difference >= 0):
        invert = False

    if (move_vertical):
        _press(ser, '2' if not invert else '4', count=abs(difference), sleep_time=0.5)
    else:
        _press(ser, '1' if not invert else '3', count=abs(difference), sleep_time=0.5)

def oh_text_showing(vid: cv2.VideoCapture):
    frame = _getframe(vid)
    return get_text(frame=frame, top_left=Point(y=590, x=260), bottom_right=Point(y=635, x=351), invert=True) == 'Oh?'

def handle_fetch(ser: serial.Serial, vid: cv2.VideoCapture,):
    _press(ser, 'a', duration=0.75, sleep_time=0.2)
    _press(ser, 'w', duration=0.5, sleep_time=0.2)
    _press(ser, 'e', duration=2, sleep_time=0.2)
    time.sleep(0.5)
  

    # Now stading in front of worker and talking to him
    frame = _getframe(vid)
    oh_text = oh_text_showing(vid)

    if (oh_text):
        handle_hatch(ser, vid)
        return
    
    _press(ser, 'A', sleep_time=1)
    handle_return_from_fetch(ser, vid)

def handle_return_from_fetch(ser: serial.Serial, vid: cv2.VideoCapture,):
    frame = _getframe(vid)
    current_text = get_text(frame=frame, top_left=Point(y=586, x=262), bottom_right=Point(y=641, x=495), invert=True)
    
    if current_text == 'Welcome to th':
        print('No egg')
        _press(ser, 'B', count=5, sleep_time=1)
    elif current_text == 'We found your':
        fetched_eggs = config.get('fetched_eggs')
        config.update({'fetched_eggs': fetched_eggs + 1})
        print(f'Fetching egg {fetched_eggs}')
        _press(ser, 'A', count=5, sleep_time=0.6)
        _press(ser, 'B', count=5, sleep_time=1)
    else:
        return


def handle_hatch(ser: serial.Serial, vid: cv2.VideoCapture,):
    hatched_eggs = config.get('hatched_eggs')
    config.update({'hatched_eggs': hatched_eggs + 1})
   
    print(f'Hatching egg {hatched_eggs}')
    _press(ser, 'B', sleep_time=1)

    for x in range(12):
        _press(ser, 'B', sleep_time=1.5)

    print(f'Done hatching')
    _press(ser, 'a', duration=0.75, sleep_time=0.2)
    _press(ser, 'w', duration=0.5, sleep_time=0.2)
    _press(ser, 'e', duration=2, sleep_time=0.2)

def handle_process_eggs(ser: serial.Serial, vid: cv2.VideoCapture,):
    print('Processing eggs!')
    config.update({'fetched_eggs': 0, 'hatched_eggs': 0})
    _press(ser, 'X', sleep_time=1.5)
    _press(ser, 'A', sleep_time=1.5)
    _press(ser, 'R', sleep_time=2)

    _press(ser, 'a', sleep_time=.5)

    line_count = 5

    # Check for any shiny
    for x in range(5):
        _press(ser, 's', sleep_time=.75)
        is_shiny = check_if_shiny(vid)
        if (is_shiny):
            print(f'We have a shiny at index {x}!')
            increment_counter(caught_index=x)
            line_count = line_count - 1
            # Pick shiny up 
            print('Picking shiny up')
            _press(ser, 'A', sleep_time=0.75, count=2)
            time.sleep(1)
            # Put in open spot
            print('Putting in open spot')
            _press(ser, 'w', count = x + 1, sleep_time=0.5)
            _press(ser, 'd', sleep_time=0.5)
            _press(ser, 'R', sleep_time=2)
            move_location = get_location(config.get('open_slot'))
            config.update({'open_slot': config.get('open_slot') + 1})

            make_move(ser, from_pos=0, to_pos=move_location.row, move_vertical=True)
            make_move(ser, from_pos=0, to_pos=move_location.col, move_vertical=False)
            _press(ser, 'A', sleep_time=1.5)

            # Come back
            make_move(ser, from_pos=move_location.row, to_pos=0, move_vertical=True)
            make_move(ser, from_pos=move_location.col, to_pos=0, move_vertical=False)
            _press(ser, 'a', sleep_time=0.5)
            _press(ser, 's', count = x, sleep_time=0.5)
            _press(ser, 'L', sleep_time=2)
        else:   
            print(f'Pokemon at index {x} is not shiny')

    increment_counter(caught_index=None)
    _press(ser, 'w', count=line_count - 1, sleep_time=0.25)

    # Delete all non shiny
    for _ in range(line_count):
        _press(ser, 'A', sleep_time=.75)
        _press(ser, 'w', count=2, sleep_time=0.25)
        _press(ser, 'A', sleep_time=.75)
        _press(ser, 'w', sleep_time=0.25)
        _press(ser, 'A', count=2, sleep_time=.75)

    # Bring over next batch
    _press(ser, 'd', sleep_time=.5)
    _press(ser, 'w', sleep_time=.5)
    _press(ser, 'Y', count=2, sleep_time=0.25)
    _press(ser, 'A', sleep_time=0.3)
    _press(ser, 's', count=4, sleep_time=0.25)
    _press(ser, 'A', sleep_time=0.3)
    _press(ser, 'a', sleep_time=0.3)
    _press(ser, 's', sleep_time=0.3)
    _press(ser, 'A', sleep_time=.5)

    print('Exiting eggs')
    _press(ser, 'B', count=3, sleep_time=3)
    time.sleep(1)
    _press(ser, 's', duration=1)
    _press(ser, 'a', duration=1)

def check_if_shiny(vid: cv2.VideoCapture):
    frame = _getframe(vid)

    y1, x1, y2, x2 = 112, 1185, 151, 1253
    roi = frame[y1:y2, x1:x2]
    target_color = (64, 63, 255)

    found = any(_color_near(pixel, target_color) for row in roi for pixel in row)

    if found:
        return True
    
    return False

config = ConfigManager()

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--serial', default='/dev/tty.usbserial-110')
    args = parser.parse_args()

    vid = cv2.VideoCapture(2)
    vid.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    vid.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    vid.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    start_time = time.time()

    # print(get_text(frame=_getframe(vid), top_left=Point(y=586, x=262), bottom_right=Point(y=641, x=495), invert=True))
    # return 0
    with serial.Serial(args.serial, 9600) as ser, _shh(ser):
        time.sleep(1)
        # go_to_change_grip(ser)
        # connect_and_go_to_game(ser)
        # handle_process_eggs(ser, vid)
        # print(check_if_shiny(vid))
        # handle_fetch(ser, vid)
        # return 0
        while True:

            for x in range (5):
                if (oh_text_showing(vid)):
                    handle_hatch(ser, vid)
                    break

                _press(ser, 's', duration=0.5, write_null_byte=False)
                _press(ser, 'a', duration=0.5, write_null_byte=False)
                _press(ser, 'w', duration=0.5, write_null_byte=False)
                _press(ser, 'd', duration=0.5, write_null_byte=False)

            handle_return_from_fetch(ser, vid)
            # return 0
            if (config.get('fetched_eggs') < 5):
                handle_fetch(ser, vid)

            if (config.get('fetched_eggs') > 4 and config.get('hatched_eggs') < 5):
                continue

            if (config.get('fetched_eggs') > 4 and config.get('hatched_eggs') > 4):
                ser.write(b'0')
                time.sleep(0.5)

                handle_process_eggs(ser, vid)

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
