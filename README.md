# 🏧 Object-Oriented ATM Management System

A complete console-based banking/ATM application built in **Python** using
**Object-Oriented Programming**. It simulates real ATM operations with proper
encapsulation, input validation, exception handling, and JSON-based data
persistence.

---

## 📁 Project Structure

```
ATM project/
├── account.py          # Account class — encapsulated customer data
├── transaction.py      # Transaction class — individual transaction records
├── bank.py             # Bank class — manages accounts & JSON persistence
├── atm.py              # ATM class — console user interface
├── main.py             # Entry point — run this file
├── accounts.json       # Auto-generated data store (created on first run)
└── README.md           # This file
```

---

## 🚀 How to Run in VS Code

### Prerequisites

- **Python 3.8+** installed ([download](https://www.python.org/downloads/))
- **No external packages required** — uses only Python standard library

### Steps

1. **Open the project folder** in VS Code:
   - `File → Open Folder → select "ATM project"`

2. **Open a terminal** in VS Code:
   - `Terminal → New Terminal` (or press `` Ctrl+` ``)

3. **Run the program**:
   ```bash
   python main.py
   ```

4. **On first run**, three sample accounts are created automatically.

---

## 👤 Sample Account Credentials

| Account # | Customer Name   | PIN    | Initial Balance |
|-----------|-----------------|--------|-----------------|
| `1001`    | Rishabh Sharma  | `1234` | ₹50,000.00      |
| `1002`    | Priya Patel     | `5678` | ₹75,000.00      |
| `1003`    | Amit Kumar      | `4321` | ₹30,000.00      |

---

## 🧪 Example Test Cases

### Test 1 — Successful Login & Balance Enquiry

```
Input:
  Account Number: 1001
  PIN: 1234
  Menu Choice: 1 (Balance Enquiry)

Expected Output:
  ✓ Welcome, Rishabh Sharma!
  Account:  1001
  Name:     Rishabh Sharma
  Balance:  ₹50,000.00
```

### Test 2 — Cash Deposit

```
Input:
  (Logged in as 1001)
  Menu Choice: 2 (Cash Deposit)
  Amount: 5000

Expected Output:
  ✓ Deposit successful!
    Amount deposited: ₹5,000.00
    New balance:      ₹55,000.00
    Transaction ID:   TXN-XXXXXX
```

### Test 3 — Cash Withdrawal

```
Input:
  (Logged in as 1001, balance ₹55,000)
  Menu Choice: 3 (Cash Withdrawal)
  Amount: 2000

Expected Output:
  ✓ Withdrawal successful!
    Amount withdrawn:  ₹2,000.00
    Remaining balance: ₹53,000.00
    Transaction ID:    TXN-XXXXXX
```

### Test 4 — Fund Transfer

```
Input:
  (Logged in as 1001)
  Menu Choice: 4 (Fund Transfer)
  Receiver Account: 1002
  Amount: 3000

Expected Output:
  ✓ Transfer successful!
    Amount sent:       ₹3,000.00
    To account:        1002
    Your new balance:  ₹50,000.00
    Transaction ID:    TXN-XXXXXX
```

### Test 5 — Insufficient Balance

```
Input:
  (Logged in as 1003, balance ₹30,000)
  Menu Choice: 3 (Cash Withdrawal)
  Amount: 50000

Expected Output:
  ✗ Withdrawal failed: Insufficient balance. Available: ₹30,000.00
```

### Test 6 — Wrong PIN (3 Attempts → Block)

```
Input:
  Account Number: 1001
  PIN: 0000 (attempt 1)
  PIN: 1111 (attempt 2)
  PIN: 9999 (attempt 3)

Expected Output:
  ✗ Incorrect PIN. 2 attempt(s) remaining.
  ✗ Incorrect PIN. 1 attempt(s) remaining.

  ╔══════════════════════════════════════════════╗
  ║  ACCESS BLOCKED — Too many failed attempts  ║
  ║  Please contact your bank for assistance.   ║
  ╚══════════════════════════════════════════════╝
```

### Test 7 — Transfer to Same Account

```
Input:
  (Logged in as 1001)
  Menu Choice: 4 (Fund Transfer)
  Receiver Account: 1001

Expected Output:
  ✗ Transfer failed: Cannot transfer to the same account.
```

### Test 8 — Non-Numeric Input

```
Input:
  Menu Choice: 2 (Cash Deposit)
  Amount: abc

Expected Output:
  ✗ Deposit failed: could not convert string to float: 'abc'
```

### Test 9 — Negative Amount

```
Input:
  Menu Choice: 2 (Cash Deposit)
  Amount: -500

Expected Output:
  ✗ Deposit failed: Deposit amount must be greater than zero.
```

### Test 10 — PIN Change

```
Input:
  (Logged in as 1001)
  Menu Choice: 7 (Change PIN)
  Current PIN: 1234
  New PIN: 9999
  Confirm PIN: 9999

Expected Output:
  ✓ PIN changed successfully!
    Transaction ID: TXN-XXXXXX
```

### Test 11 — Data Persistence

```
Steps:
  1. Login to 1001, deposit ₹5,000, logout.
  2. Close the program.
  3. Run `python main.py` again.
  4. Login to 1001, check balance.

Expected: Balance reflects the ₹5,000 deposit from step 1.
```

---

## 📖 OOP Concepts Applied

### 1. Classes & Objects

The system is built from four classes, each representing a real-world entity:

| Class         | Represents              |
|---------------|-------------------------|
| `Transaction` | A single banking event  |
| `Account`     | A customer's bank account |
| `Bank`        | The bank managing all accounts |
| `ATM`         | The ATM machine interface |

Each class is instantiated as an **object** at runtime.

### 2. Encapsulation

Sensitive data is hidden behind **private attributes** (prefixed with `_`):

```python
class Account:
    self._pin = pin               # Private — not directly accessible
    self._balance = balance       # Private — read via check_balance()
    self._transaction_history = []  # Private — read via get_mini_statement()
```

The PIN can only be verified (not read) via `verify_pin()`, and the balance can
only be changed through validated methods like `deposit()` and `withdraw()`.

### 3. Composition

Objects contain other objects to model real relationships:

- A **Bank** *has-a* collection of **Account** objects.
- An **Account** *has-a* list of **Transaction** objects.
- An **ATM** *has-a* reference to a **Bank** object.

### 4. Separation of Concerns

Each class has a single, focused responsibility:

| Class         | Responsibility                              |
|---------------|---------------------------------------------|
| `Transaction` | Store transaction data                      |
| `Account`     | Manage one customer's data and rules        |
| `Bank`        | Coordinate accounts and persist data        |
| `ATM`         | Handle all user interaction (console I/O)   |

### 5. Exception Handling

Every user input is wrapped in `try/except` blocks so invalid input never
crashes the program:

```python
try:
    amount = float(input("Enter amount: "))
    txn = account.deposit(amount)
except ValueError as e:
    print(f"Error: {e}")
```

### 6. Class Methods (Alternate Constructors)

`Transaction.from_dict()` and `Account.from_dict()` are **class methods**
that reconstruct objects from dictionary data (loaded from JSON):

```python
@classmethod
def from_dict(cls, data: dict) -> "Transaction":
    return cls(...)
```

### 7. Magic Methods

`__str__()` provides human-readable output; `__repr__()` provides
developer-friendly debugging output:

```python
>>> print(account)
Account(1001) — Rishabh Sharma — Balance: ₹50,000.00
```

---

## 💡 Suggestions for Future Improvements

| Feature                     | Description                                              |
|-----------------------------|----------------------------------------------------------|
| **GUI Interface**           | Use Tkinter or PyQt to build a graphical ATM interface   |
| **Database Storage**        | Replace JSON with SQLite for better data management      |
| **Password Hashing**        | Hash PINs using `hashlib` instead of storing plaintext   |
| **Multi-Currency Support**  | Support USD, EUR, GBP with conversion rates              |
| **Account Creation via UI** | Let users create new accounts from the ATM interface     |
| **Receipt Generation**      | Generate a text/PDF receipt after each transaction       |
| **Interest Calculation**    | Add savings account interest based on balance            |
| **Admin Dashboard**         | Separate admin login to view all accounts and reports    |
| **Email/SMS Notifications** | Send alerts for transactions using `smtplib`             |
| **Unit Tests**              | Add `pytest` test suite for automated regression testing |
| **Logging**                 | Use Python's `logging` module for audit trails           |
| **API Layer**               | Wrap the Bank class in a Flask/FastAPI REST API           |

---

## 📜 License

This project is for **educational purposes only**. Built as a demonstration
of Object-Oriented Programming in Python.

---

*Developed as part of the ATM Management System project.*
