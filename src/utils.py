from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_FILE = PROJECT_ROOT / "data" / "expenses.csv"
STANDARD_COLUMNS = ["date", "amount", "category", "description"]


@dataclass
class Expense:
    date: str          # YYYY-MM-DD
    amount: float
    category: str
    description: str


def ensure_csv_header(path: Path = DEFAULT_DATA_FILE) -> None:
    """Create the CSV and header if it doesn't exist or is empty."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists() or path.stat().st_size == 0:
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(STANDARD_COLUMNS)


def _standardize_col_name(col: str) -> str:
    """Map common column variants to our standard schema."""
    c = col.strip().lower()
    mapping = {
        "date": "date",
        "transaction date": "date",
        "txn date": "date",

        "amount": "amount",
        "amt": "amount",
        "value": "amount",
        "debit": "amount",

        "category": "category",
        "type": "category",

        "description": "description",
        "desc": "description",
        "merchant": "description",
        "narration": "description",
        "details": "description",
        "notes": "description",
    }
    return mapping.get(c, c)


def _parse_date(value: str) -> Optional[str]:
    v = (value or "").strip()
    if not v:
        return None

    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(v, fmt).strftime("%Y-%m-%d")
        except ValueError:
            pass

    try:
        return datetime.fromisoformat(v.replace("Z", "")).strftime("%Y-%m-%d")
    except ValueError:
        return None


def _parse_amount(value: str) -> Optional[float]:
    v = (value or "").strip().replace("$", "").replace(",", "")
    if not v:
        return None
    try:
        amt = float(v)
    except ValueError:
        return None
    if amt <= 0:
        return None
    return round(amt, 2)


def load_expenses(path: Path = DEFAULT_DATA_FILE) -> List[Expense]:
    """
    Load expenses from CSV and return a cleaned list.
    Skips bad rows instead of crashing.
    """
    ensure_csv_header(path)

    with path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            return []

        # Map standardized name -> original header
        field_map = {_standardize_col_name(h): h for h in reader.fieldnames}

        cleaned: List[Expense] = []
        for row in reader:
            raw_date = row.get(field_map.get("date", ""), "")
            raw_amount = row.get(field_map.get("amount", ""), "")
            raw_category = row.get(field_map.get("category", ""), "")
            raw_desc = row.get(field_map.get("description", ""), "")

            date = _parse_date(str(raw_date))
            amount = _parse_amount(str(raw_amount))
            category = str(raw_category).strip()
            description = str(raw_desc).strip()

            if not date or amount is None or not category or not description:
                continue

            cleaned.append(Expense(date=date, amount=amount, category=category, description=description))

    return cleaned


def save_expenses(expenses: List[Expense], path: Path = DEFAULT_DATA_FILE) -> None:
    """Overwrite CSV with cleaned expenses (standard schema)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(STANDARD_COLUMNS)
        for e in expenses:
            writer.writerow([e.date, f"{e.amount:.2f}", e.category, e.description])


def export_clean_copy(source: Path = DEFAULT_DATA_FILE, target: Optional[Path] = None) -> Path:
    """Load + clean expenses from source and write to a new clean file."""
    if target is None:
        target = source.parent / "expenses_clean.csv"

    expenses = load_expenses(source)
    save_expenses(expenses, target)
    return target
