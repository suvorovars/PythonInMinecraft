import cv2
import os

# Разбор GIF на кадры
gif_path = 'animation.gif'
output_folder = 'frames'
os.makedirs(output_folder, exist_ok=True)

# Читаем гифку и сохраняем кадры
cap = cv2.VideoCapture(gif_path)
frame_count = 0
while True:
    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.resize(frame, (80, 60))
    cv2.imwrite(os.path.join(output_folder, f'frame_{frame_count}.png'), frame)
    frame_count += 1
cap.release()

print("Кадры из GIF сохранены!")