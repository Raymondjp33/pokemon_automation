from __future__ import annotations

import uuid

import cv2
import numpy

def getframe(vid: cv2.VideoCapture) -> numpy.ndarray:
    _, frame = vid.read()
    if cv2.waitKey(1) & 0xFF == ord('q'):
        raise SystemExit(0)
    return frame

def main() -> int:

    vid = cv2.VideoCapture(2)
    vid.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    vid.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    vid.set(cv2.CAP_PROP_BUFFERSIZE, 1) 
    while True:
        user_input = input("> ").strip()

        if user_input.lower() == 'exit':
            break

        frame = getframe(vid)
        cv2.imwrite(f"/Volumes/Untitled/Dataset Incoming/{uuid.uuid4()}.png", frame)  
        print("Screenshot saved!")
    return 0



if __name__ == '__main__':
    raise SystemExit(main())
