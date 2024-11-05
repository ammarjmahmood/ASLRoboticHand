import os
import cv2
import time

DATA_DIR = './data'
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

number_of_classes = 25
dataset_size = 100

# Try different camera indices
def find_working_camera():
    for i in range(10):  # Try first 10 indices
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                print(f"Working camera found at index {i}")
                return cap
            cap.release()
    return None

# Initialize camera
cap = find_working_camera()
if cap is None:
    print("No working camera found!")
    exit()

try:
    for j in range(number_of_classes):
        if not os.path.exists(os.path.join(DATA_DIR, str(j))):
            os.makedirs(os.path.join(DATA_DIR, str(j)))
        
        print('Collecting data for class {}'.format(j))
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to grab frame")
                break
                
            cv2.putText(frame, 'Ready? Press "Q" ! :)', (100, 50), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 255, 0), 3,
                        cv2.LINE_AA)
            cv2.imshow('frame', frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            
        counter = 0
        while counter < dataset_size:
            ret, frame = cap.read()
            if not ret:
                print("Failed to grab frame")
                break
                
            cv2.imshow('frame', frame)
            cv2.waitKey(1)
            
            cv2.imwrite(os.path.join(DATA_DIR, str(j), '{}.jpg'.format(counter)), frame)
            counter += 1
            
            # Add a small delay
            time.sleep(0.1)

finally:
    cap.release()
    cv2.destroyAllWindows()