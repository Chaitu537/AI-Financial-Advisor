from agent.chat_agent import run_agent

while True:

    user = input("\nYou: ")

    if user.lower() == "exit":
        break

    response = run_agent(user)

    print("\nAgent:")
    print(response)