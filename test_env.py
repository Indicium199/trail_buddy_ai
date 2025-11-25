from communicator_agent import CommunicationAgent
import os
from dotenv import load_dotenv

# --- Load .env ---
load_dotenv(dotenv_path="./.env")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not set in .env")

# --- Create communicator agent ---
comm_agent = CommunicationAgent()

# Example coordinates (replace with a trail's lat/lng)
lat = 54.5561  # e.g., Grasmoor
lng = -3.3205

# --- Fetch nearby pubs/cafes ---
results = comm_agent.get_nearby_pubs_cafes(lat, lng, api_key=GEMINI_API_KEY)

# --- Print results ---
if results:
    print("Nearby pubs and cafes:")
    for i, place in enumerate(results):
        print(f"{i+1}. {place['name']} – {place['distance']} km – {place['description']}")
else:
    print("No nearby pubs/cafes found.")
