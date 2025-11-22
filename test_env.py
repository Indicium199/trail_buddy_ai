import os
from dotenv import load_dotenv

# Explicitly load .env from the current directory
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
loaded = load_dotenv(dotenv_path=dotenv_path)

print("Dotenv loaded:", loaded)
print("Path used:", dotenv_path)

api_key = os.getenv("GEMINI_API_KEY")
print("GEMINI_API_KEY read by Python:", api_key)
