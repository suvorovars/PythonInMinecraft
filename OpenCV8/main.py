import cv2
import mediapipe as mp
import time
import random
import numpy as np
from mcpi.minecraft import Minecraft
from mcpi import entity  # Модуль для работы с мобами

# Подключаемся к серверу Minecraft
mc = Minecraft.create()

# Настраиваем видеопоток с веб-камеры
cap = cv2.VideoCapture(0)

# Инициализация Face Mesh для распознавания лица (Mediapipe)
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh()  # Используем модель Face Mesh для получения 468 ключевых точек
mp_draw = mp.solutions.drawing_utils  # Объект для отрисовки ключевых точек (при необходимости)

# Определяем списки мобов
# Дружелюбные мобы для счастливого выражения
friendly_mobs = [entity.HORSE, entity.COW, entity.SHEEP]
# Враждебные мобы для злого выражения
hostile_mobs = [entity.ZOMBIE, entity.CREEPER, entity.SKELETON]


def get_emotion(face_landmarks, width, height):
    """
    Определяет эмоцию по ключевым точкам лица.
    Используются точки губ для определения улыбки и точки бровей для определения злости.

    Условия:
    - Если отношение высоты рта к ширине (smile_ratio) больше 0.025, лицо считается счастливым.
    - Если нормированное расстояние между внутренними точками бровей (norm_brow_distance) меньше 0.27,
      лицо считается злым.
    - Иначе, лицо нейтральное.
    """
    # Извлекаем ключевые точки рта:
    # Точка 61 - левый угол рта, 291 - правый угол рта
    # Точки 13 и 14 - верхняя и нижняя губа соответственно
    left_mouth = face_landmarks.landmark[61]
    right_mouth = face_landmarks.landmark[291]
    upper_lip = face_landmarks.landmark[13]
    lower_lip = face_landmarks.landmark[14]

    # Преобразуем нормализованные координаты в пиксели
    x_left = int(left_mouth.x * width)
    y_left = int(left_mouth.y * height)
    x_right = int(right_mouth.x * width)
    y_right = int(right_mouth.y * height)
    y_upper = int(upper_lip.y * height)
    y_lower = int(lower_lip.y * height)

    # Вычисляем ширину и высоту рта
    mouth_width = np.linalg.norm(np.array([x_right, y_right]) - np.array([x_left, y_left]))
    mouth_height = abs(y_lower - y_upper)
    # Рассчитываем отношение: чем больше значение, тем более выражен рот (могут быть нюансы интерпретации)
    smile_ratio = mouth_height / mouth_width

    # Извлекаем внутренние точки бровей:
    # Точка 55 (левая) и 285 (правая) – внутренние точки бровей
    left_inner_brow = face_landmarks.landmark[55]
    right_inner_brow = face_landmarks.landmark[285]
    x_left_brow = int(left_inner_brow.x * width)
    y_left_brow = int(left_inner_brow.y * height)
    x_right_brow = int(right_inner_brow.x * width)
    y_right_brow = int(right_inner_brow.y * height)

    # Вычисляем расстояние между бровями
    brow_distance = np.linalg.norm(np.array([x_right_brow, y_right_brow]) - np.array([x_left_brow, y_left_brow]))

    # Нормализуем по межглазному расстоянию (точки 33 и 263)
    left_eye = face_landmarks.landmark[33]
    right_eye = face_landmarks.landmark[263]
    x_left_eye, y_left_eye = int(left_eye.x * width), int(left_eye.y * height)
    x_right_eye, y_right_eye = int(right_eye.x * width), int(right_eye.y * height)
    interocular_distance = np.linalg.norm(np.array([x_left_eye, y_left_eye]) - np.array([x_right_eye, y_right_eye]))

    norm_brow_distance = brow_distance / interocular_distance

    # Выводим значения для отладки (при необходимости)
    print(f"Smile ratio: {smile_ratio:.3f}, Norm brow distance: {norm_brow_distance:.3f}")

    # Определяем эмоцию по заданным порогам
    if smile_ratio > 0.025:
        return "happy"
    elif norm_brow_distance < 0.27:
        return "angry"
    else:
        return "neutral"


def spawn_mob(mob_list):
    """
    Спавнит случайного моба из списка mob_list рядом с игроком.
    """
    x, y, z = mc.player.getTilePos()
    mob_type = random.choice(mob_list)
    # Спавним моба с небольшим случайным смещением от позиции игрока
    mc.spawnEntity(x + random.randint(-3, 3), y, z + random.randint(-3, 3), mob_type)


# Основной цикл программы
while True:
    ret, frame = cap.read()  # Читаем кадр с камеры
    if not ret:
        break

    # Зеркальное отражение кадра для удобства пользователя
    frame = cv2.flip(frame, 1)
    height, width, _ = frame.shape

    # Преобразуем изображение в RGB (Mediapipe требует RGB)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Обрабатываем кадр с помощью Face Mesh
    result = face_mesh.process(rgb_frame)

    # Если обнаружено лицо, обрабатываем найденные ключевые точки
    if result.multi_face_landmarks:
        for face_landmarks in result.multi_face_landmarks:
            # Определяем эмоцию по лицу с использованием ключевых точек губ и бровей
            emotion = get_emotion(face_landmarks, width, height)
            # Отображаем определённую эмоцию на экране
            cv2.putText(frame, f"Emotion: {emotion}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # Спавним мобов в зависимости от определённой эмоции
            if emotion == "happy":
                spawn_mob(friendly_mobs)
                mc.postToChat("Ты улыбаешься! Появились мирные мобы!")
            elif emotion == "angry":
                spawn_mob(hostile_mobs)
                mc.postToChat("Ты зол! Осторожно, появились монстры!")

    # Отображаем видео с наложенной информацией
    cv2.imshow("Emotion Detection", frame)

    # Выход из программы при нажатии клавиши ESC (код 27)
    if cv2.waitKey(1) & 0xFF == 27:
        break

# Освобождаем ресурсы: закрываем видеопоток и окно
cap.release()
cv2.destroyAllWindows()
