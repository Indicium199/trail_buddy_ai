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
    print("Agent:", response)

    # --- Main conversation loop ---
    while True:
        # Get input from the user
        user_input = input("You: ")

        # Pass the user input to RootAgent for handling
        response = root_agent.handle_user_message(
            user_input, data_agent, planner_agent, communication_agent
        )
        print("Agent:", response)

        # If the conversation is finished, break the loop
        if root_agent.state.get("awaiting_input") == "end":
            print("\nThanks for using Trail Buddy! Happy hiking! 🥾\n")
            break

# --- Run the program only if this file is executed directly ---
if __name__ == "__main__":
    main()
