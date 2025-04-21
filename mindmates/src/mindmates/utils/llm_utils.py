import os
from pathlib import Path
from dotenv import load_dotenv, find_dotenv

from google import genai

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# print(GEMINI_API_KEY)
client = genai.Client(api_key=GEMINI_API_KEY)

def call_gemini(prompt, model="gemini-1.5-flash-8b"):
    response = client.models.generate_content(
        model=model, contents=prompt
    )
    return response.text

def filter_lifestyle_experts(chat_history, lifestyle_expert_list):
    prompt = f"""Does the following conversation mention or imply [{', '.join(lifestyle_expert_list)}]. Reply "Yes" or "No" for each topic in the following format (replacing name of agent with the element in the list):
    name of agent 1: Yes
    name of agent 2: No
    
    Conversation:
    {chat_history}"""
    response = call_gemini(prompt)
    result = response.split("\n")[:-1]
    return result