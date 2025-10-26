from typing import Dict, List, Tuple
from risk_policy import band_for_score
from config import EQUITY_SPLIT, BOND_SPLIT, ALLOCATION_ROUND_STEP

def round_to_step(x: float, step: float = ALLOCATION_ROUND_STEP) -> float:
    """Round to the nearest step for clean allocation percentages"""
    import math
    return round(x / step) * step

def build_band_targets(score: int) -> Dict[str, float]:
    """Build target allocation percentages for a given risk score"""
    b = band_for_score(score)
    total = b.target_equity + b.target_bonds + b.target_cash + b.target_alts
    if abs(total - 1.0) > 1e-9:
        corr = 1.0 - total
        return {
            "equity": b.target_equity,
            "bonds": b.target_bonds,
            "cash": max(0.0, b.target_cash + corr),
            "alts": b.target_alts,
        }
    return {"equity": b.target_equity, "bonds": b.target_bonds, "cash": b.target_cash, "alts": b.target_alts}

def target_sleeves(score: int, jurisdiction: str) -> List[Dict]:
    """
    Returns deterministic target sleeves with weights:
    [
      {"class":"equity","subclass":"US","weight":...},
      ...
      {"class":"bonds","subclass":"CoreIG","weight":...},
      {"class":"alts","subclass":"REIT","weight":...},
      {"class":"cash","subclass":"CASH","weight":...}
    ]
    """
    j = jurisdiction.upper()
    bands = build_band_targets(score)
    sleeves: List[Dict] = []

    # Equity
    for sub, frac in EQUITY_SPLIT[j].items():
        sleeves.append({"class":"equity","subclass":sub,"weight": bands["equity"]*frac})
    # Bonds
    for sub, frac in BOND_SPLIT[j].items():
        sleeves.append({"class":"bonds","subclass":sub,"weight": bands["bonds"]*frac})
    # Alts (REITs)
    if bands["alts"] > 0:
        sleeves.append({"class":"alts","subclass":"REIT","weight": bands["alts"]})
    # Cash
    if bands["cash"] > 0:
        sleeves.append({"class":"cash","subclass":"CASH","weight": bands["cash"]})

    # Round, renormalize to 1.0
    rounded = [{**x, "weight": round_to_step(x["weight"])} for x in sleeves]
    s = sum(x["weight"] for x in rounded)
    scaled = [{**x, "weight": (x["weight"]/s) if s>0 else 0.0} for x in rounded]
    residual = 1.0 - sum(x["weight"] for x in scaled)
    # put residual on largest non-cash bucket
    non_cash = [x for x in scaled if x["class"] != "cash"] or scaled
    largest = max(non_cash, key=lambda z: z["weight"])
    largest["weight"] += residual
    return sorted(scaled, key=lambda z: z["weight"], reverse=True)
