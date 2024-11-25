import cv2
import mediapipe as mp
import numpy as np
import subprocess
import time
import threading
from queue import Queue
import sys

# Initialize MediaPipe
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

# Initialize hand tracking
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,  # Track only one hand
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
)

def calculate_finger_bend(finger_points):
    """Calculate how bent a finger is from 0 (straight) to 1 (fully bent)"""
    # Get the three points that make up the finger
    root, middle, tip = finger_points
    
    # Calculate angles between the finger segments
    angle = calculate_angle(root, middle, tip)
    
    # Normalize angle to a 0-1 range where:
    # 180 degrees (straight) = 0
    # ~90 degrees (bent) = 1
    bend_value = (180 - angle) / 90
    return min(max(bend_value, 0), 1)  # Clamp between 0 and 1

def calculate_angle(p1, p2, p3):
    """Calculate angle between three points"""
    v1 = np.array([p1.x - p2.x, p1.y - p2.y])
    v2 = np.array([p3.x - p2.x, p3.y - p2.y])
    
    cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
    angle = np.arccos(np.clip(cos_angle, -1.0, 1.0))
    return np.degrees(angle)

def get_finger_positions(hand_landmarks):
    """Get normalized bend values for each finger"""
    # Finger landmark indices
    fingers = {
        'thumb': [1, 2, 4],     # CMC, MCP, TIP
        'index': [5, 6, 8],     # MCP, PIP, TIP
        'middle': [9, 10, 12],  # MCP, PIP, TIP
        'ring': [13, 14, 16],   # MCP, PIP, TIP
        'pinky': [17, 18, 20]   # MCP, PIP, TIP
    }
    
    bend_values = []
    for finger in fingers.values():
        points = [hand_landmarks.landmark[i] for i in finger]
        bend = calculate_finger_bend(points)
        bend_values.append(bend)
    
    return bend_values

def map_to_servo_values(bend_values):
    """Map bend values (0-1) to servo values"""
    # Convert each bend value to a servo position
    servo_positions = []
    for bend in bend_values:
        # Map 0-1 to servo range (375-150)
        servo_val = int(375 - (bend * (375-150)))
        servo_positions.append(servo_val)
    return servo_positions

def run_cpp_program(servo_values):
    """Send servo values to C++ program"""
    try:
        # Convert values to strings
        value_str = ','.join(map(str, servo_values))
        subprocess.run(['./hand_mirror', value_str], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running C++ program: {e}")

def main():
    cap = cv2.VideoCapture(0)
    last_servo_update = time.time()
    UPDATE_INTERVAL = 0.1  # Update servos every 100ms
    
    print("Starting hand mirroring program...")
    print("Press ESC to quit")
    
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            continue

        # Convert image and process
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = hands.process(image)
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Draw hand landmarks
                mp_drawing.draw_landmarks(
                    image,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style()
                )

                # Get finger positions and update servos if enough time has passed
                current_time = time.time()
                if current_time - last_servo_update >= UPDATE_INTERVAL:
                    bend_values = get_finger_positions(hand_landmarks)
                    servo_values = map_to_servo_values(bend_values)
                    
                    # Display values on image
                    cv2.putText(image, f"Servo values: {servo_values}", 
                              (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                              1, (0, 255, 0), 2)
                    
                    run_cpp_program(servo_values)
                    last_servo_update = current_time

        # Show image
        cv2.imshow('Hand Tracking', image)
        if cv2.waitKey(5) & 0xFF == 27:  # ESC key
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting program...")
        sys.exit(0)