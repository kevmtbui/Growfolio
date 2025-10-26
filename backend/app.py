# app.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from gemini_service import create_user_profile, explain_stock
from profile_creator import create_user_profile as create_advanced_profile
from explanations import explain_stock_recommendation
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
            {"id": 4, "text": "Total monthly debt/loan payments (enter 0 if none)", "type": "float"},
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
            {"id": 10, "text": "How much of your net savings are you willing to invest?", "type": "slider", "min": 0, "max": 100},
            {"id": 11, "text": "Would you prefer steady growth or higher potential returns (which results in more ups and downs)?", "type": "scale", "min": 1, "max": 5}
        ]
    },
    {   "id": 3,
        "title": "Personal Profile",
        "questions": [
            {"id": 12, "text": "If your investment dropped 20% in a month, what would you do?", "type": "multiple_choice",
             "options": ["Sell everything", "Sell some", "Do nothing", "Buy more"]},
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

@app.post("/create_advanced_profile")
async def generate_advanced_profile(req: Request):
    """
    Receives user answers and creates advanced portfolio with real-time data
    Returns comprehensive profile with ETF selections, quotes, and news
    """
    data = await req.json()
    try:
        profile = create_advanced_profile(data)
        return {"user_profile": profile}
    except Exception as e:
        return {"error": f"Failed to create advanced profile: {str(e)}"}

@app.post("/analyze_trader_type")
async def analyze_trader_type(req: Request):
    """
    Receives user profile and determines trader type routing
    Returns appropriate analysis based on trader type
    """
    data = await req.json()
    user_profile = data.get("user_profile", {})
    trader_type = data.get("trader_type", "")
    
    if trader_type == "day_trader":
        # Route to ML model for short-term predictions
        return await handle_day_trader_analysis(user_profile)
    elif trader_type == "retirement_investor":
        # Route to advanced portfolio system for long-term allocation
        return await handle_retirement_analysis_advanced(user_profile)
    else:
        return {"error": "Invalid trader type. Must be 'day_trader' or 'retirement_investor'"}

async def handle_day_trader_analysis(user_profile: dict):
    """
    Handles day trader analysis using ML model (placeholder for now)
    """
    # Placeholder ML predictions - replace with actual ML model when ready
    ml_predictions = {
        "predictions": [
            {"ticker": "AAPL", "action": "buy", "confidence": 78, "timeframe": "15min"},
            {"ticker": "MSFT", "action": "hold", "confidence": 65, "timeframe": "30min"},
            {"ticker": "NVDA", "action": "sell", "confidence": 82, "timeframe": "1hour"},
            {"ticker": "TSLA", "action": "buy", "confidence": 71, "timeframe": "45min"}
        ],
        "market_sentiment": "bullish",
        "volatility_level": "medium",
        "recommended_position_size": "small"
    }
    
    return {
        "trader_type": "day_trader",
        "analysis": ml_predictions,
        "timestamp": "2024-01-15T10:30:00Z"
    }

async def handle_retirement_analysis_advanced(user_profile: dict):
    """
    Handles retirement investor analysis using advanced portfolio system
    """
    try:
        # Extract risk score and jurisdiction from user profile
        risk_score = user_profile.get("risk_score", 5)
        jurisdiction = user_profile.get("jurisdiction", "CA")
        
        # Use the advanced portfolio system
        from advisor import advise_online
        from explanations import summarize_advice
        
        advice = advise_online(risk_score, jurisdiction)
        explanation = summarize_advice(advice)
        advice["explanation"] = explanation
        
        return {
            "trader_type": "retirement_investor", 
            "analysis": advice,
            "timestamp": "2024-01-15T10:30:00Z"
        }
    except Exception as e:
        # Fallback to basic Gemini analysis
        from gemini_service import create_retirement_portfolio
        portfolio_allocation = create_retirement_portfolio(user_profile)
        
        return {
            "trader_type": "retirement_investor", 
            "analysis": portfolio_allocation,
            "timestamp": "2024-01-15T10:30:00Z",
            "fallback": True,
            "error": str(e)
        }
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
    
    try:
        # Use the new explanation system
        explanation = explain_stock_recommendation(stock_name, user_profile, ml_output)
    except Exception as e:
        # Fallback to basic explanation
        explanation = explain_stock(stock_name, user_profile, ml_output)
    
    return {
        "stock": stock_name,
        "ml_output": ml_output,
        "gemini_explanation": explanation
    }
