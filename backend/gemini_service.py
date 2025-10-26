# gemini_service.py
import os
from dotenv import load_dotenv
import google.generativeai as genai
import json
import math

# Load API key from .env
load_dotenv()
GEN_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEN_KEY)

def _clamp(x, a, b):
    return max(a, min(b, x))

def _map(val, table, default):
    return table.get(str(val).lower(), default)

def _parse_horizon_years(user):
    """
    Uses Q7 (goal), Q8 (horizon bucket), Q9 (retirement age), Q6 (age).
    Falls back to a sensible default if fields are missing.
    """
    goal = str(user.get("7", "")).lower()
    age = float(user.get("6", 0) or 0)

    # If retirement goal, use retirement_age - age
    if "retire" in goal:
        retire_age = float(user.get("9", 0) or 0)
        if retire_age > age:
            return max(0.0, retire_age - age)

    # Otherwise parse horizon bucket in Q8
    horizon_raw = str(user.get("8", "")).lower()
    # Map common bucket labels to midpoints (years)
    buckets = {
        "<1 year": 0.5, "under 1 year": 0.5, "less than 1 year": 0.5,
        "1–3 years": 2.0, "1-3 years": 2.0, "1 to 3 years": 2.0,
        "3–7 years": 5.0, "3-7 years": 5.0, "3 to 7 years": 5.0,
        "7–15 years": 11.0, "7-15 years": 11.0, "7 to 15 years": 11.0,
        "15+ years": 20.0, "15 plus years": 20.0, "15 or more years": 20.0
    }
    for k, v in buckets.items():
        if k in horizon_raw:
            return v

    # Fallback if nothing matches
    return 5.0

def risk_assesment_score(user: dict) -> float:
    """
    Computes a 1-10 risk score with 0.1 precision based on your questionnaire.
    Keys used (by your current PRD numbering):
      1 income (net monthly), 2 expenses (dict), 3 savings, 4 debt (text/flag),
      5 dependents, 6 age, 7 goal, 8 horizon bucket, 9 retirement age,
      10 invest %, 11 growth preference (risk comfort 1–5 or text),
      12 reaction to 20% drop, 13 experience, 14 check freq.
    Returns: effective_risk (float, e.g., 6.8)
    """

    # --- Extract & derive basics ---
    income = float(user.get("1", 0) or 0)
    expenses_by_cat = user.get("2", {}) or {}
    expenses = float(sum(expenses_by_cat.values())) if isinstance(expenses_by_cat, dict) else float(user.get("2", 0) or 0)
    savings = float(user.get("3", 0) or 0)
    age = float(user.get("6", 0) or 0)
    dependents = int(user.get("5", 0) or 0)
    invest_percent = float(user.get("10", 0) or 0)
    horizon_years = _parse_horizon_years(user)

    # Reaction to drawdown (Q12)
    reaction_raw = str(user.get("12", "")).lower()
    reaction_map = {
        "sell everything": 0.00, "sell all": 0.00, "sell_all": 0.00,
        "sell some": 0.33, "sell_some": 0.33,
        "do nothing": 0.66, "do_nothing": 0.66,
        "buy more": 1.00, "buy_more": 1.00, "buy the dip": 1.00
    }
    reaction_score = _map(reaction_raw, reaction_map, 0.33)

    # Experience (Q13)
    exp_raw = str(user.get("13", "")).lower()
    exp_map = {"beginner": 0.20, "intermediate": 0.60, "advanced": 1.00}
    experience_score = _map(exp_raw, exp_map, 0.20)

    # Check frequency (Q14)
    freq_raw = str(user.get("14", "")).lower()
    freq_map = {"rarely": 0.20, "monthly": 0.40, "weekly": 0.70, "daily": 1.00}
    check_freq_score = _map(freq_raw, freq_map, 0.40)

    # Debt ratio (monthly debt / income) - Q4 is now a numeric field
    monthly_debt = float(user.get("4", 0) or 0)
    debt_ratio = monthly_debt / max(1.0, income) if income > 0 else 0.0

    # Emergency buffer in months
    monthly_expenses = max(1.0, expenses)  # avoid divide-by-zero
    emergency_months = savings / monthly_expenses

    # --- Normalize to 0..1 (higher = more risk-tolerant) ---
    age_score        = _clamp((45 - age) / 25.0, 0.0, 1.0)                     # younger → higher
    dependents_score = 1.0 if dependents == 0 else max(0.0, 1.0 - 0.25*dependents)
    horizon_score    = _clamp(horizon_years / 30.0, 0.0, 1.0)                   # 30y+ ~ 1
    invest_pct_score = _clamp(invest_percent / 80.0, 0.0, 1.0)                  # 80%+ ~ 1
    debt_penalty     = 0.6 * _clamp((debt_ratio - 0.20) / 0.30, 0.0, 1.0)       # >20% hurts up to 0.6
    buffer_bonus     = 0.3 * _clamp((emergency_months - 3.0) / 3.0, 0.0, 1.0)   # >3 months helps up to 0.3

    composite = (
        0.18*age_score +
        0.10*dependents_score +
        0.20*horizon_score +
        0.12*invest_pct_score +
        0.15*reaction_score +
        0.10*experience_score +
        0.05*check_freq_score
        - debt_penalty
        + buffer_bonus
    )
    base = round((_clamp(composite, 0.0, 1.0) * 9.0 + 1.0), 1)  # scale to 1..10

    # --- Safety caps (don’t change what you *show* unless you want to; use “effective” in logic) ---
    effective = base
    if emergency_months < 1.0:
        effective = min(effective, 4.0)
    if debt_ratio > 0.50:
        effective = min(effective, 4.0)
    if horizon_years < 1.0:
        effective = min(effective, 5.0)
    if reaction_raw in ("sell everything", "sell all", "sell_all"):
        effective = min(effective, 5.0)

    # Return the score you’ll pass to Gemini (use `effective` for allocations/recos)
    return round(effective, 1)

