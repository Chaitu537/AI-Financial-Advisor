from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os

load_dotenv()

class AgentService:

    def __init__(self):

        self.model = ChatGroq(
            model="llama-3.3-70b-versatile",
            api_key=os.getenv("GROQ_API_KEY")
        )

    def get_advice(self, expenses):

        prompt = f"""
You are an expert AI Financial Advisor.

Analyze the following expenses:

{expenses}

Provide:

1. Total Spending
2. Category-wise Analysis
3. Budget Suggestions
4. Savings Advice
5. Financial Health Score out of 10

Be concise and practical.
"""
        response = self.model.invoke(prompt)

        return response.content