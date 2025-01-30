import numpy as np
import cv2

# Загрузка текстуры блока
texture = cv2.imread("textures/DIRT.png")

# Преобразование изображения в массив
image_array = np.array(texture)

# Нахождение среднего цвета по каналам RGB
average_color = np.mean(image_array, axis=(0, 1))

# Преобразуем цвет к целым числам (OpenCV хранит их как float)
average_color = average_color.astype(int)[::-1]

print(f"Средний цвет текстуры: {average_color}")
