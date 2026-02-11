import csv
from pathlib import Path
from datetime import datetime

DATA_FILE = Path("data/expenses.csv")

def prompt_date() -> str:
    """Prompt the user for a date and validate the input, default to today if left blank."""
    raw = input("Enter date (YYYY-MM-DD) or press Enter for today: ").strip()
    if raw == "":
        return datetime.today().strftime("%Y-%m-%d")
    try:
        datetime.strptime(raw, "%Y-%m-%d")
        return raw
    except ValueError:
        print("Invalid date format. Please enter in YYYY-MM-DD format.")
        return prompt_date()
    
def prompt_amount() -> float:
    """Prompt the user for an amount and validate the input."""
    raw = input("Enter amount: ").strip()
    try:
        return float(raw)
    except ValueError:
        print("Invalid amount. Please enter a numeric value.")
    if float(raw) <= 0:
        raise ValueError("Amount must be greater than zero.")
    return round(float(raw), 2)

def prompt_category() -> str:
    """Prompt the user for a category and validate the input."""
    raw = input("Enter category: ").strip()
    if not raw:
        raise ValueError("Category cannot be empty.")
    return raw

def prompt_description() -> str:
    """Prompt the user for a description (optional)."""
    desc = input("Enter description (optional): ").strip()
    if not desc:
        raise ValueError("Description cannot be empty.")
    return desc

def ensure_csv_header(path: Path) -> None:
    """Ensure the CSV file has a header row."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists() or path.stat().st_size == 0:
        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Date", "Amount", "Category", "Description"])
            
def add_expense(date: str, amount: float, category: str, description: str) -> None:
    """Add an expense to the CSV file."""
    ensure_csv_header(DATA_FILE)
    with open(DATA_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([date, f"{amount:.2f}", category, description])
        
def main():
    print("==== Add New Expense ====")
    try:
        date = prompt_date()
        amount = prompt_amount()
        category = prompt_category()
        description = prompt_description()
        add_expense(date, amount, category, description)
        print("Expense added successfully!")
    except ValueError as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
    