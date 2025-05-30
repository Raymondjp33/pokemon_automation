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
import re

from config_manager import ConfigManager

os.environ['TESSDATA_PREFIX'] = '/opt/homebrew/Cellar/tesseract/5.5.0_1/share/tessdata'
pytesseract.pytesseract.tesseract_cmd = r'/opt/homebrew/Cellar/tesseract/5.5.0_1/bin/tesseract'


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

def write_shiny_text():
    shiny_text_path = Path(f"shiny_text_switch2.txt")
    with shiny_text_path.open("w") as file1:
         file1.write('I got the shiny! My switch\nwill be off until I am\nback. Make sure to come\nback when/after I catch it!')

def increment_counter(pokemon_name, caught_index=None):
    counter_path = Path(f'current-counter.txt')
    data_path = Path(__file__).resolve().parent.parent.parent / 'backend' / 'switch2_data.json'
    stream_data_path = Path(__file__).resolve().parent.parent.parent  / 'backend' / 'stream_data.json'
    
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
    count += 1

    with data_path.open("r") as data_file, stream_data_path.open("r") as stream_data_file:
        data = json.load(data_file)
        stream_data = json.load(stream_data_file)

    current_pokemon = None

    for entry in data["pokemon"]:
        if entry["pokemon"] == pokemon_name:
            current_pokemon = entry
            break
         
    end_program = False
    if (caught_index is not None):
        catches = current_pokemon["catches"]

        catches.append(  {
                    "caught_timestamp": int(time.time() * 1000),
                    "encounters": current_pokemon["encounters"] + 1,
                    "encounter_method": "fishing",
                })
        
        if len(catches) >= stream_data["switch2_target"]:
            end_program = True
    else:
        current_pokemon["encounters"] = current_pokemon["encounters"] + 1
        with counter_path.open("w") as file1:
            file1.write(str(count))
            
    with open(data_path, 'w') as data_file:
        json.dump(data, data_file, indent=4)

    return end_program

def extract_encounter_text(vid: cv2.VideoCapture) -> str:
    frame = _getframe(vid)
    height, width = frame.shape[:2]
    crop_box = frame[int(height * 0.8):height, 0:width]
    cropped_rgb = cv2.cvtColor(crop_box, cv2.COLOR_BGR2RGB)
    text = pytesseract.image_to_string(cropped_rgb)
    return text.strip()

def extract_pokemon_name(text):
    match = re.search(r"You encountered a wild (\w+)!?", text)
    if match:
        return match.group(1)
    return None

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--serial', default='/dev/tty.usbserial-110')
    args = parser.parse_args()

    vid = cv2.VideoCapture(2)
    vid.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    vid.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    vid.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    x_val = 1143
    y_val = 640

    start_time = time.time()
    timeout = 0

    with serial.Serial(args.serial, 9600) as ser, _shh(ser):
        time.sleep(1)
        while True:

            # Start fishing
            _press(ser, 'A')
            time.sleep(2)

            # Wait to reel
            bad_reel = False
            frame = _getframe(vid)
            while not _color_near(frame[241][720], (240, 240, 240)) and timeout < 200:
                # print(frame[241][720])
                time.sleep(0.1)
                frame = _getframe(vid)
                timeout += 1
                if timeout % 5 == 0:
                    current_text = get_text(frame=frame, top_left=Point(597, 273), bottom_right=Point(636, 752), invert=True)
                    if current_text == "You reeled your line in too slow!" or current_text == 'You reeled your line in too fast!':
                        bad_reel = True
                        break
        
            if (bad_reel):
                print('Reeled too slow or fast!')
                time.sleep(1)
                _press(ser, 'B')
                time.sleep(7)
                continue
            
            # Reel the pokemon
            print('Reeling!')
            _press(ser, 'A')
            timeout = 0

            while timeout < 60:
                frame = _getframe(vid)
                current_text = extract_encounter_text(vid)
                # print(f'here and current text is {current_text}')
                timeout += 1
                pokemon = None
                if 'You encountered' in current_text:
                    time.sleep(0.1)
                    current_text = extract_encounter_text(vid)
                    pokemon = extract_pokemon_name(current_text)
                    break
                time.sleep(0.4)

                if timeout % 5 == 0:
                    current_text = get_text(frame=frame, top_left=Point(597, 273), bottom_right=Point(636, 752), invert=True)
                    if current_text == "You reeled your line in too slow!" or current_text == 'You reeled your line in too fast!':
                        bad_reel = True
                        break
            
            if (bad_reel):
                print('Reeled too slow or fast!')
                time.sleep(1)
                _press(ser, 'B')
                time.sleep(7)
                continue
            timeout = 0

            # Wait for encounter text to go away, noting delay
            _await_pixel(ser, vid, x=x_val, y=y_val, pixel=(58, 58, 58))
            print(f'{pokemon} appeared!')
            _await_not_pixel(ser, vid, x=x_val, y=y_val, pixel=(58, 58, 58))
            log_frame = _getframe(vid)
            t0 = time.time()

            _await_pixel(ser, vid, x=x_val, y=y_val, pixel=(58, 58, 58))
            t1 = time.time()

            delay = t1 - t0
            print(f'dialog delay: {delay:.3f}s')

            if (delay) > 0.5:
                print('SHINY!!!')
                _press(ser, 'C', duration=2)
                _press(ser, 'H', duration=1)
                _press(ser, 's', duration=0.25)
                _press(ser, 'd', duration=0.25)
                _press(ser, 'd', duration=0.25)
                _press(ser, 'd', duration=0.25)
                _press(ser, 'd', duration=0.25)
                _press(ser, 'd', duration=0.25)
                _press(ser, 'd', duration=0.25)
                _press(ser, 'A', duration=1)
                _press(ser, 'w', duration=1)
                _press(ser, 'A', duration=1)
                increment_counter(pokemon_name=pokemon, frame=log_frame)
                write_shiny_text()
                return 0

            increment_counter(pokemon_name=pokemon)

            frame = _getframe(vid)
            while not numpy.array_equal(frame[669][1152], (255, 255, 255)):
                frame = _getframe(vid)
                time.sleep(1)
            
            _press(ser, 'w', sleep_time=.5)
            _press(ser, 'A',  sleep_time= 6)

 
            end_time = time.time()
            print(f'Total runtime: {(end_time-start_time):.3f}s')
            start_time = time.time()
            time.sleep(7)
            # return 0

    vid.release()
    cv2.destroyAllWindows()
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
