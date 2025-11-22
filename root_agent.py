import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

class RootAgent:
    """Handles conversation, clarification, and AI responses via Gemini."""

    def __init__(self, model_name="gemini-2.5-flash"):
        # Load API key from .env
        load_dotenv(dotenv_path="./.env")
        API_KEY = os.getenv("GEMINI_API_KEY")
        if not API_KEY or API_KEY == "YOUR_API_KEY_HERE":
            raise ValueError(
                "GEMINI_API_KEY not found or still a placeholder. "
                "Please set your real key in .env"
            )

        self.client = genai.Client(api_key=API_KEY)
        self.model = model_name

        # Conversation state
        self.state = {
            "awaiting_input": None,   # "difficulty_choice" or "max_distance"
            "difficulty": None,
            "max_distance": None,
            "selected_trail": None    # Store the chosen trail for weather lookup
        }

    # --- Call Gemini AI ---
    def ask_gemini(self, prompt, max_output_tokens=200):
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(max_output_tokens=max_output_tokens)
        )
        # Ensure always returns a string
        return response.text if response.text else "Sorry, I couldn't generate a response."

    # --- Handle conversation ---
    def handle_user_message(self, user_msg, data_agent, planner_agent, communication_agent):
        """
        user_msg: str - what user typed
        data_agent: DataAgent instance
        planner_agent: PlannerAgent instance
        communication_agent: CommunicationAgent instance
        """

        # Stage 1: Difficulty choice
        if self.state["awaiting_input"] == "difficulty_choice":

            # Clarification question
            if "what does" in user_msg.lower() or "explain" in user_msg.lower():
                for level in ["very easy", "easy", "moderate", "hard", "very hard"]:
                    if level in user_msg.lower():
                        prompt = (
                            f"You are a helpful hiking guide. Explain clearly what a {level} trail is, "
                            "including terrain, distance, and difficulty for beginners."
                        )
                        explanation = self.ask_gemini(prompt)
                        if explanation:
                            return explanation
                        else:
                            return f"A {level} trail is suitable for beginners: generally short, relatively flat, and easy to walk."
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

                # Filter trails using PlannerAgent
                filtered_trails = planner_agent.get_trails_by_criteria(
                    difficulty=self.state["difficulty"],
                    max_distance=distance
                )

                # Store the first matching trail for weather lookup
                if filtered_trails:
                    self.state["selected_trail"] = filtered_trails[0]  # store trail dict
                else:
                    self.state["selected_trail"] = None

                # AI summarization of filtered trails
                prompt = (
                    f"You are a friendly hiking assistant. Here are the trails found: "
                    f"{filtered_trails}.\n"
                    f"Write a short, friendly summary for the user."
                )
                summary = self.ask_gemini(prompt)
                return summary if summary else "Here are the trails I found for you!"

            except ValueError:
                return "Please enter a valid number for maximum distance in km."

        # Start conversation if nothing is set
        if self.state["awaiting_input"] is None:
            self.state["awaiting_input"] = "difficulty_choice"
            return "What kind of trail are you looking to do? (Very Easy/Easy/Moderate/Hard/Very Hard)"
