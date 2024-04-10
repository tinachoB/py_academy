"""
Main entry point for the client project.
"""
import json
from typing import Optional

import requests
import speech_recognition as sr
from gtts import gTTS
import pygame
from io import BytesIO
from speech_recognition import UnknownValueError, WaitTimeoutError


def voice_to_text() -> Optional[str]:
    recognizer = sr.Recognizer()
    recognizer.pause_threshold = 0.8
    recognizer.energy_threshold = 4000

    with sr.Microphone() as origen:
        try:
            print("Start asking your question to the bot...")
            audio = recognizer.listen(origen, timeout=5, phrase_time_limit=10)
            result = recognizer.recognize_google(audio, language="es-ar")

            print("You said: " + result)
            return result

        except (WaitTimeoutError, UnknownValueError):
            print(f"Nothing to process.")
        except Exception as e:
            print(f"Exception: {e}")
    return None


def text_to_voice(message: str) -> None:
    tts = gTTS(text=message, lang="es")

    buffer = BytesIO()
    tts.write_to_fp(buffer)
    buffer.seek(0)

    pygame.mixer.init()
    pygame.mixer.music.load(buffer)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)


def main() -> None:
    question = voice_to_text()
    if question:
        data = {"ask": question, "session_id": "", "categories": []}
        response = requests.post("http://localhost:8000/api/bot", data=json.dumps(data))
        if response.status_code == 200:
            answer = response.json()["answer"]
            print(f"Answer: {answer}")
            text_to_voice(answer)


# Main entry point
if __name__ == "__main__":
    main()
