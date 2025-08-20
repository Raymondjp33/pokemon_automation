from __future__ import annotations

import argparse
import time

import serial
from common import *

def main() -> int:

    switch1 = SWITCH1_SERIAL
    switch2 = SWITCH2_SERIAL
    switch3 = SWITCH3_SERIAL

    parser = argparse.ArgumentParser()
    # parser.add_argument('--serial', default=SERIAL_DEFAULT)
    # parser.add_argument('--serial', default=switch2) # Switch 2
    parser.add_argument('--serial', default=switch1) # Switch 1
    parser.add_argument('--switch', type=float, default=1)

    args = parser.parse_args()

    serial_input = switch1 if args.switch == 1 else switch2 if args.switch == 2 else switch3

    with serial.Serial(serial_input, 9600) as ser:
        time.sleep(1)
        while True:
            user_input = input("> ").strip()
            inputs = user_input.split(' ')

            duration = 0.1
            count = 1
            if (inputs.__contains__('duration')):
                duration = float(inputs[inputs.index('duration') + 1])

            if (inputs.__contains__('count')):
                count = int(inputs[inputs.index('count') + 1])

            if user_input.lower() == 'exit':
                break
            
            elif user_input:  # Filter single character keys
                for _ in range(count):
                    ser.write(user_input[0].encode())
                    time.sleep(duration)
                    ser.write(b'.')
                    time.sleep(.05)
                    print(f"Sent: {user_input[0]}")



    return 0


if __name__ == '__main__':
    raise SystemExit(main())
