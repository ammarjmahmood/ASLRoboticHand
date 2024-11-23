# ## Install requirements
# pip3 install opencv-python mediapipe numpy

# ## Run the program
# sudo python3 hand_tracking.py

# ------------------------------------------------------------

import cv2
import mediapipe as mp
import numpy as np
import smbus
import time
from math import atan2, degrees
from collections import deque

class RoboticHand:
    def __init__(self):
        self.bus = smbus.SMBus(1)
        self.I2C_ADDR = 0x40
        
        # Servo range
        self.STRAIGHT = 375
        self.BENT = 150
        
        # Smoothing buffers for each finger
        self.position_buffers = [deque(maxlen=3) for _ in range(5)]
        for buffer in self.position_buffers:
            buffer.extend([self.STRAIGHT] * 3)
        
        self.init_controller()
        self.positions = [self.STRAIGHT] * 5

    def init_controller(self):
        self.bus.write_byte_data(self.I2C_ADDR, 0x00, 0x00)
        time.sleep(0.05)
        prescale = int(25000000.0 / 4096.0 / 50.0 - 1)
        old_mode = self.bus.read_byte_data(self.I2C_ADDR, 0x00)
        self.bus.write_byte_data(self.I2C_ADDR, 0x00, (old_mode & 0x7F) | 0x10)
        self.bus.write_byte_data(self.I2C_ADDR, 0xFE, prescale)
        self.bus.write_byte_data(self.I2C_ADDR, 0x00, old_mode)
        time.sleep(0.05)
        self.bus.write_byte_data(self.I2C_ADDR, 0x00, old_mode | 0x80)

    def smooth_position(self, finger, new_position):
        """Apply smoothing to servo movements"""
        self.position_buffers[finger].append(new_position)
        return int(sum(self.position_buffers[finger]) / len(self.position_buffers[finger]))

    def move_servo(self, channel, value):
        """Move servo with smoothing"""
        value = self.smooth_position(channel, value)
        value = max(self.BENT, min(self.STRAIGHT, value))
        
        if abs(self.positions[channel] - value) > 2:  # Only move if change is significant
            self.positions[channel] = value
            channel = 4 * channel
            self.bus.write_byte_data(self.I2C_ADDR, 0x06 + channel, 0)
            self.bus.write_byte_data(self.I2C_ADDR, 0x07 + channel, 0)
            self.bus.write_byte_data(self.I2C_ADDR, 0x08 + channel, value & 0xFF)
            self.bus.write_byte_data(self.I2C_ADDR, 0x09 + channel, value >> 8)

