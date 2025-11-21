class RootAgent:
    """Handles conversation state and routes user messages."""

    def __init__(self):
        # Conversation state
        self.state = {
            "awaiting_input": None,   # Can be "difficulty_choice" or "max_distance"
            "difficulty": None,
            "max_distance": None
        }

    def handle_user_message(self, user_msg, data_agent, planner_agent, communication_agent):
        """
        Handles the user input, routes clarifications, difficulty selection,
        and maximum distance input.
        """
        # --- Stage 1: Difficulty Choice ---
        if self.state["awaiting_input"] == "difficulty_choice":

            # 🔹 Clarification detected
            if "what does" in user_msg.lower() or "explain" in user_msg.lower():
                for level in ["easy", "moderate", "hard"]:
                    if level in user_msg.lower():
                        definition = data_agent.get_difficulty_definition(level)
                        # Do NOT advance the stage; still waiting for selection
                        return communication_agent.format_definition(definition)

            # 🔹 Difficulty selection
            for level in ["easy", "moderate", "hard"]:
                if level in user_msg.lower():
                    self.state["difficulty"] = level
                    self.state["awaiting_input"] = "max_distance"  # Move to next stage
                    return "Maximum distance in km?"

            # Neither clarification nor selection
            return "Please choose: Easy, Moderate, or Hard."

        # --- Stage 2: Max Distance ---
        if self.state["awaiting_input"] == "max_distance":
            try:
                distance = float(user_msg)
                self.state["max_distance"] = distance
                self.state["awaiting_input"] = None  # Conversation stage complete
                # Return filtered trails from PlannerAgent
                return planner_agent.get_trails_by_criteria(
                    difficulty=self.state["difficulty"],
                    max_distance=distance
                )
            except ValueError:
                return "Please enter a valid number for maximum distance in km."

        # --- Start Conversation if nothing is set ---
        if self.state["awaiting_input"] is None:
            self.state["awaiting_input"] = "difficulty_choice"
            return "What kind of trail are you looking to do? (Easy/Moderate/Hard)"
