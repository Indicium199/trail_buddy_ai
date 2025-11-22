# Import the different helper agent classes
from data_agent import DataAgent                   # Handles storing & retrieving information
from planner_agent import PlannerAgent             # Builds plans or steps based on the data
from communicator_agent import CommunicationAgent  # Formats & communicates messages to the user
from root_agent import RootAgent                   # Orchestrates the conversation and AI responses

def main():
    # --- Create the agents ---
    data_agent = DataAgent()                       # The "memory" agent for trail data & weather
    planner_agent = PlannerAgent(data_agent)       # The "planning" agent that selects trails based on criteria
    communication_agent = CommunicationAgent()     # The "conversation" agent for message formatting
    root_agent = RootAgent()                       # The orchestrator that handles the user conversation

    # --- Initial user greeting ---
    print("Hey! Your trail buddy is ready to plan a new adventure! ✔️\n")

    # --- Start conversation with empty input ---
    response = root_agent.handle_user_message(
        "", data_agent, planner_agent, communication_agent
    )
    print(response)

    # --- Main conversation loop ---
    selected_trail = None  # Store the selected trail for weather lookup
    while True:
        # Get input from the user
        user_input = input("You: ")

        # Pass the user input to RootAgent for handling
        response = root_agent.handle_user_message(
            user_input, data_agent, planner_agent, communication_agent
        )
        print("Agent:", response)

        # Update selected trail if RootAgent has chosen one
        if root_agent.state.get("selected_trail"):
            selected_trail = root_agent.state["selected_trail"]

        # If the conversation is finished, offer next actions
        if root_agent.state["awaiting_input"] is None:
            # Ask user what they want to do next
            user_choice = input(
                "\nWould you like the current weather forecast for this trail or something else? (weather/other): "
            )

            if user_choice.lower() == "weather":
                if selected_trail is None:
                    # Safety check in case no trail was actually selected
                    print("\nSorry, no trail information is available for weather lookup.\n")
                else:
                    # --- Get trail coordinates ---
                    trail_lat = selected_trail["Lat"]
                    trail_lon = selected_trail["Lng"]

                    # --- Fetch actual weather from API ---
                    weather = data_agent.get_weather(trail_lat, trail_lon)
                    weather_desc = data_agent.map_weather_code(weather["weather_code"])

                    # --- Create a plain weather summary ---
                    weather_summary = (
                        f"Temperature: {weather['temperature']}°C, "
                        f"Wind speed: {weather['windspeed']} km/h, "
                        f"Condition: {weather_desc}"
                    )

                    # --- Ask AI to rewrite the weather in a friendly style ---
                    prompt = (
                        f"You are a friendly hiking assistant. "
                        f"Here is the current weather at {selected_trail['Trail']}: {weather_summary}. "
                        f"Write a short, cheerful message to tell the user."
                    )
                    friendly_weather = root_agent.ask_gemini(prompt)

                    # If AI fails, fallback to a built-in friendly message
                    if not friendly_weather or "Sorry" in friendly_weather:
                        friendly_weather = (
                            f"Hey! 🌤️ The weather at {selected_trail['Trail']} is {weather_desc}, "
                            f"with a temperature of {weather['temperature']}°C and wind speed of {weather['windspeed']} km/h. "
                            "Perfect for your hike!"
                        )

                    # Print the friendly AI-generated weather message
                    print("\n" + friendly_weather + "\n")

            else:
                # User chose to do something else
                print("\nAlright! Let me know if you want to plan a different trail.\n")

            # End the conversation loop for now
            break

# --- Run the program only if this file is executed directly ---
if __name__ == "__main__":
    main()
