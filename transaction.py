"""
transaction.py — Transaction Data Class
=========================================
Represents a single banking transaction (deposit, withdrawal, transfer, etc.).
Each transaction captures a unique ID, type, amount, timestamp, resulting
balance, and success/failure status.

OOP Concepts Used:
    - Encapsulation: transaction data is bundled into a single object.
    - Class methods: `from_dict()` acts as an alternate constructor.
    - Magic methods: `__str__()` provides a human-readable summary.
"""

import uuid
from datetime import datetime


class Transaction:
    """
    A record of one banking transaction.

    Attributes:
        transaction_id (str):   Unique ID like 'TXN-A3F9B2'.
        transaction_type (str): One of 'Deposit', 'Withdrawal',
                                'Transfer Sent', 'Transfer Received',
                                'PIN Change'.
        amount (float):         Transaction amount (0.0 for PIN changes).
        date_time (str):        ISO-8601 timestamp of when the txn occurred.
        balance_after (float):  Account balance immediately after this txn.
        status (str):           'Success' or 'Failed'.
    """

    # ------------------------------------------------------------------ #
    #  Valid transaction types (used for validation)
    # ------------------------------------------------------------------ #
    VALID_TYPES = {
        "Deposit",
        "Withdrawal",
        "Transfer Sent",
        "Transfer Received",
        "PIN Change",
    }

    def __init__(
        self,
        transaction_type: str,
        amount: float,
        balance_after: float,
        status: str = "Success",
        transaction_id: str = None,
        date_time: str = None,
    ):
        """
        Create a new Transaction.

        Args:
            transaction_type: Type of transaction (see VALID_TYPES).
            amount:           Money involved (use 0.0 for PIN changes).
            balance_after:    Balance snapshot after the transaction.
            status:           'Success' or 'Failed'.
            transaction_id:   (Optional) Provide when loading from file;
                              auto-generated otherwise.
            date_time:        (Optional) Provide when loading from file;
                              auto-generated otherwise.
        """
        # Auto-generate a short, readable transaction ID if not supplied.
        # Format: TXN-<6 hex chars>  e.g. TXN-A3F9B2
        if transaction_id is None:
            short_hex = uuid.uuid4().hex[:6].upper()
            self.transaction_id = f"TXN-{short_hex}"
        else:
            self.transaction_id = transaction_id

        # Validate the transaction type
        if transaction_type not in self.VALID_TYPES:
            raise ValueError(
                f"Invalid transaction type '{transaction_type}'. "
                f"Must be one of {self.VALID_TYPES}."
            )
        self.transaction_type = transaction_type

        self.amount = float(amount)
        self.balance_after = float(balance_after)
        self.status = status

        # Auto-stamp the current date/time if not provided
        if date_time is None:
            self.date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        else:
            self.date_time = date_time

    # ------------------------------------------------------------------ #
    #  Serialisation helpers (for JSON persistence)
    # ------------------------------------------------------------------ #
    def to_dict(self) -> dict:
        """Convert this Transaction to a JSON-safe dictionary."""
        return {
            "transaction_id": self.transaction_id,
            "transaction_type": self.transaction_type,
            "amount": self.amount,
            "date_time": self.date_time,
            "balance_after": self.balance_after,
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Transaction":
        """
        Reconstruct a Transaction from a dictionary (loaded from JSON).

        Args:
            data: Dictionary with keys matching the Transaction attributes.

        Returns:
            A new Transaction instance.
        """
        return cls(
            transaction_type=data["transaction_type"],
            amount=data["amount"],
            balance_after=data["balance_after"],
            status=data.get("status", "Success"),
            transaction_id=data.get("transaction_id"),
            date_time=data.get("date_time"),
        )

    # ------------------------------------------------------------------ #
    #  Human-readable representation
    # ------------------------------------------------------------------ #
    def __str__(self) -> str:
        """
        One-line summary used in statements and history views.
        Example:
            TXN-A3F9B2 | 2026-08-26 01:55:00 | Deposit       | +5000.00 | Bal: 55000.00 | Success
        """
        # Choose a sign prefix based on credit / debit
        if self.transaction_type in ("Deposit", "Transfer Received"):
            sign = "+"
        elif self.transaction_type in ("Withdrawal", "Transfer Sent"):
            sign = "-"
        else:
            sign = " "  # PIN Change

        amount_str = f"{sign}{self.amount:>10.2f}"

        return (
            f"{self.transaction_id} | "
            f"{self.date_time} | "
            f"{self.transaction_type:<18s} | "
            f"{amount_str} | "
            f"Bal: {self.balance_after:>10.2f} | "
            f"{self.status}"
        )

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return (
            f"Transaction(id={self.transaction_id!r}, "
            f"type={self.transaction_type!r}, "
            f"amount={self.amount}, "
            f"status={self.status!r})"
        )
