import csv
import requests

class DataAgent:
    """Fetch trail data and provide difficulty definitions."""

    # Difficulty descriptions
    DIFFICULTY_DESCRIPTIONS = {
        "easy": "Easy trails are generally flat, short, and suitable for beginners. Elevation gain is minimal.",
        "moderate": "Moderate trails may include hills or uneven terrain, requiring a bit more stamina.",
        "hard": "Hard trails are steep, long, and require good fitness, navigation skills, and proper gear."
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
                    "Lng": float(row["Lng"])
                })
        return trails

    def get_difficulty_definition(self, difficulty):
        return self.DIFFICULTY_DESCRIPTIONS.get(difficulty.lower(), "Unknown difficulty")
