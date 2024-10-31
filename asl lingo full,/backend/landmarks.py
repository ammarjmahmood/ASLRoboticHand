# https://github.com/google-ai-edge/mediapipe-samples/blob/main/examples/hand_landmarker/python/hand_landmarker.ipynb

import math
import typing

from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
import numpy as np
import cv2

MARGIN = 10  # pixels
FONT_SIZE = 1
FONT_THICKNESS = 1
HANDEDNESS_TEXT_COLOR = (88, 205, 54)  # vibrant green

def draw_landmarks_on_image(rgb_image, detection_result):
    hand_landmarks_list = detection_result.hand_landmarks
    handedness_list = detection_result.handedness
    annotated_image = np.copy(rgb_image)

    # Loop through the detected hands to visualize.
    for idx in range(len(hand_landmarks_list)):
        hand_landmarks = hand_landmarks_list[idx]
        handedness = handedness_list[idx]

        # Draw the hand landmarks.
        hand_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
        hand_landmarks_proto.landmark.extend([
            landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in hand_landmarks
        ])
        minz = min(l.z for l in detection_result.hand_world_landmarks[idx])
        solutions.drawing_utils.draw_landmarks(
            annotated_image,
            hand_landmarks_proto,
            solutions.hands.HAND_CONNECTIONS,
            {i: solutions.drawing_utils.DrawingSpec(
                color=(round(landmark.z*10000),)*3,
                circle_radius=1+round(50*(landmark.z-minz)),
            ) for i, landmark in enumerate(detection_result.hand_world_landmarks[idx])},
            solutions.drawing_styles.get_default_hand_connections_style())

        # Get the top left corner of the detected hand's bounding box.
        height, width, _ = annotated_image.shape
        x_coordinates = [landmark.x for landmark in hand_landmarks]
        y_coordinates = [landmark.y for landmark in hand_landmarks]
        text_x = int(min(x_coordinates) * width)
        text_y = int(min(y_coordinates) * height) - MARGIN

        # Draw handedness (left or right hand) on the image.
        cv2.putText(annotated_image, f"{handedness[0].category_name}",
                                (text_x, text_y), cv2.FONT_HERSHEY_DUPLEX,
                                FONT_SIZE, HANDEDNESS_TEXT_COLOR, FONT_THICKNESS, cv2.LINE_AA)

    return annotated_image


# STEP 1: Import the necessary modules.
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# STEP 2: Create an HandLandmarker object.
base_options = python.BaseOptions(model_asset_path='hand_landmarker.task')
options = vision.HandLandmarkerOptions(base_options=base_options,
                                       num_hands=2)
detector = vision.HandLandmarker.create_from_options(options)

def main():
    # STEP 3: Load the input image.
    image = mp.Image.create_from_file("image.jpg")

    # STEP 4: Detect hand landmarks from the input image.
    detection_result = detector.detect(image)

    # STEP 5: Process the classification result. In this case, visualize it.
    annotated_image = draw_landmarks_on_image(image.numpy_view(), detection_result)
    cv2.imwrite("annotated.jpg", cv2.cvtColor(annotated_image, cv2.COLOR_RGB2BGR))

def normalize(landmarks):
    def translate(positions, delta):
        return [pos + delta for pos in positions]
    def scale(positions, factor):
        return [pos * factor for pos in positions]
    landmarks = [np.array(pos) for pos in landmarks]
    # transform point 0 to origin (bottom of palm)
    landmarks = translate(landmarks, -landmarks[0])
    # scale all points using distance from 0 and 9
    landmarks = scale(landmarks, 100 / math.dist(landmarks[9], landmarks[0]))
    # rotate so palm is facing forwards, points 0, 1, 9 plane
    return [list(pos) for pos in landmarks]

def closeness(L1, L2):
    L1 = [np.array(pos) for pos in L1]
    L2 = [np.array(pos) for pos in L2]
    cmp = [
        [0,4], [0,8], [0,12], [0,16], [0,20],
        [5,8], [9,12], [13,16], [17,20],
        [4,8], [8,12], [12,16], [16,20],
        [4,6], [6,10], [10,14], [14,18],
        [8,10], [8,11],
        [3,6],
        [4,5], [4,8], [4,12], [4,14], [4,17],
    ]
    # return sum(
        # math.dist(l1, l2)
        # for l1, l2 in zip(L1, L2)
    # )
    L1s = sum(math.dist(L1[a], L1[b]) for a,b in cmp) / len(cmp)
    L2s = sum(math.dist(L2[a], L2[b]) for a,b in cmp) / len(cmp)
    # L1s = L2s = 1
    X = [
        max(da/db, db/da) - 1
        for a,b in cmp
        for da,db in [[math.dist(L1[a], L1[b])/L1s, math.dist(L2[a], L2[b])/L2s]]
    ]
    NAMES = "wrist thumb1 thumb2 thumb3 thumb4 index1 index2 index3 index4 mid1 mid2 mid3 mid4 ring1 ring2 ring3 ring4 pinky1 pinky2 pinky3 pinky4".split()
    return {
        "closeness": sum(x // 0.2 for x in X),
        "_debug": {
            "X": X,
            "apart": [
                [
                    x // 0.01 * 0.01,
                    *[NAMES[v] for v in cmp[i]],
                ]
                for i,x in enumerate(X)
                if x >= 0.2
            ],
        },
    }

def closest(
    positions: list[list[float]],
    stored: dict[str, list[tuple[list[list[float]], str]]],
) -> list[tuple[float, str, str, typing.Any]]:
    # stored is {name: [(positions, filename)]}
    # return [(closeness, name, filename, _debug)]
    return [
        ((C := closeness(positions, stored_positions))["closeness"], name, filename, C["_debug"])
        for name, store in stored.items()
        for stored_positions, filename in store
    ]

if __name__ == "__main__":
    main()
