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

class Color(NamedTuple):
    b: int
    g: int
    r: int

def _press(ser: serial.Serial, s: str, duration: float = .1, count: int = 1, sleep_time = .05) -> None:
    for _ in range(count):
        # print(f'{s=} {duration=}')
        ser.write(s.encode())
        time.sleep(duration)
        ser.write(b'.')
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
    _press(ser, '0')

def go_to_change_grip(ser: serial.Serial):
    _press(ser, 'H')
    time.sleep(1)
    _press(ser, 's')
    _press(ser, 'd', count=4)
    _press(ser, 'A')
    time.sleep(1)
    _press(ser, 'A')
    # time.sleep(1)
    # _press(ser, 'A')
    
def reset_game(ser: serial.Serial, vid: cv2.VideoCapture,):
    _press(ser, 'H')
    time.sleep(1)
    _press(ser, 'X')
    time.sleep(1)
    _press(ser, 'A')


def get_to_statue(ser: serial.Serial):
    _press(ser, 'd', duration=0.3, sleep_time=0.3)
    _press(ser, 'w', duration=3)
    _press(ser, 'A', sleep_time=1, count=3)

def increment_day(ser: serial.Serial):
    _press(ser, 's',sleep_time=0.3)
    _press(ser, 'd', count=7)
    _press(ser, 'A', sleep_time=1.25)
    _press(ser, 's', count=17)
    _press(ser, 'd')
    _press(ser, 's', count=10)
    _press(ser, 'A', sleep_time=0.75)
    _press(ser, 's', count=2)
    _press(ser, 'A', sleep_time=0.75)
    _press(ser, 'd')
    _press(ser, 'w')
    _press(ser, 'd', count=5)
    _press(ser, 'A', sleep_time=0.75)

def run_away(ser: serial.Serial):
    _press(ser, 'w', sleep_time=0.5)
    _press(ser, 'A', sleep_time=5)
    _press(ser, 'A', sleep_time=1.5)

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

  
    with serial.Serial(args.serial, 9600) as ser, _shh(ser):
        time.sleep(1)
        # go_to_change_grip(ser)
        # connect_and_go_to_game(ser)
        # get_to_statue(ser)
        # increment_day(ser)
        # reset_game(ser, vid)
        # return 0
        while True:
           
           # From the loading screen of den after invite others
           _press(ser, 'H', sleep_time=1)

           # Increment to next day
           increment_day(ser)

           # Go back to game
           _press(ser, 'H', count=2, sleep_time=1)

           # Exit and then start den again
           _press(ser, 's')
           _press(ser, 'A', sleep_time=0.75, count=5)
           _press(ser, 'A', sleep_time=3.5)
           _press(ser, 'A', sleep_time=0.5, count=4)
           time.sleep(3)
        #    return 0


    vid.release()
    cv2.destroyAllWindows()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
