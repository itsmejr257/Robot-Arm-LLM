# Human-Robot Interaction with a LLM Intermediary

## Objective

This project aims to transform the traditional robotics pipeline from:

1. Human gives tasks via Natural Language.
2. Programmer performs decision making.
3. Programmer generates code for the robotic scenario.
4. Robot performs the action.

into:

1. Human gives tasks via Natural Language.
2. LLM performs decision making and generates code for the robotic scenario.
3. Robot performs the action.

This projects utilizes features present in the OpenAi API (ChatGPT4o) to create a seamless interaction between a human and a robot, giving the illusion of natural interaction.

## Table of Contents

- [Setup](#setup)
  - [Tools Used](#tools-used)
  - [Installation](#installation)
  - [Configuration](#configuration)
- [Design Principles](#design-principles)
- [Project Examples](#project-examples)
- [Usage](#usage)
## Setup

### Tools Used
1. Robot : UFactory Lite6, equipped with a Realsense D455
  - UFactory Lite6 and Realsense D455 was directly connected to the PC via ethernet and USB respectively
2. Programming Language : Python
3. OS : Ubuntu 22.04

### Installation
1. Setup [xArm-Python-SDK](https://github.com/xArm-Developer/xArm-Python-SDK)
2. Clone this repository

   ```bash 
   git clone placeholder
   ```
3. Setup OpenAI API Key

   ```bash
   python3 setup-openai-key.py
   ```
4. Install Dependencies
   ```bash
   pip install -e requirements.txt

## Design Principles

1. **Prompt to be Sent:** A set of high-level robot API (in this case, the xArm Python SDK), along with specific instructions such as its bounds.
2. **Process (Basic and Drawinf Bot):** 
   - User sends a message to the API.
   - The API returns Python code to be executed on the robot, along with its intentions.
   - Python code is extracted from the assistant's message and executed locally.
3. **Process (RealSense Bot):**
   - User sends a message to the API.
   - API returns either a request for a function call, or a message
   - If Request for Function Call, Function is automatically ran, and results are sent back to the LLM
   - If Message, Immediately printed back to User.

## Project Examples

1. **Robot Arm Alone:** Interaction with the robot arm using only the high-level robot API.
2. **Robot Arm with Camera:** Interaction using the Function Calling API to enhance capabilities.
3. **Drawing Robot:** Interaction using both the high-level robot API and the Function Calling API.

## Usage
1. Robot Arm Alone

   ```bash
   python3 chatgpt-base.py
   ```
2. Drawing Robot Arm

   ```bash
   python3 chatgpt-drawing.py
   ```
   
3. Robot Arm with Realsense D455

   ```bash
   python3 chatgpt-realsense.py
   python3 chatgpt-realsense-speech.py #If you wish to communicate with robot via speech
   ```
   Within the file
   ```python
   ##FOR IMPORTS
   from detector import detect #Use this if using yolov5
   from v8detector import detect #Use this if using yolov8

   
   ```

