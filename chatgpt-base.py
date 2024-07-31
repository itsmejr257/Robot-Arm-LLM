from openai import OpenAI
import re
import argparse
import math
import numpy as np
import os
import sys
from xarm.wrapper import XArmAPI
from speechNoArmMovement import speak
import speech_recognition as sr

parser = argparse.ArgumentParser()
parser.add_argument("--prompt", type=str, default="prompts/lite6_basic.txt")
parser.add_argument("--sysprompt", type=str, default="system_prompts/lite6_basic.txt")
args = parser.parse_args()

print("Initializing ChatGPT...")
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise ValueError("No API key found. Please set the OPENAI_API_KEY environment variable.")

client = OpenAI(
    api_key = api_key
)

with open(args.sysprompt, "r") as f:
    sysprompt = f.read()


chat_history = [
    {
        "role": "system",
        "content": sysprompt
    },
    {
    "role": "user",
    "content": "Hello Robot!"
    },
    {
    "role": "assistant",
    "content": """```python
    current_position = arm.get_position()
    arm.set_position(x=current_position[1][0], y=current_position[1][1] + 10, z=current_position[1][2])
    ```
    Hello Human i was waving to you!
    """
    }
]

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


def ask(prompt):
    chat_history.append(
        {
            "role": "user",
            "content": prompt,
        }
    )
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=chat_history,
        temperature=0
    )
    chat_history.append(
        {
            "role": "assistant",
            "content": completion.choices[0].message.content,
        }
    )
    return chat_history[-1]["content"]


print(f"Done.")

code_block_regex = re.compile(r"```(.*?)```", re.DOTALL)


def extract_python_code(content):
    code_blocks = code_block_regex.findall(content)
    if code_blocks:
        full_code = "\n".join(code_blocks)

        if full_code.startswith("python"):
            full_code = full_code[7:]

        return full_code
    else:
        return None

def extract_text(content):
    # Find all code blocks
    code_blocks = code_block_regex.findall(content)
    
    # Find the position of the last code block
    last_code_block_end = content.rfind(f"```{code_blocks[-1]}```")
    
    # Extract the text after the last code block
    text_after_code = content[last_code_block_end + len(f"```{code_blocks[-1]}```"):].strip()
    
    return text_after_code if text_after_code else None
class colors:  # You may need to change color settings
    RED = "\033[31m"
    ENDC = "\033[m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"

## Initialization of Arm ------------------------------------------
print(f"Initializing Arm...")
#ip = '192.168.1.189'
#arm = XArmAPI(ip)
#arm.motion_enable(enable=True)
#arm.set_mode(0)
#arm.set_state(state=0)

#arm.reset(wait=True)
#arm.set_position(208.8,-3.9,230.9)
print(f"Done.")

with open(args.prompt, "r") as f:
    prompt = f.read()

ask(prompt)
print("Welcome to the Arm chatbot! What do you want me to do?")

while True:
    question = input(colors.YELLOW + "Lite6> " + colors.ENDC)

    """
    try:
        question = recognize_speech_from_mic()
    except:
        speak("sorry i couldnt catch what you were saying. Say it again")
        continue
        """
    
    if question == "!quit" or question == "!exit":
        break

    if question == "!clear":
        os.system("cls")
        continue

    response = ask(question)

    print(f"\n{response}\n")

    code = extract_python_code(response)
    text = extract_text(response)
    if code is not None:
        print("Please wait while I run the code in the Arm...")
        #exec(extract_python_code(response))
        print("Done!\n")

    speak(str(text))
        
    #arm.go_home()
