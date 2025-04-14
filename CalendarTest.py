from dotenv import load_dotenv
from google import genai
import os

load_dotenv()
api_key = os.environ.get("GOOGLE_API_KEY")

if not api_key:
    # Use the API key
    print("API Key not found in .env file!")
    exit()

client = genai.Client(api_key=api_key)

response = client.models.generate_content(
    model="gemini-2.0-flash", contents="Write a haiku about monkeys"
)
print(response.text)