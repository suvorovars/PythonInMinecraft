import time
import random
from mcrcon import MCRcon

# RCON конфигурация
RCON_HOST = "localhost"
RCON_PORT = 25575
RCON_PASSWORD = "admin"

# Параметры лабиринта
WIDTH = 37  # ширина лабиринта (в клетках, нечетное число)
HEIGHT = 37  # высота лабиринта (в клетках, нечетное число)
WALL_HEIGHT = 3  # высота стен
ORIGIN_X, ORIGIN_Y, ORIGIN_Z = -200, 100, 200  # начальные координаты области лабиринта

# Точка старта и финиша (относительно origin)
START = (1, 1)
GOAL = (WIDTH - 2, HEIGHT - 2)  # клетка, где будет размещён блок-финиш

# Время между обновлениями лабиринта (в секундах)
REFRESH_INTERVAL = 15


def generate_maze(w, h):
    """Генерирует лабиринт алгоритмом recursive backtracker.
       0 – стена, 1 – проход"""
    maze = [[0] * w for _ in range(h)]

    def carve(x, y):
        dirs = [(2, 0), (-2, 0), (0, 2), (0, -2)]
        random.shuffle(dirs)
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if 0 < nx < w - 1 and 0 < ny < h - 1 and maze[ny][nx] == 0:
                maze[y + dy // 2][x + dx // 2] = 1
                maze[ny][nx] = 1
                carve(nx, ny)

    maze[START[1]][START[0]] = 1
    carve(START[0], START[1])
    return maze


def build_maze(mcr, maze):
    """Строит лабиринт в Minecraft: стены из камня, проходы – воздух.
       Дополнительно ставит золотой блок в клетке финиша."""
    for j, row in enumerate(maze):
        for i, cell in enumerate(row):
            x = ORIGIN_X + i
            z = ORIGIN_Z + j
            # Строим пол
            mcr.command(f"setblock {x} {ORIGIN_Y - 1} {z} minecraft:stone")
            if cell == 0:
                # Стена: заполняем вертикальный столбец от ORIGIN_Y до ORIGIN_Y+WALL_HEIGHT-1
                for y in range(ORIGIN_Y, ORIGIN_Y + WALL_HEIGHT):
                    mcr.command(f"setblock {x} {y} {z} minecraft:stone")
            else:
                # Проход: очищаем вертикальный столбец (воздух)
                for y in range(ORIGIN_Y, ORIGIN_Y + WALL_HEIGHT):
                    mcr.command(f"setblock {x} {y} {z} minecraft:air")
    # Отмечаем финиш: ставим золотой блок в клетке GOAL
    finish_x = ORIGIN_X + GOAL[0]
    finish_z = ORIGIN_Z + GOAL[1]
    for y in range(ORIGIN_Y, ORIGIN_Y + WALL_HEIGHT):
        mcr.command(f"setblock {finish_x} {y} {finish_z} minecraft:gold_block")
    mcr.command("say Лабиринт Обновился")



def teleport_to_start(mcr):
    """Телепортирует игрока к стартовой точке лабиринта."""
    sx = ORIGIN_X + START[0]
    sy = ORIGIN_Y
    sz = ORIGIN_Z + START[1]
    mcr.command(f"tp @p {sx} {sy} {sz}")


def player_at_goal(mcr):
    """Проверяет, достиг ли игрок области финиша.
       Финиш считается достигнутым, если игрок близок к центру клетки финиша."""
    resp = mcr.command("data get entity @p Pos")
    try:
        coords = resp.split('[')[1].split(']')[0].split(',')
        px = float(coords[0].strip()[:-1])
        pz = float(coords[2].strip()[:-1])
        gx = ORIGIN_X + GOAL[0] + 0.5  # центр клетки
        gz = ORIGIN_Z + GOAL[1] + 0.5
        return abs(px - gx) < 1 and abs(pz - gz) < 1
    except Exception as e:
        print("Ошибка парсинга позиции игрока:", e)
        return False


def clear_maze(mcr):
    """Очищает область лабиринта, заливая её воздухом."""
    for j in range(HEIGHT):
        for i in range(WIDTH):
            x = ORIGIN_X + i
            z = ORIGIN_Z + j
            for y in range(ORIGIN_Y - 1, ORIGIN_Y + WALL_HEIGHT):
                mcr.command(f"setblock {x} {y} {z} minecraft:air")


def main():
    with MCRcon(RCON_HOST, RCON_PASSWORD, port=RCON_PORT) as mcr:
        mcr.connect()
        mcr.command("say Лабиринт начинается!")

        # Построение начального лабиринта
        maze = generate_maze(WIDTH, HEIGHT)
        build_maze(mcr, maze)
        # Телепортируем игрока на стартовую позицию
        teleport_to_start(mcr)

        last_refresh = time.time()
        # Основной цикл: проверка прохождения и обновление лабиринта
        while True:
            if player_at_goal(mcr):
                mcr.command("say Поздравляем! Лабиринт пройден!")
                break
            if time.time() - last_refresh > REFRESH_INTERVAL:
                mcr.command("say Лабиринт меняется...")
                maze = generate_maze(WIDTH, HEIGHT)
                build_maze(mcr, maze)

                last_refresh = time.time()
            time.sleep(1)

        # Откат изменений: очищаем область лабиринта
        mcr.command("say Очищаю лабиринт...")
        clear_maze(mcr)
        mcr.command("say Игра завершена!")
        mcr.disconnect()


if __name__ == "__main__":
    main()
