import cv2
import mediapipe as mp
import time
from mcpi.minecraft import Minecraft

# Подключаем Minecraft
mc = Minecraft.create()

# Инициализация Mediapipe для распознавания рук
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_draw = mp.solutions.drawing_utils

# Настройка видеопотока
cap = cv2.VideoCapture(0)

# Параметры для хранения данных о кадрах
positions = []  # Список для хранения координат кончика указательного пальца и времени
max_frames = 10  # Максимальное число кадров для анализа


def add_position(positions, x, y, current_time):
    """
    Добавляет координаты (x, y) и время в список positions.
    Если количество элементов превышает max_frames, удаляет самый старый.
    """
    positions.append((x, y, current_time))
    if len(positions) > max_frames:
        positions.pop(0)


def analyze_gesture(positions, swipe_threshold=50, time_threshold=1.0):
    """
    Анализирует последовательность кадров и определяет, был ли совершен свайп.
    Если горизонтальное смещение (dx) больше swipe_threshold,
    вертикальное смещение (dy) меньше половины этого порога,
    и время (dt) меньше time_threshold, возвращает:
        'swipe_right' при движении вправо,
        'swipe_left' при движении влево.
    Иначе возвращает 'unknown'.
    """
    x_start, y_start, t_start = positions[0]
    x_end, y_end, t_end = positions[-1]
    dt = t_end - t_start
    dx = x_end - x_start
    dy = y_end - y_start

    if dt < time_threshold and abs(dx) > swipe_threshold and abs(dy) < swipe_threshold // 2:
        if dx > 0:
            return "swipe_right"
        else:
            return "swipe_left"
    return "unknown"


def perform_minecraft_action(gesture):
    """
    Выполняет действие в Minecraft в зависимости от распознанного жеста.
    При 'swipe_right' строится башня из камня.
    При 'swipe_left' очищается зона (заменяются блоки на воздух).
    """
    pos = mc.player.getTilePos()
    if gesture == "swipe_right":
        mc.postToChat("Свайп вправо! Строим башню.")
        mc.setBlocks(pos.x + 1, pos.y - 5, pos.z + 1, pos.x + 1, pos.y + 5, pos.z + 1, 57)
    elif gesture == "swipe_left":
        mc.postToChat("Свайп влево! Очищаем зону.")
        mc.setBlocks(pos.x - 5, pos.y - 5, pos.z - 5, pos.x + 5, pos.y + 5, pos.z + 5, 0)  # 0 = воздух


# Основной цикл программы
while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Отзеркаливаем изображение для удобства
    frame = cv2.flip(frame, 1)
    height, width, _ = frame.shape
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_frame)

    gesture = "unknown"

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            # Рисуем скелет руки на экране
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            # Отслеживаем кончик указательного пальца (landmark 8)
            landmark = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            x = int(landmark.x * width)
            y = int(landmark.y * height)
            # Добавляем координаты в список
            add_position(positions, x, y, time.time())
            cv2.circle(frame, (x, y), 5, (0, 255, 0), cv2.FILLED)

            # Если накоплено достаточное количество кадров, анализируем жест
            if len(positions) == max_frames:
                gesture = analyze_gesture(positions)
                if gesture != "unknown":
                    cv2.putText(frame, f'Gesture: {gesture}', (10, 50),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    perform_minecraft_action(gesture)
                    time.sleep(0.2)
                    # Очищаем список, чтобы избежать повторного срабатывания
                    positions.clear()
    else:
        # Если рука не обнаружена, очищаем список
        positions.clear()

    cv2.imshow("Minecraft Gesture Control", frame)
    if cv2.waitKey(1) & 0xFF == 27:  # Нажмите Esc для выхода
        break

cap.release()
cv2.destroyAllWindows()
