from __future__ import annotations

import argparse

import cv2
import numpy

from engine import Color
from engine import get_text
from engine import make_vid
from engine import Point


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--image')
    parser.add_argument('--screenshot')
    args = parser.parse_args()

    if args.image:
        def getframe() -> numpy.ndarray:
            return cv2.imread(args.image)
    else:
        vid = make_vid()

        def getframe() -> numpy.ndarray:
            return vid.read()[1]

    pos = Point(y=-1, x=-1)
    start: Point | None = None

    def cb(event: int, x: int, y: int, flags: object, param: object) -> None:
        nonlocal start, pos

        if event == cv2.EVENT_MOUSEMOVE:
            pos = Point(y=y, x=x)
        elif event == cv2.EVENT_LBUTTONDOWN:
            start = Point(y=y, x=x)
        elif event == cv2.EVENT_LBUTTONUP:
            assert start is not None
            start = start.denorm(frame.shape)
            end = Point(y=y, x=x).denorm(frame.shape)

            current = getframe()
            if start == end:
                print(f'match_px({end}, {Color(*current[y][x])})')
                arr = numpy.array([[current[y][x]]])
                print(f'hsv: {cv2.cvtColor(arr, cv2.COLOR_BGR2HSV)}')
            else:
                start, end = min(start, end), max(start, end)
                for invert in (True, False):
                    text = get_text(current, start, end, invert=invert)
                    print('match_text(')
                    print(f'    {text!r},')
                    print(f'    {start},')
                    print(f'    {end},')
                    print(f'    invert={invert},')
                    print(')')

            start = None

    cv2.namedWindow('game2')
    cv2.setMouseCallback('game2', cb)

    if args.screenshot:
        frame = getframe()
        cv2.imwrite(f"{args.screenshot}.png", frame)  # Save as PNG
        print("Screenshot saved!")
        return 0

    while True:
        frame = getframe()

        if start is not None:
            cv2.rectangle(
                frame,
                (start.x, start.y),
                (pos.x, pos.y),
                Color(b=255, g=0, r=0),
                1,
            )

        cv2.imshow('game2', frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            raise SystemExit(0)
        elif key == ord('s'):
            cv2.imwrite('screen.png', frame)

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
