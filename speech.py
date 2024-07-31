## Use this if you wish for arm to move while it speaks
from pathlib import Path
from openai import OpenAI
import os
from playsound import playsound
from xarm.wrapper import XArmAPI
import time

ip = '192.168.1.189'
arm = XArmAPI(ip)
home_position = [-26, 1.4, 35.4, 0, 34, -25.7]  # Joint Values NOT XYZRPY
left_position = [-30, 1.4, 35.4, 0, 34, -25.7]
right_position = [-22, 1.4, 35.4, 0, 34, -25.7]

def return_home():
    arm.set_servo_angle(angle=home_position, speed=50, wait=True)

def speak(input):
    client = OpenAI()

    speech_file_path = Path(__file__).parent / "speech.mp3"
    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=input
    )

    response.write_to_file(speech_file_path)
    
    # Start the movement
    moving = True
    def move_arm():
        while moving:
            arm.set_servo_angle(angle=left_position, speed=20, wait=True)
            if not moving:
                break
            arm.set_servo_angle(angle=right_position, speed=20, wait=True)
    
    import threading
    move_thread = threading.Thread(target=move_arm)
    move_thread.start()

    # Play the speech
    playsound(speech_file_path)
    
    # Stop the movement after the speech is done
    moving = False
    move_thread.join()

    # Return to home position
    return_home()
