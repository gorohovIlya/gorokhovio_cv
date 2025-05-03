import cv2
import numpy as np
import time
import json
import os
import random
from collections import defaultdict

cv2.namedWindow("Camera", cv2.WINDOW_NORMAL)
capture = cv2.VideoCapture(0)
capture.set(cv2.CAP_PROP_EXPOSURE, 1)
capture.set(cv2.CAP_PROP_EXPOSURE, -5)

color = (59, 129, 215) #HSV

lower = np.array([50, 85, 145])
upper = np.array([72, 255, 255])

def get_color(image):
    x,y,w,h = cv2.selectROI("Color selection", image)
    x,y,w,h = int(x), int(y), int(w), int(h)
    roi = image[y:y+h, x:x+w]
    color = (np.median(roi[:, :, 0]),
             np.median(roi[:, :, 1]),
             np.median(roi[:, :, 2]),
             )
    cv2.destroyWindow("Color selection")
    return color

def get_ball(image, color):
    n_lower = (np.max(color[0] - 8), color[1] * 0.8, color[2] * 0.8)
    n_upper = (color[0] + 8, 255, 255)
    mask = cv2.inRange(image, n_lower, n_upper)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if len(contours) > 0:
        contour = max(contours, key=cv2.contourArea)
        (x, y), radius = cv2.minEnclosingCircle(contour)
        if radius > 30:
            return True, (int(x), int(y), radius, mask)
    return False, (-1, -1, -1, np.array([]))


path = "settings.json"
if os.path.exists(path):
    base_colors = json.load(open(path, "r"))
else:
    base_colors = {}
game_started = False
guess_colors = []
while capture.isOpened():
    ret, frame = capture.read()
    curr_time = time.time()
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
    key = chr(cv2.waitKey(1) & 0xFF)
    if key == "q":
        break
    if key in "123":
        color = get_color(hsv)
        base_colors[key] = color
        print(base_colors)
    all_masks = []
    balls_info = []
    for key in base_colors:
        retr, (x, y, radius, mask) = get_ball(hsv, base_colors[key])
        all_masks.append(mask)
        if retr:
            balls_info.append((x, y, radius))
        for x, y, radius in balls_info:
            cv2.circle(frame, (x, y), int(radius), (255, 0, 255), 2)

        if len(base_colors) == 3 and not game_started:
            guess_colors = list(base_colors)
            random.shuffle(guess_colors)
            game_started = True

        if game_started:
            balls_coords = defaultdict(lambda: 0)
            for k in base_colors.keys():
                retr, (x, y, radius, mask) = get_ball(hsv, np.array(base_colors[k]))
                if retr:
                    balls_coords[k] = x
                    res = sorted(list(balls_coords), key=lambda x: balls_coords[x])
                    print(f"{res=}")
                    print(f"{guess_colors=}")
                    if "".join(res) == "".join(guess_colors):
                        cv2.putText(frame, "YOU WIN!",
                                    (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 0, 0))
                        print("KHBNkljbnkl")
    cv2.putText(frame, f"Game started = {game_started}",
                (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255))
    cv2.imshow("Camera", frame)

capture.release()
cv2.destroyAllWindows()

json.dump(base_colors, open(path, "w"))