from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

# Get API key
API_KEY = os.getenv("GEMINI_API_KEY")

# Check if it loaded
print("API key loaded:", API_KEY is not None)
