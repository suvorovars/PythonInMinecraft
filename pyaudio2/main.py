import time
import speech_recognition as sr
from mcrcon import MCRcon

# Настройки RCON и игрока
RCON_HOST, RCON_PORT, RCON_PASSWORD = "localhost", 25575, "admin"
PLAYER = "i_am_npc"

# Словарь синонимов команд
COMMAND_SYNONYMS = {
    "вперёд":     ["вперёд", "идти вперед", "наперёд"],
    "назад":      ["назад", "идти назад"],
    "прыжок":     ["прыжок", "прыгай"],
    "ставь блок": ["поставь блок", "ставь блок", "блок"],
    "день":       ["день", "установи день"],
    "ночь":       ["ночь", "установи ночь"],
}

def recognize_wake(rec, mic):
    with mic as source:
        audio = rec.listen(source, phrase_time_limit=1)
    try:
        return rec.recognize_google(audio, language="ru-RU").lower()
    except:
        return ""

def recognize_command(rec, mic):
    with mic as source:
        audio = rec.listen(source, phrase_time_limit=3)
    try:
        return rec.recognize_google(audio, language="ru-RU").lower()
    except:
        return ""

def find_command(text):
    for key, variants in COMMAND_SYNONYMS.items():
        for v in variants:
            if v in text:
                return key
    return None

def main():
    # Инициализация распознавания речи
    rec = sr.Recognizer()
    mic = sr.Microphone()
    print("Подкачка уровня шума...")
    with mic as source:
        rec.adjust_for_ambient_noise(source, duration=4)

    # Подключаемся к RCON
    with MCRcon(RCON_HOST, RCON_PASSWORD, port=RCON_PORT) as mcr:
        mcr.connect()
        print("Система голосового управления запущена.")
        print("Скажите wake-слово 'Майнкрафт' для начала.")

        while True:
            wake = recognize_wake(rec, mic)
            if "майнкрафт" in wake or "minecraft" in wake:
                mcr.command(f"say {PLAYER}, я слушаю...")
                cmd_text = recognize_command(rec, mic)
                print("Распознано:", cmd_text)

                cmd_key = find_command(cmd_text)
                if cmd_key:
                    # Получаем локальную позицию игрока
                    resp = mcr.command(f"data get entity {PLAYER} Pos")
                    print("Локальная позиция игрока:", resp)
                    # Здесь можно распарсить resp, но для примера исполним простое действие:
                    if cmd_key == "вперёд":
                        mcr.command(f"tp {PLAYER} ~ ~ ~1")
                    elif cmd_key == "назад":
                        mcr.command(f"tp {PLAYER} ~ ~ ~-1")
                    elif cmd_key == "прыжок":
                        mcr.command(f"execute at {PLAYER} run tp {PLAYER} ~ ~1 ~")
                    elif cmd_key == "ставь блок":
                        mcr.command(f"setblock ~ ~-1 ~ minecraft:stone")
                    elif cmd_key == "день":
                        mcr.command("time set day")
                    elif cmd_key == "ночь":
                        mcr.command("time set night")

                    mcr.command(f"say {PLAYER}, команда '{cmd_key}' выполнена!")
                else:
                    mcr.command(f"say Не понял: '{cmd_text}'")
                print("Жду wake-слово...")

if __name__ == "__main__":
    main()
