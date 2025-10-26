import os
import requests
import time
from typing import List, Dict, Any

FINNHUB_KEY = os.getenv("FINNHUB_API_KEY")
if not FINNHUB_KEY:
    print("Warning: FINNHUB_API_KEY not set. Using mock data for development.")
    FINNHUB_KEY = "demo"  # Allow development without API key

BASE = "https://finnhub.io/api/v1"
DEFAULT_TIMEOUT = 20
RATE_SLEEP = 0.2  # be gentle

def _get(path: str, params: Dict[str, Any]) -> Any:
    """Make API request with rate limiting"""
    if FINNHUB_KEY == "demo":
        # Return mock data for development
        return _get_mock_data(path, params)
    
    params = {**params, "token": FINNHUB_KEY}
    r = requests.get(f"{BASE}{path}", params=params, timeout=DEFAULT_TIMEOUT)
    r.raise_for_status()
    time.sleep(RATE_SLEEP)
    return r.json()

def _get_mock_data(path: str, params: Dict[str, Any]) -> Any:
    """Return mock data for development when API key is not available"""
    if path == "/search":
        return {
            "result": [
                {"symbol": "VTI", "description": "Vanguard Total Stock Market ETF", "type": "ETF"},
                {"symbol": "VEA", "description": "Vanguard FTSE Developed Markets ETF", "type": "ETF"},
                {"symbol": "BND", "description": "Vanguard Total Bond Market ETF", "type": "ETF"},
                {"symbol": "VCN", "description": "Vanguard FTSE Canada All Cap Index ETF", "type": "ETF"},
            ]
        }
    elif path == "/quote":
        symbol = params.get("symbol", "VTI")
        return {
            "c": 250.50,  # current price
            "d": 2.15,   # change
            "dp": 0.87,   # percent change
            "h": 252.00,  # high
            "l": 248.00,  # low
            "o": 249.00,  # open
            "pc": 248.35  # previous close
        }
    elif path == "/stock/profile2":
        symbol = params.get("symbol", "VTI")
        return {
            "country": "US",
            "currency": "USD",
            "exchange": "NASDAQ",
            "finnhubIndustry": "Financial Services",
            "ipo": "2001-05-31",
            "logo": "https://static.finnhub.io/logo/87cb30d8-80df-11ea-8951-00000000092a.png",
            "marketCapitalization": 250000000000,
            "name": "Vanguard Total Stock Market ETF",
            "phone": "",
            "shareOutstanding": 1000000000,
            "ticker": symbol,
            "weburl": "https://investor.vanguard.com/etf/profile/VTI"
        }
    elif path == "/etf/holdings":
        return {}  # Empty for most ETFs
    elif path == "/company-news":
        return []  # Empty news for mock
    else:
        return {}

# ---------- Discovery / search ----------
def search_symbols(query: str) -> List[Dict[str, Any]]:
    """General search across stocks, ETFs. Returns array with fields: symbol, description, type, etc."""
    data = _get("/search", {"q": query})
    return data.get("result", [])

# ---------- Quotes ----------
def get_quote(symbol: str) -> Dict[str, Any]:
    """Realtime quote: c=current, dp=percent change, h/l/o etc."""
    data = _get("/quote", {"symbol": symbol})
    return data

def batch_quotes(symbols: List[str]) -> Dict[str, Dict[str, Any]]:
    """Get quotes for multiple symbols"""
    out = {}
    for s in symbols:
        out[s] = get_quote(s)
    return out

# ---------- Profiles (ETF/company) ----------
def company_profile(symbol: str) -> Dict[str, Any]:
    """Profile for symbol (works for equities/ETFs). Expense ratio often under 'etf' endpoints, but profile still useful."""
    return _get("/stock/profile2", {"symbol": symbol})

def etf_profile_holdings(symbol: str) -> Dict[str, Any]:
    """ETF profile/holdings (availability varies by plan). We still call it; if empty, we fall back to profile."""
    try:
        data = _get("/etf/holdings", {"symbol": symbol})
    except Exception:
        data = {}
    return data or {}

# ---------- News ----------
def company_news(symbol: str, from_date: str, to_date: str) -> List[Dict[str, Any]]:
    """News for symbol in a date range YYYY-MM-DD."""
    try:
        return _get("/company-news", {"symbol": symbol, "from": from_date, "to": to_date})
    except Exception:
        return []
