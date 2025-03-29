import cv2
import mediapipe as mp
from mcrcon import MCRcon

mp_drawing = mp.solutions.drawing_utils
mp_holistic = mp.solutions.holistic

RCON_HOST = "127.0.0.1"
RCON_PORT = 25575
RCON_PASSWORD = "superpassword"

cap = cv2.VideoCapture(0)

mcr = MCRcon(RCON_HOST, RCON_PASSWORD, port=RCON_PORT)
holistic = mp_holistic.Holistic(static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5)
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = holistic.process(rgb_frame)

    if results.pose_landmarks:
        mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS)
        left_wrist = results.pose_landmarks.landmark[mp_holistic.PoseLandmark.LEFT_WRIST] # можно найти по номеру 15
        right_wrist = results.pose_landmarks.landmark[mp_holistic.PoseLandmark.RIGHT_WRIST]

        if left_wrist.x < 0.4:
            mcr.command("tp @a ~-1 ~ ~")  # Движение влево
        elif right_wrist.x > 0.6:
            mcr.command("tp @a ~1 ~ ~")  # Движение вправо

    if results.left_hand_landmarks:
        mp_drawing.draw_landmarks(frame, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS)

    if results.right_hand_landmarks:
        mp_drawing.draw_landmarks(frame, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS)

    cv2.imshow("Frame", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
