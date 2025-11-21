class PlannerAgent:
    """Select trails based on difficulty and max distance."""

    def __init__(self, data_agent):
        self.data_agent = data_agent
        self.trails = self.data_agent.load_trails()

    def get_trails_by_criteria(self, difficulty, max_distance):
        filtered = [
            t["Trail"] for t in self.trails
            if t["Difficulty"] == difficulty.lower() and t["Distance_km"] <= max_distance
        ]
        if filtered:
            return f"Here are {difficulty} trails under {max_distance} km: {', '.join(filtered)}."
        else:
            return f"No {difficulty} trails found under {max_distance} km."
