"""
atm.py — ATM Class (Console Interface)
========================================
Controls the complete ATM workflow: authentication, menu display, and all
banking operations.  ALL console I/O lives in this file — no other class
prints to stdout.

OOP Concepts Used:
    - Separation of concerns: UI logic is isolated from business logic.
    - Delegation: ATM delegates data operations to Bank and Account.
    - Exception handling: every input is wrapped so the program never crashes.
"""

from bank import Bank
from utils import CURRENCY


class ATM:
    """
    Console-based ATM user interface.

    Attributes:
        bank            (Bank):    The bank that this ATM is connected to.
        current_account (Account): The currently logged-in account (or None).
        MAX_PIN_ATTEMPTS (int):    Maximum wrong PIN tries before blocking.
    """

    MAX_PIN_ATTEMPTS = 3

    def __init__(self, bank: Bank):
        """
        Initialise the ATM with a reference to the Bank.

        Args:
            bank: The Bank object containing all accounts.
        """
        self.bank = bank
        self.current_account = None

    # ================================================================== #
    #  Main Loop
    # ================================================================== #
    def run(self):
        """
        Start the ATM application.

        Loops between authentication and the main menu until the user
        chooses to exit the application entirely.
        """
        self._print_welcome_banner()

        while True:
            try:
                # --- Authentication phase --- #
                authenticated = self._authenticate_user()
                if not authenticated:
                    # User chose to exit from the login screen
                    break

                # --- Main menu phase --- #
                self._main_menu_loop()

            except KeyboardInterrupt:
                # Handle Ctrl+C gracefully
                print("\n\n  ⚠  Session interrupted. Saving data...")
                self.bank.save_accounts()
                print("  ✓ Data saved. Goodbye!\n")
                break

        self._print_exit_banner()

    # ================================================================== #
    #  Authentication
    # ================================================================== #
    def _authenticate_user(self) -> bool:
        """
        Prompt for account number and PIN.

        Allows up to MAX_PIN_ATTEMPTS wrong PIN entries before temporarily
        blocking access for that account.

        Returns:
            True if authentication succeeded, False if the user wants to
            exit the application.
        """
        self._print_section_header("USER AUTHENTICATION")

        while True:
            # --- Get account number --- #
            acct_num = input("  Enter Account Number (or 'exit' to quit): ").strip()

            if acct_num.lower() == "exit":
                return False

            if not acct_num:
                print("  ✗ Account number cannot be empty.\n")
                continue

            # Check if account exists
            account = self.bank.find_account(acct_num)
            if account is None:
                print(f"  ✗ Account '{acct_num}' not found. Please try again.\n")
                continue

            # --- Get PIN (up to 3 attempts) --- #
            attempts = 0
            while attempts < self.MAX_PIN_ATTEMPTS:
                pin = input(f"  Enter PIN (attempt {attempts + 1}/{self.MAX_PIN_ATTEMPTS}): ").strip()

                if self.bank.authenticate(acct_num, pin):
                    self.current_account = account
                    print(f"\n  ✓ Welcome, {account.customer_name}!")
                    print(f"    Account: {account.account_number}")
                    return True
                else:
                    attempts += 1
                    remaining = self.MAX_PIN_ATTEMPTS - attempts
                    if remaining > 0:
                        print(f"  ✗ Incorrect PIN. {remaining} attempt(s) remaining.\n")
                    else:
                        print("\n  ╔══════════════════════════════════════════════╗")
                        print("  ║  ACCESS BLOCKED — Too many failed attempts  ║")
                        print("  ║  Please contact your bank for assistance.   ║")
                        print("  ╚══════════════════════════════════════════════╝\n")

            # After 3 failures, loop back to ask for account number again
            continue

    # ================================================================== #
    #  Main Menu
    # ================================================================== #
    def _main_menu_loop(self):
        """
        Display the main menu and process user selections until logout.
        """
        while True:
            self._display_menu()
            choice = input("  Enter your choice (1-8): ").strip()

            if choice == "1":
                self._process_balance_enquiry()
            elif choice == "2":
                self._process_deposit()
            elif choice == "3":
                self._process_withdrawal()
            elif choice == "4":
                self._process_transfer()
            elif choice == "5":
                self._display_mini_statement()
            elif choice == "6":
                self._display_full_history()
            elif choice == "7":
                self._process_pin_change()
            elif choice == "8":
                self._logout()
                break
            else:
                print("\n  ✗ Invalid choice. Please enter a number from 1 to 8.\n")

    def _display_menu(self):
        """Print the main operations menu."""
        name = self.current_account.customer_name
        acct = self.current_account.account_number
        print()
        print("  ╔══════════════════════════════════════════════╗")
        print(f"  ║  ATM MAIN MENU — {name:<27s} ║")
        print(f"  ║  Account: {acct:<35s}║")
        print("  ╠══════════════════════════════════════════════╣")
        print("  ║  1.  Balance Enquiry                        ║")
        print("  ║  2.  Cash Deposit                           ║")
        print("  ║  3.  Cash Withdrawal                        ║")
        print("  ║  4.  Fund Transfer                          ║")
        print("  ║  5.  Mini Statement (last 5 transactions)   ║")
        print("  ║  6.  Full Transaction History               ║")
        print("  ║  7.  Change PIN                             ║")
        print("  ║  8.  Logout                                 ║")
        print("  ╚══════════════════════════════════════════════╝")

    # ================================================================== #
    #  1. Balance Enquiry
    # ================================================================== #
    def _process_balance_enquiry(self):
        """Display the current account balance."""
        self._print_section_header("BALANCE ENQUIRY")
        balance = self.current_account.check_balance()
        print(f"  Account:  {self.current_account.account_number}")
        print(f"  Name:     {self.current_account.customer_name}")
        print(f"  Balance:  {CURRENCY}{balance:,.2f}")
        self._pause()

    # ================================================================== #
    #  2. Cash Deposit
    # ================================================================== #
    def _process_deposit(self):
        """Prompt for an amount and deposit it into the current account."""
        self._print_section_header("CASH DEPOSIT")

        try:
            amount_str = input(f"  Enter deposit amount: {CURRENCY}").strip()
            amount = float(amount_str)

            txn = self.current_account.deposit(amount)
            self.bank.save_accounts()

            print(f"\n  ✓ Deposit successful!")
            print(f"    Amount deposited: {CURRENCY}{txn.amount:,.2f}")
            print(f"    New balance:      {CURRENCY}{txn.balance_after:,.2f}")
            print(f"    Transaction ID:   {txn.transaction_id}")

        except ValueError as e:
            print(f"\n  ✗ Deposit failed: {e}")

        self._pause()

    # ================================================================== #
    #  3. Cash Withdrawal
    # ================================================================== #
    def _process_withdrawal(self):
        """Prompt for an amount and withdraw it from the current account."""
        self._print_section_header("CASH WITHDRAWAL")

        balance = self.current_account.check_balance()
        print(f"  Available balance: {CURRENCY}{balance:,.2f}")

        try:
            amount_str = input(f"  Enter withdrawal amount: {CURRENCY}").strip()
            amount = float(amount_str)

            txn = self.current_account.withdraw(amount)
            self.bank.save_accounts()

            print(f"\n  ✓ Withdrawal successful!")
            print(f"    Amount withdrawn:  {CURRENCY}{txn.amount:,.2f}")
            print(f"    Remaining balance: {CURRENCY}{txn.balance_after:,.2f}")
            print(f"    Transaction ID:    {txn.transaction_id}")

        except ValueError as e:
            print(f"\n  ✗ Withdrawal failed: {e}")

        self._pause()

    # ================================================================== #
    #  4. Fund Transfer
    # ================================================================== #
    def _process_transfer(self):
        """Prompt for receiver account and amount, then transfer funds."""
        self._print_section_header("FUND TRANSFER")

        balance = self.current_account.check_balance()
        print(f"  Your balance: {CURRENCY}{balance:,.2f}")

        try:
            receiver_num = input("  Enter receiver account number: ").strip()

            if not receiver_num:
                print("\n  ✗ Receiver account number cannot be empty.")
                self._pause()
                return

            amount_str = input(f"  Enter transfer amount: {CURRENCY}").strip()
            amount = float(amount_str)

            sender_txn, receiver_txn = self.bank.transfer_funds(
                sender=self.current_account,
                receiver_acct_num=receiver_num,
                amount=amount,
            )
            self.bank.save_accounts()

            print(f"\n  ✓ Transfer successful!")
            print(f"    Amount sent:       {CURRENCY}{sender_txn.amount:,.2f}")
            print(f"    To account:        {receiver_num}")
            print(f"    Your new balance:  {CURRENCY}{sender_txn.balance_after:,.2f}")
            print(f"    Transaction ID:    {sender_txn.transaction_id}")

        except ValueError as e:
            print(f"\n  ✗ Transfer failed: {e}")

        self._pause()

    # ================================================================== #
    #  5. Mini Statement
    # ================================================================== #
    def _display_mini_statement(self):
        """Show the 5 most recent transactions."""
        self._print_section_header("MINI STATEMENT (Last 5 Transactions)")

        transactions = self.current_account.get_mini_statement()

        if not transactions:
            print("  No transactions yet.")
        else:
            self._print_transaction_table(transactions)

        print(f"\n  Current Balance: {CURRENCY}{self.current_account.check_balance():,.2f}")
        self._pause()

    # ================================================================== #
    #  6. Full Transaction History
    # ================================================================== #
    def _display_full_history(self):
        """Show the complete transaction history."""
        self._print_section_header("FULL TRANSACTION HISTORY")

        transactions = self.current_account.get_full_history()

        if not transactions:
            print("  No transactions yet.")
        else:
            print(f"  Total transactions: {len(transactions)}\n")
            self._print_transaction_table(transactions)

        print(f"\n  Current Balance: {CURRENCY}{self.current_account.check_balance():,.2f}")
        self._pause()

    # ================================================================== #
    #  7. Change PIN
    # ================================================================== #
    def _process_pin_change(self):
        """Prompt for old and new PIN, then change it."""
        self._print_section_header("CHANGE PIN")

        try:
            old_pin = input("  Enter current PIN: ").strip()
            new_pin = input("  Enter new 4-digit PIN: ").strip()
            confirm_pin = input("  Confirm new PIN: ").strip()

            if new_pin != confirm_pin:
                print("\n  ✗ PINs do not match. PIN change cancelled.")
                self._pause()
                return

            txn = self.current_account.change_pin(old_pin, new_pin)
            self.bank.save_accounts()

            print(f"\n  ✓ PIN changed successfully!")
            print(f"    Transaction ID: {txn.transaction_id}")

        except ValueError as e:
            print(f"\n  ✗ PIN change failed: {e}")

        self._pause()

    # ================================================================== #
    #  8. Logout
    # ================================================================== #
    def _logout(self):
        """Save data and log out the current user."""
        self.bank.save_accounts()
        name = self.current_account.customer_name
        self.current_account = None

        print()
        print("  ╔══════════════════════════════════════════════╗")
        print(f"  ║  Goodbye, {name + '!':<35s}║")
        print("  ║  Your session has been securely closed.     ║")
        print("  ║  Data saved successfully.                   ║")
        print("  ╚══════════════════════════════════════════════╝")
        print()

    # ================================================================== #
    #  Display Helpers
    # ================================================================== #
    def _print_welcome_banner(self):
        """Print the ATM welcome banner when the program starts."""
        print()
        print("  ╔══════════════════════════════════════════════╗")
        print("  ║                                              ║")
        print("  ║      ██████╗  █████╗ ███╗   ██╗██╗  ██╗     ║")
        print("  ║      ██╔══██╗██╔══██╗████╗  ██║██║ ██╔╝     ║")
        print("  ║      ██████╔╝███████║██╔██╗ ██║█████╔╝      ║")
        print("  ║      ██╔══██╗██╔══██║██║╚██╗██║██╔═██╗      ║")
        print("  ║      ██████╔╝██║  ██║██║ ╚████║██║  ██╗     ║")
        print("  ║      ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝     ║")
        print("  ║                                              ║")
        print("  ║       ATM MANAGEMENT SYSTEM  v1.0            ║")
        print("  ║       Secure • Fast • Reliable               ║")
        print("  ║                                              ║")
        print("  ╚══════════════════════════════════════════════╝")
        print()

    def _print_exit_banner(self):
        """Print a farewell message when the program exits."""
        print()
        print("  ╔══════════════════════════════════════════════╗")
        print("  ║   Thank you for using our ATM services!     ║")
        print("  ║   Have a great day! 😊                       ║")
        print("  ╚══════════════════════════════════════════════╝")
        print()

    def _print_section_header(self, title: str):
        """Print a styled section header."""
        print()
        print(f"  ┌── {title} " + "─" * max(0, 40 - len(title)) + "┐")

    def _print_transaction_table(self, transactions: list):
        """
        Print a formatted table of transactions.

        Args:
            transactions: List of Transaction objects to display.
        """
        # Header
        print(f"  {'ID':<12s} │ {'Date & Time':<19s} │ {'Type':<18s} │ {'Amount':>12s} │ {'Balance':>12s} │ Status")
        print(f"  {'─' * 12}─┼─{'─' * 19}─┼─{'─' * 18}─┼─{'─' * 12}─┼─{'─' * 12}─┼─{'─' * 20}")

        for txn in transactions:
            # Determine the sign for display
            if txn.transaction_type in ("Deposit", "Transfer Received"):
                sign = "+"
            elif txn.transaction_type in ("Withdrawal", "Transfer Sent"):
                sign = "-"
            else:
                sign = " "

            amount_display = f"{sign}{CURRENCY}{txn.amount:,.2f}"

            print(
                f"  {txn.transaction_id:<12s} │ "
                f"{txn.date_time:<19s} │ "
                f"{txn.transaction_type:<18s} │ "
                f"{amount_display:>12s} │ "
                f"{CURRENCY}{txn.balance_after:>10,.2f} │ "
                f"{txn.status}"
            )

    def _pause(self):
        """Wait for the user to press Enter before returning to the menu."""
        input("\n  Press Enter to continue...")
