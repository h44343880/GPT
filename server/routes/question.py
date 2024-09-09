from fastapi import APIRouter, Request
from fastapi.responses import FileResponse
from server.dto import GPTAudioRequest
from fastapi.responses import StreamingResponse
from typing import List

from dotenv import load_dotenv
import os
import json
from src.server_app import main

import jwt
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

router = APIRouter()
load_dotenv(dotenv_path=".env", override=True)

# Function to read public key from a PEM file and return it as a byte string
def load_public_key_pem(pem_file_path):
    # Read the PEM file
    with open(pem_file_path, 'rb') as pem_file:
        pem_data = pem_file.read()
    
    # Load the public key
    public_key = serialization.load_pem_public_key(pem_data, backend=default_backend())

    # Return the public key in PEM format as a byte string
    return public_key

# Example usage
pem_file_path = 'keys/jwtRSA256-public.pem'  # Specify the path to your PEM file
public_key = load_public_key_pem(pem_file_path)

def file_generator(file_paths: List[str]):
    for file_path in file_paths:
        with open(file_path, "rb") as file:
            yield file.read()

@router.post("/GPTAudio/")
async def generate_audio(req: GPTAudioRequest, request: Request) -> StreamingResponse:
    access_token = request.headers['Authorization'].split(' ')[1]
    payload = jwt.decode(access_token, public_key, algorithms=["RS256"])
    user_id = payload['sub']

    text_path = os.getenv('TEXT_PATH')
    with open(f"{text_path}", "w") as f:
        f.write(req.question)
    
    main()

    # load audio file paths from output.json
    output_json_folder = os.getenv('OUTPUT_DIR')
    with open(f"{output_json_folder}/output.json", 'r') as f:
        dict = json.load(f)
    print(dict)
    audio_paths = list()
    for item in dict["content"]:
        audio_paths.append(item["audio_file_path"])

    return StreamingResponse(content=file_generator(audio_paths), media_type="audio/mpeg")
