# app.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from gemini_service import create_user_profile, explain_stock
import json

app = FastAPI()

# CORS settings for local Chrome extension demo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with "chrome-extension://<your-extension-id>" for stricter security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Hardcoded questions served dynamically
QUESTION_SECTIONS = [
    {   "id": 1,
        "title": "Financial Snapshot",
        "questions": [
            {"id": 1, "text": "What is your net monthly take-home income (after taxes)?", "type": "float"},
            {"id": 2, "text": "What are your average monthly expenses? (break down by category)", "type": "categories",
             "categories": ["Housing", "Groceries", "Utilities", "Transportation", "Miscellaneous"]},
            {"id": 3, "text": "How much do you currently have in savings or investments?", "type": "float"},
            {"id": 4, "text": "Do you have any debt or ongoing loan payments?", "type": "multiple_choice",
             "options": ["None", "Credit cards", "Student loans", "Car loans", "Other"]},
            {"id": 5, "text": "How many dependents rely on your income?", "type": "int"},
            {"id": 6, "text": "What is your age?", "type": "int"}
        ]
    },
    {   "id": 2,
        "title": "Investment Goals",
        "questions": [
            {"id": 7, "text": "What's your primary investment goal?", "type": "multiple_choice",
             "options": ["Retirement", "Short-term trading", "Supplemental Income"]},
            {"id": 8, "text": "How long do you plan to keep this money invested?", "type": "dropdown",
             "options": ["<1 year", "1-3 years", "3-7 years", "7-15 years", "15+ years"]},
            {"id": 9, "text": "If retirement, at what age would you like to retire?", "type": "int"},
            {"id": 10, "text": "How much of your net savings are you willing to invest?", "type": "slider", "min": 1, "max": 100},
            {"id": 11, "text": "Would you prefer steady growth or higher potential returns (which results in more ups and downs)?", "type": "scale", "min": 1, "max": 5},
            {"id": 12, "text": "If your investment dropped 20$ one month, what would you most likely do?", "type": "multiple_choice",
             "options": ["Sell everything", "Sell some", "Do nothing", "Buy more"]}
        ]
    },
    {   "id": 3,
        "title": "Personal Profile",
        "questions": [
            {"id": 13, "text": "How experienced are you with investing?", "type": "multiple_choice",
             "options": ["Beginner", "Intermediate", "Advanced"]},
            {"id": 14, "text": "How often do you check your portfolio or market news?", "type": "multiple_choice",
             "options": ["Daily", "Weekly", "Monthly", "Rarely"]},
            {"id": 15, "text": "Which statement best describes you?", "type": "multiple_choice",
             "options": [
                 "I'd rather miss some gains than lose money.",
                 "I'm okay with short-term losses if I can earn more long-term.",
                 "I enjoy taking calculated risks."
             ]},
            {"id": 16, "text": "Would you prefer your portfolio to prioritize…", "type": "multiple_choice",
             "options": ["Safety & Stability", "Balanced Growth", "Aggressive Growth"]}
        ]
    }
]


@app.get("/get_question_sections")
async def get_question_sections():
    """
    Returns all question sections as JSON
    Frontend can render one section at a time.
    """
    return {"sections": QUESTION_SECTIONS}

@app.post("/create_profile")
async def generate_profile(req: Request):
    """
    Receives user answers (~10 questions) from Chrome extension
    Returns a structured user profile created via Gemini
    """
    data = await req.json()
    profile = create_user_profile(data)
    return {"user_profile": profile}

@app.post("/recommend_stock")
async def recommend_stock(req: Request):
    """
    Receives a stock ticker + user profile + ML output placeholder
    Returns stock recommendation explanation using Gemini
    """
    data = await req.json()
    stock_name = data.get("stock_name")
    user_profile = data.get("user_profile")
    ml_output = data.get("ml_output", {"confidence": 80, "action": "buy"})  # Placeholder ML output
    
    if not stock_name or not user_profile:
        return {"error": "Missing stock_name or user_profile"}
    
    explanation = explain_stock(stock_name, user_profile, ml_output)
    return {
        "stock": stock_name,
        "ml_output": ml_output,
        "gemini_explanation": explanation
    }