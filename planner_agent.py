import random

class PlannerAgent:
    """Select trails based on difficulty and max distance, with scoring and ranking."""

    def __init__(self, data_agent):
        self.data_agent = data_agent
        self.trails = self.data_agent.load_trails()

    def _score_trail(self, trail, desired_difficulty, max_distance):
        """Compute a score for a trail based on difficulty and distance."""
        score = 0

        # Difficulty scoring: exact match = 1, near match = 0.5, else 0
        difficulty_order = ["very easy", "easy", "moderate", "hard", "very hard"]
        trail_diff_index = difficulty_order.index(trail["Difficulty"].lower())
        desired_index = difficulty_order.index(desired_difficulty.lower())

        if trail_diff_index == desired_index:
            score += 1.0
        elif abs(trail_diff_index - desired_index) == 1:
            score += 0.5

        # Distance scoring: closer to max_distance is better
        if trail["Distance_km"] <= max_distance:
            score += trail["Distance_km"] / max_distance  # normalized 0-1
        else:
            score -= 0.5  # Penalize trails exceeding max_distance slightly

        return score

    def get_trails_by_criteria(self, difficulty, max_distance):
        scored_trails = []

        for trail in self.trails:
            score = self._score_trail(trail, difficulty, max_distance)
            if score > 0:  # keep only positive-scoring trails
                scored_trails.append((trail, score))

        if not scored_trails:
            # Handle edge case: no suitable trail
            return {"message": "No trails match your criteria. Here are some closest options:",
                    "trails": sorted(self.trails, key=lambda t: abs(t["Distance_km"] - max_distance))[:5]}

        # Sort by score descending
        scored_trails.sort(key=lambda x: x[1], reverse=True)

        # Handle tie-breaking randomly
        final_trails = []
        i = 0
        while i < len(scored_trails):
            tie_group = [scored_trails[i]]
            j = i + 1
            while j < len(scored_trails) and scored_trails[j][1] == scored_trails[i][1]:
                tie_group.append(scored_trails[j])
                j += 1
            random.shuffle(tie_group)  # randomize tie group
            final_trails.extend([t[0] for t in tie_group])
            i = j

        return final_trails

    # --- New method to generate natural-language trail description ---
    def get_trail_details(self, trail_name, gemini_client):
        """
        Look up the trail row from CSV and ask Gemini to generate a friendly natural-language description.
        """
        trail_data = None
        for t in self.trails:
            if t["Trail"].lower() == trail_name.lower():
                trail_data = t
                break

        if not trail_data:
            return "I couldn't find details for that trail."

        prompt = f"""
You are an expert Lake District trail guide.

Generate a friendly, vivid trail description for hikers based on the structured data below.
Do NOT invent facts — stay close to the info provided.

TRAIL NAME: {trail_data['Trail']}
DISTANCE (km): {trail_data['Distance_km']}
DIFFICULTY: {trail_data['Difficulty']}
FELL HEIGHT (m): {trail_data.get('Fell_Height_ft', '?')}
ROUTE SUMMARY: {trail_data.get('Route', 'N/A')}
VIEWS / HIGHLIGHTS: {trail_data.get('Views', 'N/A')}

Write a natural-sounding paragraph (4–6 sentences).
"""
        response = gemini_client.generate_content(prompt)
        return response.text if response.text else f"{trail_name} is a great trail!"
