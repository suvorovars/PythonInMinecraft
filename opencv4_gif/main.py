import os
import time

import cv2
from mcpi import block
from mcpi.minecraft import Minecraft

# Подключение к Minecraft
mc = Minecraft.create()

import json
import ast

# Загрузка JSON
with open("textures.json", "r") as json_file:
    block_colors = json.load(json_file)

# Функция для преобразования ключей
def convert_key(k):
    try:
        return ast.literal_eval(k)  # Пробуем преобразовать в кортеж
    except (ValueError, SyntaxError):
        return int(k)  # Если ошибка — это обычное число

block_colors = {convert_key(k): v for k, v in block_colors.items()}


def get_closest_block(pixel_color):
    closest_block = None
    min_difference = float('inf')  # Начинаем с очень большого числа

    for block_name, block_color in block_colors.items():
        # Считаем разницу по каждому каналу
        diff_r = abs(int(pixel_color[0]) - block_color[0])
        diff_g = abs(int(pixel_color[1]) - block_color[1])
        diff_b = abs(int(pixel_color[2]) - block_color[2])

        # Считаем сумму разниц
        total_diff = diff_r ** 2 + diff_g ** 2 + diff_b ** 2

        # Если нашли меньшую разницу — запоминаем этот блок
        if total_diff < min_difference:
            min_difference = total_diff
            closest_block = block_name

    return closest_block


# Начальные координаты
x, y, z = mc.player.getTilePos()

# Фрагмент кода для вставки в существующую программу
frame_files = sorted(os.listdir('frames'))
for frame_file in frame_files:
    img = cv2.imread(os.path.join('frames', frame_file))
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            color = img[i, j]
            block_type = get_closest_block(color[::-1])
            mc.setBlock(x + j, y - i, z, block_type)
    time.sleep(0.5)
print("Анимация завершена!")
