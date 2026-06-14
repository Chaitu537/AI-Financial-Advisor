import pandas as pd

def calculate_health_score(df: pd.DataFrame) -> dict:
    """
    Computes system financial health metrics. 
    Guaranteed to return a structured dictionary.
    """
    default_payload = {"score": 10, "total_outlay": 0.0, "exposure_matrix": {}}
    
    if df.empty:
        return default_payload
        
    try:
        total_outlay = df["amount"].sum()
        unique_categories = df["category"].nunique()
        score = 10
        
        if unique_categories <= 2 and len(df) > 3:
            score -= 2
            
        grouped = df.groupby("category")["amount"].sum()
        for cat, amt in grouped.items():
            exposure_ratio = amt / total_outlay if total_outlay > 0 else 0
            if exposure_ratio > 0.60 and cat not in ["Housing"]:
                score -= 3
                
        if total_outlay > 35000:
            score -= 2
        elif total_outlay > 15000:
            score -= 1
            
        return {
            "score": max(1, min(10, int(score))),
            "total_outlay": float(total_outlay),
            "exposure_matrix": grouped.to_dict()
        }
    except Exception:
        return default_payload

def generate_savings_advice(df: pd.DataFrame) -> dict:
    """Generates structured advice based on the calculated health metrics."""
    if df.empty:
        return {"advice": "Initialize telemetry input matrix streams to extract targeted capital optimization routines."}
        
    score_data = calculate_health_score(df)
    
    score = score_data.get("score", 10) if isinstance(score_data, dict) else score_data
    total = score_data.get("total_outlay", df["amount"].sum()) if isinstance(score_data, dict) else df["amount"].sum()
    
    if score >= 8:
        advice_string = f"Your asset allocation velocity is well optimized (Current Volume: ₹{total:,.2f}). Ready to transition into premium wealth accumulation vehicles like Equity SIPs."
    elif score >= 5:
        advice_string = f"Moderate vulnerabilities captured. Total running volume is at ₹{total:,.2f}. Try reducing non-essential outlays across your highest spending categories by 15%."
    else:
        advice_string = f"Critical risk metrics identified. Current running total of ₹{total:,.2f} requires aggressive structural adjustment. Minimize your flexible assets completely."
        
    return {"advice": advice_string}