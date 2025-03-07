import cv2
import mediapipe as mp
import time
import keyboard
from mcpi.minecraft import Minecraft
from mcpi import block

# Подключаемся к Minecraft
mc = Minecraft.create()

# Инициализация видеопотока
cap = cv2.VideoCapture(0)

# Настройка Mediapipe для распознавания рук
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_draw = mp.solutions.drawing_utils

# Список типов блоков
block_types = [block.STONE, block.GRASS, block.WOOD, block.GOLD_BLOCK]
current_block_index = 0

# Параметры холста
canvas_distance = 20
canvas_width = 40
canvas_height = 40

key_pressed = False


def is_pinch(hand_landmarks, width, height, pinch_threshold=40):
    thumb = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
    index = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    x_thumb = int(thumb.x * width)
    y_thumb = int(thumb.y * height)
    x_index = int(index.x * width)
    y_index = int(index.y * height)
    distance = ((x_index - x_thumb) ** 2 + (y_index - y_thumb) ** 2) ** 0.5
    return (distance < pinch_threshold), (x_index, y_index)


while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Зеркальное отражение кадра (для удобства пользователя)
    frame = cv2.flip(frame, 1)
    height_frame, width_frame, _ = frame.shape
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_frame)

    # Обработка нажатия клавиши 'N'
    if keyboard.is_pressed('n') and not key_pressed:
        current_block_index = (current_block_index + 1) % len(block_types)
        key_pressed = True
        time.sleep(0.2)
    elif not keyboard.is_pressed('n'):
        key_pressed = False

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            pinch_detected, point = is_pinch(hand_landmarks, width_frame, height_frame)
            if pinch_detected:
                player_pos = mc.player.getTilePos()
                canvas_center_z = player_pos.z + canvas_distance

                # Корректировка направления по оси X
                dx_img = point[0] - width_frame / 2
                dy_img = point[1] - height_frame / 2

                # Инвертируем offset_x для устранения зеркальности
                offset_x = -(dx_img / width_frame) * canvas_width  # Добавлен минус!
                offset_y = -(dy_img / height_frame) * canvas_height

                draw_x = player_pos.x + offset_x
                draw_y = player_pos.y + offset_y
                draw_z = canvas_center_z

                try:
                    mc.setBlock(int(draw_x), int(draw_y), int(draw_z), block_types[current_block_index])
                except Exception as e:
                    print(f"Ошибка: {e}")

                cv2.putText(frame, f"Block: {block_types[current_block_index]}", (10, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow("Minecraft Air Drawing", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
