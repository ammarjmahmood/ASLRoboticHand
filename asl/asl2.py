import cv2
import numpy as np
import mediapipe as mp
import speech_recognition as sr
import pytesseract
from datetime import datetime
import os
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('asl_detector.log'),
        logging.StreamHandler()
    ]
)

class EnhancedASLDetector:
    def __init__(self):
        # Initialize ASL detection components
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils
        
        # Initialize speech recognition
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Initialize modes
        self.MODES = {
            'ASL': 0,
            'VOICE': 1,
            'TEXT': 2
        }
        self.current_mode = self.MODES['ASL']
        
        # Create output directory
        self.output_dir = 'detection_results'
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Calibrate the speech recognition for ambient noise
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
            logging.info("Microphone calibrated for ambient noise")

    def save_to_file(self, data, mode):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.output_dir, f"detected_{mode.lower()}_{timestamp}.txt")
        try:
            with open(filename, 'w') as f:
                if isinstance(data, list):
                    f.write(','.join(data) + '\n')
                else:
                    f.write(str(data) + '\n')
            logging.info(f"Successfully saved data to {filename}")
            return filename
        except Exception as e:
            logging.error(f"Error saving to file: {e}")
            return None

    def process_voice_input(self):
        try:
            with self.microphone as source:
                logging.info("Listening for voice input...")
                audio = self.recognizer.listen(source, timeout=2)
                text = self.recognizer.recognize_google(audio)
                letters = list(text.upper())
                filename = self.save_to_file(letters, 'voice')
                logging.info(f"Voice input processed: {text}")
                return letters, filename
        except sr.WaitTimeoutError:
            logging.warning("No speech detected")
            return None, None
        except sr.UnknownValueError:
            logging.warning("Could not understand audio")
            return None, None
        except sr.RequestError as e:
            logging.error(f"Could not request results: {e}")
            return None, None

    def detect_text_in_image(self, frame):
        try:
            # Convert frame to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Apply thresholding to preprocess the image
            gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
            
            # Apply some image processing to improve text detection
            gray = cv2.medianBlur(gray, 3)
            
            # Perform text detection
            text = pytesseract.image_to_string(gray, config='--psm 11')
            
            # Clean and process the detected text
            if text.strip():
                letters = list(text.upper().replace(' ', '').replace('\n', ''))
                if letters:
                    filename = self.save_to_file(letters, 'text')
                    logging.info(f"Text detected: {''.join(letters)}")
                    return letters, filename
            return None, None
        except Exception as e:
            logging.error(f"Error in text detection: {e}")
            return None, None

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
        if self.current_mode == self.MODES['ASL']:
            # Existing ASL detection code
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

            return frame, detected_letter, None

        elif self.current_mode == self.MODES['TEXT']:
            # Text detection mode
            letters, filename = self.detect_text_in_image(frame)
            if letters:
                text_display = ','.join(letters)
                cv2.putText(frame, f"Detected Text: {text_display}", (10, 50),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            return frame, letters, filename

        return frame, None, None

def main():
    try:
        detector = EnhancedASLDetector()
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            logging.error("Failed to open camera")
            return
        
        # Print controls
        print("\n=== ASL Detector Controls ===")
        print("SPACE - Hold to activate voice input")
        print("P     - Toggle text detection mode")
        print("ENTER - Save detected ASL letter")
        print("Q     - Quit")
        print("==========================\n")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                logging.error("Failed to grab frame")
                break

            frame = cv2.flip(frame, 1)
            
            # Display current mode
            mode_text = list(detector.MODES.keys())[detector.current_mode]
            cv2.putText(frame, f"Mode: {mode_text}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

            processed_frame, detection, filename = detector.process_frame(frame)

            key = cv2.waitKey(1) & 0xFF
            
            # Handle key presses
            if key == ord('q'):
                logging.info("Quitting application")
                break
            elif key == ord('p'):  # Toggle text detection mode
                detector.current_mode = detector.MODES['TEXT'] if detector.current_mode != detector.MODES['TEXT'] else detector.MODES['ASL']
                logging.info(f"Switched to {list(detector.MODES.keys())[detector.current_mode]} mode")
            elif key == 32:  # Spacebar for voice input
                detector.current_mode = detector.MODES['VOICE']
                letters, filename = detector.process_voice_input()
                if letters:
                    print(f"Voice input detected: {','.join(letters)}")
                    print(f"Saved to {filename}")
                detector.current_mode = detector.MODES['ASL']
	    elif key == 13 and detection:  # Enter key
                filename = detector.save_to_file(detection, 'asl')
                if filename:
                    print(f"Saved detection {detection} to {filename}")
                    logging.info(f"Saved ASL detection: {detection}")

            # Display frame
            try:
                cv2.imshow('Enhanced ASL Detection', processed_frame)
            except cv2.error as e:
                logging.error(f"Error displaying frame: {e}")
                break

    except KeyboardInterrupt:
        logging.info("Application terminated by user")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
    finally:
        # Clean up
        try:
            cap.release()
            cv2.destroyAllWindows()
            logging.info("Resources released successfully")
        except Exception as e:
            logging.error(f"Error during cleanup: {e}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.critical(f"Critical error in main: {e}")
        raise
