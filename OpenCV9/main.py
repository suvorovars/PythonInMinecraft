import keyboard
import cv2
import mcpi
import mcpi.minecraft
import mediapipe as mp

cap = cv2.VideoCapture(0)

mp_holistic = mp.solutions.holistic
holistic = mp_holistic.Holistic()
mp_drawing = mp.solutions.drawing_utils

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    height, width, _ = frame.shape

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = holistic.process(rgb_frame)

    if results.pose_landmarks:
        mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS)
    if results.left_hand_landmarks or results.right_hand_landmarks:
        hand_landmark = results.left_hand_landmarks \
            if results.left_hand_landmarks else results.right_hand_landmarks
        index_finger = hand_landmark.landmark[8]
        x, y = index_finger.x, index_finger.y
        mp_drawing.draw_landmarks(frame, hand_landmark, mp_holistic.HAND_CONNECTIONS)
        cv2.putText(frame, f"X: {x}, Y: {y}", (int(width / 2), int(height / 2)),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # код, который нажимает на клавишу A если палец находится в левой части экрана
        # и на клавишу D если палец находится в правой части экрана


        if x < 0.4:
            keyboard.press('a')
        elif x > 0.6:
            keyboard.press('d')

    cv2.imshow("Ну где же ручки?", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
