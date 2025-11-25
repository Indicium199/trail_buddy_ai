import requests

class CommunicationAgent:
    """Format responses for the user and fetch external data like nearby pubs/cafes."""

    def format_definition(self, definition):
        return f"{definition} Would you like to select this difficulty?"

    def get_nearby_pubs_cafes(self, lat, lng, radius=3000, api_key=None):
        """
        Fetch nearby pubs and cafes using Google Places API.
        Returns a list of dicts with name, distance, and description.
        """
        if api_key is None:
            raise ValueError("Gemini API key is required.")

        places = []
        # Types: cafe, bar, restaurant, pub
        types = "cafe|bar|restaurant|pub"

        url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        params = {
            "location": f"{lat},{lng}",
            "radius": radius,
            "type": types,
            "key": api_key
        }

        response = requests.get(url, params=params)
        if response.status_code != 200:
            return []

        data = response.json()
        for place in data.get("results", [])[:10]:  # limit to top 10
            place_lat = place.get("geometry", {}).get("location", {}).get("lat", lat)
            place_lng = place.get("geometry", {}).get("location", {}).get("lng", lng)
            distance = round(((place_lat - lat)**2 + (place_lng - lng)**2)**0.5 * 111, 2)  # rough km
            places.append({
                "name": place.get("name"),
                "distance": distance,
                "description": place.get("vicinity", "No description")
            })
        return places
