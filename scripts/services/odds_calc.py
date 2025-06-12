

from __future__ import annotations

import argparse
import time

import serial

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--odds', type=int, default=4096) 
    parser.add_argument('--tries', type=int, default=1)

    args = parser.parse_args()

    tries = args.tries
    odds = args.odds
    prob = 1 - (1 - (1 / odds)) ** tries

    print(f"Probability of at least one success after {tries} tries: {prob * 100:.4f}%")

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
