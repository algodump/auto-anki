import requests
import json
import logging
import os.path as path
from env import Env

def load_prompt(prompt_name, words):
    prompt = open(path.join("prompts", prompt_name)).read()
    words_as_str = ", ".join(words)
    prompt += f"\nHere are the words: {words_as_str}"

    return prompt

class AiModel:
    def __init__(self):
        pass

    def name(self) -> str:
        pass

    def generate_response(self):
        pass

class Gpt4All(AiModel):
    def __init__(self, prompt_name, words):
        self.url = "http://localhost:4891/v1/chat/completions"

        prompt = load_prompt(prompt_name, words)
        self.data = {
            "model": "Llama 3.2 3B Instruct",
            "messages": [{"role":"user", "content":f"{prompt}"}],
            "max_tokens": 1024,
        }
    
    def generate_response(self):
        try:
            logging.info(f"Sending a request to Gpt4All, API server - {self.url}")
            response = requests.post(self.url, data=json.dumps(self.data))
            logging.info("Waiting for a response...")

            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            logging.error(f"Error ocurred while generating response {e}, response status code: {response.status_code}, response description = {response.text}")
    
    def name(self) -> str:
        return "GPT"

