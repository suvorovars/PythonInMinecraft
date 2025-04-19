import time
import speech_recognition as sr
from mcrcon import MCRcon

RCON_HOST = "localhost"
RCON_PORT = 25575
RCON_PASSWORD = "admin"

COMMANDS = {
    "вперёд":   "tp @p ~ ~ ~1",
    "назад":    "tp @p ~ ~ ~-1",
    "влево":    "tp @p ~-1 ~ ~",
    "вправо":   "tp @p ~1 ~ ~",
    "прыжок":   "execute at @p run tp @p ~ ~1 ~",
    "день":     "time set day",
    "ночь":     "time set night",
    "блок":     "setblock ~ ~-1 ~ minecraft:stone"
}

def recognize_command(recognizer, mic):
    """Слушаем микрофон и возвращаем распознанный текст."""
    with mic as source:
        audio = recognizer.listen(source, phrase_time_limit=3)
    try:
        return recognizer.recognize_google(audio, language="ru-RU").lower()
    except sr.UnknownValueError:
        return None
    except sr.RequestError:
        return None

def main():
    # Инициализация
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    with mic as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)

    print("Голосовой контроль запущен. Говорите команду или 'стоп' для выхода.")

    with MCRcon(RCON_HOST, RCON_PASSWORD, port=RCON_PORT) as mcr:
        mcr.connect()
        while True:
            text = recognize_command(recognizer, mic)
            if not text:
                continue
            print("Распознано:", text)

            if text in ("выход", "стоп"):
                mcr.command("say Голосовой контроль завершен!")
                break

            cmd = COMMANDS.get(text)
            if cmd:
                mcr.command(cmd)
                print("Выполнена команда:", cmd)
            else:
                print("Неизвестная команда:", text)
        mcr.disconnect()

if __name__ == "__main__":
    main()
