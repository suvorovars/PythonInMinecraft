import cv2
from mcpi import block
from mcpi.minecraft import Minecraft

# Подключение к Minecraft
mc = Minecraft.create()
image = cv2.imread("img.png")
resized_image = cv2.resize(image, (100, 50), interpolation=cv2.INTER_AREA)
# cv2.imshow("low image", resized_image)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

block_colors = {
    block.STONE: [126, 126, 126],
    block.GOLD_BLOCK: [248, 199, 44],     
    block.Block(35, 14) : [161, 39, 34],
    block.Block(35, 5) : [51, 136, 44],
    block.Block(35, 0) : [221, 221, 221],
    block.Block(35, 9): [106, 138, 201],
    block.Block(35, 1): [221, 135, 49],
    block.DIRT: [138, 99, 68],
}


def get_closest_block(pixel_color):
    closest_block = None
    min_difference = float('inf')  # Начинаем с очень большого числа

    for block_name, block_color in block_colors.items():
        # Считаем разницу по каждому каналу
        diff_r = abs(int(pixel_color[0]) - block_color[0])
        diff_g = abs(int(pixel_color[1]) - block_color[1])
        diff_b = abs(int(pixel_color[2]) - block_color[2])

        # Считаем сумму разниц
        total_diff = diff_r + diff_g + diff_b

        # Если нашли меньшую разницу — запоминаем этот блок
        if total_diff < min_difference:
            min_difference = total_diff
            closest_block = block_name

    return closest_block


# Начальные координаты
x, y, z = mc.player.getTilePos()

# Для каждого пикселя выбираем блок и строим его
for i in range(resized_image.shape[0]):  # Строки
    for j in range(resized_image.shape[1]):  # Столбцы
        pixel_color = resized_image[i, j][::-1]  # Цвет пикселя
        block_type = get_closest_block(pixel_color)  # Находим подходящий блок

        # Размещаем блок в Minecraft
        mc.setBlock(x + j, y - i, z, block_type)
print(resized_image[10, 10])