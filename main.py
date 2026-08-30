"""
main.py — Entry Point
=======================
This is the file you run to start the ATM application.

How it works:
    1. Creates a Bank object (loads accounts from accounts.json).
    2. Creates an ATM object connected to that Bank.
    3. Starts the ATM's main loop.

Usage:
    python main.py
"""

import sys

# --- Windows console fix ------------------------------------------------- #
# On Windows, the default console encoding (cp1252) can't display Unicode
# characters like ✓, ╔, ║, etc.  Reconfiguring stdout/stderr to UTF-8
# ensures all our box-drawing and status symbols render correctly.
# This is safe on Linux/macOS where UTF-8 is already the default.
if sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        # Python < 3.7 fallback (very unlikely but safe)
        pass

from bank import Bank
from atm import ATM



def main():
    """
    Application entry point.

    Instantiates the Bank (which auto-loads or seeds account data),
    connects it to an ATM instance, and starts the interactive loop.
    """
    print("\n  Initialising ATM system...")

    # Step 1 — Create the Bank (loads data from accounts.json)
    bank = Bank()

    # Step 2 — Create the ATM connected to this Bank
    atm = ATM(bank)

    # Step 3 — Run the ATM (enters the authentication + menu loop)
    atm.run()


# This guard ensures main() only runs when the file is executed directly,
# not when it's imported as a module (a Python best practice).
if __name__ == "__main__":
    main()
