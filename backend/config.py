"""
Global configuration for portfolio allocation
"""
DEFAULT_JURISDICTION = "CA"   # "US" or "CA"

# Equity/bond sleeve composition per jurisdiction (sums to 1.0 inside the sleeve)
EQUITY_SPLIT = {
    "US": {"US": 0.65, "IntlDev": 0.25, "EM": 0.10},
    "CA": {"Canada": 0.20, "US": 0.50, "IntlDev": 0.25, "EM": 0.05},
}

BOND_SPLIT = {
    "US": {"CoreIG": 0.80, "LongDur": 0.10, "TIPS": 0.10},
    "CA": {"CoreIG": 0.90, "LongDur": 0.10},  # add TIPS/real return if you later wire a data source
}

# Rounding for nice pie charts (0.005 = 0.5%)
ALLOCATION_ROUND_STEP = 0.005
