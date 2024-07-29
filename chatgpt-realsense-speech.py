from openai import OpenAI
from xarm.wrapper import XArmAPI
#from detector import detect
from v8detector import detect
import json
from functionsrealsense import *
from openai import OpenAI
import re
import argparse
import math
import numpy as np
import os
import time
from speech import speak
import speech_recognition as sr

parser = argparse.ArgumentParser()
parser.add_argument("--sysprompt", type=str, default="system_prompts/lite6_realsense.txt")
args = parser.parse_args()

ip = '192.168.1.189'
arm = XArmAPI(ip)
arm.motion_enable(enable=True)
arm.set_mode(0)  # Set the arm to position control mode
arm.set_state(state=0)

return_home()

armFunction = [
    {
        "name": "detect",
        "description" : "Scans the play area and gets all visible items in frame of camera, returns a list of item names and their corresponding camera coordinates"
    },
    {
        "name": "return_home",
        "description" : "Moves the robot arm back to its home position to detect objects"
    },
    {
        "name" : "arm_point_from_camera_coord",
        "description" : "Given the Camera Coordinates of an object, moves the arm to point at the specified camera coordinates",
        "parameters": {
            "type": "object",
            "properties": {
                "x": {"type": "number", "description" : "The Camera X coordinate of Object"},
                "y": {"type": "number", "description" : "The camera Y coordinate of the Object"},
            },
            "required": ["x", "y"]
        }
    }
]

print("Initializing ChatGPT...")
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise ValueError("No API key found. Please set the OPENAI_API_KEY environment variable.")

client = OpenAI(
    api_key = api_key
)

with open(args.sysprompt, "r") as f:
    sysprompt = f.read()

messages = [ 
    { "role" : "system", "content" : sysprompt },
]

completion = client.chat.completions.create(
    model="gpt-4o",
    messages = messages,
    functions = armFunction
)

def listen_for_wake_word(wake_word="hello robot"):
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("Listening for the wake word...")
        recognizer.adjust_for_ambient_noise(source)

        while True:
            audio_data = recognizer.listen(source)
            try:
                text = recognizer.recognize_google(audio_data).lower()
                if wake_word in text:
                    print("Wake word detected!")
                    return
            except sr.UnknownValueError:
                pass
            except sr.RequestError:
                print("Could not request results from Google Speech Recognition service")

def recognize_speech_from_mic():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        print("Listening for your speech...")

        audio_data = recognizer.listen(source)
        try:
            print("Recognizing your speech...")
            text = recognizer.recognize_google(audio_data)
            print(f"You said: {text}")
            return text
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand the audio")
            raise Exception("Dont Understand")
        except sr.RequestError:
            print("Could not request results from Google Speech Recognition service")
            raise Exception("Dont Understand")
        
def handle_response(responseMessage):
    while hasattr(responseMessage, 'function_call') and responseMessage.function_call is not None and responseMessage.function_call.name in globals():
        print(f"GPT has called the {responseMessage.function_call.name} function")
        function = globals()[responseMessage.function_call.name]

        if responseMessage.function_call.name == "arm_point_from_camera_coord":
            args = json.loads(responseMessage.function_call.arguments)
            x = args.get('x')
            y = args.get('y')
            function = globals()[responseMessage.function_call.name]
            function(x, y)
            items = "Function successfully ran"
        else:
            items = function()

        function_name = responseMessage.function_call.name


        messages.append(
            { "role": "function", "name": f"{function_name}", "content": json.dumps(items) }
        )
    
        secondResponse = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            functions=armFunction
        )

        messages.append(secondResponse.choices[0].message)
        print(secondResponse.choices[0].message)
        responseMessage = secondResponse.choices[0].message

    speak(responseMessage.content)
    return responseMessage

def ask(prompt):
    messages.append(
        {
            "role": "user",
            "content": prompt,
        }
    )
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        functions=armFunction,
    )

    if (completion.choices[0].message.content is not None):
        messages.append(
            {
                "role": "assistant",
                "content": completion.choices[0].message.content,
            }
        )
        
    return completion.choices[0].message


class colors:  # You may need to change color settings
    RED = "\033[31m"
    ENDC = "\033[m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"

while True:
    #question = input(colors.YELLOW + "Lite6> " + colors.ENDC)

    try:
        question = recognize_speech_from_mic()
    except:
        speak("sorry i couldnt catch what you were saying. Say it again")
        continue
    
    if question == "!quit" or question == "!exit":
        break

    if question == "!clear":
        os.system("cls")
        continue

    response = ask(question)

    if response.function_call is not None:
        response = handle_response(response)
    else:
        speak(response.content)
        print(f"\n{response}\n")

        