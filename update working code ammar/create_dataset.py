# going to do post processing for the images we took

import os
import pickle

import mediapipe as mp
import cv2 

import matplotlub.pyplot as plt

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

hands = mp_hands.Hands(static_image_mode = True, min_detection_confidence = 0.3) # object hands detector

DATA_DIR = './data' // save data in this directory

data = [] # data of all the points

labels = [] # caterogies 

for dir_ in os.listdir(DATA_DIR):
    for img_path in os.listdir(os.path.join(DATA_DIR, dir)):
        img = cv2.imread(os.path.join(DATA_DIR, dir_, imag_path))
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        results = hands.process(img_rgb) # rocessing the image rgb and detect all the landmarks in the image

        if results.multi_hand_landmarks: 
            for hand_landmarks in results.multi_hand_landmarks:
                for i in range (len (hand_landmarks.landmark)):
                    print(hand_landmarks.landmark[i]) # have an image detect the landmarks, put them in an array and then get coordinates to train out classifier
                    x = hand_landmarks.landmarks[i].x
                    y = hand_landmarks.landmarks[i].y
                    data_aux.append(x)
                    data_aux.append(y)

            data.append(data_aux)
            labels.append(dir_)

f = open("data.pickle", "wb") # way to save in a binary way we did in highschool
pickle.dump({"data":data, "labels": labels}, f)
f.close()

                # gives us the positions when it itereates the landmarks on the image
               # mp_drawing.draw_landmarks(
               #     img_bgr, # image we want to draw
               #     hand_landmarks, #model output
               #     mp_hands.HANDS_CONNECTIONS, # hand connections
               #     mp_drawing_styles.get_default_hand_landmarks_styles(),
               #     mp_drawing_styles.get_default_hand_connections_style()
               # )
            

        plt.figure()
        plt.imshow(img_rgb)

plt.show()