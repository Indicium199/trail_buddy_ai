import csv
import requests

class DataAgent:
    """Fetch trail data, provide difficulty definitions, and weather info."""

    # Difficulty descriptions
    DIFFICULTY_DESCRIPTIONS = {
        "very easy": "Very easy trails are extremely gentle and short, with minimal elevation changes. Perfect for beginners, families, or a relaxing stroll. Mostly flat and well-maintained paths.",
        "easy": "Easy trails are generally short, and suitable for beginners. Elevation gain is minimal.",
        "moderate": "Moderate trails may include hills or uneven terrain, requiring a bit more stamina.",
        "hard": "Hard trails are steep, long, and require good fitness, navigation skills, and proper gear.",
        "very hard": "Very hard trails are long, steep, or rugged, requiring excellent fitness, navigation skills, and proper gear. Not recommended for beginners — only experienced hikers should attempt these routes."
    }

    def __init__(self, csv_path="data/lake_district_trails.csv"):
        self.csv_path = csv_path

    def load_trails(self):
        trails = []
        with open(self.csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                trails.append({
                    "Trail": row["Trail"],
                    "Difficulty": row["Difficulty"].lower(),
                    "Distance_km": float(row["Distance_km"]),
                    "Lat": float(row["Lat"]),
                    "Lng": float(row["Lng"]),
                    "Views": row.get("Views", ""),
                    "Fell_Height": row.get("Fell_Height", "")
                })
        return trails

    # 🔹 Difficulty descriptions
    def get_difficulty_definition(self, difficulty):
        return self.DIFFICULTY_DESCRIPTIONS.get(difficulty.lower(), "Unknown difficulty")

    # 🔹 Weather fetching
    def get_weather(self, lat, lon):
        """Fetch current weather from Open-Meteo API."""
        url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}&current_weather=true"
        )
        response = requests.get(url)
        data = response.json()
        cw = data.get("current_weather", {})
        return {
            "temperature": cw.get("temperature", "N/A"),
            "windspeed": cw.get("windspeed", "N/A"),
            "weather_code": cw.get("weathercode", "N/A")
        }

    # 🔹 Map weather code to description
    def map_weather_code(self, code):
        weather_map = {
            0: "Clear sky",
            1: "Mainly clear",
            2: "Partly cloudy",
            3: "Overcast",
            45: "Fog",
            48: "Depositing rime fog",
            51: "Light drizzle",
            53: "Moderate drizzle",
            55: "Dense drizzle",
            56: "Light freezing drizzle",
            57: "Dense freezing drizzle",
            61: "Slight rain",
            63: "Moderate rain",
            65: "Heavy rain",
            66: "Light freezing rain",
            67: "Heavy freezing rain",
            71: "Slight snow fall",
            73: "Moderate snow fall",
            75: "Heavy snow fall",
            77: "Snow grains",
            80: "Slight rain showers",
            81: "Moderate rain showers",
            82: "Violent rain showers",
            85: "Slight snow showers",
            86: "Heavy snow showers",
            95: "Thunderstorm",
            96: "Thunderstorm with slight hail",
            99: "Thunderstorm with heavy hail"
        }
        return weather_map.get(code, "Unknown")
