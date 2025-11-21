import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
print("API key loaded:", API_KEY is not None)

# Create client
client = genai.Client(api_key=API_KEY)

class RootAgent:
    def __init__(self, model_name="gemini-2.5-flash"):
        self.model = model_name

    def ask_gemini(self, prompt, max_output_tokens=200):
        response = client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                max_output_tokens=max_output_tokens
            )
        )
        return response.text
