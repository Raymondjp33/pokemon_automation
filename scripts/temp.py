from services.common import *
import cv2
import pytesseract
    
def run_live_ocr_bottom_right():
    cap = make_vid(SWITCH2_VID_NUM)  # default webcam

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Resize frame (optional for performance)
        # frame = cv2.resize(frame, (640, 480))  # or your target size

        h, w = frame.shape[:2]

        # Crop to bottom-right quadrant
        roi = frame[h//2:, w//2:]  # [rows, cols] = [height, width]

        # Convert to RGB for Tesseract
        roi_rgb = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)

        # OCR on the cropped region
        data = pytesseract.image_to_data(roi_rgb, output_type=pytesseract.Output.DICT)

        # Draw results on ROI
        for i, word in enumerate(data['text']):
            if word.strip() and int(data['conf'][i]) > 60:
                x, y, w_box, h_box = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                cv2.rectangle(roi, (x, y), (x + w_box, y + h_box), (0, 255, 0), 2)
                cv2.putText(roi, word, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        # Show the original frame with ROI in bottom-right overlaid
        frame[h//2:, w//2:] = roi
        cv2.imshow("Live OCR - Bottom Right", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

def ocr_from_region(frame, top_left, bottom_right, nums_only = False):
    x1, y1 = top_left
    x2, y2 = bottom_right
    roi = frame[y1:y2, x1:x2]
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

    config = '-c tessedit_char_whitelist=0123456789/' if nums_only else '--psm 6'
    data = pytesseract.image_to_data(gray, config=config, output_type=pytesseract.Output.DICT)
    lines = []

    for i, text in enumerate(data['text']):
        text = text.strip()
        conf = int(data['conf'][i])
        if text and (conf > 30 if nums_only else conf > 50):
            x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]

           
            matched = False
            for line in lines:
                if abs(line['y'] - y) < 10:
                    line['entries'].append((x, text))
                    matched = True
                    break
            
            if not matched:
                lines.append({'y': y, 'entries': [(x, text)]})

    for line in lines:
        line['entries'].sort()

    # Sort lines top to bottom
    lines.sort(key=lambda l: l['y'])

    words = [' '.join([t for _, t in line['entries']]) for line in lines]

    return words

move1 = Point(y=435, x=913), Point(y=495, x=1127)
move1P = Point(y=440, x=1155), Point(y=488, x=1254)

move2 = Point(y=504, x=914), Point(y=564, x=1129)
move2P = Point(y=515, x=1155), Point(y=554, x=1254)

move3 =  Point(y=573, x=918), Point(y=633, x=1128)
move3P = Point(y=584, x=1155), Point(y=625, x=1254)

move4 = Point(y=644, x=917), Point(y=703, x=1129)
move4P =Point(y=652, x=1155), Point(y=694, x=1254)

moves = [(move1, move1P), (move2, move2P), (move3, move3P), (move4, move4P),]

def print_moves(frame):

    for move in moves:
        move_info = move[0]
        move_p = move[1]

        info = ocr_from_region(frame, (move_info[0].x, move_info[0].y), (move_info[1].x, move_info[1].y))
        p = ocr_from_region(frame, (move_p[0].x, move_p[0].y), (move_p[1].x, move_p[1].y), nums_only=True)
        
        if len(info) <= 0 or len(p) <= 0:
            print(f'Empty array issue info: {info}, p: {p}')
            continue
        move_name = info[0]
        move_status = None
        move_p = p[0]
        if len(info) >= 2:
            move_status = info[1]
        
        print(f'Move: {move_name}, {"" if move_status is None else f"Status: {move_status}, "}P: {move_p}')
    
def main():
    ser_str = SWITCH1_SERIAL


    start_time = time.time()
    with serial.Serial(ser_str, 9600) as ser, shh(ser):
        time.sleep(1)
        while True:
                press(ser, 'A', sleep_time=1)
                # press(ser, 'q', duration=0.27, write_null_byte=False)
                # press(ser, 'e', duration=0.1, write_null_byte=False)
                # press(ser, 'c', duration=0.25, write_null_byte=False)
                # press(ser, 'z', duration=0.12, write_null_byte=False)


                # press(ser, 'q', duration=0.35, write_null_byte=False,)
                # press(ser, 'w', duration=0.1, write_null_byte=False)
                # press(ser, 'e', duration=0.1, write_null_byte=False)
                # press(ser, 'd', duration=0.1, write_null_byte=False)
                # press(ser, 'c', duration=0.25, write_null_byte=False)
                # press(ser, 's', duration=0.1, write_null_byte=False)
                # press(ser, 'z', duration=0.15, write_null_byte=False)

                # press(ser, 'a', duration=0.1, write_null_byte=False)


    cv2.destroyAllWindows()
    return 0
        
main()