import csv
import requests

class DataAgent:
    """Fetch trail data and weather from Open-Meteo."""

    def __init__(self, csv_path="data/lake_district_trails.csv"):
        self.csv_path = csv_path

    def load_trails(self):
        """Load trail info from CSV."""
        trails = []
        with open(self.csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                trails.append({
                    "Trail": row["Trail"],
                    "Difficulty": row["Difficulty"],
                    "Distance_km": row["Distance_km"],
                    "Lat": float(row["Lat"]),
                    "Lng": float(row["Lng"])
                })
        return trails

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

    def map_weather_code(self, code):
        """Convert Open-Meteo numeric code to human-readable description."""
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
