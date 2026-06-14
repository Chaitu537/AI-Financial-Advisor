import requests

BASE_URL = "http://127.0.0.1:8000"


def get_health_score():
    response = requests.get(f"{BASE_URL}/health-score")
    return response.json()


def get_spending_alert():
    response = requests.get(f"{BASE_URL}/spending-alert")
    return response.json()


def get_ai_advice():
    response = requests.get(f"{BASE_URL}/ai-advice")
    return response.json()


print("Health Score:")
print(get_health_score())

print("\nSpending Alert:")
print(get_spending_alert())

print("\nAI Advice:")
print(get_ai_advice())