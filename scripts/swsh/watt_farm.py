from services.common import *
import cv2

def main():
    ser_str = SWITCH2_SERIAL

    with serial.Serial(ser_str, 9600) as ser, shh(ser):
        time.sleep(1)
        while True:
                press(ser, 'H', sleep_time=1)
                press(ser, 'd', count=2)
                press(ser, 's')
                press(ser, 'd', count=2)
                press(ser, 'A', sleep_time=1.25)
                press(ser, 's', duration=1.75)
                press(ser, 'd', sleep_time=0.3)
                press(ser, 's', count=9)
                press(ser, 'A', sleep_time=0.5)
                press(ser, 's', count=2)
                press(ser, 'A', sleep_time=0.5)
                press(ser, 'd')
                press(ser, 'w')
                press(ser, 'd', count=5)
                press(ser, 'A', sleep_time=0.5)
                press(ser, 'H', sleep_time=0.5, count=2)
                time.sleep(0.8)
                press(ser, 's', sleep_time=0.5)
                press(ser, 'A', sleep_time=0.5, count=3)
                time.sleep(3)
                press(ser, 'A', sleep_time=0.5, count=5)
                time.sleep(2.5)


    cv2.destroyAllWindows()
    return 0
        
main()