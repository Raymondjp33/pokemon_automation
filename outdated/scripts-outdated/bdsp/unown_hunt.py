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

def increment_counter(frame=None):
    counter_path = Path(f'switch1-counter.txt')
    data_path = Path(__file__).resolve().parent.parent.parent / 'backend' / 'switch1_data.json'
    
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

    with data_path.open("r") as data_file:
        data = json.load(data_file)

    current_pokemon = None

    for entry in data["pokemon"]:
        if entry["pokemon"] == 'Unown':
            current_pokemon = entry
            break
    
    current_pokemon["encounters"] = entry["encounters"] + 1
    if (frame is not None):
        catches = current_pokemon["catches"]

        catches.append(  {
                    "caught_timestamp": int(time.time() * 1000),
                    "encounters": current_pokemon["encounters"]
                })
        cv2.imwrite(f"/Volumes/DexDrive/poke screenshots/Unown - {count}.png", frame)
  
    with counter_path.open("w") as file1:
        file1.write(str(count))
            
    with open(data_path, 'w') as data_file:
        json.dump(data, data_file, indent=4)

      
def write_shiny_text():
    shiny_text_path = Path(f"shiny_text.txt")
    with shiny_text_path.open("w") as file1:
        file1.write('I got the shiny! My switch\nwill be off until I am\nback. Make sure to come\nback when/after I catch it!')


def handle_encounter(vid: cv2.VideoCapture, ser: serial.Serial):
    timeout = 0
    x_val = 960
    y_val = 660

    while timeout < 60:
        frame = _getframe(vid)
        current_text = get_text(frame=frame, top_left=Point(y=584, x=115), bottom_right=Point(y=642, x=590), invert=True)
        # print(f'here and current text is ${current_text}')
        if (current_text == 'You encountered a wild Unown!'):
            print('Wild Unown!')
            break
        time.sleep(0.4)

    _await_not_pixel(ser, vid, x=x_val, y=y_val, pixel=(255, 255, 255))
    log_frame = _getframe(vid)
    print(f'Unown pixel gone') 
    t0 = time.time()

    _await_pixel(ser, vid, x=x_val, y=y_val, pixel=(255, 255, 255))
    print('Go Breloom!')
    t1 = time.time()

    delay = t1 - t0
    print(f'dialog delay: {delay:.3f}s')

    if ((delay) > 0.7):
        return (True ,log_frame)
    
    # Wait until we can run
    _await_pixel(ser, vid, x=1111, y=672, pixel=(238, 127, 115))
    time.sleep(0.5)

    print('Running')
    _press(ser, 'w', sleep_time=0.3)
    _press(ser, 'A', sleep_time=0.3)

    _await_pixel(ser, vid, x=x_val, y=y_val, pixel=(255, 255, 255))
    _await_not_pixel(ser, vid, x=x_val, y=y_val, pixel=(255, 255, 255))

    _await_pixel(ser, vid, x=x_val, y=y_val, pixel=(7, 7, 7))
    _await_not_pixel(ser, vid, x=x_val, y=y_val, pixel=(7, 7, 7))
    print('Exited battle')

    return (False, log_frame)

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--serial', default='/dev/tty.usbmodem1201')
    args = parser.parse_args()

    vid = cv2.VideoCapture(1)
    vid.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    vid.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    vid.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    start_time = time.time()
  
    with serial.Serial(args.serial, 9600) as ser, _shh(ser):
        time.sleep(1)
        while True:
            start_time = time.time()

            # encountering = False
            # going_left = False

            # while not encountering:
            #     _press(ser, 'a' if going_left else 'd', duration=0.3)
            #     going_left = not going_left
            #     frame = _getframe(vid)
            #     if (_color_near(frame[660][960], (255, 255, 255))):
            #         print('Encounter starting!')
            #         encountering = True

            _press(ser, 'X', sleep_time=0.75)
            _press(ser, 'A', sleep_time=1)
            _press(ser, 'A', sleep_time=0.5)
            _press(ser, 's')
            _press(ser, 'A')
            
            shiny_encounter = handle_encounter(vid, ser)
            if (shiny_encounter[0]):
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
                increment_counter(frame=shiny_encounter[1],)
                write_shiny_text()
                return 0

            increment_counter()

            time.sleep(1) 
            end_time = time.time()
            print(f'Full encounter took {(end_time-start_time):.3f}s')
            # return 0

    vid.release()
    cv2.destroyAllWindows()
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
