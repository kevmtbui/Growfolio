# gemini_service.py
import os
from dotenv import load_dotenv
import google.generativeai as genai
import json

# Load API key from .env
load_dotenv()
GEN_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEN_KEY)

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

    disposable_income = income - expenses
    invest_amount = (savings + disposable_income) * (invest_percentage / 100)

    """
    Generate a structured user profile using Gemini AI.
    Handles:
    - Financial Snapshot (income, category-based expenses, savings, debt, dependents, age)
    - Investment Goals
    - Behavioral Profile
    """
    prompt = f"""
User answered the questionnaire:

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

Behavioral / Psychological:
Experience level: {user_data.get('13')}
Portfolio checking frequency: {user_data.get('14')}
Investor style: {user_data.get('15')}
Portfolio priority: {user_data.get('16')}

You are a seasoned financial advisor of 20+ years at a large Canadian bank. As a financial advisor, you are well-versed in investing, and offering people options to grow their portfolios. 
You also understand when someone is at financial risk, and advise them to not invest. As a top financial advisor, you are in charge of analyzing the users questionaire thoroughly (provided above), 
and determining if they should invest. If so, you'll determine what types of investments they should make depending on what their goal is. If you determine they should not invest, you'll provide a succint 
yet professional response as to why they shouldn't do so, based on the information they provided.  

There are a few edge cases you need to look out for, which are listed below. These cases determine if the user shouldn't invest. As a financial advisor, you are responsible for offering these users accurate
financial advice, as it can have a large impact on their lives. As a top financial advisor, it's essential to not only provide advice, but to teach individuals and improve their financial literacy.



Generate a structured JSON profile with keys:
- disposable_income
- risk_tolerance
- investment_goal
- spending_habits
- credit_history_summary
- behavioral_profile

Ensure JSON is valid and parsable.
"""
    
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    
    try:
        # Try to parse Gemini output as JSON
        profile = json.loads(response.text)  # For hackathon/demo only; safer: json.loads() if valid JSON
    except:
        # fallback: return raw text
        profile = {"raw_profile": response.text}
    
    return profile

def explain_stock(stock_name: str, user_profile: dict, ml_output: dict) -> str:
    """
    Uses Gemini to convert ML prediction + user profile into plain-language recommendation
    """
    prompt = f"""
    User profile: {json.dumps(user_profile)}
    ML output: {json.dumps(ml_output)}
    Explain why stock {stock_name} is suitable or not for this user in plain English.
    """
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text