def create_user_profile(user_data: dict) -> dict:
    investment_goal = user_data.get("7", "").lower()
    income = user_data.get("1", 0)
    expenses = sum(user_data.get("2", {}).values())  # Housing + Groceries + etc.
    savings = user_data.get("3", 0)
    dependents = user_data.get("5", 0)
    invest_percentage = user_data.get("10", 0)
    risk_level = user_data.get("11", 3)
    age = user_data.get("6", 0)
    experience = user_data.get("13", "")

    riskScore = risk_assesment_score(user_data)
    disposable_income = income - expenses
    
    """
    Generate a structured user profile using Gemini AI.
    Handles:
    - Financial Snapshot (income, category-based expenses, savings, debt, dependents, age)
    - Investment Goals
    - Behavioral Profile
    """
    prompt = f"""
    You are a seasoned financial advisor of 20+ years at a large Canadian bank. As a financial advisor, you are well-versed in investing, and offering people options to grow their portfolios. 
    You also understand when someone is at financial risk, and advise them to not invest. As a top financial advisor, you are in charge of receiving and analyzing detailed financial questionaire forms from users.
    These forms contain a variety of financial information relating to the individual, their financial standing, and their interest in investing. You are in charge of analyzing these users, and determining if they should invest. 
    If so, you'll determine what types of investments they should make depending on what their goal is. If you determine they should not invest, you'll provide a succint yet professional response as to why they shouldn't do so, based on the information they provided.  
    
    The questionaire is split into 3 sections, which are provided below.
    
    Financial Snapshot:
    Income: {user_data.get('1')}
    Expenses by category: {json.dumps(user_data.get('2'))}
    Savings: {user_data.get('3')}
    Debt: {user_data.get('4')}
    Dependents: {user_data.get('5')}
    Age: {user_data.get('6')}

    Investment Goals:
    Primary goal: {user_data.get('7')}
    Investment horizon: {user_data.get('8')}
    Target retirement age: {user_data.get('9')}
    Percentage to invest: {user_data.get('10')}
    Growth preference: {user_data.get('11')}
    Reaction to 20% loss: {user_data.get('12')}

    Investment Behaviour Insights:
    Experience level: {user_data.get('13')}
    Portfolio checking frequency: {user_data.get('14')}
    Investor style: {user_data.get('15')}
    Portfolio priority: {user_data.get('16')}

    There are a few edge cases you need to look out for, which are listed below. These cases determine if the user shouldn't invest. As a financial advisor, you are responsible for offering these users accurate
    financial advice, as it can have a large impact on their lives. As a top financial advisor, it's essential to not only provide advice, but to teach individuals and improve their financial literacy. The analysis 
    should be succint, detailed, and understandable for an individual with modterate to low financial literacy. The output file should stricly be a working/functioning JSON file. If the user's income - expenses is negative, if they have 0 savings, 
    or if they are aged >=60 and want to keep their money invested for 15+ years, then invevsting is not ideal.  

    Also utlilze the user's risk assesment score: {riskScore}, which is a 1-10 risk score with 0.1 precision based on the questionnaire.
    """  
    
    model = genai.GenerativeModel("models/gemini-2.5-flash")
    response = model.generate_content(prompt)
    
    try:
        # Try to parse Gemini output as JSON
        profile = json.loads(response.text)  # For hackathon/demo only; safer: json.loads() if valid JSON
    except:
        # fallback: return raw text
        profile = {"raw_profile": response.text}
    
    return profile

