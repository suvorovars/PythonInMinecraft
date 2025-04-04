import time
import random
from mcrcon import MCRcon

# Конфигурация RCON и имя игрока
RCON_HOST = "127.0.0.1"
RCON_PORT = 25575
RCON_PASSWORD = "admin"
PLAYER_NAME = "i_am_npc"
ZOMBIE_KILL_GOAL = 10

# Список наград (настройте по своему желанию)
reward_items = [
    "minecraft:diamond",
    "minecraft:golden_apple",
    "minecraft:iron_sword",
    "minecraft:potion{Potion:\"minecraft:healing\"}"
]


# Начальное значение убийств (получаем с сервера)
def get_zombie_kills(mcr):
    response = mcr.command(f"scoreboard players get {PLAYER_NAME} zombieKills")
    print(response)
    # Ожидаем ответ в формате: 'Steve has 3 zombieKills'
    try:
        parts = response.split()
        kills = int(parts[2])
        return kills
    except Exception as e:
        print("Ошибка парсинга счёта:", e)
        return 0


def give_reward(mcr):
    item = random.choice(reward_items)
    mcr.command(f"give {PLAYER_NAME} {item} 1")
    mcr.command(f"say {PLAYER_NAME} получил награду: {item}!")


def monitor_scoreboard():
    with MCRcon(RCON_HOST, RCON_PASSWORD, port=RCON_PORT) as mcr:
        # Отправляем стартовое сообщение
        mcr.command("say Охота на зомби началась!")

        prev_kills = get_zombie_kills(mcr)
        while prev_kills < ZOMBIE_KILL_GOAL:
            time.sleep(1)  # Ждём 1 секунду между проверками
            current_kills = get_zombie_kills(mcr)
            if current_kills > prev_kills:
                # Убийство зафиксировано, выдаем награду
                mcr.command(f"say Убито зомби: {current_kills}/{ZOMBIE_KILL_GOAL}")
                give_reward(mcr)
                prev_kills = current_kills

        mcr.command(f"say Поздравляем, {PLAYER_NAME}! Ты победил в охоте на зомби!")


monitor_scoreboard()
