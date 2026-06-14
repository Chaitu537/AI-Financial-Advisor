import os
import pandas as pd
import requests

CSV_FILE = "data/expenses.csv"

# Category Normalization Map
CATEGORY_MAP = {
    "food": "Food", "din": "Food", "dine": "Food", "restaurant": "Food", "cafe": "Food", "grocery": "Food", "groceries": "Food",
    "dress": "Shopping", "clothes": "Shopping", "clothing": "Shopping", "shoppinf": "Shopping", "shopping": "Shopping", "mall": "Shopping",
    "party": "Entertainment", "prty": "Entertainment", "club": "Entertainment", "movie": "Entertainment", "movies": "Entertainment", "bar": "Entertainment",
    "fuel": "Utilities", "gas": "Utilities", "electricity": "Utilities", "power": "Utilities", "water": "Utilities", "bill": "Utilities", "bills": "Utilities",
    "rent": "Housing", "flat": "Housing", "room": "Housing"
}

def normalize_category(raw_cat: str) -> str:
    cleaned = str(raw_cat).strip().lower()
    return CATEGORY_MAP.get(cleaned, cleaned.capitalize())

def log_multiple_expenses(expenses: list) -> str:
    """
    Parses an incoming batch array list of extracted dictionaries, normalizes tokens, 
    and saves records directly into the CSV database ledger.
    """
    if not expenses:
        return "Advisory Engine Parse Fault: Empty tracking token matrix received."
        
    try:
        df = pd.read_csv(CSV_FILE)
        new_records = []
        logged_descriptions = []
        
        for record in expenses:
            try:
                amt = float(record.get("amount", 0))
                raw_cat = str(record.get("category", "Other"))
                normalized_cat = normalize_category(raw_cat)
                
                if amt <= 0:
                    continue
                    
                new_records.append({"amount": amt, "category": normalized_cat})
                logged_descriptions.append(f"₹{amt:.2f} to '{normalized_cat}'")
            except (ValueError, TypeError):
                continue
                
        if new_records:
            df_new = pd.DataFrame(new_records)
            df_updated = pd.concat([df, df_new], ignore_index=True)
            df_updated.to_csv(CSV_FILE, index=False)
            
            # Integrated Inline Dashboard Warning System
            alert_prefix = ""
            total_food = df_updated[df_updated["category"] == "Food"]["amount"].sum()
            if total_food > 4000:
                alert_prefix = "⚠️ [SYSTEM ADVISORY CEILING EXCEEDED: Running food outlays point to anomalous overhead risk!]\n"
                
            return f"{alert_prefix}Successfully committed transactions: {', '.join(logged_descriptions)}."
        return "Transaction execution rejected: No valid numerical amounts recognized."
    except Exception as e:
        return f"Database Write Aborted: {str(e)}"

def get_live_stock_price(ticker: str) -> str:
    """Queries Alpha Vantage tracking indices for current valuation metrics."""
    api_key = os.environ.get("ALPHA_VANTAGE_KEY")
    if not api_key:
        return "Stock Quant Engine Error: Infrastructure access keys unverified."
        
    clean_ticker = str(ticker).strip().upper()
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={clean_ticker}&apikey={api_key}"
    
    try:
        response = requests.get(url, timeout=8)
        if response.status_code == 200:
            data = response.json()
            quote = data.get("Global Quote", {})
            if quote and "05. price" in quote:
                price = float(quote["05. price"])
                change_pct = quote.get("10. change percent", "0.00%")
                return f"Alpha Vantage System Quote: {clean_ticker} is currently trading at ${price:,.2f} USD with a daily variance metric of {change_pct}."
            return f"Alpha Vantage Stream Note: Ticker '{clean_ticker}' data is resting or API threshold has been hit."
        return f"Infrastructure Response Error: Received HTTP status code {response.status_code}."
    except Exception as e:
        return f"Telematics Failure: Alpha Vantage sync down: {str(e)}"

def search_live_market_data(query: str) -> str:
    """Deploys Tavily networks to aggregate contextual macro financial intelligence."""
    api_key = os.environ.get("TAVILY_API_KEY")
    if not api_key:
        return "Web Research Engine Error: Target access credential parameters undefined."
        
    url = "https://api.tavily.com/search"
    payload = {
        "api_key": api_key,
        "query": query,
        "search_depth": "basic",
        "include_answer": True
    }
    
    try:
        res = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=10)
        if res.status_code == 200:
            return res.json().get("answer") or "Tavily Index completed search but returned an empty context matrix."
        return f"Tavily Network Failure: Returned status code {res.status_code}."
    except Exception as e:
        return f"Search Telemetry Network Error: Tavily gateway connection aborted: {str(e)}"