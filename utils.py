"""
utils.py — Shared Utility Functions
=====================================
Small helpers shared across the ATM application.

Currently provides:
    - CURRENCY: a currency symbol string ('₹' on UTF-8 terminals, 'Rs.' on
      Windows consoles that don't support the Rupee sign).
"""

import sys


def _detect_currency_symbol() -> str:
    """
    Return '₹' if the console encoding supports it, otherwise 'Rs.'.

    Windows' default cp1252 encoding cannot render the ₹ character, so
    we fall back to the ASCII-safe 'Rs.' prefix.
    """
    encoding = getattr(sys.stdout, "encoding", "") or ""
    try:
        "₹".encode(encoding)
        return "₹"
    except (UnicodeEncodeError, LookupError):
        return "Rs."


# Module-level constant — import this wherever you need a currency prefix.
CURRENCY = _detect_currency_symbol()
