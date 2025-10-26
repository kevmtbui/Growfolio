from typing import Dict, Any, List
from datetime import date, timedelta
from risk_policy import band_for_score
from allocator import target_sleeves
from selector_online import pick_etfs_for_sleeves
from online_data import batch_quotes, company_news

def advise_online(risk_score: int, jurisdiction: str) -> Dict[str, Any]:
    """Generate comprehensive portfolio advice using real-time data"""
    band = band_for_score(risk_score)
    sleeves = target_sleeves(risk_score, jurisdiction)  # deterministic weights

    # 1) Ask Gemini to select ETFs ONLINE via tools (for non-cash sleeves)
    picks = pick_etfs_for_sleeves(jurisdiction, sleeves)

    # 2) Build final portfolio list by mapping subclass -> chosen symbol, with weights
    subclass_to_symbol = {p["subclass"]: p for p in picks}
    portfolio: List[Dict[str, Any]] = []
    for s in sleeves:
        if s["class"] == "cash":
            portfolio.append({
                "asset": "CASH", 
                "name": "Cash Reserve", 
                "weight": s["weight"], 
                "notes": "Liquidity buffer"
            })
        else:
            pick = subclass_to_symbol.get(s["subclass"])
            if not pick:
                raise RuntimeError(f"No pick for subclass {s['subclass']}")
            portfolio.append({
                "asset": pick["symbol"],
                "name": pick["name"],
                "weight": s["weight"],
                "notes": f"{s['class']}/{s['subclass']}",
                "reasons": pick.get("reasons", []),
                "expense_ratio": pick.get("expense_ratio")
            })

    # 3) Live quotes
    tickers = [x["asset"] for x in portfolio if x["asset"] != "CASH"]
    quotes = batch_quotes(tickers)

    # 4) Recent news window (last 7 days)
    to_d = date.today()
    from_d = to_d - timedelta(days=7)
    news = {}
    for t in tickers:
        try:
            news[t] = company_news(t, from_d.isoformat(), to_d.isoformat())[:5]
        except Exception:
            news[t] = []

    return {
        "risk": {
            "score": risk_score,
            "title": band.title,
            "description": band.description
        },
        "jurisdiction": jurisdiction.upper(),
        "sleeves": sleeves,      # deterministic sleeve targets
        "portfolio": portfolio,  # sleeves mapped to live-picked ETFs
        "quotes": quotes,        # finnhub live quotes
        "news": news             # recent articles
    }
