from typing import Dict, Any
from config import DEFAULT_JURISDICTION
from advisor import advise_online
from explanations import summarize_advice, explain_stock_recommendation

def risk_assessment_score(raw_answers: Dict[str, Any]) -> int:
    """
    Your real 1–10 scoring logic based on the 16 questions goes here.
    Must return int in [1,10].
    """
    # Import the existing risk assessment from gemini_service
    from gemini_service import risk_assesment_score
    score = risk_assesment_score(raw_answers)
    return max(1, min(10, int(score)))

def create_user_profile(raw_answers: Dict[str, Any]) -> Dict[str, Any]:
    """Create comprehensive user profile with online portfolio advice"""
    jurisdiction = (raw_answers.get("jurisdiction") or DEFAULT_JURISDICTION).upper()

    # 1) Compute risk score
    score = risk_assessment_score(raw_answers)

    # 2) Produce fully online advice (bands → sleeves → Gemini ETF picks → quotes/news)
    advice = advise_online(score, jurisdiction)

    # 3) Human-facing explanation with Gemini (text only)
    explanation = summarize_advice(advice)
    advice["explanation"] = explanation

    # 4) Assemble profile
    profile = {
        "age": raw_answers.get("age"),
        "horizon_years": raw_answers.get("horizon_years"),
        "goals": raw_answers.get("goals", []),
        "jurisdiction": jurisdiction,
        "preferences": raw_answers.get("preferences", {}),
        "risk_score": score,
        "advice": advice
    }
    return profile