class HandTracker:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        # Increased confidence thresholds for better accuracy
        self.hands = self.mp_hands.Hands(
            max_num_hands=1,  # Track only one hand
            model_complexity=1,  # Higher complexity for better accuracy
            min_detection_confidence=0.8,  # Increased from 0.7
            min_tracking_confidence=0.6    # Increased from 0.5
        )
        self.mp_draw = mp.solutions.drawing_utils
        
        # Landmark indices
        self.FINGER_TIPS = [4, 8, 12, 16, 20]  # Thumb, Index, Middle, Ring, Pinky tips
        self.FINGER_PIPS = [3, 7, 11, 15, 19]  # Second joints
        self.FINGER_MCPS = [2, 6, 10, 14, 18]  # Base joints
        
        # Angle smoothing buffers
        self.angle_buffers = [deque(maxlen=5) for _ in range(5)]
        self.prev_angles = [0] * 5

    def calculate_finger_angles(self, hand_landmarks):
        """Calculate precise finger angles"""
        angles = []
        
        for finger in range(5):
            # Get joint positions
            tip = np.array([
                hand_landmarks.landmark[self.FINGER_TIPS[finger]].x,
                hand_landmarks.landmark[self.FINGER_TIPS[finger]].y,
                hand_landmarks.landmark[self.FINGER_TIPS[finger]].z
            ])
            pip = np.array([
                hand_landmarks.landmark[self.FINGER_PIPS[finger]].x,
                hand_landmarks.landmark[self.FINGER_PIPS[finger]].y,
                hand_landmarks.landmark[self.FINGER_PIPS[finger]].z
            ])
            mcp = np.array([
                hand_landmarks.landmark[self.FINGER_MCPS[finger]].x,
                hand_landmarks.landmark[self.FINGER_MCPS[finger]].y,
                hand_landmarks.landmark[self.FINGER_MCPS[finger]].z
            ])
            
            # Calculate vectors using 3D coordinates
            v1 = pip - mcp
            v2 = tip - pip
            
            # Calculate angle between vectors
            angle = np.arccos(np.clip(np.dot(v1, v2) / 
                            (np.linalg.norm(v1) * np.linalg.norm(v2)), -1.0, 1.0))
            angle = np.degrees(angle)
            
            # Apply smoothing
            self.angle_buffers[finger].append(angle)
            smoothed_angle = sum(self.angle_buffers[finger]) / len(self.angle_buffers[finger])
            
            angles.append(smoothed_angle)
        
        return angles

    def map_angle_to_servo(self, angle, finger):
        """Map angles to servo positions with improved precision"""
        # Customized mapping for each finger
        if finger == 0:  # Thumb
            return np.interp(angle, [0, 90], [375, 150])
        else:  # Other fingers
            return np.interp(angle, [0, 110], [375, 150])

def main():
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    tracker = HandTracker()
    robot = RoboticHand()
    
    # Variables for FPS calculation
    fps_start_time = time.time()
    fps_frame_count = 0
    fps = 0
    
    print("\nHand Tracking Started")
    print("=====================")
    print("Controls:")
    print("- Keep your palm facing the camera")
    print("- Move your hand slowly for better tracking")
    print("- Press 'q' to quit")
    print("- Press 'r' to reset hand position")
    print("=====================\n")

    while cap.isOpened():
        success, image = cap.read()
        if not success:
            continue

        # FPS calculation
        fps_frame_count += 1
        if fps_frame_count >= 30:
            fps = fps_frame_count / (time.time() - fps_start_time)
            fps_start_time = time.time()
            fps_frame_count = 0

        # Process image
        image = cv2.flip(image, 1)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = tracker.hands.process(image_rgb)

        # Clear background for better visualization
        overlay = image.copy()
        cv2.rectangle(overlay, (0, 0), (200, 180), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.6, image, 0.4, 0, image)

        if results.multi_hand_landmarks:
            # Get the hand closest to the camera (largest in frame)
            main_hand = max(results.multi_hand_landmarks, 
                          key=lambda x: sum(lm.z for lm in x.landmark))
            
            # Draw landmarks
            tracker.mp_draw.draw_landmarks(
                image, main_hand, tracker.mp_hands.HAND_CONNECTIONS,
                tracker.mp_draw.DrawingSpec(color=(0,255,0), thickness=2, circle_radius=2),
                tracker.mp_draw.DrawingSpec(color=(0,0,255), thickness=2)
            )
            
            # Calculate and apply finger positions
            angles = tracker.calculate_finger_angles(main_hand)
            
            for finger, angle in enumerate(angles):
                servo_pos = tracker.map_angle_to_servo(angle, finger)
                robot.move_servo(finger, servo_pos)
                
                # Display finger angles
                finger_names = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']
                cv2.putText(
                    image,
                    f"{finger_names[finger]}: {int(angle)}°",
                    (10, 30 + finger * 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 255),
                    2
                )

        # Display FPS
        cv2.putText(
            image,
            f"FPS: {int(fps)}",
            (10, 170),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2
        )

        cv2.imshow('Hand Tracking', image)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('r'):
            # Reset hand position
            for i in range(5):
                robot.move_servo(i, robot.STRAIGHT)

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)