import pyrealsense2 as rs
import numpy as np
import cv2
import base64
from openai import OpenAI
import os

import requests

def upload_image_to_freeimage(image_path, api_key):
    url = "https://freeimage.host/api/1/upload"
    with open(image_path, 'rb') as image_file:
        files = {
            'source': image_file,
            'type': 'file',
        }
        data = {
            'key': api_key,
            'format': 'json'
        }
        response = requests.post(url, data=data, files=files)
        if response.status_code == 200:
            result = response.json()
            if result['status_code'] == 200:
                return result['image']['url']
            else:
                raise Exception(f"Failed to upload image. Error: {result['status_txt']}")
        else:
            raise Exception(f"Failed to upload image. Status code: {response.status_code}, Response: {response.text}")

api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise ValueError("No API key found. Please set the OPENAI_API_KEY environment variable.")


def process_image_cgpt(image_path):
    image_upload_api_key = '6d207e02198a847aa98d0a2a901485a5'
    try:
        link = upload_image_to_freeimage(image_path, image_upload_api_key)
        print(f"Image uploaded successfully: {link}")
    except Exception as e:
        print(e)


    client = OpenAI(
        api_key = api_key
    )

    response = client.chat.completions.create(
      model="gpt-4o-mini",
      messages=[
        {
          "role": "user",
          "content": [
            {"type": "text", "text": "Describe what do you see in this image? Make sure to include the relative positions and distance to each other"},
            {
              "type": "image_url",
              "image_url": {
                "url": link,
              },
            },
          ],
        }
      ],
      max_tokens=300,
    )

    return response.choices[0].message.content