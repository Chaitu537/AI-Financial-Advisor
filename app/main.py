from fastapi import FastAPI
from app.models.expense_model import Expense
from app.services.agent_service import AgentService

import json
import os

app = FastAPI(
    title="AI Financial Advisor"
)

agent = AgentService()

DB_FILE = "expenses.json"


def load_expenses():

    if os.path.exists(DB_FILE):

        with open(DB_FILE, "r") as file:
            return json.load(file)

    return []


def save_expenses(expenses):

    with open(DB_FILE, "w") as file:

        json.dump(
            expenses,
            file,
            indent=4
        )


dummy_db = load_expenses()


@app.get("/")
def root():

    return {
        "message": "AI Financial Advisor Running"
    }


@app.post("/add-expense")
def add_expense(expense: Expense):

    global dummy_db

    dummy_db.append(
        expense.model_dump()
    )

    save_expenses(
        dummy_db
    )

    return {
        "message": "Expense Added",
        "data": expense
    }


@app.get("/expenses")
def get_expenses():

    return {
        "expenses": dummy_db
    }


@app.get("/ai-advice")
def ai_advice():

    advice = agent.get_advice(dummy_db)

    return {
        "advice": advice
    }


@app.get("/health-score")
def health_score():

    if not dummy_db:

        return {
            "score": 0,
            "message": "No expenses found"
        }

    total = sum(
        expense["amount"]
        for expense in dummy_db
    )

    score = 10

    if total > 5000:
        score -= 2

    if total > 10000:
        score -= 2

    return {
        "score": score,
        "total_expense": total
    }


@app.get("/spending-alert")
def spending_alert():

    if not dummy_db:

        return {
            "alert": "No expenses found"
        }

    category_totals = {}

    for expense in dummy_db:

        category = expense["category"]
        amount = expense["amount"]

        if category not in category_totals:
            category_totals[category] = 0

        category_totals[category] += amount

    highest_category = max(
        category_totals,
        key=category_totals.get
    )

    return {
        "highest_spending_category": highest_category,
        "amount": category_totals[highest_category],
        "alert": f"You are spending the most on {highest_category}"
    }