import os
import pickle
import mediapipe as mp
import cv2
import numpy as np

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

hands = mp_hands.Hands(static_image_mode=True, min_detection_confidence=0.3)

DATA_DIR = './data'

data = []
labels = []
REQUIRED_DATA_LENGTH = 42  # 21 landmarks with x,y coordinates each

for dir_ in os.listdir(DATA_DIR):
    dir_path = os.path.join(DATA_DIR, dir_)
    if os.path.isdir(dir_path):
        print(f"Processing directory: {dir_}")
        for img_path in os.listdir(dir_path):
            data_aux = []
            img = cv2.imread(os.path.join(dir_path, img_path))
            if img is None:
                print(f"Failed to load image: {img_path}")
                continue
                
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            results = hands.process(img_rgb)

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    # Get x and y lists for normalization
                    x_ = []
                    y_ = []
                    for i in range(len(hand_landmarks.landmark)):
                        x = hand_landmarks.landmark[i].x
                        y = hand_landmarks.landmark[i].y
                        x_.append(x)
                        y_.append(y)
                    
                    # Normalize coordinates
                    for i in range(len(hand_landmarks.landmark)):
                        x = hand_landmarks.landmark[i].x
                        y = hand_landmarks.landmark[i].y
                        data_aux.append(x - min(x_))
                        data_aux.append(y - min(y_))

                # Check if we have the correct number of points
                if len(data_aux) == REQUIRED_DATA_LENGTH:
                    data.append(data_aux)
                    labels.append(dir_)
                    print(f"Processed image {img_path} from class {dir_}")
                else:
                    print(f"Skipping {img_path} due to incorrect number of points: {len(data_aux)}")

# Convert to numpy arrays and check shapes
data = np.array(data)
labels = np.array(labels)

print(f"Data shape: {data.shape}")
print(f"Labels shape: {labels.shape}")
print(f"Total processed images: {len(data)}")
print(f"Number of classes: {len(set(labels))}")

# Save the processed data
f = open('data.pickle', 'wb')
pickle.dump({'data': data, 'labels': labels}, f)
f.close()

print("Data saved to data.pickle")