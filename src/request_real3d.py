import requests
import os
from dotenv import load_dotenv

load_dotenv()
def request_real3d(sentence_list): 
    url = "http://140.123.97.203:8001/real3d/"
    AUDIO_DIR = os.getenv("AUDIO_DIR")
    for item in sentence_list:
        data = {
            "drv_aud": {AUDIO_DIR}/item['audio_file_path']
        }
        requests.post(url, json=data)