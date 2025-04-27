from __future__ import annotations

import argparse
import time

import serial

def main() -> int:
    parser = argparse.ArgumentParser()
    # parser.add_argument('--serial', default=SERIAL_DEFAULT)
    # parser.add_argument('--serial', default='/dev/tty.usbserial-120') # Switch 2
    parser.add_argument('--serial', default='/dev/tty.usbmodem1101') # Switch 1
    
    args = parser.parse_args()

    with serial.Serial(args.serial, 9600) as ser:
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
                ser.write(user_input[0].encode())
                time.sleep(duration)
                ser.write(b'.')
                time.sleep(.05)
                print(f"Sent: {user_input[0]}")



    return 0


if __name__ == '__main__':
    raise SystemExit(main())
