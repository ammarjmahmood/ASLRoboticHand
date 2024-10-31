import json

import numpy as np
import cv2
import landmarks
import mediapipe as mp

stored = {}
try:
    with open("stored.json", mode="r") as file:
        if file.read():
            file.seek(0)
            stored = json.load(file)
except FileNotFoundError:
    print("no stored.json loaded")

# x to exit
cap = cv2.VideoCapture(0)
try:
    if not cap.isOpened():
        exit("cannot open camera")
    while True:
        ret, bgr_data = cap.read()
        if not ret:
            exit("no frame to read")
        cv2.imshow("frame", bgr_data)
        char = cv2.waitKey(1)
        if char == b"x"[0]: # exit
            exit()
        rgb_data = cv2.cvtColor(bgr_data, cv2.COLOR_BGR2RGB)
        frame = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_data)
        result = landmarks.detector.detect(frame)
        if len(result.hand_world_landmarks) != 1:
            print(f'unexpected number of hands: {len(result.hand_world_landmarks)}')
            continue
        positions = [[landmark.x, landmark.y, landmark.z] for landmark in result.hand_world_landmarks[0]]
        positions = landmarks.normalize(positions)
        if not stored:
            print("matched nothing")
            continue
        scores = landmarks.closest(positions, stored)
        best_score = min(score[0] for score in scores)
        names = {score[1] for score in scores if best_score == score[0]}
        if len(names) != 1:
            print(f'multiple names matched: {(names)}')
            continue
        best = [score for score in scores if best_score == score[0]][0]
        print(f'matched {best[0]} {best[2]}')
finally:
    cap.release()
    cv2.destroyAllWindows()
