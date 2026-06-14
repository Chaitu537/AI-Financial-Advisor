import streamlit as st
import pandas as pd
import os
import json
from groq import Groq
from agent.financial_health import (
    calculate_health_score,
    generate_savings_advice
)

CSV_FILE = "data/expenses.csv"

# --- DATABASE SETUP ---
os.makedirs("data", exist_ok=True)
if not os.path.exists(CSV_FILE):
    df = pd.DataFrame(columns=["amount", "category"])
    df.to_csv(CSV_FILE, index=False)

st.set_page_config(
    page_title="Autonomous Financial Agent",
    page_icon="🤖",
    layout="wide"
)

# --- GROQ API SETUP ---
API_KEY = os.environ.get("GROQ_API_KEY")

if not API_KEY:
    with st.sidebar:
        st.warning("⚠️ GROQ_API_KEY not found in environment variables.")
        API_KEY = st.text_input("Enter Groq API Key:", type="password")

# --- MULTI-EXPENSE TOOL ---
def log_multiple_expenses(expenses: list) -> str:
    try:
        df_local = pd.read_csv(CSV_FILE)
        logged_items = []
        new_rows = []
        
        for item in expenses:
            amt = float(item.get("amount", 0))
            cat = str(item.get("category", "Uncategorized")).strip().strip("'\"").capitalize()
            if amt > 0:
                new_rows.append({"amount": amt, "category": cat})
                logged_items.append(f"₹{amt:.2f} under '{cat}'")
        
        if new_rows:
            df_new = pd.DataFrame(new_rows)
            df_updated = pd.concat([df_local, df_new], ignore_index=True)
            df_updated.to_csv(CSV_FILE, index=False)
            return f"SUCCESS: Logged {', '.join(logged_items)}."
        return "ERROR: No valid entries found."
    except Exception as e:
        return f"ERROR: {str(e)}"

tools_schema = [
    {
        "type": "function",
        "function": {
            "name": "log_multiple_expenses",
            "description": "Logs one or multiple expense entries simultaneously. Use whenever the user states they spent money.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expenses": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "amount": {"type": "number"},
                                "category": {"type": "string"}
                            },
                            "required": ["amount", "category"]
                        }
                    }
                },
                "required": ["expenses"]
            }
        }
    }
]

# --- CHAT UI INTERFACE ---
st.title("🤖 Autonomous Financial Agent")
st.write("Powered by Groq Llama 3.3.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

prompt = st.chat_input("Talk to your agent...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    if API_KEY:
        client = Groq(api_key=API_KEY)
        
        current_df = pd.read_csv(CSV_FILE)
        data_context = "No transactions logged yet."
        if len(current_df) > 0:
            summary = current_df.groupby("category")["amount"].sum().to_string()
            data_context = f"Logged Summary:\n{summary}\nTotal Spent: ₹{current_df['amount'].sum()}"

        system_prompt = f"You are a Personal Finance Assistant. Help users with budgeting and finance topics. Current Data:\n{data_context}"

        try:
            with st.spinner("Processing..."):
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    tools=tools_schema,
                    tool_choice="auto"
                )
                
                response_message = response.choices[0].message
                
                if response_message.tool_calls:
                    tool_call = response_message.tool_calls[0]
                    args = json.loads(tool_call.function.arguments)
                    tool_result = log_multiple_expenses(expenses=args.get("expenses", []))
                    
                    second_response = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": prompt},
                            response_message,
                            {"role": "tool", "tool_call_id": tool_call.id, "name": "log_multiple_expenses", "content": tool_result}
                        ]
                    )
                    reply_text = second_response.choices[0].message.content
                else:
                    reply_text = response_message.content

        except Exception as e:
            reply_text = f"❌ Error: {str(e)}"
    else:
        reply_text = "⚠️ Provide your Groq API Key in the sidebar."

    st.session_state.messages.append({"role": "assistant", "content": reply_text})
    st.rerun()

# --- DASHBOARD METRICS ---
st.divider()
df = pd.read_csv(CSV_FILE)
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    st.subheader("📋 Core Data Ledger")
    st.dataframe(df, use_container_width=True, height=250)
    if len(df) > 0:
        st.metric("Total Spending", f"₹{df['amount'].sum():,.2f}")

with col2:
    st.subheader("📊 Spending Distribution")
    if len(df) > 0:
        st.bar_chart(df.groupby("category")["amount"].sum(), use_container_width=True)
    else:
        st.info("No data entries recorded yet.")

with col3:
    st.subheader("🩺 Financial Health Insights")
    if len(df) > 0:
        try:
            raw_score = calculate_health_score(df)
            raw_advice = generate_savings_advice(df)
            
            score = raw_score.get("score", "N/A") if isinstance(raw_score, dict) else raw_score
            st.metric("Financial Health Score", f"{score} / 10")
            
            st.markdown("**AI Optimization Advice:**")
            st.write(raw_advice.get("advice", str(raw_advice)) if isinstance(raw_advice, dict) else raw_advice)
        except Exception as e:
            st.error(f"Error running insights: {str(e)}")
    else:
        st.info("Log items to calculate analytics.")