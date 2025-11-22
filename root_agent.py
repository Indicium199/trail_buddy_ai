import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

class RootAgent:
    """Handles conversation, clarification, and AI responses via Gemini."""

    def __init__(self, model_name="gemini-2.5-flash"):
        # Load API key from .env
        load_dotenv()
        API_KEY = os.getenv("GEMINI_API_KEY")
        if not API_KEY:
            raise ValueError("GEMINI_API_KEY not found in environment. Please set it in .env")

        self.client = genai.Client(api_key=API_KEY)
        self.model = model_name

        # Conversation state
        self.state = {
            "awaiting_input": None,   # "difficulty_choice" or "max_distance"
            "difficulty": None,
            "max_distance": None
        }

    # --- Call Gemini AI ---
    def ask_gemini(self, prompt, max_output_tokens=200):
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(max_output_tokens=max_output_tokens)
        )
        return response.text

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
                for level in ["easy", "moderate", "hard"]:
                    if level in user_msg.lower():
                        # AI explanation
                        prompt = f"Explain in simple terms what a {level} hiking trail is."
                        return self.ask_gemini(prompt)

            # User selects difficulty
            for level in ["easy", "moderate", "hard"]:
                if level in user_msg.lower():
                    self.state["difficulty"] = level
                    self.state["awaiting_input"] = "max_distance"
                    return "Maximum distance in km?"

            return "Please choose: Easy, Moderate, or Hard."

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

                # AI summarization of filtered trails
                prompt = (
                    f"You are a friendly hiking assistant. Here are the trails found: "
                    f"{filtered_trails}.\n"
                    f"Write a short, friendly summary for the user."
                )
                return self.ask_gemini(prompt)

            except ValueError:
                return "Please enter a valid number for maximum distance in km."

        # Start conversation if nothing is set
        if self.state["awaiting_input"] is None:
            self.state["awaiting_input"] = "difficulty_choice"
            return "What kind of trail are you looking to do? (Easy/Moderate/Hard)"

