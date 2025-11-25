import requests
import math

class CommunicationAgent:
    """Format responses for the user and fetch external data like nearby pubs/cafes using OSM."""

    def format_definition(self, definition):
        return f"{definition} Would you like to select this difficulty?"

    # --- Haversine formula for accurate distance in km ---
    @staticmethod
    def haversine(lat1, lon1, lat2, lon2):
        R = 6371  # Earth radius in km
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        a = math.sin(dphi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2)**2
        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    def get_nearby_pubs_cafes(self, lat, lng, place_type="cafe", radius_km=5):
        """
        Fetch nearby pubs or cafes using OpenStreetMap / Overpass API.
        Returns a list of dicts with name and distance.
        place_type: "pub" or "cafe"
        radius_km: search radius in km
        """
        # Validate place type
        if place_type not in ["pub", "cafe"]:
            raise ValueError("place_type must be 'pub' or 'cafe'.")

        # Convert radius to degrees (approx)
        delta_deg = radius_km / 111  # 1 deg ~ 111 km
        south, north = lat - delta_deg, lat + delta_deg
        west, east = lng - delta_deg, lng + delta_deg

        # Overpass API query
        overpass_url = "https://overpass-api.de/api/interpreter"
        query = f"""
        [out:json];
        node
          ["amenity"="{place_type}"]
          ({south},{west},{north},{east});
        out;
        """
        response = requests.get(overpass_url, params={"data": query})
        if response.status_code != 200:
            return []

        data = response.json()
        results = []

        for elem in data.get("elements", []):
            name = elem.get("tags", {}).get("name", "Unnamed")
            elem_lat = elem.get("lat")
            elem_lng = elem.get("lon")
            distance = round(self.haversine(lat, lng, elem_lat, elem_lng), 2)
            results.append({"name": name, "distance_km": distance})

        # Sort by distance
        return sorted(results, key=lambda x: x["distance_km"])
