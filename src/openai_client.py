from openai import OpenAI
import re
class OpenAIClient:
    def __init__(self, api_key, model="gpt-4o-mini"):
        self.api_key = api_key
        print(self.api_key)
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.chatanywhere.tech/v1"
        )
        self.model = model
    
    def generate_article(self, text):
        res = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": text}
            ]
        )
        response = res.choices[0].message.content
        return response


    def get_emotion(self, prompt, max_retries=100):
        retries = 0
        while retries < max_retries:
            res = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
            )
            response = res.choices[0].message.content
            if self.is_response_format_correct(response):
                print(response)
                return response
            retries += 1
        raise ValueError("Failed to get a valid response after multiple retries.")
                    
    def is_response_format_correct(self, response):
        lines = response.split('\n')
        for line in lines:
            match = re.match(r".+ @.+", line)
            if(match == None):
                return False
        return True