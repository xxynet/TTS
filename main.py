import pygame
import subprocess
import keyboard
import pyperclip
import time
from langdetect import detect
import configparser
from plyer import notification


config = configparser.ConfigParser()
config.read('config.ini')
en_speaker = config.get('speaker', 'en')
zh_cn_speaker = config.get('speaker', 'zh-cn')
ja_speaker = config.get('speaker', 'ja')
ko_speaker = config.get('speaker', 'ko')

send_notification = config.get('settings', 'notification')


def detect_language(text):
    try:
        language = detect(text)
        return language
    except:
        return "Unknown"

def select_speaker(language):
    if language == 'zh-cn':
        return zh_cn_speaker
    elif language == 'en':
        return en_speaker
    elif language == 'ja':
        return ja_speaker
    elif language == 'ko':
        return ko_speaker
    else:
        return en_speaker

def notify(title,message):
    notification.notify(
        title=title,
        message=message,
        app_icon=None,
        timeout=2,
    )


key_count = 0
start_time = None

def on_key_event(event):
    global key_count, start_time

    if event.event_type == keyboard.KEY_DOWN and event.name == 'c' and keyboard.is_pressed('ctrl'):
        current_time = time.time()

        if start_time is None or (current_time - start_time) <= 1:
            key_count += 1
        else:
            key_count = 1

        start_time = current_time

        if key_count == 3:
            clipboard_content = pyperclip.paste()
            print("Detected 3 Ctrl+C presses within 1 second.")
            print("Clipboard Content:", clipboard_content)

            language = detect_language(clipboard_content)
            print("Detected Language:", language)

            if send_notification == 'true':
                notify("TTS", "Content: " + clipboard_content + "\n" + "Detected Language: " + language)

            text = clipboard_content
            speaker = select_speaker(language)
            # Create TTS Voice Note
            command = f'edge-tts --voice "{speaker}" --text "{text}" --write-media output.mp3'
            subprocess.run(command, shell=True)

            pygame.mixer.init()
            pygame.mixer.music.load("output.mp3")
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            pygame.mixer.quit()




            key_count = 0
            start_time = None

keyboard.hook(on_key_event)

try:
    keyboard.wait()
except KeyboardInterrupt:
    pass
finally:
    keyboard.unhook_all()