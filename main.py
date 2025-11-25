from data_agent import DataAgent
from planner_agent import PlannerAgent
from communicator_agent import CommunicationAgent  # NEW
from root_agent import RootAgent
import os
from dotenv import load_dotenv

def main():
    # --- Load environment variables ---
    load_dotenv(dotenv_path="./.env")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if not GEMINI_API_KEY:
        raise ValueError("Please set GEMINI_API_KEY in your .env file.")

    # --- Create the agents ---
    data_agent = DataAgent()
    planner_agent = PlannerAgent(data_agent)
    communicator_agent = CommunicationAgent()  # NEW
    root_agent = RootAgent(planner_agent, data_agent, communicator_agent)  # pass communicator_agent

    # --- Initial greeting ---
    print("Hey! Your trail buddy is ready to plan a new adventure! ✔️\n")

    # --- Get the agent's first message before user types anything ---
    initial_message = root_agent.handle_user_message("")  # empty string triggers initial prompt
    print("Agent:", initial_message)

    # --- Conversation loop ---
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("\nThanks for using Trail Buddy! Have a great hike! 🌲🏞️")
            break

        response = root_agent.handle_user_message(user_input)
        print("Agent:", response)

if __name__ == "__main__":
    main()
