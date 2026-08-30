"""
bank.py — Bank Class
======================
Manages a collection of Account objects and handles persistence (loading
from and saving to a JSON file).  Acts as the "service layer" between the
ATM user interface and the individual Account objects.

OOP Concepts Used:
    - Composition: the Bank *has-a* collection of Account objects.
    - Separation of concerns: persistence logic lives here, not in Account.
    - Factory pattern: _seed_sample_data() creates demo accounts.
"""

import json
import os
from account import Account


class Bank:
    """
    Manages all customer accounts and provides persistence via JSON files.

    Attributes:
        accounts   (dict): Maps account_number → Account object.
        _data_file (str):  Path to the JSON file for saving/loading data.
    """

    def __init__(self, data_file: str = None):
        """
        Initialise the Bank.

        If the JSON data file exists, accounts are loaded from it.
        Otherwise, sample accounts are seeded and saved automatically.

        Args:
            data_file: Path to the JSON file. Defaults to 'accounts.json'
                       in the same directory as this script.
        """
        if data_file is None:
            # Store the JSON file alongside the source code
            script_dir = os.path.dirname(os.path.abspath(__file__))
            data_file = os.path.join(script_dir, "accounts.json")

        self._data_file = data_file
        self.accounts: dict[str, Account] = {}

        # Load existing data or seed fresh demo accounts
        if os.path.exists(self._data_file):
            self.load_accounts()
        else:
            self._seed_sample_data()
            self.save_accounts()

    # ================================================================== #
    #  Account Lookup
    # ================================================================== #
    def find_account(self, account_number: str):
        """
        Look up an account by its number.

        Args:
            account_number: The account number string to search for.

        Returns:
            The Account object if found, or None.
        """
        return self.accounts.get(str(account_number))

    # ================================================================== #
    #  Authentication
    # ================================================================== #
    def authenticate(self, account_number: str, pin: str):
        """
        Authenticate a user by account number and PIN.

        Args:
            account_number: The account number to look up.
            pin:            The PIN to verify against the account.

        Returns:
            The Account object if authentication succeeds, or None.
        """
        account = self.find_account(account_number)
        if account is not None and account.verify_pin(pin):
            return account
        return None

    # ================================================================== #
    #  Account Creation
    # ================================================================== #
    def create_account(
        self,
        account_number: str,
        customer_name: str,
        pin: str,
        balance: float = 0.0,
    ) -> Account:
        """
        Register a new account with the bank.

        Args:
            account_number: Unique identifier for the account.
            customer_name:  Full name of the customer.
            pin:            4-digit PIN string.
            balance:        Initial balance (default 0.0).

        Returns:
            The newly created Account object.

        Raises:
            ValueError: If account number already exists, name is empty,
                        or PIN format is invalid.
        """
        acct_num = str(account_number)

        if acct_num in self.accounts:
            raise ValueError(
                f"Account number '{acct_num}' already exists."
            )

        if not customer_name or not customer_name.strip():
            raise ValueError("Customer name cannot be empty.")

        # Account.__init__ validates PIN format and balance
        account = Account(
            account_number=acct_num,
            customer_name=customer_name,
            pin=pin,
            balance=balance,
        )
        self.accounts[acct_num] = account
        return account

    # ================================================================== #
    #  Fund Transfer (orchestrator)
    # ================================================================== #
    def transfer_funds(
        self, sender: Account, receiver_acct_num: str, amount: float
    ) -> tuple:
        """
        Transfer money from one account to another.

        This method orchestrates both the debit (sender) and credit
        (receiver) sides of the transfer within the bank.

        Args:
            sender:            The authenticated sender Account object.
            receiver_acct_num: The destination account number.
            amount:            The amount to transfer.

        Returns:
            A tuple of (sender_txn, receiver_txn) Transaction objects.

        Raises:
            ValueError: If receiver doesn't exist, sender == receiver,
                        amount is invalid, or balance is insufficient.
        """
        receiver_acct_num = str(receiver_acct_num)

        # --- Validate receiver --- #
        if sender.account_number == receiver_acct_num:
            raise ValueError("Cannot transfer to the same account.")

        receiver = self.find_account(receiver_acct_num)
        if receiver is None:
            raise ValueError(
                f"Receiver account '{receiver_acct_num}' does not exist."
            )

        # --- Perform the transfer --- #
        # Debit sender first (this validates amount and balance)
        sender_txn = sender.transfer_out(amount, receiver_acct_num)

        # Credit receiver
        receiver_txn = receiver.transfer_in(amount, sender.account_number)

        return sender_txn, receiver_txn

    # ================================================================== #
    #  Persistence — Load
    # ================================================================== #
    def load_accounts(self):
        """
        Load all accounts from the JSON data file.

        Reads the file, deserialises each account dictionary into an
        Account object, and populates self.accounts.
        """
        try:
            with open(self._data_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.accounts = {}
            for acct_data in data.get("accounts", []):
                account = Account.from_dict(acct_data)
                self.accounts[account.account_number] = account

            print(f"  ✓ Loaded {len(self.accounts)} account(s) from file.")

        except (json.JSONDecodeError, KeyError) as e:
            print(f"  ✗ Error reading data file: {e}")
            print("    Starting with sample accounts instead.")
            self._seed_sample_data()

    # ================================================================== #
    #  Persistence — Save
    # ================================================================== #
    def save_accounts(self):
        """
        Save all accounts to the JSON data file.

        Serialises every Account (including its transaction history)
        and writes the result as formatted JSON.
        """
        data = {
            "accounts": [
                acct.to_dict() for acct in self.accounts.values()
            ]
        }

        try:
            with open(self._data_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except IOError as e:
            print(f"  ✗ Error saving data: {e}")

    # ================================================================== #
    #  Sample Data Seeder
    # ================================================================== #
    def _seed_sample_data(self):
        """
        Populate the bank with three demo accounts.

        Called automatically on first run when no JSON file exists.
        """
        sample_accounts = [
            {
                "account_number": "1001",
                "customer_name": "Rishabh Sharma",
                "pin": "1234",
                "balance": 50_000.00,
            },
            {
                "account_number": "1002",
                "customer_name": "Priya Patel",
                "pin": "5678",
                "balance": 75_000.00,
            },
            {
                "account_number": "1003",
                "customer_name": "Amit Kumar",
                "pin": "4321",
                "balance": 30_000.00,
            },
        ]

        self.accounts = {}
        for info in sample_accounts:
            account = Account(
                account_number=info["account_number"],
                customer_name=info["customer_name"],
                pin=info["pin"],
                balance=info["balance"],
            )
            self.accounts[account.account_number] = account

        print("  ✓ Sample accounts created (first-time setup).")

    # ================================================================== #
    #  Utility
    # ================================================================== #
    def get_all_account_numbers(self) -> list:
        """Return a sorted list of all registered account numbers."""
        return sorted(self.accounts.keys())

    def __str__(self) -> str:
        return f"Bank({len(self.accounts)} accounts)"

    def __repr__(self) -> str:
        return self.__str__()
