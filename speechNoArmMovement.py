#Use this if you do not want Arm to move when it speaks
from pathlib import Path
from openai import OpenAI
import os
from playsound import playsound
import time

def speak(input):
    client = OpenAI()

    speech_file_path = Path(__file__).parent / "speech.mp3"
    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=input
    )

    response.write_to_file(speech_file_path)


    # Play the speech
    playsound(speech_file_path)
    