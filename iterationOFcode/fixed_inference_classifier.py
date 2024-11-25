import pickle
import cv2
import mediapipe as mp
import numpy as np
import subprocess
import time
import threading
from queue import Queue
import sys
import os

def clear_console():
    os.system('clear' if os.name == 'posix' else 'cls')

model_dict = pickle.load(open('./model.p', 'rb'))
model = model_dict['model']

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

hands = mp_hands.Hands(static_image_mode=True, min_detection_confidence=0.3)

# Restored original labels_dict with 25 letters
labels_dict = {
    0: 'A', 1: 'B', 2: 'C', 3: 'D', 4: 'E', 5: 'F',
    6: 'G', 7: 'H', 8: 'I', 9: 'J', 10: 'K', 11: 'L',
    12: 'M', 13: 'N', 14: 'O', 15: 'P', 16: 'Q', 17: 'R',
    18: 'S', 19: 'T', 20: 'U', 21: 'V', 22: 'W', 23: 'X',
    24: 'Y'  # Note: Z typically not included as it requires motion
}

input_queue = Queue()
prediction_queue = Queue()
running = True

def print_input_prompt():
    print("\n" + "="*50)
    print("TYPE HERE AND PRESS ENTER TO SPELL A WORD")
    print("Type 'q' to quit")
    print("="*50)
    return input(">> ")

def run_cpp_program(letter):
    try:
        letter = letter.upper()
        if letter in ['J', 'Z']:
            print(f"Letter {letter} requires motion and is not supported")
            return
        if not letter.isalpha():
            print(f"Invalid character: {letter}")
            return
            
        print(f"\nDisplaying letter: {letter}")
        process = subprocess.Popen(['./hand_test', letter])
        return process
    except Exception as e:
        print(f"Error running C++ program: {e}")
        return None

def spell_word(word):
    print("\n" + "="*50)
    print(f"NOW SPELLING: {word}")
    print("="*50)
    
    for letter in word.upper():
        if letter.isspace():
            print("\nPausing for space...")
            time.sleep(2)
            continue
            
        if letter in ['J', 'Z']:
            print(f"\nSkipping letter {letter} (requires motion)")
            continue
            
        if not letter.isalpha():
            print(f"\nSkipping invalid character: {letter}")
            continue
            
        process = run_cpp_program(letter)
        if process:
            process.wait()
        time.sleep(0.5)

    print("\nFinished spelling!")

def input_thread():
    global running
    while running:
        try:
            text = print_input_prompt()
            if text.lower() == 'q':
                running = False
                break
            if text.strip():
                input_queue.put(text)
        except EOFError:
            running = False
            break

def prediction_thread():
    global running
    last_prediction = None
    last_prediction_time = time.time()
    COOLDOWN_TIME = 2
    current_process = None
    
    while running:
        try:
            if not prediction_queue.empty():
                predicted_character = prediction_queue.get()
                current_time = time.time()
                
                if (predicted_character != last_prediction and 
                    current_time - last_prediction_time >= COOLDOWN_TIME):
                    
                    if current_process and current_process.poll() is None:
                        current_process.terminate()
                        current_process.wait()
                    
                    print(f"\nDetected letter: {predicted_character}")
                    current_process = run_cpp_program(predicted_character)
                    last_prediction = predicted_character
                    last_prediction_time = current_time
            
            time.sleep(0.01)
            
        except Exception as e:
            print(f"Error in prediction thread: {e}")
            continue

def camera_thread():
    global running
    cap = cv2.VideoCapture(0)
    
    while running:
        while not input_queue.empty():
            text = input_queue.get()
            spell_word(text)
            
        data_aux = []
        x_ = []
        y_ = []

        ret, frame = cap.read()
        if not ret:
            continue

        H, W, _ = frame.shape
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame_rgb)

        if results.multi_hand_landmarks:
            # Process the first hand only, just like in original code
            hand_landmarks = results.multi_hand_landmarks[0]  # Take first hand
            
            mp_drawing.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS,
                mp_drawing_styles.get_default_hand_landmarks_style(),
                mp_drawing_styles.get_default_hand_connections_style())

            # Collect x, y coordinates first
            for i in range(len(hand_landmarks.landmark)):
                x = hand_landmarks.landmark[i].x
                y = hand_landmarks.landmark[i].y
                x_.append(x)
                y_.append(y)

            # Then create the data_aux array
            for i in range(len(hand_landmarks.landmark)):
                x = hand_landmarks.landmark[i].x
                y = hand_landmarks.landmark[i].y
                data_aux.append(x - min(x_))
                data_aux.append(y - min(y_))

            x1 = int(min(x_) * W) - 10
            y1 = int(min(y_) * H) - 10
            x2 = int(max(x_) * W) - 10
            y2 = int(max(y_) * H) - 10

            prediction = model.predict([np.asarray(data_aux)])
            predicted_character = labels_dict[int(prediction[0])]
            
            # Add prediction to queue
            prediction_queue.put(predicted_character)

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 0), 4)
            cv2.putText(frame, predicted_character, (x1, y1 - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 0, 0), 3, cv2.LINE_AA)

        cv2.putText(frame, "Press ESC to quit, or type in console", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2, cv2.LINE_AA)
        
        cv2.imshow('frame', frame)
        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC key
            running = False
            break

    cap.release()
    cv2.destroyAllWindows()

def main():
    print("\nStarting Sign Language Interpreter")
    print("You can:")
    print("1. Show hand signs to the camera")
    print("2. Type words to spell out")
    print("3. Press ESC to quit")
    print("4. Type 'q' and press Enter to quit")
    print("\nInitializing camera...")
    
    input_thread_ = threading.Thread(target=input_thread)
    prediction_thread_ = threading.Thread(target=prediction_thread)
    
    input_thread_.daemon = True
    prediction_thread_.daemon = True
    
    input_thread_.start()
    prediction_thread_.start()

    camera_thread()

    global running
    running = False
    input_thread_.join(timeout=1)
    prediction_thread_.join(timeout=1)
    print("\nProgram terminated.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting program...")
        running = False
        sys.exit(0)