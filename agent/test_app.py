import streamlit as st
import pandas as pd
import os
import json
from groq import Groq
from dotenv import load_dotenv

# Absolute Internal Architecture Imports
from tool_router import (
    log_multiple_expenses,
    search_live_market_data,
    get_live_stock_price
)
from financial_health import (
    calculate_health_score,
    generate_savings_advice
)

load_dotenv()

CSV_FILE = "data/expenses.csv"
os.makedirs("data", exist_ok=True)
if not os.path.exists(CSV_FILE):
    pd.DataFrame(columns=["amount", "category"]).to_csv(CSV_FILE, index=False)

st.set_page_config(
    page_title="Autonomous AI Financial Hub",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Enterprise CSS Override Injector
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600&family=JetBrains+Mono:wght@400;600&display=swap');
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Space Grotesk', sans-serif;
        background-color: #0E1117;
    }
    .metric-card {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        margin-bottom: 16px;
    }
    .metric-title { font-size: 0.9rem; color: #94A3B8; font-weight: 600; text-transform: uppercase; tracking-wider; }
    .metric-value { font-size: 2.2rem; font-weight: 700; color: #F8FAFC; margin: 8px 0; }
    .metric-footer { font-size: 0.85rem; color: #38BDF8; font-family: 'JetBrains Mono', monospace; }
    .chat-bubble-user {
        background: #2563EB; color: #FFFFFF; padding: 14px 18px; border-radius: 18px 18px 2px 18px;
        margin: 10px 0; max-width: 80%; float: right; clear: both; box-shadow: 0 2px 10px rgba(37,99,235,0.2);
    }
    .chat-bubble-agent {
        background: #1E293B; color: #E2E8F0; padding: 14px 18px; border-radius: 18px 18px 18px 2px;
        margin: 10px 0; max-width: 80%; float: left; clear: both; border: 1px solid #334155;
    }
</style>
""", unsafe_allow_html=True)

GROQ_KEY = os.environ.get("GROQ_API_KEY")

# --- INITIALIZE CHAT MEMORY STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- SIDEBAR SYSTEMS DIAGNOSTIC & SESSION CONTROL ---
with st.sidebar:
    st.markdown("## 🛡️ 2-Engine Status Matrix")
    st.markdown("---")
    
    if GROQ_KEY:
        st.markdown('<div style="background:#064E3B; border-left:5px solid #10B981; padding:12px; border-radius:4px; margin-bottom:10px; color:#A7F3D0; font-size:0.85rem; font-family:\'JetBrains Mono\'">Core LLM Engine: ACTIVE</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="background:#7F1D1D; border-left:5px solid #EF4444; padding:12px; border-radius:4px; margin-bottom:10px; color:#FCA5A5; font-size:0.85rem; font-family:\'JetBrains Mono\'">Core LLM Engine: OFFLINE</div>', unsafe_allow_html=True)
        
    if os.environ.get("TAVILY_API_KEY"):
        st.markdown('<div style="background:#064E3B; border-left:5px solid #10B981; padding:12px; border-radius:4px; margin-bottom:10px; color:#A7F3D0; font-size:0.85rem; font-family:\'JetBrains Mono\'">Web Research Engine: ACTIVE</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="background:#7F1D1D; border-left:5px solid #EF4444; padding:12px; border-radius:4px; margin-bottom:10px; color:#FCA5A5; font-size:0.85rem; font-family:\'JetBrains Mono\'">Web Research Engine: OFFLINE</div>', unsafe_allow_html=True)
        
    if os.environ.get("ALPHA_VANTAGE_KEY"):
        st.markdown('<div style="background:#064E3B; border-left:5px solid #10B981; padding:12px; border-radius:4px; margin-bottom:10px; color:#A7F3D0; font-size:0.85rem; font-family:\'JetBrains Mono\'">Stock Quant Engine: ACTIVE</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="background:#7F1D1D; border-left:5px solid #EF4444; padding:12px; border-radius:4px; margin-bottom:10px; color:#FCA5A5; font-size:0.85rem; font-family:\'JetBrains Mono\'">Stock Quant Engine: OFFLINE</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("## ⚙️ Session Control Panel")
    
    # Action 1: Clear Chat Session Only
    if st.button("🧹 Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.toast("Chat memory cleared! Ready for a fresh talk.", icon="🧼")
        st.rerun()
        
    # Action 2: Reset Entire Ledger and Chat
    if st.button("🚨 Hard Reset App Data", use_container_width=True, type="primary"):
        # Reset memory state
        st.session_state.messages = []
        # Re-initialize blank csv ledger
        pd.DataFrame(columns=["amount", "category"]).to_csv(CSV_FILE, index=False)
        st.toast("All transactions and chats completely reset!", icon="💥")
        st.rerun()

# --- TOOLS ROUTING MANIFEST DEFINITION ---
tools_manifest = [
    {
        "type": "function",
        "function": {
            "name": "log_multiple_expenses",
            "description": "Extracts and commits a raw batch list array of monetary expenditures or income allocations into the local storage database ledger.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expenses": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "amount": {"type": "number", "description": "The exact calculated numerical quantity expended."},
                                "category": {"type": "string", "description": "The target classification token e.g., Food, Shopping, Utilities."}
                            },
                            "required": ["amount", "category"]
                        }
                    }
                },
                "required": ["expenses"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_live_market_data",
            "description": "Scans internet resources and Tavily indices to gather real-time macro-financial reporting, compliance news, and trends.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string", "description": "Targeted optimization research query string."}},
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_live_stock_price",
            "description": "Queries the Alpha Vantage clusters to get alpha metrics and standard stock quote structures.",
            "parameters": {
                "type": "object",
                "properties": {"ticker": {"type": "string", "description": "The capitalized ticker sequence format, e.g., AAPL, TSLA."}},
                "required": ["ticker"]
            }
        }
    }
]

# --- MAIN DASHBOARD FRAME ---
st.markdown("<h2 style='margin-bottom:0;'>📊 Live Operations Dashboard</h2>", unsafe_allow_html=True)
st.markdown("<p style='color:#64748B; font-size:1.05rem; margin-top:0;'>Autonomous AI Financial Advisor Terminal</p>", unsafe_allow_html=True)

chat_container = st.container()
with chat_container:
    for msg in st.session_state.messages:
        bubble_class = "chat-bubble-user" if msg["role"] == "user" else "chat-bubble-agent"
        st.markdown(f'<div class="{bubble_class}">{msg["content"]}</div>', unsafe_allow_html=True)
st.markdown('<div style="clear:both;"></div>', unsafe_allow_html=True)

user_input = st.chat_input("Track expenses, ask for financial info, or fetch live stock data...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.rerun()

if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    current_prompt = st.session_state.messages[-1]["content"]
    
    if not GROQ_KEY:
        st.session_state.messages.append({"role": "assistant", "content": "Advisory Execution halted: Primary Groq AI Engine credentials missing."})
        st.rerun()
        
    client = Groq(api_key=GROQ_KEY)
    
    df_context = pd.read_csv(CSV_FILE)
    context_string = "Ledger Matrix currently empty."
    if not df_context.empty:
        context_string = df_context.groupby("category")["amount"].sum().to_dict()
        
    system_prompt = f"""You are an elite Autonomous AI Financial Advisor. You are witty, authoritative, and deeply grounded in wealth management strategies.
    
    Current User Financial Allocation State:
    {context_string}

    CRITICAL INSTRUCTIONS:
    1. If the user presents one or multiple expenses (e.g., '300 food and 400 dress'), invoke 'log_multiple_expenses'.
    2. If the user requests stock prices, extract the ticker symbol and invoke 'get_live_stock_price'.
    3. If the user requests macro data or news, synthesize a query and invoke 'search_live_market_data'.
    4. For general greetings or chat (e.g., 'hi', 'hello', 'what is SIP'), answer elegantly in pure markdown without calling tools.
    """
    
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": current_prompt}
            ],
            tools=tools_manifest,
            tool_choice="auto"
        )
        
        response_msg = response.choices[0].message
        
        if response_msg.tool_calls:
            tool_call = response_msg.tool_calls[0]
            func_name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            
            if func_name == "log_multiple_expenses":
                tool_output = log_multiple_expenses(args.get("expenses", []))
            elif func_name == "search_live_market_data":
                tool_output = search_live_market_data(args.get("query", ""))
            elif func_name == "get_live_stock_price":
                tool_output = get_live_stock_price(args.get("ticker", ""))
            else:
                tool_output = "Execution routed to an unmapped telemetry channel."
                
            second_pass = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": current_prompt},
                    response_msg,
                    {"role": "tool", "tool_call_id": tool_call.id, "name": func_name, "content": tool_output}
                ]
            )
            final_reply = second_pass.choices[0].message.content
        else:
            final_reply = response_msg.content
            
    except Exception as err:
        final_reply = f"🚨 System Engine Exception Intercepted: {str(err)}"
        
    st.session_state.messages.append({"role": "assistant", "content": final_reply})
    st.rerun()

# --- VISUALIZATIONS ---
st.markdown("---")
df_ledger = pd.read_csv(CSV_FILE)

col_left, col_mid, col_right = st.columns([1, 1, 1], gap="medium")

with col_left:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown('<p class="metric-title">📋 Core Data Ledger</p>', unsafe_allow_html=True)
    if not df_ledger.empty:
        st.dataframe(df_ledger, use_container_width=True, height=220)
        st.markdown(f'<p class="metric-footer">Aggregate Outflows: ₹{df_ledger["amount"].sum():,.2f}</p>', unsafe_allow_html=True)
    else:
        st.markdown('<p style="color:#475569; font-size:0.9rem;">Vault empty. Awaiting records initialization.</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_mid:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown('<p class="metric-title">🍩 Interactive Portfolio Weight</p>', unsafe_allow_html=True)
    if not df_ledger.empty:
        import plotly.express as px
        grouped_df = df_ledger.groupby("category", as_index=False)["amount"].sum()
        fig = px.pie(
            grouped_df, values="amount", names="category", hole=0.5,
            template="plotly_dark", color_discrete_sequence=px.colors.sequential.Plotly3
        )
        fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), showlegend=False, height=220)
        st.plotly_chart(fig, use_container_width=True, key="portfolio_pie")
    else:
        st.markdown('<p style="color:#475569; font-size:0.9rem;">Vault empty. Awaiting records initialization.</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown('<p class="metric-title">🩺 Core Diagnostic Health</p>', unsafe_allow_html=True)
    if not df_ledger.empty:
        score_metrics = calculate_health_score(df_ledger)
        advice_payload = generate_savings_advice(df_ledger)
        
        if isinstance(score_metrics, dict):
            final_score = score_metrics.get("score", 10)
        else:
            final_score = score_metrics
            
        st.markdown(f'<div class="metric-value">{final_score} <span style="font-size:1rem; color:#64748B;">/ 10</span></div>', unsafe_allow_html=True)
        
        if isinstance(advice_payload, dict):
            final_advice = advice_payload.get("advice", "")
        else:
            final_advice = str(advice_payload)
            
        st.markdown(f'<p style="color:#E2E8F0; font-size:0.85rem; line-height:1.4;">💡 {final_advice}</p>', unsafe_allow_html=True)
    else:
        st.markdown('<p style="color:#475569; font-size:0.9rem;">Log items to run macro financial optimization diagnostics.</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)