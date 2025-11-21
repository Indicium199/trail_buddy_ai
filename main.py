from data_agent import DataAgent
from root_agent import RootAgent

def main():
    print("Hey! Your trail buddy is ready to plan a new adventure! ✔️\n")

    root_agent = RootAgent()
    data_agent = DataAgent()
    trails = data_agent.load_trails()

    # Step 1: Ask user for trail preferences
    difficulty = input("What kind of trail are you looking to do? (Easy/Moderate/Hard) ").strip().lower()
    distance_max = input("Maximum distance in km? ").strip()

    try:
        distance_max = float(distance_max)
    except ValueError:
        print("Invalid distance. Using no limit.")
        distance_max = float("inf")

    # Step 2: Filter trails based on user input
    filtered_trails = [
        t for t in trails
        if t["Difficulty"].lower() == difficulty and float(t["Distance_km"]) <= distance_max
    ]

    if not filtered_trails:
        print("No trails match your criteria.")
        return

    # Step 3: Pick the first matching trail (or you could rank them)
    trail = filtered_trails[0]

    # Step 4: Fetch live weather
    weather = data_agent.get_weather(trail["Lat"], trail["Lng"])
    weather_desc = data_agent.map_weather_code(weather["weather_code"])

    # Step 5: Ask Gemini to generate a friendly recommendation
    prompt = (
        f"The user wants a {difficulty} trail under {distance_max} km. "
        f"Trail: {trail['Trail']} ({trail['Difficulty']}, {trail['Distance_km']} km). "
        f"Current weather: {weather_desc}, Temp: {weather['temperature']}°C, Wind: {weather['windspeed']} km/h. "
        "Write a friendly hiking recommendation."
    )
    response = root_agent.ask_gemini(prompt)
    print("\n" + response)

if __name__ == "__main__":
    main()
