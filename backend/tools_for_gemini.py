from typing import Any, Dict, List
from online_data import search_symbols, get_quote, company_profile, etf_profile_holdings, company_news

# ---- Tools that Gemini can call ----
def tool_search_assets(query: str, prefer_type: str | None = None) -> List[Dict[str, Any]]:
    """
    prefer_type: 'ETF' or 'Common Stock' etc. (Finnhub 'type' field)
    """
    results = search_symbols(query)
    if prefer_type:
        results = [r for r in results if r.get("type") == prefer_type]
    # Normalize fields
    out = []
    for r in results[:20]:
        out.append({
            "symbol": r.get("symbol"),
            "description": r.get("description"),
            "type": r.get("type"),
        })
    return out

def tool_get_quote(symbols: List[str]) -> Dict[str, Any]:
    """Get live quotes for a list of symbols"""
    return {s: get_quote(s) for s in symbols}

def tool_get_profile(symbol: str) -> Dict[str, Any]:
    """Get profile (and ETF holdings if available) for a symbol"""
    prof = company_profile(symbol)
    etf = etf_profile_holdings(symbol)  # may be limited; we include if present
    return {"profile": prof, "etf": etf}

def tool_get_news(symbol: str, from_date: str, to_date: str) -> List[Dict[str, Any]]:
    """Get recent news for a symbol in a date range"""
    return company_news(symbol, from_date, to_date)

# ---- JSON schemas for Gemini function calling ----
GEMINI_TOOLS = [
    {
        "name": "search_assets",
        "description": "Search for stocks/ETFs by keyword and optional type filter.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "prefer_type": {"type": "string"}
            },
            "required": ["query"]
        }
    },
    {
        "name": "get_quote",
        "description": "Get live quotes for a list of symbols.",
        "parameters": {
            "type": "object",
            "properties": {
                "symbols": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["symbols"]
        }
    },
    {
        "name": "get_profile",
        "description": "Get profile (and ETF holdings if available) for a symbol.",
        "parameters": {
            "type": "object",
            "properties": {"symbol": {"type": "string"}},
            "required": ["symbol"]
        }
    },
    {
        "name": "get_news",
        "description": "Get recent news for a symbol in a date range (YYYY-MM-DD).",
        "parameters": {
            "type": "object",
            "properties": {
                "symbol": {"type": "string"},
                "from_date": {"type": "string"},
                "to_date": {"type": "string"}
            },
            "required": ["symbol", "from_date", "to_date"]
        }
    }
]

# Actual tool function map
GEMINI_TOOL_FUNCS = {
    "search_assets": lambda args: tool_search_assets(args.get("query", ""), args.get("prefer_type")),
    "get_quote": lambda args: tool_get_quote(args.get("symbols", [])),
    "get_profile": lambda args: tool_get_profile(args.get("symbol", "")),
    "get_news": lambda args: tool_get_news(args.get("symbol", ""), args.get("from_date", ""), args.get("to_date", "")),
}
