import json

import cv2
import numpy as np
from mcpi.minecraft import Minecraft

import time

import pyautogui


def build_texture_wall(width, height, block_id):
    """
    Функция для построения стены из блоков перед игроком.
    :param width: ширина стены
    :param height: высота стены
    :param block_id: ID блока для постройки
    """
    mc = Minecraft.create()
    x, y, z = mc.player.getTilePos()

    # Разворачиваем игрока в стандартное положение
    mc.player.setRotation(0)  # Поворачиваем на восток
    mc.player.setPitch(0)

    # Строим стену из блоков
    mc.setBlocks(x - width // 2, y - height // 2, z + 5, x + width // 2, y + height // 2, z + 5, block_id)
    mc.postToChat(f"Построена стена с блоком {block_id}")

def take_screenshot():
    """
    Функция для снятия скриншота экрана.
    """
    time.sleep(5)  # Даём время на открытие Minecraft
    time.sleep(3)
    screenshot = pyautogui.screenshot()  # Делаем скриншот
    return screenshot


def get_cropped_image(screenshot, crop_width=200, crop_height=200):
    """
    Функция для обрезки изображения.
    :param screenshot: скриншот
    :param crop_width: ширина обрезанной области
    :param crop_height: высота обрезанной области
    """
    screen_width, screen_height = pyautogui.size()
    x1 = (screen_width - crop_width) // 2
    y1 = (screen_height - crop_height) // 2
    x2 = x1 + crop_width
    y2 = y1 + crop_height

    # Преобразуем скриншот в массив numpy и обрезаем его
    image_np = np.array(screenshot)
    image_np = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
    cropped_image = image_np[y1:y2, x1:x2]
    return cropped_image

def get_average_color(image_np):
    """
    Функция для вычисления среднего цвета изображения.
    :param image_np: изображение в формате numpy
    """
    avg_color = np.mean(image_np, axis=(0, 1)).astype(int)
    return avg_color[::-1]  # Возвращаем цвет в формате RGB


blocks = [(35, i) for i in range(1, 14)]  # id блоков

pyautogui.hotkey('alt', 'tab')  # Переключаемся на вкладку с майнкрафтом
pyautogui.press('f1')  # отключаем интерфейс
# pyautogui.press('f11')  # открываем майнкрафт на весь экран
time.sleep(5)  # Задержка для открытия Minecraft; нажмите на "Вернуться к игре"

textures = {}

for b in blocks:
    build_texture_wall(40, 30, b)  # Построение стены
    time.sleep(2)
    img = take_screenshot()  # Снятие скриншота
    cropped_img = get_cropped_image(img)  # Обрезка изображения
    avg_color = get_average_color(cropped_img)  # Вычисление среднего цвета
    textures[str(b)] = avg_color.tolist() # Сохранение цвета в словарь
    print(f"Средний цвет блока {b}: {avg_color}")

# Сохранение данных в JSON-файл
with open("textures.json", "w") as json_file:
    json.dump(textures, json_file, indent=4)
    print("Данные сохранены в textures.json")

print(textures)