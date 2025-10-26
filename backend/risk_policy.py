from dataclasses import dataclass

@dataclass(frozen=True)
class RiskBand:
    title: str
    description: str
    score_range: range
    # Deterministic targets (sum = 1.0)
    target_equity: float
    target_bonds: float
    target_cash: float
    target_alts: float

RISK_BANDS = [
    RiskBand("Very Conservative", "Capital preservation first; minimal volatility.",
             range(1, 3), target_equity=0.20, target_bonds=0.70, target_cash=0.08, target_alts=0.02),
    RiskBand("Conservative", "Income-oriented with limited drawdowns.",
             range(3, 4), target_equity=0.30, target_bonds=0.60, target_cash=0.07, target_alts=0.03),
    RiskBand("Moderately Conservative", "Balanced tilt to bonds; controlled equity risk.",
             range(4, 6), target_equity=0.45, target_bonds=0.47, target_cash=0.05, target_alts=0.03),
    RiskBand("Moderate", "Balanced growth & income; diversified risk.",
             range(6, 7), target_equity=0.60, target_bonds=0.33, target_cash=0.04, target_alts=0.03),
    RiskBand("Moderately Aggressive", "Growth-tilted with meaningful drawdown risk.",
             range(7, 9), target_equity=0.75, target_bonds=0.20, target_cash=0.03, target_alts=0.02),
    RiskBand("Aggressive", "Maximize long-run growth; high volatility acceptable.",
             range(9, 11), target_equity=0.90, target_bonds=0.07, target_cash=0.02, target_alts=0.01),
]

def band_for_score(score: int) -> RiskBand:
    """Get the risk band for a given risk score (1-10)"""
    for b in RISK_BANDS:
        if score in b.score_range:
            return b
    return RISK_BANDS[-1]  # Default to most aggressive if score > 10
