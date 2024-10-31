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
# q to query saved positions
# r to reload stored.json (needed if you edit it manually)
# h to see hand positions
# s to save position (type in name in terminal)
cap = cv2.VideoCapture(0)
try:
    if not cap.isOpened():
        exit("cannot open camera")
    while True:
        try:
            ret, bgr_data = cap.read()
            if not ret:
                exit("no frame to read")
            cv2.imshow("frame", bgr_data)
            char = cv2.waitKey(1)
            if char == b"x"[0]: # exit
                exit()
            if char == b"r"[0]:  # reload stored.json
                try:
                    with open("stored.json", mode="r") as file:
                        if file.read():
                            file.seek(0)
                            stored = json.load(file)
                except FileNotFoundError:
                    print("no stored.json loaded")
            if char not in [*b"sqh"]:  # save or query
                continue
            rgb_data = cv2.cvtColor(bgr_data, cv2.COLOR_BGR2RGB)
            frame = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_data)
            result = landmarks.detector.detect(frame)
            if len(result.hand_world_landmarks) != 1:
                print(f'unexpected number of hands: {len(result.hand_world_landmarks)}')
                continue
            positions = [[landmark.x, landmark.y, landmark.z] for landmark in result.hand_world_landmarks[0]]
            positions = landmarks.normalize(positions)
            cv2.destroyAllWindows()
            if not stored:
                print("matched nothing")
                out_bgr_data = landmarks.draw_landmarks_on_image(bgr_data, result)
                cv2.imshow("no match", out_bgr_data)
            else:
                scores = landmarks.closest(positions, stored)
                best_score = min(score[0] for score in scores)
                names = {score[1] for score in scores if best_score == score[0]}
                if len(names) != 1:
                    print(f'multiple names matched: {(names)}')
                    out_bgr_data = landmarks.draw_landmarks_on_image(bgr_data, result)
                    cv2.imshow("multiple match", out_bgr_data)
                else:
                    best = [score for score in scores if best_score == score[0]][0]
                    print(json.dumps(best[3], indent=4))
                    print(f'matched {best[0]} {best[2]}')
                    match_bgr_data = cv2.imread(best[2], cv2.IMREAD_COLOR)
                    cv2.imshow("match", match_bgr_data)
            while True:
                char = cv2.waitKey(1)
                if char in [*b"qx"]:
                    break
                if char == b"s"[0]:
                    name = input("name: ")
                    taken_names = {name for _, name in stored.get(name, [])}
                    filename = f'{name}.jpg'
                    if filename in taken_names:
                        i = 1
                        while filename in taken_names:
                            i += 1
                            filename = f'{name}{"-"*(name[-1:] in "-0123456789")}{i}.jpg'
                    cv2.imwrite(filename, bgr_data)
                    stored.setdefault(name, []).append((positions, filename))
                    with open("stored.json", mode="w") as file:
                        json.dump(stored, file, separators=",:")
                    break
                if char == b"h"[0]:
                    cv2.destroyAllWindows()
                    out_bgr_data = landmarks.draw_landmarks_on_image(bgr_data, result)
                    cv2.imshow("hand landmarks", out_bgr_data)
            cv2.destroyAllWindows()
            while True:
                char = cv2.waitKey(1)
                print(char)
                if char == -1:
                    break
        except Exception:
            import traceback
            traceback.print_exc()
            continue
finally:
    cap.release()
    cv2.destroyAllWindows()
