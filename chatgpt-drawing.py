from openai import OpenAI
import re
import argparse
import math
import numpy as np
import os
import sys
import functions
from xarm.wrapper import XArmAPI
from drawable_objects import DRAWABLE_OBJECTS

parser = argparse.ArgumentParser()
parser.add_argument("--prompt", type=str, default="prompts/lite6_drawing.txt")
parser.add_argument("--sysprompt", type=str, default="system_prompts/lite6_drawing.txt")
args = parser.parse_args()

print("Initializing ChatGPT...")
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise ValueError("No API key found. Please set the OPENAI_API_KEY environment variable.")

client = OpenAI(
    api_key = api_key
)

function_for_arm = [
    {
        "name": "move_arm",
        "description": "Moves the robotic arm to the specified coordinates. Ensure function is called with positional arguements. E.g, move_arm(x,y,z)",
        "parameters": {
            "type": "object",
            "properties": {
                "x": {"type": "number", "description": "X coordinate"},
                "y": {"type": "number", "description": "Y coordinate"},
                "z": {"type": "number", "description": "Z coordinate"}
            },
            "required": ["x", "y", "z"]
        }
    },
    {
        "name": "get_position",
        "description": "Gets the current position of the robotic arm. Returns a tuple of the form (code, [x, y, z, roll, pitch, yaw])",
        "parameters": {
            "type": "object",
            "properties": {
                "is_radian": {"type": ["boolean", "null"], "description": "Return values in radians if true"}
            },
            "required": []
        }
    },
    {
        "name": "draw_realistic",
        "description": f"Draws a realistic sketch of a provided image. Only use this function when asked to draw one of the following objects: {', '.join(DRAWABLE_OBJECTS.keys())}. Do not use for any other object. Function uses positional arguements",
        "parameters": {
            "type": "object",
            "properties": {
                "image": {"type": "string", "description": "Refers to the name of the image."}
            }
        }
    }
]

with open(args.sysprompt, "r") as f:
    sysprompt = f.read()

chat_history = [
    {
        "role": "system",
        "content": sysprompt
    },
    {
        "role": "user",
        "content": "move the arm 10 units up"
    },
    {
        "role": "assistant",
        "content": """```python
functions.move_arm(arm.get_position()[0], arm.get_position()[1], arm.get_position()[2] + 10)

This code uses the move_arm() function to move the robotic arm to a new position that is 10 units up from the current position. It does this by getting the current position of the arm using get_position() and then calling move_arm() with the same X and Y coordinates, but with the Z coordinate increased by 10. The arm will then move to this new position using move_arm()."""
    }
]

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
        functions=function_for_arm,
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


class colors:  # You may need to change color settings
    RED = "\033[31m"
    ENDC = "\033[m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"

## Initialization of Arm ------------------------------------------
print(f"Initializing Arm...")
ip = '192.168.1.189'
arm = XArmAPI(ip)
arm.motion_enable(enable=True)
arm.set_mode(0)
arm.set_state(state=0)

#arm.reset(wait=True)
arm.set_position(208.8,-3.9,230.9)
print(f"Done.")

with open(args.prompt, "r") as f:
    prompt = f.read()

ask(prompt)
print("Welcome to the Arm chatbot! What do you want me to do?")

while True:
    question = input(colors.YELLOW + "Lite6> " + colors.ENDC)

    if question == "!quit" or question == "!exit":
        break

    if question == "!clear":
        os.system("cls")
        continue

    response = ask(question)

    print(f"\n{response}\n")

    code = extract_python_code(response)
    if code is not None:
        print("Please wait while I run the code in the Arm...")
        exec(extract_python_code(response))
        print("Done!\n")
        
    arm.set_position(208.8,-3.9,230.9)
