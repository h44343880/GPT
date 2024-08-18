﻿from dotenv import load_dotenv
import os
from gpt_sovits_client import GPTSoVITSClient
from openai_client import OpenAIClient
import json
from datetime import datetime

def get_article(file_path):
    with open(file_path, 'r', encoding='UTF-8') as f:
        return f.read()
        
def get_prompt(file_path):
    with open(file_path, 'r', encoding='UTF-8') as f:
        return f.read()
    
# there may be a better way to do this
def append_article_to_prompt(prompt, article, emotions_list):
    placeholder_emotions_text = "replace_with_emotion_list" # maybe put this in env?
    new_prompt = prompt+article # append article to prompt
    replace_index = new_prompt.find(placeholder_emotions_text)
    new_prompt = new_prompt[:replace_index]+','.join(emotions_list)+new_prompt[replace_index+len(placeholder_emotions_text)-1:]
    return new_prompt

def export_to_json(export_path, response): # TODO: need to change the "response" variable name?
    json_string = json.dumps({"content": response}, ensure_ascii=False, indent=4)
    print(json_string)
    with open(export_path, 'w+', encoding='UTF-8') as f:
        f.write(json_string)
        
def get_sentence_emotion_array(response, emotions_list):
    lines = response.split('\n')
    sentence_emotion_array = []
    for line in lines:
        if '@' in line:
            sentence, emotion = line.split(' @')
            sentence_emotion_array.append({
                'sentence': sentence,
                'emotion': next(filter(lambda emo: emo in emotion, emotions_list), None) # match emotion from emotions_list
            })
    return sentence_emotion_array

def save_audio(audio, file_path, character_name, sentence):
    date = datetime.today().strftime('%m-%d-%H-%M-%S')
    filename = f"{character_name}_{sentence}_{date}.mp3"
    audio_file_path = f"{file_path}/{filename}"
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(audio_file_path), exist_ok=True)

    # Open the file in binary write mode and write audio data
    with open(audio_file_path, 'wb') as audio_file:
        audio_file.write(audio)
    return audio_file_path

def get_audio_for_each_sentence(sentence_emotion_list, gpt_sovits_client, CHARACTER_NAME, AUDIO_PATH):
    for sentence_emotion in sentence_emotion_list:
        audio = gpt_sovits_client.get_audio_with_post(character=CHARACTER_NAME, emotion=sentence_emotion['emotion'], text=sentence_emotion['sentence'])
        # save audio to audio directory
        audio_file_path = save_audio(audio, AUDIO_PATH, CHARACTER_NAME, sentence_emotion['sentence'])
        # save audio file path to sentence_emotion
        sentence_emotion['audio_file_path'] = f"./{audio_file_path}" # TODO: need to change the path to absolute path


def main():
    load_dotenv(dotenv_path=".env", override=True)
    LOG_PATH = os.getenv("LOG_DIR")
    absolute_path = os.getcwd() # TODO
    # logging.basicConfig(filename="test.log", level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', stream='stdout')
    
    # load env vars
    PROMPT_PATH = os.getenv("PROMPT_PATH")
    ARTICLE_PATH = os.getenv("ARTICLE_PATH")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    GPT_SOVITS_ENDPOINT = os.getenv("GPT_SOVITS_ENDPOINT")
    CHARACTER_NAME = os.getenv("CHARACTER_NAME")
    AUDIO_PATH = os.getenv("AUDIO_DIR")
    OUTPUT_PATH = os.getenv("OUTPUT_DIR")
    print(f"Loaded env vars, {LOG_PATH}, {PROMPT_PATH}, {ARTICLE_PATH}, {OPENAI_API_KEY}, {GPT_SOVITS_ENDPOINT}, {CHARACTER_NAME}, {AUDIO_PATH}, {OUTPUT_PATH}")
    
    # pre-processing prompt
    article = get_article(ARTICLE_PATH)
    prompt = get_prompt(PROMPT_PATH)
    
    # get emotions list
    gpt_sovits_client = GPTSoVITSClient(GPT_SOVITS_ENDPOINT)
    character_list = gpt_sovits_client.get_character_list()
    emotions_list = character_list[CHARACTER_NAME]
    # emotions_list = ["開心", "難過"]
    
    # finalize prompt
    finalized_prompt = append_article_to_prompt(prompt=prompt, emotions_list=emotions_list, article=article)
    
    # get emotions for each sentence
    openai_client = OpenAIClient(api_key=OPENAI_API_KEY)
    try:
        response = openai_client.get_emotion(prompt=finalized_prompt)
    except ValueError as e:
        # TODO: add to log
        pass
    
    # parse response
    sentence_emotion_list = get_sentence_emotion_array(response, emotions_list)
    
    # get audio for each sentence
    get_audio_for_each_sentence(sentence_emotion_list, gpt_sovits_client, CHARACTER_NAME, AUDIO_PATH) # TODO: maybe there's a better way?
        
    # export to json
    date = datetime.today().strftime('%m-%d-%H-%M-%S')
    export_to_json(OUTPUT_PATH + f'/{date}.json', sentence_emotion_list)

    # close gpt sovits connection    
    gpt_sovits_client.close()
    
if __name__ == '__main__':
    main()