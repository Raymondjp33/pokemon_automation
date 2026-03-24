from __future__ import annotations

import argparse
import time

import serial
from common import SWITCH1_SERIAL, SWITCH2_SERIAL, SWITCH3_SERIAL, press


def main() -> int:

    switch1 = SWITCH1_SERIAL
    switch2 = SWITCH2_SERIAL
    switch3 = SWITCH3_SERIAL

    parser = argparse.ArgumentParser()
    # parser.add_argument('--serial', default=SERIAL_DEFAULT)
    # parser.add_argument('--serial', default=switch2) # Switch 2
    parser.add_argument("--serial", default=switch1)  # Switch 1
    parser.add_argument("--switch", type=float, default=1)

    args = parser.parse_args()

    serial_input = switch1 if args.switch == 1 else switch2 if args.switch == 2 else switch3

    with serial.Serial(serial_input, 9600) as ser:
        time.sleep(1)
        while True:
            user_input = input("> ").strip()
            inputs = user_input.split(" ")

            duration = 0.1
            count = 1
            if inputs.__contains__("dur"):
                duration = float(inputs[inputs.index("dur") + 1])

            if inputs.__contains__("count"):
                count = int(inputs[inputs.index("count") + 1])

            if user_input.lower() == "exit":
                break

            elif user_input:  # Filter single character keys
                for _ in range(count):
                    # print(f'Here and user input is {inputs[0]}')
                    # ser.write(inputs[0].encode())
                    # ser.write(b'\n')
                    # time.sleep(duration)
                    # ser.write('0\n'.encode())
                    # time.sleep(.05)
                    # print(f"Sent: {inputs[0]}")
                    press(ser, inputs[0], duration=duration, count=count)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
