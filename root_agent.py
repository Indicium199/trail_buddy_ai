import os
from dotenv import load_dotenv
from google import genai
from google.genai import types


# --- Friendly trail formatting function ---
def format_trail_recommendations(trails, desired_difficulty, max_distance):
    """
    Format trail recommendations for the user.
    Automatically detects the correct trail name key and capitalizes difficulty consistently.
    """
    if not trails:
        return f"Sorry, no trails found within {max_distance} km for {desired_difficulty} difficulty."

    # Determine the correct key for the trail name
    sample_trail = trails[0]
    if 'Trail' in sample_trail:
        name_key = 'Trail'
    elif 'name' in sample_trail:
        name_key = 'name'
    elif 'Name' in sample_trail:
        name_key = 'Name'
    elif 'trail_name' in sample_trail:
        name_key = 'trail_name'
    else:
        print("DEBUG: Unknown trail keys:", list(sample_trail.keys()))
        name_key = list(sample_trail.keys())[0]  # fallback

    exact_matches = []
    near_matches = []

    for t in trails:
        if t.get("Difficulty", "").lower() == desired_difficulty.lower():
            exact_matches.append(t)
        else:
            near_matches.append(t)

    formatted = "Hello there! 👋 I've found some trails for you to explore!\n\n"

    if exact_matches:
        formatted += f"**Exact difficulty matches ({len(exact_matches)}):**\n"
        for t in exact_matches:
            formatted += f" - {t.get(name_key)} ({t.get('Distance_km', '?')} km)\n"

    if near_matches:
        formatted += f"\n**Close options ({len(near_matches)}):**\n"
        for t in near_matches:
            formatted += f" - {t.get(name_key)} ({t.get('Distance_km', '?')} km, {t.get('Difficulty', '?').title()})\n"

    if exact_matches:
        longest_trail = max(exact_matches, key=lambda x: x.get("Distance_km", 0))
        formatted += f"\nIf you're up for a challenge, consider: **{longest_trail.get(name_key)}** ({longest_trail.get('Distance_km', '?')} km)\n"

    return formatted


# --- RootAgent class ---
class RootAgent:
    """Handles conversation, clarification, and AI responses via Gemini."""

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
            "awaiting_input": None,   # "difficulty_choice" or "max_distance"
            "difficulty": None,
            "max_distance": None,
            "selected_trail": None
        }

    # --- Call Gemini AI ---
    def ask_gemini(self, prompt, max_output_tokens=200):
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(max_output_tokens=max_output_tokens)
        )
        return response.text if response.text else "Sorry, I couldn't generate a response."

    # --- Handle conversation ---
    def handle_user_message(self, user_msg, data_agent, planner_agent, communication_agent):
        # Stage 1: Difficulty choice
        if self.state["awaiting_input"] == "difficulty_choice":
            if "what does" in user_msg.lower() or "explain" in user_msg.lower():
                for level in ["very easy", "easy", "moderate", "hard", "very hard"]:
                    if level in user_msg.lower():
                        prompt = (
                            f"You are a helpful hiking guide. Explain clearly what a {level} trail is, "
                            "including terrain, distance, and difficulty for beginners."
                        )
                        explanation = self.ask_gemini(prompt)
                        return explanation if explanation else f"A {level} trail is suitable for beginners: generally short, relatively flat, and easy to walk."
                return "Please specify Very Easy, Easy, Moderate, Hard or Very Hard to get an explanation."

            # User selects difficulty
            for level in ["very easy", "easy", "moderate", "hard", "very hard"]:
                if level in user_msg.lower():
                    self.state["difficulty"] = level
                    self.state["awaiting_input"] = "max_distance"
                    return "Maximum distance in km?"
            return "Please choose: Very Easy, Easy, Moderate, Hard or Very Hard."

        # Stage 2: Max distance
        if self.state["awaiting_input"] == "max_distance":
            try:
                distance = float(user_msg)
                self.state["max_distance"] = distance
                self.state["awaiting_input"] = None

                # Get ranked trails using PlannerAgent
                filtered_trails = planner_agent.get_trails_by_criteria(
                    difficulty=self.state["difficulty"],
                    max_distance=distance
                )

                # Debug print for inspection
                #if filtered_trails:
                    #print("DEBUG: First trail dictionary keys:", list(filtered_trails[0].keys()))
                    #print("DEBUG: First trail dictionary content:", filtered_trails[0])
                #else:
                    #print("DEBUG: No trails returned by PlannerAgent")

                # Store first matching trail for weather lookup
                self.state["selected_trail"] = filtered_trails[0] if filtered_trails else None

                # Format a friendly message
                summary = format_trail_recommendations(
                    filtered_trails,
                    desired_difficulty=self.state["difficulty"],
                    max_distance=distance
                )
                return summary

            except ValueError:
                return "Please enter a valid number for maximum distance in km."

        # Start conversation if nothing is set
        if self.state["awaiting_input"] is None:
            self.state["awaiting_input"] = "difficulty_choice"
            return "What kind of trail are you looking to do? (Very Easy/Easy/Moderate/Hard/Very Hard)"
