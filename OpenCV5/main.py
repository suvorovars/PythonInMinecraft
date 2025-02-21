# Импорт необходимых библиотек:
import cv2  # Библиотека для работы с изображениями и видео
import mediapipe as mp  # Библиотека для распознавания жестов и обработки изображений от Google
import pyautogui  # Библиотека для эмуляции нажатия клавиш
import time  # Библиотека для работы со временем (задержки)

# Инициализация модуля распознавания рук из Mediapipe:
mp_hands = mp.solutions.hands
# Создаем объект для обработки рук с заданными пороговыми значениями:
# min_detection_confidence — минимальная достоверность обнаружения руки,
# min_tracking_confidence — минимальная достоверность отслеживания обнаруженной руки.
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.5)
# Объект для рисования аннотаций (ключевых точек и соединений) на кадре:
mp_draw = mp.solutions.drawing_utils

# Открываем видеопоток с веб-камеры (индекс 0 означает первую камеру):
cap = cv2.VideoCapture(0)

# Основной цикл обработки видеопотока:
while True:
    # Чтение кадра с камеры. ret будет True, если кадр успешно считан.
    ret, frame = cap.read()
    if not ret:
        break  # Если не удалось получить кадр, выходим из цикла

    # Зеркальное отображение кадра, чтобы пользователь видел "зеркальное" отражение своих движений:
    frame = cv2.flip(frame, 1)

    # Получаем размеры кадра (высота и ширина) для последующих вычислений координат:
    height, width, _ = frame.shape

    # Конвертируем цветовое пространство кадра из BGR (по умолчанию в OpenCV) в RGB,
    # так как Mediapipe работает именно с RGB-изображениями:
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Обработка кадра с помощью Mediapipe для обнаружения рук:
    result = hands.process(rgb_frame)

    # Если руки обнаружены, result.multi_hand_landmarks будет содержать список найденных рук:
    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            # Рисуем ключевые точки руки и соединения между ними на исходном кадре:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Извлекаем координаты кончиков большого и указательного пальцев:
            thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
            index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]

            # Преобразуем относительные координаты (от 0 до 1) в пиксели, умножая на ширину и высоту кадра:
            x_thumb = int(thumb_tip.x * width)
            y_thumb = int(thumb_tip.y * height)
            x_index = int(index_tip.x * width)
            y_index = int(index_tip.y * height)

            # Для наглядности рисуем окружности на кончиках пальцев:
            cv2.circle(frame, (x_thumb, y_thumb), 10, (0, 255, 0), cv2.FILLED)
            cv2.circle(frame, (x_index, y_index), 10, (0, 255, 0), cv2.FILLED)

            # Вычисляем евклидово расстояние между точками кончиков большого и указательного пальцев:
            distance = ((x_index - x_thumb) ** 2 + (y_index - y_thumb) ** 2) ** 0.5

            # Если расстояние меньше порогового значения (например, 40 пикселей),
            # считаем, что пользователь соединил пальцы (жест "щипок"):
            if distance < 40:
                # Выводим текст на экран для подтверждения, что жест распознан:
                cv2.putText(frame, 'Space Pressed!', (10, 50), cv2.FONT_HERSHEY_SIMPLEX,
                            1, (0, 0, 255), 2)
                # Эмулируем нажатие клавиши "пробел" с помощью pyautogui:
                pyautogui.press('space')
                # Задержка 0.3 секунды для предотвращения повторного срабатывания одного жеста:
                time.sleep(0.3)

    # Отображаем обработанный кадр в окне с названием "Hand Gesture Recognition":
    cv2.imshow("Hand Gesture Recognition", frame)

    # Если нажата клавиша ESC (код 27), выходим из цикла:
    if cv2.waitKey(1) & 0xFF == 27:
        break

# Освобождаем видеопоток и закрываем все окна, чтобы корректно завершить работу:
cap.release()
cv2.destroyAllWindows()