def create_retirement_portfolio(user_profile: dict) -> dict:
    """
    Uses Gemini to create a retirement portfolio allocation based on user profile
    """
    risk_score = user_profile.get("risk_score", 5)
    age = user_profile.get("age", 35)
    horizon_years = user_profile.get("horizon_years", 20)
    income = user_profile.get("income", 0)
    expenses = user_profile.get("expenses", 0)
    
    prompt = f"""You are a seasoned financial advisor of 20+ years at a large Canadian bank. As a financial advisor, you are well-versed in investing, and offering people options to grow their portfolios. 
    You also understand when someone is at financial risk, and advise them with safe options to do so. As a top financial advisor, you are in charge of receiving and analyzing detailed financial questionaire forms from users.
    These forms contain a variety of financial information relating to the individual, their financial standing, and their interest in investing. You are in charge of analyzing these users, and determining how they should invest. 
    As a financial advisor, you are responsible for offering these users accurate financial advice, as it can have a large impact on their lives. As a top financial advisor, it's essential to not only provide advice, but to 
    teach individuals and improve their financial literacy. The analysis should be succint, detailed, and understandable for an individual with modterate to low financial literacy. 
    Your explanations should teach/explain to users about potential investments they can make.
    
    TASK:
    Create a retirement portfolio allocation for a client with the following profile:

    
Age: {age}, Investment Horizon: {horizon_years} years, Risk Score: {risk_score}/10, Monthly Income: ${income}, Monthly Expenses: ${expenses}

Respond ONLY with valid JSON in this exact format (no markdown, no explanations outside the JSON):
{{
    "asset_allocation": {{
        "stocks": {{"percentage": 60, "recommendations": ["VTI (Vanguard Total Stock Market ETF)", "VEA (Vanguard FTSE Developed Markets ETF)"]}},
        "bonds": {{"percentage": 30, "recommendations": ["BND (Vanguard Total Bond Market ETF)", "AGG (iShares Core U.S. Aggregate Bond ETF)"]}},
        "cash": {{"percentage": 10, "recommendations": ["Money Market Fund"]}}
    }},
    "rationale": "Brief 2-3 sentence explanation of why this allocation fits the client's profile and goals",
    "rebalancing": "Rebalancing schedule recommendation",
    "risk_notes": "Key risk considerations"
}}"""
    
    model = genai.GenerativeModel("models/gemini-2.5-flash")
    response = model.generate_content(prompt)
    
    try:
        # Try to parse Gemini output as JSON
        # Remove markdown code blocks if present
        text = response.text.strip()
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
        
        portfolio = json.loads(text)
    except:
        # Fallback: return structured data with cleaned text
        # Clean up the response text - remove markdown formatting and prompt echoes
        cleaned_text = response.text.strip()
        
        # Remove markdown headers and formatting
        cleaned_text = cleaned_text.replace("**", "")
        cleaned_text = cleaned_text.replace("##", "")
        cleaned_text = cleaned_text.replace("* ", "")
        
        # Remove any lines that look like they're echoing the prompt
        lines = cleaned_text.split('\n')
        content_lines = []
        skip_prompt_echo = False
        
        for line in lines:
            # Skip lines that are clearly from the prompt/system message
            if any(phrase in line.lower() for phrase in [
                "as a certified financial planner",
                "client profile summary",
                "**client profile",
                "you are a certified"
            ]):
                skip_prompt_echo = True
                continue
            
            # Skip bullet points that are just restating the profile
            if skip_prompt_echo and (line.strip().startswith("*") or line.strip().startswith("-")):
                continue
            
            # Once we hit actual content, stop skipping
            if line.strip() and not line.strip().startswith("*") and not line.strip().startswith("-"):
                skip_prompt_echo = False
            
            if line.strip() and not skip_prompt_echo:
                content_lines.append(line)
        
        cleaned_text = '\n'.join(content_lines).strip()
        
        # If still too verbose or empty, use a simple fallback
        if len(cleaned_text) > 1000 or len(cleaned_text) < 50:
            cleaned_text = f"Balanced portfolio allocation designed for moderate risk tolerance with a {horizon_years}-year investment horizon. Diversified across stocks, bonds, and cash to optimize growth while managing volatility."
        
        portfolio = {
            "asset_allocation": {
                "stocks": {"percentage": 60, "recommendations": ["VTI (Vanguard Total Stock Market ETF)", "VEA (Vanguard FTSE Developed Markets ETF)"]},
                "bonds": {"percentage": 30, "recommendations": ["BND (Vanguard Total Bond Market ETF)", "AGG (iShares Core U.S. Aggregate Bond ETF)"]},
                "cash": {"percentage": 10, "recommendations": ["Money Market Fund"]}
            },
            "rationale": cleaned_text,
            "rebalancing": "Annual rebalancing recommended",
            "risk_notes": "Monitor portfolio quarterly and adjust based on market conditions"
        }
    
    return portfolio