from agent.tool_router import (
    health_score,
    spending_alert,
    ai_advice,
    add_expense
)

from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os
import json
import re

load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY")
)


def choose_action(user_input):

    prompt = f"""
You are an AI Financial Advisor Agent.

Available actions:

1. add_expense
2. health_score
3. spending_alert
4. ai_advice

Rules:

If user is mentioning spending money,
choose add_expense.

Examples:

I spent 500 on food
-> add_expense

I spent 1000 on transport
-> add_expense

How healthy are my finances?
-> health_score

Am I spending too much?
-> spending_alert

Give me financial advice
-> ai_advice

User:
{user_input}

Return ONLY action name.
"""

    response = llm.invoke(prompt)

    return response.content.strip()


def extract_expense(user_input):

    prompt = f"""
Extract expense information.

User:
{user_input}

Return ONLY valid JSON:

{{
    "amount": number,
    "category": "category",
    "description": "description"
}}
"""

    response = llm.invoke(prompt)

    try:
        json_text = re.search(
            r"\{.*\}",
            response.content,
            re.DOTALL
        ).group()

        return json.loads(json_text)

    except:
        return None


while True:

    user = input("\nYou: ")

    if user.lower() == "exit":
        break

    action = choose_action(user)

    print(f"\n[Action Selected] -> {action}")

    if action == "add_expense":

        expense = extract_expense(user)

        if expense:

            result = add_expense(
                expense["amount"],
                expense["category"],
                expense["description"]
            )

            print("\nAgent:")
            print("Expense added successfully!")

        else:

            print("\nAgent:")
            print("Could not understand the expense.")

    elif action == "health_score":

        result = health_score()

        explanation = llm.invoke(
            f"""
Explain this financial health result:

{result}
"""
        )

        print("\nAgent:")
        print(explanation.content)

    elif action == "spending_alert":

        result = spending_alert()

        explanation = llm.invoke(
            f"""
Explain this spending result:

{result}
"""
        )

        print("\nAgent:")
        print(explanation.content)

    elif action == "ai_advice":

        result = ai_advice()

        explanation = llm.invoke(
            f"""
Explain this advice:

{result}
"""
        )

        print("\nAgent:")
        print(explanation.content)

    else:

        print("\nAgent:")
        print("I could not determine what to do.")