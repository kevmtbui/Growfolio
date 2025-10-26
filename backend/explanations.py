import os
import json
import google.generativeai as genai
from prompts import SYSTEM_POLICY_EXPLANATION, SYSTEM_POLICY_STOCK_EXPLANATION

GEMINI_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_KEY:
    raise RuntimeError("GEMINI_API_KEY not set.")
genai.configure(api_key=GEMINI_KEY)

def summarize_advice(advice: dict) -> str:
    """
    Use Gemini to turn the structured advice into a clean, concise explanation.
    """
    model = genai.GenerativeModel("models/gemini-2.5-flash")
    prompt = (
        f"{SYSTEM_POLICY_EXPLANATION}\n"
        f"ADVICE_JSON:\n{json.dumps(advice)}"
    )
    resp = model.generate_content(prompt)
    return (resp.text or "").strip()

def explain_stock_recommendation(stock_name: str, user_profile: dict, ml_output: dict) -> str:
    """
    Uses Gemini to convert ML prediction + user profile into plain-language recommendation
    """
    model = genai.GenerativeModel("models/gemini-2.5-flash")
    prompt = f"""
    {SYSTEM_POLICY_STOCK_EXPLANATION}
    
    User profile: {json.dumps(user_profile)}
    ML output: {json.dumps(ml_output)}
    Stock: {stock_name}
    
    Provide a clear explanation of why this stock recommendation makes sense for this user.
    """
    response = model.generate_content(prompt)
    return response.text
