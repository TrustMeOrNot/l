import cv2
import mediapipe as mp
import pyautogui
import serial
import time

# Initialize serial connection (adjust 'COM3' and 9600 to your port and baud rate)
arduino = serial.Serial('COM4', 9600)

# Set the correct camera index obtained from list_cameras.py
camera_index = 3  # Change this to the correct index found
cap = cv2.VideoCapture(camera_index)

if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

pose_detector = mp.solutions.pose.Pose()
drawing_utils = mp.solutions.drawing_utils
screen_width, screen_height = pyautogui.size()

# Add a delay between commands to prevent sending too many signals too quickly
command_delay = 0.5  # Delay in seconds
last_command_time = time.time()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        continue
    
    frame = cv2.flip(frame, 1)
    frame_height, frame_width, _ = frame.shape
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    output = pose_detector.process(rgb_frame)
    pose_landmarks = output.pose_landmarks
    if pose_landmarks:
        drawing_utils.draw_landmarks(frame, pose_landmarks, mp.solutions.pose.POSE_CONNECTIONS)
        landmarks = pose_landmarks.landmark

        # Track key body parts (e.g., nose for head position)
        nose = landmarks[mp.solutions.pose.PoseLandmark.NOSE]
        nose_x = int(nose.x * frame_width)
        nose_y = int(nose.y * frame_height)
        cv2.circle(img=frame, center=(nose_x, nose_y), radius=10, color=(0, 255, 255))

        # Convert nose coordinates to screen coordinates
        index_x = screen_width / frame_width * nose_x
        index_y = screen_height / frame_height * nose_y

        # Determine direction based on nose position with reduced sensitivity
        current_time = time.time()
        if current_time - last_command_time > command_delay:
            if index_y < screen_height / 3 and screen_width / 3 <= index_x <= 2 * screen_width / 3:
                arduino.write(b'fire\n')
                arduino.write(b'down\n')  # Change from 'down' to 'up'
                print("FIRE AND UP!")
                last_command_time = current_time
            else:
                if index_x < screen_width / 4:
                    arduino.write(b'right\n')  # Change from 'left' to 'right'
                    last_command_time = current_time
                elif index_x > 3 * screen_width / 4:
                    arduino.write(b'left\n')  # Change from 'right' to 'left'
                    last_command_time = current_time
                elif index_y < screen_height / 4:
                    arduino.write(b'down\n')  # Change from 'up' to 'down'
                    last_command_time = current_time
                elif index_y > 3 * screen_height / 4:
                    arduino.write(b'up\n')  # Change from 'down' to 'up'
                    last_command_time = current_time

    cv2.imshow('Person Tracker', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
arduino.close()
