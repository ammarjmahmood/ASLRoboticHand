import cv2
import numpy as np
import mediapipe as mp

class ASLDetector:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils

    def get_finger_states(self, landmarks):
        # Get fingertip and pip (second joint) y-coordinates
        fingertips = [8, 12, 16, 20]  # Index, middle, ring, pinky
        pips = [6, 10, 14, 18]        # Second joints
        
        # Compare y-coordinates for each finger (except thumb)
        states = []
        for tip, pip in zip(fingertips, pips):
            states.append(landmarks[tip].y < landmarks[pip].y)
        
        # Special case for thumb
        thumb_extended = (landmarks[4].x < landmarks[3].x if landmarks[0].x < 0.5 
                         else landmarks[4].x > landmarks[3].x)
        states.insert(0, thumb_extended)
        
        return states

    def get_finger_angles(self, landmarks):
        angles = []
        fingers = [
            [1,2,3,4],    # thumb
            [5,6,7,8],    # index
            [9,10,11,12], # middle
            [13,14,15,16],# ring
            [17,18,19,20] # pinky
        ]
        
        for finger in fingers:
            angle = self.calculate_angle(
                landmarks[finger[0]], 
                landmarks[finger[1]],
                landmarks[finger[2]]
            )
            angles.append(angle)
            
        return angles

    def calculate_angle(self, p1, p2, p3):
        vector1 = np.array([p1.x - p2.x, p1.y - p2.y])
        vector2 = np.array([p3.x - p2.x, p3.y - p2.y])
        
        cosine = np.dot(vector1, vector2) / (np.linalg.norm(vector1) * np.linalg.norm(vector2))
        angle = np.arccos(np.clip(cosine, -1.0, 1.0))
        return np.degrees(angle)

    def detect_letter(self, landmarks):
        states = self.get_finger_states(landmarks.landmark)
        angles = self.get_finger_angles(landmarks.landmark)
        
        # Key points
        thumb_tip = landmarks.landmark[4]
        index_tip = landmarks.landmark[8]
        middle_tip = landmarks.landmark[12]
        ring_tip = landmarks.landmark[16]
        pinky_tip = landmarks.landmark[20]
        
        # A: Fist with thumb out
        if all(not state for state in states[1:]) and states[0]:
            return 'A'
        
        # B: Flat hand, fingers together
        elif all(state for state in states) and all(abs(landmarks.landmark[tip].x - landmarks.landmark[8].x) < 0.03 
                                                  for tip in [12, 16, 20]):
            return 'B'
        
        # C: Curved hand
        elif (not any(states) and angles[1] < 130 and angles[2] < 130 
              and abs(thumb_tip.x - index_tip.x) < 0.1):
            return 'C'
        
        # D: Index up, others closed
        elif states[1] and not any(states[2:]) and thumb_tip.y > index_tip.y:
            return 'D'
        
        # E: All fingers closed
        elif not any(states):
            return 'E'
        
        # F: Index and thumb connected, others extended
        elif not states[0] and all(states[1:]) and abs(index_tip.x - middle_tip.x) < 0.02:
            return 'F'
        
        # G: Index pointing at thumb
        elif states[1] and not any(states[2:]) and abs(thumb_tip.y - index_tip.y) < 0.05:
            return 'G'
        
        # H: Index and middle out sideways
        elif states[1] and states[2] and not states[3] and not states[4] and abs(index_tip.x - middle_tip.x) > 0.05:
            return 'H'
        
        # I: Pinky only
        elif not states[1] and not states[2] and not states[3] and states[4]:
            return 'I'
        
        # J: Same as I with motion (simplified to I)
        elif not states[1] and not states[2] and not states[3] and states[4]:
            return 'J'
        
        # K: Index and middle up, thumb at middle joint
        elif states[1] and states[2] and not states[3] and not states[4] and abs(thumb_tip.y - landmarks.landmark[10].y) < 0.05:
            return 'K'
        
        # L: L-shape with thumb and index
        elif states[0] and states[1] and not any(states[2:]) and abs(thumb_tip.x - index_tip.x) > 0.1:
            return 'L'
        
        # M: Three fingers over thumb
        elif not states[0] and states[1] and states[2] and states[3] and not states[4]:
            return 'M'
        
        # N: Two fingers over thumb
        elif not states[0] and states[1] and states[2] and not states[3] and not states[4]:
            return 'N'
        
        # O: Circle shape
        elif (not any(states) and all(abs(landmarks.landmark[tip].x - landmarks.landmark[4].x) < 0.05 
              for tip in [8, 12, 16, 20])):
            return 'O'
        
        # P: Two finger gun pointing down
        elif states[1] and not any(states[2:]) and thumb_tip.y < index_tip.y:
            return 'P'
        
        # Q: Two finger gun pointing down and to the side
        elif states[1] and not any(states[2:]) and index_tip.y > landmarks.landmark[6].y:
            return 'Q'
        
        # R: Crossed fingers
        elif all(state for state in states) and abs(index_tip.x - middle_tip.x) > 0.02:
            return 'R'
        
        # S: Fist with thumb over fingers
        elif not any(states[1:]) and states[0] and thumb_tip.x > index_tip.x:
            return 'S'
        
        # T: Index bent, thumb between index and middle
        elif not states[1] and not states[2] and states[0]:
            return 'T'
        
        # U: Index and middle parallel
        elif states[1] and states[2] and not states[3] and not states[4] and abs(index_tip.x - middle_tip.x) < 0.02:
            return 'U'
        
        # V: Peace sign
        elif states[1] and states[2] and not states[3] and not states[4] and abs(index_tip.x - middle_tip.x) > 0.04:
            return 'V'
        
        # W: Three fingers up
        elif states[1] and states[2] and states[3] and not states[4]:
            return 'W'
        
        # X: Hook shape with index
        elif states[1] and not any(states[2:]) and angles[1] < 90:
            return 'X'
        
        # Y: Thumb and pinky out only
        elif states[0] and states[4] and not any(states[1:4]):
            return 'Y'
        
        # Z: Same as Z with motion (simplified to Z)
        elif states[1] and not any(states[2:]) and angles[1] > 150:
            return 'Z'
        
        return None

    def process_frame(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        detected_letter = None

        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
            self.mp_draw.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
            detected_letter = self.detect_letter(hand_landmarks)

            if detected_letter:
                cv2.putText(frame, f"Detected: {detected_letter}", (10, 50),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        return frame, detected_letter

def main():
    detector = ASLDetector()
    cap = cv2.VideoCapture(0)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        processed_frame, letter = detector.process_frame(frame)

        if letter:
            print(f"Detected: {letter}")

        cv2.imshow('ASL Detection', processed_frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == 13 and letter:  # Enter key
            with open('detected_letters.txt', 'a') as f:
                f.write(f"{letter}\n")
            print(f"Saved letter {letter} to file")

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()