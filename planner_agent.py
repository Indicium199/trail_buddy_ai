class PlannerAgent:
    """Select trails based on difficulty and max distance."""

    def __init__(self, data_agent):
        self.data_agent = data_agent
        self.trails = self.data_agent.load_trails()

    def get_trails_by_criteria(self, difficulty, max_distance):
        # Filter the trails as dictionaries
        filtered = [
            t for t in self.trails
            if t["Difficulty"] == difficulty.lower() and t["Distance_km"] <= max_distance
        ]
        if filtered:
            # Return the list of dictionaries
            return filtered
        else:
            return []  # empty list if no trails found
