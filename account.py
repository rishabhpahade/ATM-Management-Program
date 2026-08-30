"""
account.py — Account Class
============================
Stores and manages a single customer's banking information.
Encapsulates sensitive data (PIN, balance) behind validated methods so they
can never be modified directly from outside the class.

OOP Concepts Used:
    - Encapsulation: _pin, _balance, and _transaction_history are private.
    - Validated mutators: deposit(), withdraw(), change_pin() enforce rules.
    - Composition: an Account *contains* a list of Transaction objects.
"""

import re
from datetime import datetime, timedelta
from transaction import Transaction
from utils import CURRENCY


class Account:
    """
    Represents a single bank account.

    Public attributes:
        account_number (str): Unique identifier for the account.
        customer_name  (str): Name of the account holder.

    Private attributes (access only via methods):
        _pin                 (str):  4-digit PIN string.
        _balance             (float): Current account balance.
        _transaction_history (list):  List of Transaction objects.
    """

    # ------------------------------------------------------------------ #
    #  Class-level constants
    # ------------------------------------------------------------------ #
    DAILY_WITHDRAWAL_LIMIT = 25_000.00   # Maximum withdrawal per day
    PIN_PATTERN = re.compile(r"^\d{4}$")  # Exactly 4 digits

    def __init__(
        self,
        account_number: str,
        customer_name: str,
        pin: str,
        balance: float = 0.0,
        transaction_history: list = None,
    ):
        """
        Initialise a new Account.

        Args:
            account_number:      Unique account identifier string.
            customer_name:       Full name of the customer.
            pin:                 4-digit PIN as a string.
            balance:             Starting balance (default 0.0).
            transaction_history: Pre-existing transactions (when loading
                                 from JSON). Default is an empty list.

        Raises:
            ValueError: If pin format is invalid or name is empty.
        """
        # --- Validate inputs --- #
        if not customer_name or not customer_name.strip():
            raise ValueError("Customer name cannot be empty.")

        if not self.PIN_PATTERN.match(pin):
            raise ValueError("PIN must be exactly 4 digits.")

        if balance < 0:
            raise ValueError("Initial balance cannot be negative.")

        # --- Assign attributes --- #
        self.account_number = str(account_number)
        self.customer_name = customer_name.strip()

        # Private attributes — the underscore prefix signals "do not touch"
        self._pin = pin
        self._balance = float(balance)
        self._transaction_history = transaction_history if transaction_history else []

    # ================================================================== #
    #  PIN Verification
    # ================================================================== #
    def verify_pin(self, pin: str) -> bool:
        """
        Check whether the supplied PIN matches the stored PIN.

        Args:
            pin: The PIN string to verify.

        Returns:
            True if the PIN matches, False otherwise.
        """
        return self._pin == str(pin)

    # ================================================================== #
    #  Balance Enquiry
    # ================================================================== #
    def check_balance(self) -> float:
        """
        Read-only accessor for the current balance.

        Returns:
            The current account balance as a float.
        """
        return self._balance

    # ================================================================== #
    #  Deposit
    # ================================================================== #
    def deposit(self, amount: float) -> Transaction:
        """
        Add money to the account.

        Args:
            amount: The amount to deposit (must be > 0).

        Returns:
            A Transaction object recording this deposit.

        Raises:
            ValueError: If amount is not positive.
        """
        amount = float(amount)
        if amount <= 0:
            raise ValueError("Deposit amount must be greater than zero.")

        self._balance += amount

        txn = Transaction(
            transaction_type="Deposit",
            amount=amount,
            balance_after=self._balance,
            status="Success",
        )
        self._transaction_history.append(txn)
        return txn

    # ================================================================== #
    #  Withdrawal
    # ================================================================== #
    def withdraw(self, amount: float) -> Transaction:
        """
        Withdraw money from the account.

        Validates:
            - Amount is positive.
            - Sufficient balance exists.
            - Daily withdrawal limit is not exceeded.

        Args:
            amount: The amount to withdraw.

        Returns:
            A Transaction object recording this withdrawal.

        Raises:
            ValueError: If any validation rule is violated.
        """
        amount = float(amount)

        if amount <= 0:
            raise ValueError("Withdrawal amount must be greater than zero.")

        if amount > self._balance:
            raise ValueError(
                f"Insufficient balance. Available: {CURRENCY}{self._balance:,.2f}"
            )

        # --- Daily withdrawal limit check --- #
        today_withdrawn = self._get_today_withdrawn()
        if today_withdrawn + amount > self.DAILY_WITHDRAWAL_LIMIT:
            remaining = max(0, self.DAILY_WITHDRAWAL_LIMIT - today_withdrawn)
            raise ValueError(
                f"Daily withdrawal limit ({CURRENCY}{self.DAILY_WITHDRAWAL_LIMIT:,.2f}) "
                f"would be exceeded. You can still withdraw up to "
                f"{CURRENCY}{remaining:,.2f} today."
            )

        self._balance -= amount

        txn = Transaction(
            transaction_type="Withdrawal",
            amount=amount,
            balance_after=self._balance,
            status="Success",
        )
        self._transaction_history.append(txn)
        return txn

    # ================================================================== #
    #  Fund Transfer — outgoing (debit side)
    # ================================================================== #
    def transfer_out(self, amount: float, receiver_acct_num: str) -> Transaction:
        """
        Debit this account for a fund transfer to another account.

        Args:
            amount:            The amount to send.
            receiver_acct_num: The destination account number (for record).

        Returns:
            A Transaction object for the debit side.

        Raises:
            ValueError: If amount is invalid or balance insufficient.
        """
        amount = float(amount)

        if amount <= 0:
            raise ValueError("Transfer amount must be greater than zero.")

        if amount > self._balance:
            raise ValueError(
                f"Insufficient balance for transfer. "
                f"Available: {CURRENCY}{self._balance:,.2f}"
            )

        # Check daily limit (transfers count towards withdrawals)
        today_withdrawn = self._get_today_withdrawn()
        if today_withdrawn + amount > self.DAILY_WITHDRAWAL_LIMIT:
            remaining = max(0, self.DAILY_WITHDRAWAL_LIMIT - today_withdrawn)
            raise ValueError(
                f"Daily withdrawal limit ({CURRENCY}{self.DAILY_WITHDRAWAL_LIMIT:,.2f}) "
                f"would be exceeded. Remaining today: {CURRENCY}{remaining:,.2f}"
            )

        self._balance -= amount

        txn = Transaction(
            transaction_type="Transfer Sent",
            amount=amount,
            balance_after=self._balance,
            status=f"Success → Acct {receiver_acct_num}",
        )
        self._transaction_history.append(txn)
        return txn

    # ================================================================== #
    #  Fund Transfer — incoming (credit side)
    # ================================================================== #
    def transfer_in(self, amount: float, sender_acct_num: str) -> Transaction:
        """
        Credit this account when receiving a fund transfer.

        Args:
            amount:           The amount received.
            sender_acct_num:  The source account number (for record).

        Returns:
            A Transaction object for the credit side.
        """
        amount = float(amount)
        self._balance += amount

        txn = Transaction(
            transaction_type="Transfer Received",
            amount=amount,
            balance_after=self._balance,
            status=f"Success ← Acct {sender_acct_num}",
        )
        self._transaction_history.append(txn)
        return txn

    # ================================================================== #
    #  PIN Change
    # ================================================================== #
    def change_pin(self, old_pin: str, new_pin: str) -> Transaction:
        """
        Change the account PIN after verifying the old PIN.

        Args:
            old_pin: The current PIN (must match stored PIN).
            new_pin: The desired new PIN (must be exactly 4 digits).

        Returns:
            A Transaction recording the PIN change.

        Raises:
            ValueError: If old PIN doesn't match or new PIN format is bad.
        """
        if not self.verify_pin(old_pin):
            raise ValueError("Current PIN is incorrect.")

        if not self.PIN_PATTERN.match(str(new_pin)):
            raise ValueError("New PIN must be exactly 4 digits.")

        if old_pin == new_pin:
            raise ValueError("New PIN must be different from the current PIN.")

        self._pin = str(new_pin)

        txn = Transaction(
            transaction_type="PIN Change",
            amount=0.0,
            balance_after=self._balance,
            status="Success",
        )
        self._transaction_history.append(txn)
        return txn

    # ================================================================== #
    #  Statement / History
    # ================================================================== #
    def get_mini_statement(self) -> list:
        """
        Return the 5 most recent transactions.

        Returns:
            A list of up to 5 Transaction objects (newest first).
        """
        return list(reversed(self._transaction_history[-5:]))

    def get_full_history(self) -> list:
        """
        Return the complete transaction history.

        Returns:
            A list of all Transaction objects (newest first).
        """
        return list(reversed(self._transaction_history))

    # ================================================================== #
    #  Serialisation (JSON)
    # ================================================================== #
    def to_dict(self) -> dict:
        """Convert this Account (including transactions) to a dictionary."""
        return {
            "account_number": self.account_number,
            "customer_name": self.customer_name,
            "pin": self._pin,
            "balance": self._balance,
            "transaction_history": [
                txn.to_dict() for txn in self._transaction_history
            ],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Account":
        """
        Reconstruct an Account from a dictionary (loaded from JSON).

        Args:
            data: Dictionary with keys matching Account attributes.

        Returns:
            A new Account instance with its full transaction history.
        """
        # Rebuild each Transaction object from its dict form
        history = [
            Transaction.from_dict(t) for t in data.get("transaction_history", [])
        ]

        return cls(
            account_number=data["account_number"],
            customer_name=data["customer_name"],
            pin=data["pin"],
            balance=data["balance"],
            transaction_history=history,
        )

    # ================================================================== #
    #  Internal helpers
    # ================================================================== #
    def _get_today_withdrawn(self) -> float:
        """
        Calculate total amount withdrawn/transferred-out today.

        Used internally to enforce the daily withdrawal limit.

        Returns:
            Sum of today's successful Withdrawal + Transfer Sent amounts.
        """
        today_str = datetime.now().strftime("%Y-%m-%d")
        total = 0.0
        for txn in self._transaction_history:
            if txn.transaction_type in ("Withdrawal", "Transfer Sent"):
                # Compare only the date portion of the timestamp
                if txn.date_time.startswith(today_str) and "Success" in txn.status:
                    total += txn.amount
        return total

    # ================================================================== #
    #  String representation
    # ================================================================== #
    def __str__(self) -> str:
        """User-friendly summary of the account."""
        return (
            f"Account({self.account_number}) — "
            f"{self.customer_name} — "
            f"Balance: {CURRENCY}{self._balance:,.2f}"
        )

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return (
            f"Account(number={self.account_number!r}, "
            f"name={self.customer_name!r}, "
            f"balance={self._balance})"
        )
