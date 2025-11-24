import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

# --- RootAgent class ---
class RootAgent:
    """Handles conversation, trail selection, and AI responses via Gemini."""

    def __init__(self, model_name="gemini-2.5-flash"):
        load_dotenv(dotenv_path="./.env")
        API_KEY = os.getenv("GEMINI_API_KEY")
        if not API_KEY or API_KEY == "YOUR_API_KEY_HERE":
            raise ValueError(
                "GEMINI_API_KEY not found or still a placeholder. "
                "Please set your real key in .env"
            )

        self.client = genai.Client(api_key=API_KEY)
        self.model = model_name

        self.state = {
            "awaiting_input": None,          # difficulty_choice, max_distance, weather_choice
            "difficulty": None,
            "max_distance": None,
            "trail_options": [],             # filtered trails
            "selected_trail": None,          # currently selected trail
            "trail_selection_loop": False    # True while user is exploring trails
        }

    # --- Call Gemini AI ---
    def ask_gemini(self, prompt, max_output_tokens=200):
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(max_output_tokens=max_output_tokens)
        )
        # Debug print to see raw AI response
        # print("DEBUG: Gemini raw response:", response)
        return getattr(response, "text", None) or "Sorry, I couldn't generate a response."

    # --- Handle user message ---
    def handle_user_message(self, user_msg, data_agent, planner_agent, communication_agent):
        msg_lower = user_msg.lower().strip()

        # --- Trail selection loop ---
        if self.state.get("trail_selection_loop"):
            # Allow selection by number or exact trail name
            trail = None
            if msg_lower.isdigit():
                index = int(msg_lower) - 1
                if 0 <= index < len(self.state["trail_options"]):
                    trail = self.state["trail_options"][index]
            else:
                trail = next((t for t in self.state["trail_options"] if t["Trail"].lower() == msg_lower), None)

            if not trail:
                return "Sorry, I didn't recognize that trail. Please choose one from the list."

            self.state["selected_trail"] = trail

            # AI-generated natural description
            prompt = f"""
            You are a friendly hiking guide. Write 2-3 cheerful sentences describing this trail naturally.
            Include these details:
            - Name: {trail['Trail']}
            - Distance: {trail['Distance_km']} km
            - Difficulty: {trail['Difficulty'].title()}
            - Views: {trail.get('Views', 'No data')}
            - Fell Height: {trail.get('Fell_Height', 'Unknown')} m
            Always return a text description.
            """
            description = self.ask_gemini(prompt)
            if not description or "Sorry" in description:
                description = (
                    f"{trail['Trail']} is a {trail['Difficulty'].title()} trail, {trail['Distance_km']} km long, "
                    f"with views: {trail.get('Views', 'No data')} and a fell height of {trail.get('Fell_Height', 'Unknown')} m. "
                    "It’s a great hike for a fun outdoor adventure!"
                )

            return description + "\n\nWould you like to select this trail or explore another one?"

        # --- Confirm selection or explore another ---
        if self.state.get("selected_trail") and self.state.get("trail_options"):
            if "this" in msg_lower:
                # User confirms trail
                self.state["trail_selection_loop"] = False
                self.state["awaiting_input"] = "weather_choice"
                return "Great! Would you like to check the weather for this trail?"
            elif "another" in msg_lower:
                # Show trail list again
                trail_list_text = "\n".join(f"{i+1}. {t['Trail']}" for i, t in enumerate(self.state["trail_options"]))
                return f"Sure! Here are your options again:\n{trail_list_text}\nWhich trail would you like to explore next?"

        # --- Difficulty choice ---
        if self.state["awaiting_input"] == "difficulty_choice" or self.state["awaiting_input"] is None:
            self.state["awaiting_input"] = "difficulty_choice"

            # Explain difficulty if asked
            if "what does" in msg_lower or "explain" in msg_lower:
                for level in ["very easy", "easy", "moderate", "hard", "very hard"]:
                    if level in msg_lower:
                        prompt = (
                            f"You are a helpful hiking guide. Explain clearly what a {level} trail is, "
                            "including terrain, distance, and difficulty for beginners."
                        )
                        explanation = self.ask_gemini(prompt)
                        return explanation if explanation else f"A {level} trail is suitable for beginners: generally short, relatively flat, and easy to walk."
                return "Please specify Very Easy, Easy, Moderate, Hard or Very Hard to get an explanation."

            # User selects difficulty
            for level in ["very easy", "easy", "moderate", "hard", "very hard"]:
                if level in msg_lower:
                    self.state["difficulty"] = level
                    self.state["awaiting_input"] = "max_distance"
                    return "Maximum distance in km?"
            return "Please choose: Very Easy, Easy, Moderate, Hard or Very Hard."

        # --- Max distance ---
        if self.state["awaiting_input"] == "max_distance":
            try:
                distance = float(user_msg)
                self.state["max_distance"] = distance
                self.state["awaiting_input"] = None

                filtered_trails = planner_agent.get_trails_by_criteria(
                    difficulty=self.state["difficulty"],
                    max_distance=distance
                )

                if not filtered_trails:
                    return "Sorry, no trails match your criteria."

                self.state["trail_options"] = filtered_trails
                self.state["trail_selection_loop"] = True

                # Show numbered list for easier selection
                trail_list_text = "\n".join(f"{i+1}. {t['Trail']}" for i, t in enumerate(filtered_trails))
                return f"Here are the trails I found within your criteria:\n{trail_list_text}\n\nWhich trail catches your eye? You can type the number or the trail name."

            except ValueError:
                return "Please enter a valid number for maximum distance in km."

        # --- Weather choice ---
        if self.state["awaiting_input"] == "weather_choice":
            if "yes" in msg_lower:
                trail = self.state["selected_trail"]
                weather = data_agent.get_weather(trail["Lat"], trail["Lng"])
                weather_desc = data_agent.map_weather_code(weather["weather_code"])
                self.state["awaiting_input"] = "end"
                return f"🌤️ The weather at {trail['Trail']} is {weather_desc}, temperature {weather['temperature']}°C, wind speed {weather['windspeed']} km/h."
            else:
                self.state["awaiting_input"] = "end"
                return "Alright! Let me know if you want to plan a different trail."

        # --- Fallback ---
        return "Sorry, I didn't understand that. Please try again."
