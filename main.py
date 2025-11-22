from data_agent import DataAgent
from planner_agent import PlannerAgent
from communicator_agent import CommunicationAgent
from root_agent import RootAgent

def main():
    data_agent = DataAgent()
    planner_agent = PlannerAgent(data_agent)
    communication_agent = CommunicationAgent()
    root_agent = RootAgent()

    print("Hey! Your trail buddy is ready to plan a new adventure! ✔️\n")

    # Start conversation
    response = root_agent.handle_user_message(
        "", data_agent, planner_agent, communication_agent
    )
    print(response)

    # Conversation loop
    while True:
        user_input = input("You: ")
        response = root_agent.handle_user_message(
            user_input, data_agent, planner_agent, communication_agent
        )
        print("Agent:", response)

        if root_agent.state["awaiting_input"] is None:
            print("\n🎉 Enjoy your hike! Restart the program to plan a new trail.\n")
            break

if __name__ == "__main__":
    main()
