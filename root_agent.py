import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

class RootAgent:
    """Handles conversation, trail selection, weather, and nearby pubs/cafes via Gemini and OSM."""

    def __init__(self, planner_agent, data_agent, communicator_agent, model_name="gemini-2.5-flash"):
        load_dotenv(dotenv_path="./.env")
        API_KEY = os.getenv("GEMINI_API_KEY")
        if not API_KEY or API_KEY == "YOUR_API_KEY_HERE":
            raise ValueError(
                "GEMINI_API_KEY not found or still a placeholder. "
                "Please set your real key in .env"
            )

        self.client = genai.Client(api_key=API_KEY)
        self.model = model_name

        self.planner_agent = planner_agent
        self.data_agent = data_agent
        self.communicator_agent = communicator_agent

        self.state = {
            "awaiting_input": "difficulty_choice",
            "difficulty": None,
            "max_distance": None,
            "trail_options": [],
            "selected_trail": None
        }

    # ------------------------------
    # Gemini wrapper
    # ------------------------------
    def ask_gemini(self, prompt, max_output_tokens=500):
        """Call Gemini generate_content API to produce text."""
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(max_output_tokens=max_output_tokens)
            )
            if response and hasattr(response, "text") and response.text:
                return response.text.strip()
            return ""
        except Exception as e:
            print("DEBUG — Gemini error:", e)
            return ""

    # ------------------------------
    # Trail description using Gemini
    # ------------------------------
    def generate_trail_description(self, trail):
        name = str(trail.get("Trail", "Unknown"))
        difficulty = str(trail.get("Difficulty", "Unknown"))
        distance = str(trail.get("Distance_km", "Unknown"))
        views = str(trail.get("Views", "N/A"))
        route = str(trail.get("Route", "N/A"))
        fell = str(trail.get("Fell_Height") or "N/A")

        prompt = (
            "You are a friendly, enthusiastic hiking guide. "
            "Write 3–5 cheerful, natural sentences describing the trail below. "
            "Include the 'Views' and 'Route' details naturally in the description — "
            "do not just list them. Add small friendly touches like 'perfect for photos' or 'great for a morning hike'.\n\n"
            f"Trail details:\n"
            f"Name: {name}\n"
            f"Difficulty: {difficulty}\n"
            f"Distance (km): {distance}\n"
            f"Views: {views}\n"
            f"Route: {route}\n"
            f"Fell height: {fell}\n\n"
            "Write your paragraph below:"
        )

        response = self.ask_gemini(prompt, max_output_tokens=500)
        if response:
            return response

        return (
            f"{name} is a {difficulty.lower()} trail, {distance} km long, "
            f"with views such as {views}. Route: {route}. Fell height: {fell} ft."
        )

    # ------------------------------
    # Conversation flow
    # ------------------------------
    def handle_user_message(self, user_msg):
        user_msg_lower = user_msg.strip().lower()

        # --- 1: Difficulty choice ---
        if self.state["awaiting_input"] == "difficulty_choice":
            for level in ["very easy", "easy", "moderate", "hard", "very hard"]:
                if level in user_msg_lower:
                    self.state["difficulty"] = level
                    self.state["awaiting_input"] = "max_distance"
                    return "Great! What’s the maximum distance you’d like to hike (in km)?"
            return "Please choose your hiking difficulty level: Very Easy, Easy, Moderate, Hard or Very Hard."

        # --- 2: Max distance ---
        if self.state["awaiting_input"] == "max_distance":
            try:
                distance = float(user_msg)
                self.state["max_distance"] = distance

                trails = self.planner_agent.get_trails_by_criteria(
                    difficulty=self.state["difficulty"],
                    max_distance=distance
                )

                self.state["trail_options"] = trails
                self.state["awaiting_input"] = "trail_selection"

                trail_list = "\n".join([f"{i+1}. {t['Trail']}" for i, t in enumerate(trails)])

                return (
                    f"Here are the trails I found within your criteria:\n{trail_list}\n\n"
                    "Which trail catches your eye? You can type the number or the trail name."
                )
            except ValueError:
                return "Please enter a valid number for maximum distance."

        # --- 3: Trail selection ---
        if self.state["awaiting_input"] == "trail_selection":
            trails = self.state["trail_options"]
            selected = None

            if user_msg_lower.isdigit():
                index = int(user_msg_lower) - 1
                if 0 <= index < len(trails):
                    selected = trails[index]
            else:
                for t in trails:
                    if t["Trail"].lower() == user_msg_lower:
                        selected = t
                        break

            if selected:
                self.state["selected_trail"] = selected
                self.state["awaiting_input"] = "confirm_selection"

                description = self.generate_trail_description(selected)
                return f"{description}\n\nWould you like to select this trail or explore another one?"
            else:
                return "Sorry, I didn’t recognize that trail. Please choose one from the list."

        # --- 4: Confirm trail selection ---
        if self.state["awaiting_input"] == "confirm_selection":
            if user_msg_lower in ["yes", "select", "this one"]:
                self.state["awaiting_input"] = "confirm_weather"
                return "Excellent choice! 🌄 Would you like the current weather for this trail?"
            elif user_msg_lower in ["no", "another", "explore another"]:
                self.state["awaiting_input"] = "trail_selection"
                trail_list = "\n".join([f"{i+1}. {t['Trail']}" for i, t in enumerate(self.state["trail_options"])])
                return (
                    f"No problem! Here are the options again:\n{trail_list}\n\n"
                    "Which trail would you like to explore?"
                )
            else:
                return "Please answer yes/no or say 'another'."

        # --- 5: Weather ---
        if self.state["awaiting_input"] == "confirm_weather":
            if user_msg_lower in ["yes", "y"]:
                trail = self.state["selected_trail"]
                lat = trail.get("Lat")
                lon = trail.get("Lng")

                weather = self.data_agent.get_weather(lat, lon)
                weather_desc = self.data_agent.map_weather_code(weather["weather_code"])

                summary = (
                    f"Temperature: {weather['temperature']}°C, "
                    f"Wind speed: {weather['windspeed']} km/h, "
                    f"Condition: {weather_desc}"
                )

                prompt = (
                    f"You are a friendly hiking assistant. "
                    f"Here is the current weather at {trail['Trail']}: {summary}. "
                    "Write a short, cheerful message to tell the user."
                )

                friendly_weather = self.ask_gemini(prompt)

                if not friendly_weather:
                    friendly_weather = (
                        f"Hey! 🌤️ The weather at {trail['Trail']} is {weather_desc}, "
                        f"with a temperature of {weather['temperature']}°C and winds at {weather['windspeed']} km/h."
                    )

                # Ask about pubs or cafes
                self.state["awaiting_input"] = "pub_or_cafe_choice"
                return f"{friendly_weather}\n\nWould you like a list of the nearest pubs or cafes to {trail['Trail']}?"

            else:
                self.state["awaiting_input"] = None
                return "Alright! Let me know if you want to plan a different trail."

        # --- 6: Pubs or cafes selection ---
        if self.state["awaiting_input"] == "pub_or_cafe_choice":
            trail = self.state["selected_trail"]
            lat = trail.get("Lat")
            lon = trail.get("Lng")

            if user_msg_lower not in ["pub", "cafe"]:
                return "Please type 'pub' or 'cafe'."

            # Call OSM-based free method
            places = self.communicator_agent.get_nearby_pubs_cafes(
                lat, lon,
                place_type=user_msg_lower,
                radius_km=5
            )

            self.state["awaiting_input"] = None

            if not places:
                return f"No nearby {user_msg_lower}s found within 2 km."

            formatted = [f"{i+1}. {p['name']} – {p['distance_km']} km" for i, p in enumerate(places)]
            return f"Here are some nearby {user_msg_lower}s:\n" + "\n".join(formatted)

        # --- Default fallback ---
        return "I'm not sure how to respond to that. Please follow the prompts."
