from pathlib import Path
import cv2
import numpy as np
from common import *

def match_template_on_video(template_path, video_source, threshold=0.8):
    # Load template
    template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
    w, h = template.shape[::-1]

    # Open video source (0 = default webcam, or use a video file path)
    cap = cv2.VideoCapture(video_source)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Convert frame to grayscale for matching
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Match template
        result = cv2.matchTemplate(gray_frame, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        # If match exceeds threshold, draw box
        if max_val >= threshold:
            top_left = max_loc
            bottom_right = (top_left[0] + w, top_left[1] + h)
            cv2.rectangle(frame, top_left, bottom_right, (0, 255, 0), 2)
            cv2.putText(frame, f"{max_val:.2f}", (top_left[0], top_left[1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # Show frame
        cv2.imshow("Template Match (Video)", frame)

        # Exit on 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

template_path = Path(__file__).resolve().parent.parent / 'templates' / 'reel_indicator.png'
match_template_on_video(template_path, SWITCH2_VID_NUM, threshold=0.9)