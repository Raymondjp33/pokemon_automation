from __future__ import annotations

import argparse
import contextlib
from pathlib import Path
import time
from collections.abc import Generator
from PIL import Image
from typing import NamedTuple

import cv2
import numpy
import serial

import tesserocr
from typing import Protocol
import functools

from config_manager import ConfigManager
import pytesseract
import os
import csv

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
        #/opt/homebrew/Cellar/tesseract/5.5.0_1/share/
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


def _press(ser: serial.Serial, s: str, duration: float = .1, count: int = 1, sleep_time = .075) -> None:
    for _ in range(count):
        # print(f'{s=} {duration=}')
        ser.write(s.encode())
        time.sleep(duration)
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

def increment_counter(delay: float, file_prefix, frame=None):
    counter_path = Path(f'{file_prefix}-counter.txt')
    log_path = Path(f"{file_prefix}-log.txt")
    
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

    timestamp  = time.strftime('%Y-%m-%d %H:%M:%S')
    star = '* ' if delay > 0.53 or delay < 0.47 else ''
    log_data = f'{star}Count: {count} - Delay: {delay} - Timestamp {timestamp}'

    # Write the updated count back to the file
    with counter_path.open("w") as file1, log_path.open("a") as file2:
        file1.write(str(count))
        file2.write(log_data + '\n')
    
    if frame is not None:
        cv2.imwrite(f"/Volumes/DexDrive/shield/{file_prefix} - {count}.png", frame)
  
def write_shiny_text():
    shiny_text_path = Path(f"shiny_text_switch2.txt")
    with shiny_text_path.open("w") as file1:
        file1.write('I got the shiny! My switch\nwill be off until I am\nback. Make sure to come\nback when/after I catch it!')

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

def extract_encounter_text(vid: cv2.VideoCapture) -> str:
    frame = _getframe(vid)
    width, height = frame.size
    crop_box = (0, int(height * 0.8), width, height) 
    cropped_image = frame.crop(crop_box)
    text = pytesseract.image_to_string(cropped_image)
    return text.strip()

def extract_encounter_text() -> str:
    image = Image.open('/Users/raymondprice/Desktop/other/test_coding/pokemon_scripts/pokemon_automation/scripts/swsh/test 1.png')
    width, height = image.size
    crop_box = (0, int(height * 0.8), width, height)  # Bottom 20% of the image
    cropped_image = image.crop(crop_box)
    text = pytesseract.image_to_string(cropped_image)
    return text.strip()

def increment_pokemon_counter(name: str):
    print(f'Incrementing counter for {name}')
    

def handle_encounter_pokemon():
    print('Encountering Pokemon')



# encounter_config = ConfigManager(Path(__file__).parent / 'encounter_data.json')
# catch_config = ConfigManager(Path(__file__).parent.parent.parent / 'backend' / 'switch1_data.json')

def main() -> int:
    print(extract_encounter_text())
    # parser = argparse.ArgumentParser()
    # parser.add_argument('--serial', default='/dev/tty.usbserial-120')
    # args = parser.parse_args()

    # vid = cv2.VideoCapture(2)
    # vid.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    # vid.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    # vid.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    # x_val = 1143
    # y_val = 640
  
    # with serial.Serial(args.serial, 9600) as ser, _shh(ser):
    #     # Encounter pokemon (Caputre pokemon name, increment encounters for specific pokemon)

    #         # If shiny - attempt catch 
    #         # If not shiny - knock pokemon out

    #     # Check status

    #         # If out of pp - Attempt going back to pokecenter
    #         # If not out of pp - continue

    #     print('running')


    # vid.release()
    # cv2.destroyAllWindows()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
