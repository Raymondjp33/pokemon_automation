from __future__ import annotations
from pathlib import Path
from typing import Protocol
from collections.abc import Generator
from typing import NamedTuple

import argparse
import contextlib
import time
import cv2
import numpy
import serial
import functools
import tesserocr
import json



SWITCH1_COUNTER_PATH = Path(__file__).resolve().parent.parent / 'configs' / 'switch1-counter.txt'
SWITCH2_COUNTER_PATH = Path(__file__).resolve().parent.parent / 'configs' / 'switch2-counter.txt'
SWITCH1_SHINY_TEXT_PATH = Path(__file__).resolve().parent.parent / 'configs' / 'switch1-shiny-text.txt'
SWITCH2_SHINY_TEXT_PATH = Path(__file__).resolve().parent.parent / 'configs' / 'switch2-shiny-text.txt'
STREAM_DATA_PATH = Path(__file__).resolve().parent.parent.parent / 'backend' / 'stream_data.json'

DB_FILE = Path(__file__).resolve().parent.parent.parent / 'backend' / 'my_pokemon.db'
REDIS_CHANNEL = "update_data"

SWITCH1_SERIAL = '/dev/tty.usbmodem1201'
SWITCH2_SERIAL = '/dev/tty.usbserial-110'

SWITCH1_VID_NUM = 2
SWITCH2_VID_NUM = 3
SWITCH3_VID_NUM = 0

def make_vid(switch_num) -> cv2.VideoCapture:
    vid = cv2.VideoCapture(switch_num)
    vid.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    vid.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    vid.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # default: 3
    return vid

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

class Matcher(Protocol):
    def __call__(self, frame: numpy.ndarray) -> bool: ...

@functools.lru_cache
def _tessapi() -> tesserocr.PyTessBaseAPI:
    return tesserocr.PyTessBaseAPI(
        '/opt/homebrew/share/tessdata',
        'eng',
        psm=tesserocr.PSM.SINGLE_LINE,
    )

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

def press(ser: serial.Serial, s: str, duration: float = .1, count: int = 1, sleep_time = .075, write_null_byte=True) -> None:
    for _ in range(count):
        # print(f'{s=} {duration=}')
        ser.write(s.encode())
        time.sleep(duration)
        if (write_null_byte):
            ser.write(b'0')
            time.sleep(sleep_time)

def getframe(vid: cv2.VideoCapture) -> numpy.ndarray:
    _, frame = vid.read()
    # cv2.imshow('game', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        raise SystemExit(0)
    return frame

def wait_and_render(vid: cv2.VideoCapture, t: float) -> None:
    end = time.time() + t
    while time.time() < end:
        getframe(vid)

def await_pixel(
        vid: cv2.VideoCapture,
        *,
        x: int,
        y: int,
        pixel: tuple[int, int, int],
        timeout: float = 90,
        exact_pixel: bool = True,
) -> None:
    end = time.time() + timeout
    frame = getframe(vid)

    compare = numpy.array_equal if exact_pixel else color_near

    while not compare(frame[y][x], pixel):
        frame = getframe(vid)

def await_not_pixel(
        vid: cv2.VideoCapture,
        *,
        x: int,
        y: int,
        pixel: tuple[int, int, int],
        timeout: float = 90,
        exact_pixel: bool = True,
) -> None:
    end = time.time() + timeout
    frame = getframe(vid)
    compare = numpy.array_equal if exact_pixel else color_near
    while compare(frame[y][x], pixel):
        frame = getframe(vid)

def color_near(pixel: numpy.ndarray, expected: tuple[int, int, int]) -> bool:
    total = 0
    for c1, c2 in zip(pixel, expected):
        total += (c2 - c1) * (c2 - c1)

    return total < 76

@contextlib.contextmanager
def shh(ser: serial.Serial) -> Generator[None]:
    try:
        yield
    finally:
        ser.write(b'.')

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
        press(ser, '2' if not invert else '4', count=abs(difference), sleep_time=0.5)
    else:
        press(ser, '1' if not invert else '3', count=abs(difference), sleep_time=0.5)