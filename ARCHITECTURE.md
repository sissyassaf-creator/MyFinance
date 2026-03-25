# MyFinance v1 — Technical Architecture

**Date:** 2026-03-25
**Status:** Architecture Complete — Ready for Implementation
**Scope:** v1 only (Working Foundation)

---

## 1. Project File Structure

```
MyFinance/
├── .env                          # ANTHROPIC_API_KEY (gitignored)
├── .env.example                  # Template showing required vars
├── .gitignore                    # .env, __pycache__, *.pyc, venv/, data/*.db
├── requirements.txt              # Pinned dependencies
├── pyproject.toml                # Project metadata, entry points
│
├── input/                        # User drops files here (gitignored contents)
│   ├── visa-mizrahi/             # Visa Mizrahi Tefahot CSV/Excel files
│   ├── diners-el-al/             # Diners El Al CSV/Excel files (same format as Visa)
│   └── max/                      # Max CSV/Excel files
│
├── data/
│   └── myfinance.db              # SQLite database (gitignored)
│
├── backups/                      # Auto-backups of SQLite before each run (gitignored)
│
├── exports/                      # Generated Excel exports (gitignored)
│
├── myfinance/                    # Main Python package
│   ├── __init__.py               # Package version (__version__ = "1.0.0")
│   ├── config.py                 # All constants, categories, column mappings, paths
│   ├── cli.py                    # CLI entry points (process, dashboard, export)
│   ├── db.py                     # SQLite connection, schema init, CRUD operations
│   │
│   ├── parsers/                  # Source-specific file parsers
│   │   ├── __init__.py           # Exports parser registry
│   │   ├── base.py               # BaseParser abstract class
│   │   ├── visa.py               # VisaParser — handles Visa Mizrahi + Diners El Al
│   │   └── max_parser.py         # MaxParser — handles Max credit card
│   │
│   ├── processing/               # Core pipeline logic
│   │   ├── __init__.py
│   │   ├── pipeline.py           # Orchestrator: detect → parse → dedup → categorize → store
│   │   ├── dedup.py              # SHA256 deduplication logic
│   │   ├── categorizer.py        # Claude API categorization + merchant cache
│   │   └── savings.py            # 3 savings detection rules
│   │
│   ├── dashboard/                # Plotly Dash application
│   │   ├── __init__.py
│   │   ├── app.py                # Dash app factory, layout, RTL setup
│   │   ├── sidebar.py            # Sidebar: process button, stats, last run
│   │   ├── tab_overview.py       # Tab 1: סקירה כללית
│   │   ├── tab_transactions.py   # Tab 2: פירוט עסקאות
│   │   └── callbacks.py          # All Dash callbacks (processing, filtering, editing)
│   │
│   └── export.py                 # Excel export logic
│
├── tests/                        # Test suite
│   ├── __init__.py
│   ├── conftest.py               # Shared fixtures (temp DB, sample data)
│   ├── sample_data/              # Sample CSV/Excel files for testing
│   │   ├── visa_sample.csv
│   │   ├── max_sample.csv
│   │   └── max_sample.xlsx
│   ├── test_parsers.py           # Parser unit tests
│   ├── test_dedup.py             # Deduplication tests
│   ├── test_categorizer.py       # Categorization tests (mocked API)
│   ├── test_savings.py           # Savings rule tests
│   ├── test_db.py                # Database CRUD tests
│   ├── test_pipeline.py          # Integration test: full pipeline
│   └── test_export.py            # Excel export tests
│
├── PRODUCT_DEFINITION.md
├── DESIGN.md
├── ARCHITECTURE.md               # This file
├── TOOLCHAIN.md
├── TASKS.md
└── PROGRESS.md
```

**Naming note:** The Max parser file is `max_parser.py` (not `max.py`) to avoid shadowing Python's built-in `max()` function.

---

## 2. Module Architecture

### Dependency Graph

```
cli.py
  ├── processing/pipeline.py      (process command)
  │     ├── parsers/visa.py
  │     ├── parsers/max_parser.py
  │     ├── processing/dedup.py
  │     ├── processing/categorizer.py  → anthropic SDK → Claude API
  │     ├── processing/savings.py
  │     └── db.py                  → SQLite
  ├── dashboard/app.py            (dashboard command)
  │     ├── dashboard/sidebar.py
  │     ├── dashboard/tab_overview.py
  │     ├── dashboard/tab_transactions.py
  │     ├── dashboard/callbacks.py
  │     └── db.py                  → SQLite (read-only for display)
  └── export.py                   (export command)
        └── db.py                  → SQLite (read-only)

config.py ← imported by nearly every module (constants, paths, categories)
db.py     ← imported by pipeline, categorizer, dashboard, export
```

### Module Responsibilities

| Module | Responsibility |
|--------|---------------|
| `config.py` | Categories list, column mappings per source, file paths, source labels, sensitive-data patterns |
| `cli.py` | `argparse`-based CLI: `myfinance process`, `myfinance dashboard`, `myfinance export` |
| `db.py` | `get_connection()`, `init_db()`, all SQL queries as functions, backup logic |
| `parsers/base.py` | `BaseParser` ABC defining the parser contract |
| `parsers/visa.py` | `VisaParser` for Visa Mizrahi + Diners El Al files |
| `parsers/max_parser.py` | `MaxParser` for Max credit card files |
| `parsers/__init__.py` | `PARSER_REGISTRY`: maps source folder name to parser class |
| `processing/pipeline.py` | `run_pipeline(input_dir)` orchestrator |
| `processing/dedup.py` | `compute_hash()`, `is_duplicate()` |
| `processing/categorizer.py` | `categorize_transactions()`, merchant map cache read/write |
| `processing/savings.py` | `detect_savings(transactions)` returning list of alerts |
| `dashboard/app.py` | `create_app()` factory returning configured Dash app |
| `dashboard/sidebar.py` | Sidebar layout component + related callbacks |
| `dashboard/tab_overview.py` | Overview tab layout |
| `dashboard/tab_transactions.py` | Transactions tab layout (ag-grid) |
| `dashboard/callbacks.py` | All callback registrations (separated from layout) |
| `export.py` | `export_month(year, month)` writes `הוצאות_YYYY_MM.xlsx` |

---

## 3. Data Flow Diagram

```
                     ┌─────────────────────────────────────────────────────┐
                     │                  USER ACTION                        │
                     │  Drop CSV/Excel files into input/<source>/ folder   │
                     │  Then run: myfinance process (or click button)      │
                     └──────────┬──────────────────────────────────────────┘
                                │
                                ▼
                ┌───────────────────────────────┐
                │  1. FILE DETECTION             │
                │  Scan input/{visa-mizrahi,     │
                │  diners-el-al, max}/ folders   │
                │  Filter: *.csv, *.xlsx, *.xls  │
                │  Check processing_log: skip    │
                │  already-processed files       │
                └──────────┬────────────────────┘
                           │ list of (filepath, source_label)
                           ▼
                ┌───────────────────────────────┐
                │  2. PARSING                    │
                │  Select parser by source:      │
                │  - visa-mizrahi → VisaParser   │
                │  - diners-el-al → VisaParser   │
                │  - max → MaxParser             │
                │  Read file with pandas          │
                │  Map Hebrew columns → standard │
                │  Normalize types (dates, nums) │
                │  Output: list[dict] per file   │
                └──────────┬────────────────────┘
                           │ raw transactions (list[dict])
                           ▼
                ┌───────────────────────────────┐
                │  3. DEDUPLICATION               │
                │  For each transaction:          │
                │  hash = SHA256(date + merchant  │
                │         + amount + source)      │
                │  Query DB: if hash exists, skip │
                │  Output: new transactions only  │
                └──────────┬────────────────────┘
                           │ deduplicated transactions
                           ▼
                ┌───────────────────────────────┐
                │  4. CATEGORIZATION              │
                │  For each unique merchant:      │
                │  a) Check merchant_map table    │
                │     → if cached, use it         │
                │  b) If not cached, collect into │
                │     batch for Claude API        │
                │  c) Call Claude API (batch of   │
                │     up to 50 merchants)         │
                │  d) Save new mappings to        │
                │     merchant_map table          │
                │  e) Apply categories to all     │
                │     transactions                │
                └──────────┬────────────────────┘
                           │ categorized transactions
                           ▼
                ┌───────────────────────────────┐
                │  5. STORE                       │
                │  INSERT INTO transactions       │
                │  INSERT INTO processing_log     │
                │  (one row per file processed)   │
                └──────────┬────────────────────┘
                           │
                           ▼
                ┌───────────────────────────────┐
                │  6. SAVINGS DETECTION           │
                │  Run 3 rules on current month   │
                │  Output: printed to console     │
                │  (also shown in dashboard)      │
                └──────────┬────────────────────┘
                           │
                           ▼
                       DONE. User launches dashboard or exports Excel.
```

### Dashboard Data Flow

```
Browser ──HTTP──▶ Dash server (localhost:8050)
                       │
                       ├── sidebar.py    → db.py → SELECT count/stats
                       ├── tab_overview  → db.py → SELECT aggregations
                       └── tab_transactions → db.py → SELECT with filters

User edits category in ag-grid → callback → UPDATE transactions SET category
                                           → INSERT/UPDATE merchant_map
```

---

## 4. SQLite Schema

```sql
-- File: db.py — executed by init_db()

CREATE TABLE IF NOT EXISTS transactions (
    transaction_id    TEXT PRIMARY KEY,          -- SHA256 hash
    date              TEXT NOT NULL,             -- ISO format YYYY-MM-DD
    charge_date       TEXT,                      -- ISO format YYYY-MM-DD
    merchant          TEXT NOT NULL,             -- Merchant name as-is from statement
    raw_description   TEXT,                      -- Full original description line
    amount_ils        REAL NOT NULL,             -- Amount in ILS (positive = expense)
    amount_original   REAL,                      -- Original amount if foreign currency
    currency_original TEXT,                      -- e.g. 'USD', 'EUR', NULL if ILS
    payment_method    TEXT DEFAULT 'regular',    -- regular | installments | immediate_debit
    installment_number INTEGER,                  -- Current installment (NULL if regular)
    installments_total INTEGER,                  -- Total installments (NULL if regular)
    category          TEXT NOT NULL DEFAULT 'לא מזוהה',  -- Hebrew category
    needs_review      INTEGER NOT NULL DEFAULT 1, -- 0=confirmed, 1=needs review
    source            TEXT NOT NULL,             -- 'visa-mizrahi' | 'diners-el-al' | 'max'
    created_at        TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);

CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(date);
CREATE INDEX IF NOT EXISTS idx_transactions_category ON transactions(category);
CREATE INDEX IF NOT EXISTS idx_transactions_source ON transactions(source);
CREATE INDEX IF NOT EXISTS idx_transactions_merchant ON transactions(merchant);
CREATE INDEX IF NOT EXISTS idx_transactions_needs_review ON transactions(needs_review);

CREATE TABLE IF NOT EXISTS merchant_map (
    merchant_name     TEXT PRIMARY KEY,          -- Normalized merchant name (stripped, lowered)
    category          TEXT NOT NULL,             -- Confirmed Hebrew category
    confirmed_by      TEXT NOT NULL DEFAULT 'api', -- 'api' | 'user'
    created_at        TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    updated_at        TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS processing_log (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path         TEXT NOT NULL,             -- Relative path from project root
    file_hash         TEXT NOT NULL,             -- SHA256 of file content (detect re-drops)
    source            TEXT NOT NULL,             -- 'visa-mizrahi' | 'diners-el-al' | 'max'
    rows_total        INTEGER NOT NULL,          -- Total rows in file
    rows_new          INTEGER NOT NULL,          -- Rows actually inserted (after dedup)
    rows_duplicate    INTEGER NOT NULL,          -- Rows skipped (duplicates)
    processed_at      TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    status            TEXT NOT NULL DEFAULT 'success'  -- 'success' | 'error'
);

CREATE INDEX IF NOT EXISTS idx_processing_log_file_hash ON processing_log(file_hash);
```

### Key Design Decisions

- **`transaction_id` is the SHA256 hash** — serves as both PK and dedup key. No auto-increment needed.
- **`needs_review` is INTEGER** — SQLite has no bool. 0=false, 1=true.
- **`processing_log.file_hash`** — hashing the file content (not just the path) detects when the same file is re-dropped under a different name, or when a renamed file has the same content.
- **Dates stored as ISO TEXT** — SQLite's date functions work on ISO strings. Avoids timezone confusion.
- **`amount_ils` is always positive** — all v1 transactions are expenses (credit card charges). No income in v1.
- **`merchant_map.merchant_name` is normalized** — see Section 6 for normalization rules.

---

## 5. Parser Interface

### Base Class

```python
# myfinance/parsers/base.py
from abc import ABC, abstractmethod
from pathlib import Path
import pandas as pd


class BaseParser(ABC):
    """Abstract base for all source parsers."""

    # Subclass must set this
    SOURCE_LABEL: str = ""

    @abstractmethod
    def parse(self, file_path: Path) -> list[dict]:
        """
        Read a CSV or Excel file and return a list of transaction dicts.

        Each dict must have these keys (matching the transactions table):
            date, charge_date, merchant, raw_description, amount_ils,
            amount_original, currency_original, payment_method,
            installment_number, installments_total, source

        Category and needs_review are NOT set here — categorizer handles that.
        transaction_id is NOT set here — dedup module handles that.
        """
        ...

    def read_file(self, file_path: Path) -> pd.DataFrame:
        """Read CSV or Excel into a DataFrame. Handles encoding detection."""
        suffix = file_path.suffix.lower()
        if suffix == '.csv':
            # Israeli CSV files are typically cp1255 or utf-8-sig encoded
            for encoding in ['utf-8-sig', 'cp1255', 'utf-8', 'iso-8859-8']:
                try:
                    return pd.read_csv(file_path, encoding=encoding)
                except (UnicodeDecodeError, UnicodeError):
                    continue
            raise ValueError(f"Cannot decode CSV file: {file_path}")
        elif suffix in ('.xlsx', '.xls'):
            return pd.read_excel(file_path)
        else:
            raise ValueError(f"Unsupported file type: {suffix}")

    def _parse_date(self, date_str: str) -> str:
        """Parse DD/MM/YYYY or DD-MM-YYYY to ISO YYYY-MM-DD."""
        if pd.isna(date_str):
            return None
        date_str = str(date_str).strip()
        for fmt in ('%d/%m/%Y', '%d-%m-%Y', '%d.%m.%Y', '%Y-%m-%d'):
            try:
                return pd.to_datetime(date_str, format=fmt).strftime('%Y-%m-%d')
            except ValueError:
                continue
        raise ValueError(f"Cannot parse date: {date_str}")

    def _parse_amount(self, value) -> float:
        """Convert amount string to float. Handles Hebrew formatting."""
        if pd.isna(value):
            return 0.0
        if isinstance(value, (int, float)):
            return float(value)
        # Remove commas, currency symbols, spaces
        cleaned = str(value).replace(',', '').replace('₪', '').replace(' ', '').strip()
        # Handle negative in parentheses: (100.50) → -100.50
        if cleaned.startswith('(') and cleaned.endswith(')'):
            cleaned = '-' + cleaned[1:-1]
        return float(cleaned)
```

### Visa Parser (covers Visa Mizrahi + Diners El Al)

```python
# myfinance/parsers/visa.py
from pathlib import Path
from myfinance.parsers.base import BaseParser


# Known Hebrew column names for Visa Mizrahi / Diners El Al statements
VISA_COLUMN_MAP = {
    'תאריך עסקה':       'date',            # Transaction date
    'תאריך חיוב':       'charge_date',      # Charge date
    'שם בית העסק':      'merchant',         # Merchant name
    'פירוט נוסף':       'raw_description',  # Additional details (optional)
    'סכום חיוב':        'amount_ils',       # Charge amount in ILS
    'סכום עסקה מקורי':  'amount_original',  # Original amount
    'מטבע מקור':        'currency_original', # Original currency
    'סוג עסקה':         'payment_method',   # Payment type
    'מספר תשלום':       'installment_info',  # e.g. "3 מתוך 12" or empty
}

# Alternate column names (different Visa statement versions)
VISA_COLUMN_ALIASES = {
    'תאריך העסקה':      'date',
    'תאריך החיוב':      'charge_date',
    'שם בית עסק':       'merchant',
    'סכום החיוב':       'amount_ils',
}


class VisaParser(BaseParser):
    """
    Parser for Visa Mizrahi Tefahot and Diners El Al credit card statements.
    Both use the same CSV/Excel format; only the source label differs.
    """

    def __init__(self, source_label: str):
        """
        Args:
            source_label: 'visa-mizrahi' or 'diners-el-al'
        """
        self.SOURCE_LABEL = source_label

    def parse(self, file_path: Path) -> list[dict]:
        df = self.read_file(file_path)
        df = self._normalize_columns(df)
        transactions = []

        for _, row in df.iterrows():
            # Skip summary/header rows that don't have a date
            if not row.get('date') or str(row.get('date')).strip() == '':
                continue

            installment_number, installments_total = self._parse_installments(
                row.get('installment_info', '')
            )

            txn = {
                'date': self._parse_date(row['date']),
                'charge_date': self._parse_date(row.get('charge_date')),
                'merchant': str(row.get('merchant', '')).strip(),
                'raw_description': str(row.get('raw_description', '')).strip(),
                'amount_ils': self._parse_amount(row.get('amount_ils', 0)),
                'amount_original': self._parse_amount(row.get('amount_original')),
                'currency_original': self._clean_currency(row.get('currency_original')),
                'payment_method': self._map_payment_method(row.get('payment_method', '')),
                'installment_number': installment_number,
                'installments_total': installments_total,
                'source': self.SOURCE_LABEL,
            }

            # Skip rows with zero amount (totals, headers)
            if txn['amount_ils'] == 0.0:
                continue

            transactions.append(txn)

        return transactions

    def _normalize_columns(self, df):
        """Map Hebrew column names to standard internal names."""
        col_map = {**VISA_COLUMN_MAP, **VISA_COLUMN_ALIASES}
        rename = {}
        for orig_col in df.columns:
            cleaned = orig_col.strip()
            if cleaned in col_map:
                rename[orig_col] = col_map[cleaned]
        return df.rename(columns=rename)

    def _parse_installments(self, info) -> tuple[int | None, int | None]:
        """Parse '3 מתוך 12' → (3, 12). Returns (None, None) if not installments."""
        import re
        if not info or str(info).strip() == '' or str(info) == 'nan':
            return None, None
        match = re.search(r'(\d+)\s*מתוך\s*(\d+)', str(info))
        if match:
            return int(match.group(1)), int(match.group(2))
        return None, None

    def _map_payment_method(self, method_str: str) -> str:
        """Map Hebrew payment type to enum value."""
        method_str = str(method_str).strip()
        method_map = {
            'רגילה': 'regular',
            'תשלומים': 'installments',
            'חיוב מיידי': 'immediate_debit',
            'הוראת קבע': 'regular',
        }
        return method_map.get(method_str, 'regular')

    def _clean_currency(self, val) -> str | None:
        """Return ISO currency code or None for ILS."""
        import pandas as pd
        if pd.isna(val) or str(val).strip() in ('', '₪', 'ILS', 'ש"ח'):
            return None
        return str(val).strip().upper()
```

### Max Parser

```python
# myfinance/parsers/max_parser.py
from pathlib import Path
from myfinance.parsers.base import BaseParser


# Max uses different Hebrew column names than Visa
MAX_COLUMN_MAP = {
    'תאריך עסקה':       'date',
    'תאריך חיוב':       'charge_date',
    'שם בית העסק':      'merchant',
    'סכום חיוב':        'amount_ils',
    'סכום מקורי':       'amount_original',
    'מטבע':             'currency_original',
    'הערות':            'raw_description',       # Max uses "notes" column
    'סוג עסקה':         'payment_method',
    'מספר תשלומים':     'installment_info',
    'תשלום':            'installment_current',    # May have separate columns
}

MAX_COLUMN_ALIASES = {
    'תאריך':            'date',
    'סכום':             'amount_ils',
    'סכום העסקה':       'amount_original',
    'תיאור':            'raw_description',
    'פירוט':            'raw_description',
}


class MaxParser(BaseParser):
    """Parser for Max credit card statements."""

    SOURCE_LABEL = 'max'

    def parse(self, file_path: Path) -> list[dict]:
        df = self.read_file(file_path)
        df = self._normalize_columns(df)
        transactions = []

        for _, row in df.iterrows():
            if not row.get('date') or str(row.get('date')).strip() == '':
                continue

            installment_number, installments_total = self._parse_installments(row)

            txn = {
                'date': self._parse_date(row['date']),
                'charge_date': self._parse_date(row.get('charge_date')),
                'merchant': str(row.get('merchant', '')).strip(),
                'raw_description': str(row.get('raw_description', '')).strip(),
                'amount_ils': self._parse_amount(row.get('amount_ils', 0)),
                'amount_original': self._parse_amount(row.get('amount_original')),
                'currency_original': self._clean_currency(row.get('currency_original')),
                'payment_method': self._map_payment_method(row.get('payment_method', '')),
                'installment_number': installment_number,
                'installments_total': installments_total,
                'source': self.SOURCE_LABEL,
            }

            if txn['amount_ils'] == 0.0:
                continue

            transactions.append(txn)

        return transactions

    def _normalize_columns(self, df):
        """Map Max-specific Hebrew columns to standard names."""
        col_map = {**MAX_COLUMN_MAP, **MAX_COLUMN_ALIASES}
        rename = {}
        for orig_col in df.columns:
            cleaned = orig_col.strip()
            if cleaned in col_map:
                rename[orig_col] = col_map[cleaned]
        return df.rename(columns=rename)

    def _parse_installments(self, row) -> tuple[int | None, int | None]:
        """Max may store installment info in separate columns or combined."""
        import re
        # Try combined format first
        info = row.get('installment_info', '')
        if info and str(info).strip() not in ('', 'nan'):
            match = re.search(r'(\d+)\s*(?:מתוך|/)\s*(\d+)', str(info))
            if match:
                return int(match.group(1)), int(match.group(2))
        # Try separate column
        current = row.get('installment_current')
        total = row.get('installments_total')
        if current and total:
            try:
                return int(current), int(total)
            except (ValueError, TypeError):
                pass
        return None, None

    def _map_payment_method(self, method_str: str) -> str:
        method_str = str(method_str).strip()
        method_map = {
            'רגילה': 'regular',
            'תשלומים': 'installments',
            'חיוב מיידי': 'immediate_debit',
            'קרדיט': 'regular',
        }
        return method_map.get(method_str, 'regular')

    def _clean_currency(self, val) -> str | None:
        import pandas as pd
        if pd.isna(val) or str(val).strip() in ('', '₪', 'ILS', 'ש"ח'):
            return None
        return str(val).strip().upper()
```

### Parser Registry

```python
# myfinance/parsers/__init__.py
from myfinance.parsers.visa import VisaParser
from myfinance.parsers.max_parser import MaxParser

# Maps input folder name → parser instance
PARSER_REGISTRY = {
    'visa-mizrahi': VisaParser(source_label='visa-mizrahi'),
    'diners-el-al': VisaParser(source_label='diners-el-al'),
    'max': MaxParser(),
}
```

---

## 6. Categorization Module

### Strategy: Batch by Unique Merchant

The key insight: many transactions share the same merchant name. We categorize **unique merchants**, not individual transactions.

```
100 transactions → maybe 30 unique merchants → 20 already cached → 10 need API call → 1 API call
```

### Merchant Name Normalization

Before cache lookup, merchant names are normalized:

```python
def normalize_merchant(name: str) -> str:
    """
    Normalize merchant name for cache matching.

    Rules:
    1. Strip whitespace
    2. Remove branch numbers / store IDs: "שופרסל 1234" → "שופרסל"
    3. Remove trailing digits after space
    4. Collapse multiple spaces
    5. Case-fold (lowercase Latin chars, Hebrew unaffected)
    6. Do NOT remove Hebrew characters or punctuation like quotation marks
       ("שופר-סל" stays "שופר-סל")
    """
    import re
    name = str(name).strip()
    name = re.sub(r'\s+\d{2,}$', '', name)     # Remove trailing store IDs
    name = re.sub(r'\s+', ' ', name)             # Collapse spaces
    name = name.casefold()                        # Lowercase Latin
    return name
```

This is intentionally conservative. v1 does NOT try to merge "שופרסל" and "שופר-סל" — that is v3 advanced normalization.

### Categorization Flow

```python
# myfinance/processing/categorizer.py

def categorize_transactions(transactions: list[dict], db_conn) -> list[dict]:
    """
    Categorize transactions using merchant_map cache + Claude API.

    Steps:
    1. Collect unique merchant names from the batch
    2. Normalize each name
    3. Look up each normalized name in merchant_map table
    4. For uncached merchants, call Claude API in a single batch
    5. Store new mappings in merchant_map
    6. Apply category to each transaction
    7. Mark needs_review=1 for 'לא מזוהה', needs_review=0 for all others
    """
    ...
```

### Claude API Call Design

**Model:** `claude-sonnet-4-20250514` (fast, cheap, good enough for categorization)

**Batch strategy:** One API call with up to 50 merchant names. If more than 50 uncached merchants, split into batches of 50.

**Prompt:**

```python
CATEGORIZATION_SYSTEM_PROMPT = """You are a financial transaction categorizer for an Israeli household.
You will receive a list of merchant names from Israeli credit card statements.
For each merchant, assign exactly one category from the following list:

1. מזון ושוק — Groceries and supermarkets
2. מסעדות ובילויים — Dining and entertainment
3. דלק ותחבורה — Fuel and transportation
4. בריאות — Health and medical
5. חינוך וילדים — Education and children
6. דיור ובית — Housing, maintenance, arnona, va'ad bayit
7. ביטוח — Insurance
8. התחייבויות קבועות — Fixed commitments (utilities, phone, internet, subscriptions)
9. ביגוד והנעלה — Clothing and shoes
10. חופשות ונסיעות — Vacations and travel
11. העברות ותשלומים — Transfers, Bit, bank fees
12. לא מזוהה — Use ONLY if you truly cannot determine the category

Rules:
- Return ONLY valid JSON: a list of objects with "merchant" and "category" keys
- "category" must be the exact Hebrew string from the list above
- Use "לא מזוהה" sparingly — most Israeli merchants are recognizable
- Do NOT include any explanation, just the JSON array
"""

CATEGORIZATION_USER_TEMPLATE = """Categorize these merchants:
{merchants_json}
"""
```

**API call:**

```python
import anthropic
import json

def _call_claude_api(merchants: list[str]) -> dict[str, str]:
    """
    Call Claude API to categorize a batch of merchant names.

    Args:
        merchants: List of normalized merchant names
    Returns:
        Dict mapping merchant_name → Hebrew category
    """
    client = anthropic.Anthropic()  # Uses ANTHROPIC_API_KEY env var

    merchants_json = json.dumps(merchants, ensure_ascii=False)

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system=CATEGORIZATION_SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": CATEGORIZATION_USER_TEMPLATE.format(merchants_json=merchants_json)
        }]
    )

    # Parse JSON from response
    result_text = response.content[0].text
    results = json.loads(result_text)

    return {item['merchant']: item['category'] for item in results}
```

### Sensitive Data Stripping

Before sending merchant names to the API, strip any embedded card numbers or account numbers:

```python
def strip_sensitive(merchant_name: str) -> str:
    """Remove card/account numbers that sometimes appear in merchant descriptions."""
    import re
    # Remove sequences of 4+ digits (card fragments)
    cleaned = re.sub(r'\b\d{4,}\b', '****', merchant_name)
    # Remove anything that looks like a card number pattern (XXXX-XXXX-XXXX-XXXX)
    cleaned = re.sub(r'\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}', '****', cleaned)
    return cleaned
```

**Important:** Sensitive stripping happens only on the data sent to the API. The original merchant name is preserved in the database.

### Merchant Cache Workflow

```
Transaction with merchant "רמי לוי שיווק 2341"
  │
  ├── normalize → "רמי לוי שיווק"
  │
  ├── SELECT category FROM merchant_map WHERE merchant_name = 'רמי לוי שיווק'
  │     ├── FOUND → use cached category, set needs_review=0
  │     └── NOT FOUND → add to API batch
  │
  └── After API call:
        INSERT INTO merchant_map (merchant_name, category, confirmed_by)
        VALUES ('רמי לוי שיווק', 'מזון ושוק', 'api')
```

When a user manually edits a category in the dashboard:
1. UPDATE the transaction row
2. UPSERT merchant_map with `confirmed_by='user'`
3. All future transactions from that merchant use the user-confirmed category

---

## 7. Dashboard Layout

### Technology Stack

- **Dash 2.x** — core framework
- **Dash Mantine Components (DMC)** — RTL-native UI components (`dir="rtl"`)
- **dash-ag-grid** — high-performance data table with inline editing
- **Plotly** — charts (pie, bar)

### App Structure

```python
# myfinance/dashboard/app.py

import dash
from dash import html
import dash_mantine_components as dmc

def create_app() -> dash.Dash:
    app = dash.Dash(
        __name__,
        title="MyFinance — הכספים שלך",
        suppress_callback_exceptions=True,
    )

    app.layout = dmc.MantineProvider(
        theme={"dir": "rtl", "fontFamily": "Assistant, Arial, sans-serif"},
        children=[
            dmc.AppShell(
                children=[
                    dmc.AppShellNavbar(sidebar_layout()),        # Right side (RTL)
                    dmc.AppShellMain(
                        dmc.Tabs(
                            value="overview",
                            children=[
                                dmc.TabsList([
                                    dmc.TabsTab("סקירה כללית", value="overview"),
                                    dmc.TabsTab("פירוט עסקאות", value="transactions"),
                                ]),
                                dmc.TabsPanel(overview_layout(), value="overview"),
                                dmc.TabsPanel(transactions_layout(), value="transactions"),
                            ],
                        )
                    ),
                ],
                navbar={"width": 280, "breakpoint": "sm"},
            )
        ],
    )

    register_callbacks(app)
    return app
```

### Component Hierarchy

```
MantineProvider (dir="rtl")
└── AppShell
    ├── AppShellNavbar (280px, right side in RTL)
    │   ├── Logo / Title: "MyFinance"
    │   ├── Button: "עבד קבצים חדשים" (Process new files)
    │   ├── Loading indicator (during processing)
    │   ├── Text: "ריצה אחרונה: DD/MM/YYYY HH:MM"
    │   ├── Divider
    │   ├── Stats group:
    │   │   ├── "קבצים בתור: N" per source folder
    │   │   └── "סה״כ עסקאות: N"
    │   └── Button: "ייצוא Excel" (Export)
    │
    └── AppShellMain
        └── Tabs
            ├── Tab: "סקירה כללית" (Overview)
            │   ├── StatsGroup: 3 cards
            │   │   ├── "סה״כ הוצאות": ₪XX,XXX
            │   │   ├── "עסקאות": N
            │   │   └── "ממתינים לבדיקה": N (red badge, clickable)
            │   ├── Grid (2 columns)
            │   │   ├── PieChart: spending by category
            │   │   └── BarChart: spend per category (sorted descending)
            │   ├── Card: "5 בתי עסק מובילים" (top 5 merchants table)
            │   ├── Card: "מטבע חוץ" (foreign currency summary, conditional)
            │   └── Card: "הצעות חיסכון" (savings alerts, from 3 rules)
            │
            └── Tab: "פירוט עסקאות" (Transactions)
                ├── Filter bar:
                │   ├── DateRangePicker (month selector)
                │   ├── MultiSelect: category filter
                │   ├── MultiSelect: source filter
                │   ├── NumberInput: min amount
                │   ├── NumberInput: max amount
                │   ├── Checkbox: "הצג ממתינים בלבד" (pending only)
                │   └── Button: "נקה מסננים" (clear filters)
                │
                └── AgGrid:
                    columns: [date, merchant, amount_ils, category, source,
                              payment_method, installment_info, needs_review]
                    features:
                    - Sort by any column
                    - Free-text search
                    - Category column is editable (dropdown with 12 categories)
                    - Rows with needs_review=1 highlighted in light yellow
                    - Amount formatted with ₪ and comma separators
                    - Dates formatted as DD/MM/YYYY
```

### Callbacks

| Callback ID | Trigger | Action |
|-------------|---------|--------|
| `process-files` | "עבד קבצים חדשים" button click | Run `pipeline.run_pipeline()` in background, update sidebar stats |
| `refresh-overview` | Tab switch to overview, after processing | Query DB aggregations, update charts and stats |
| `filter-transactions` | Any filter change | Query DB with filters, update ag-grid data |
| `edit-category` | Ag-grid cell edit on category column | UPDATE transactions + UPSERT merchant_map |
| `export-excel` | "ייצוא Excel" button click | Run export, show download link |
| `pending-badge-click` | Click on pending count | Switch to transactions tab with pending filter ON |

### Dashboard Refresh After Processing

When the user clicks "Process new files":
1. Callback triggers `run_pipeline()` synchronously (typically < 30 seconds for a month of data)
2. Pipeline returns a summary dict: `{files_processed: N, new_transactions: N, duplicates: N}`
3. Callback updates sidebar stats
4. Callback updates the active tab's data (triggers refresh of charts or table)
5. A `dmc.Notification` toast appears: "עובד: N קבצים חדשים, N עסקאות חדשות"

No polling or websockets needed — Dash callbacks are request-response.

---

## 8. Configuration

### `.env` (gitignored)

```
ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxx
```

That is the only environment variable. Everything else goes in `config.py`.

### `.env.example` (committed)

```
# MyFinance — Environment Variables
# Copy this file to .env and fill in your values

ANTHROPIC_API_KEY=sk-ant-api03-YOUR-KEY-HERE
```

### `config.py`

```python
# myfinance/config.py
from pathlib import Path

# ── Paths ──────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent.parent          # MyFinance/
INPUT_DIR = PROJECT_ROOT / "input"
DATA_DIR = PROJECT_ROOT / "data"
BACKUP_DIR = PROJECT_ROOT / "backups"
EXPORT_DIR = PROJECT_ROOT / "exports"
DB_PATH = DATA_DIR / "myfinance.db"

# Source folder names (must match input/ subdirectories)
SOURCES = {
    'visa-mizrahi': 'ויזה מזרחי טפחות',
    'diners-el-al': 'דיינרס אל על',
    'max': 'מקס',
}

# ── Categories ─────────────────────────────────────────
CATEGORIES = [
    'מזון ושוק',
    'מסעדות ובילויים',
    'דלק ותחבורה',
    'בריאות',
    'חינוך וילדים',
    'דיור ובית',
    'ביטוח',
    'התחייבויות קבועות',
    'ביגוד והנעלה',
    'חופשות ונסיעות',
    'העברות ותשלומים',
    'לא מזוהה',
]

UNRECOGNIZED_CATEGORY = 'לא מזוהה'

# ── File Detection ─────────────────────────────────────
SUPPORTED_EXTENSIONS = {'.csv', '.xlsx', '.xls'}

# ── Categorization ─────────────────────────────────────
CLAUDE_MODEL = "claude-sonnet-4-20250514"
CATEGORIZATION_BATCH_SIZE = 50      # Max merchants per API call
MAX_TOKENS = 4096

# ── Savings Rules ──────────────────────────────────────
MICRO_LEAK_THRESHOLD = 50           # ILS — individual transaction
MICRO_LEAK_MONTHLY_TOTAL = 300      # ILS — sum in one category
DUPLICATE_PAYMENT_DAYS = 2          # Days window for same merchant+amount

# Bank fee keywords (Hebrew)
BANK_FEE_KEYWORDS = [
    'עמלה', 'עמלת', 'דמי ניהול', 'דמי כרטיס', 'ריבית',
    'commission', 'fee', 'דמי', 'אגרה',
]

# ── Backup ─────────────────────────────────────────────
MAX_BACKUPS = 5                     # Keep last N backups

# ── Dashboard ──────────────────────────────────────────
DASHBOARD_HOST = "127.0.0.1"
DASHBOARD_PORT = 8050
DASHBOARD_DEBUG = False

# ── Sensitive Data Patterns ────────────────────────────
# Regex patterns to strip before sending to API
SENSITIVE_PATTERNS = [
    r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',  # Card numbers
    r'\b\d{6,}\b',                                      # Account numbers (6+ digits)
]
```

---

## 9. Entry Points

### CLI Design

```python
# myfinance/cli.py
import argparse
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        prog='myfinance',
        description='MyFinance — הכספים שלך, במחשב שלך',
    )
    subparsers = parser.add_subparsers(dest='command', required=True)

    # ── process ─────────────────────────────────────
    proc_parser = subparsers.add_parser('process', help='Process new files from input folders')
    proc_parser.add_argument(
        '--source', choices=['visa-mizrahi', 'diners-el-al', 'max'],
        help='Process only a specific source (default: all)'
    )
    proc_parser.add_argument(
        '--dry-run', action='store_true',
        help='Parse and show what would be imported without writing to DB'
    )
    proc_parser.add_argument(
        '--no-api', action='store_true',
        help='Skip Claude API categorization (mark all as לא מזוהה)'
    )

    # ── dashboard ───────────────────────────────────
    dash_parser = subparsers.add_parser('dashboard', help='Launch the dashboard')
    dash_parser.add_argument('--port', type=int, default=8050, help='Port (default: 8050)')
    dash_parser.add_argument('--debug', action='store_true', help='Enable Dash debug mode')

    # ── export ──────────────────────────────────────
    export_parser = subparsers.add_parser('export', help='Export transactions to Excel')
    export_parser.add_argument('--month', type=str, help='Month in YYYY-MM format (default: current)')

    args = parser.parse_args()

    if args.command == 'process':
        _run_process(args)
    elif args.command == 'dashboard':
        _run_dashboard(args)
    elif args.command == 'export':
        _run_export(args)


def _run_process(args):
    from dotenv import load_dotenv
    load_dotenv()

    from myfinance.db import init_db, backup_db
    from myfinance.processing.pipeline import run_pipeline

    init_db()
    backup_db()         # Always backup before processing

    result = run_pipeline(
        source_filter=args.source,
        dry_run=args.dry_run,
        skip_api=args.no_api,
    )

    print(f"\n{'='*40}")
    print(f"קבצים שעובדו: {result['files_processed']}")
    print(f"עסקאות חדשות: {result['new_transactions']}")
    print(f"כפילויות שדולגו: {result['duplicates_skipped']}")
    if result.get('savings_alerts'):
        print(f"\n💡 הצעות חיסכון:")
        for alert in result['savings_alerts']:
            print(f"  - {alert}")
    print(f"{'='*40}")


def _run_dashboard(args):
    from dotenv import load_dotenv
    load_dotenv()

    from myfinance.db import init_db
    from myfinance.dashboard.app import create_app

    init_db()
    app = create_app()
    app.run(host="127.0.0.1", port=args.port, debug=args.debug)


def _run_export(args):
    from myfinance.db import init_db
    from myfinance.export import export_month
    from datetime import date

    init_db()

    if args.month:
        year, month = map(int, args.month.split('-'))
    else:
        today = date.today()
        year, month = today.year, today.month

    path = export_month(year, month)
    print(f"Exported to: {path}")


if __name__ == '__main__':
    main()
```

### `pyproject.toml` Entry Point

```toml
[project.scripts]
myfinance = "myfinance.cli:main"
```

### How to Run

```bash
# From project root, with venv activated:

# Process all sources
python -m myfinance.cli process

# Process only Max files
python -m myfinance.cli process --source max

# Dry run — see what would be imported
python -m myfinance.cli process --dry-run

# Launch dashboard
python -m myfinance.cli dashboard

# Export current month to Excel
python -m myfinance.cli export

# Export specific month
python -m myfinance.cli export --month 2026-03
```

---

## 10. Error Handling

### Error Matrix

| Error | Where | How Handled |
|-------|-------|-------------|
| **Missing .env / ANTHROPIC_API_KEY** | `cli.py _run_process()` | Check before pipeline starts. Print clear message: "Set ANTHROPIC_API_KEY in .env file". Exit 1. |
| **No files in input folders** | `pipeline.py run_pipeline()` | Print "לא נמצאו קבצים חדשים". Return summary with all zeros. Not an error. |
| **Unreadable CSV encoding** | `base.py read_file()` | Try 4 encodings in order. If all fail, log error, skip file, add to processing_log with status='error'. |
| **Unknown column names in file** | `visa.py / max_parser.py _normalize_columns()` | If required columns (date, merchant, amount) not found after mapping, skip file with error log. |
| **Malformed date** | `base.py _parse_date()` | Try 4 date formats. If all fail, skip the row (not the entire file). Log warning. |
| **Malformed amount** | `base.py _parse_amount()` | If float conversion fails, skip the row. Log warning. |
| **Duplicate file (already processed)** | `pipeline.py` | Check processing_log by file_hash. Print "כבר עובד: {filename}". Skip silently. |
| **All transactions are duplicates** | `dedup.py` | Not an error — print "0 עסקאות חדשות מ-{filename}". Log normally. |
| **Claude API rate limit (429)** | `categorizer.py _call_claude_api()` | Retry with exponential backoff: 2s, 4s, 8s, max 3 retries. If still failing, mark uncategorized as 'לא מזוהה'. |
| **Claude API auth error (401)** | `categorizer.py` | Print "שגיאת מפתח API — check your ANTHROPIC_API_KEY". Mark all as 'לא מזוהה'. Continue pipeline. |
| **Claude API returns invalid JSON** | `categorizer.py` | Try to extract JSON from response with regex. If still fails, mark batch as 'לא מזוהה'. Log the raw response for debugging. |
| **Claude API returns wrong category** | `categorizer.py` | Validate each returned category against CATEGORIES list. If invalid, replace with 'לא מזוהה'. |
| **SQLite database locked** | `db.py` | Set `timeout=10` on connection. If still locked, print error and suggest closing the dashboard. |
| **SQLite database corrupt** | `db.py` | Detect with `PRAGMA integrity_check`. If corrupt, attempt restore from latest backup. |
| **Backup directory full / permission error** | `db.py backup_db()` | Catch OSError, print warning, continue processing (backup failure should not block work). |
| **Dashboard port already in use** | `app.py` | Catch `OSError: [Errno 48]`. Print suggestion to use `--port XXXX`. |
| **Excel export with no data** | `export.py` | Print "אין עסקאות לחודש {month}". Create no file. |

### Error Logging Strategy

v1 uses simple print-based logging to stderr. No logging framework overhead.

```python
import sys

def log_error(msg: str):
    print(f"[ERROR] {msg}", file=sys.stderr)

def log_warn(msg: str):
    print(f"[WARN] {msg}", file=sys.stderr)

def log_info(msg: str):
    print(f"[INFO] {msg}")
```

Structured logging (Python `logging` module) deferred to v2. For v1, print statements are sufficient and easier to debug.

### Backup Strategy

```python
# myfinance/db.py

def backup_db():
    """
    Copy myfinance.db to backups/myfinance_YYYYMMDD_HHMMSS.db
    Retain only the last MAX_BACKUPS copies.
    """
    import shutil
    from datetime import datetime
    from myfinance.config import DB_PATH, BACKUP_DIR, MAX_BACKUPS

    if not DB_PATH.exists():
        return  # Nothing to back up

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = BACKUP_DIR / f"myfinance_{timestamp}.db"
    shutil.copy2(DB_PATH, backup_path)

    # Prune old backups
    backups = sorted(BACKUP_DIR.glob("myfinance_*.db"), key=lambda p: p.name)
    while len(backups) > MAX_BACKUPS:
        oldest = backups.pop(0)
        oldest.unlink()
```

---

## 11. Testing Strategy

### What to Test

| Area | Test Type | What's Tested |
|------|-----------|---------------|
| **Parsers** | Unit | Column mapping, date parsing, amount parsing, installment extraction, encoding handling |
| **Deduplication** | Unit | Hash generation, duplicate detection, edge cases (same amount different merchant) |
| **Categorizer** | Unit (mocked API) | Merchant normalization, cache hit/miss, API response parsing, invalid category handling |
| **Savings rules** | Unit | Each of the 3 rules with known data |
| **Database** | Integration | Schema creation, CRUD operations, upsert merchant_map |
| **Pipeline** | Integration | End-to-end: file → DB with sample data |
| **Export** | Unit | Excel file creation, Hebrew content, formatting |

### Sample Test Data Approach

Create small, realistic CSV files in `tests/sample_data/` with known expected outputs:

**`visa_sample.csv`** (5 rows):
```csv
תאריך עסקה,תאריך חיוב,שם בית העסק,סכום חיוב,סכום עסקה מקורי,מטבע מקור,סוג עסקה,מספר תשלום
15/03/2026,01/04/2026,שופרסל דיל 1234,250.00,,,רגילה,
16/03/2026,01/04/2026,סונול דלקן,180.50,,,רגילה,
17/03/2026,01/04/2026,אמזון,89.99,24.99,USD,רגילה,
18/03/2026,01/04/2026,הפניקס ביטוח,450.00,,,תשלומים,3 מתוך 12
18/03/2026,01/04/2026,סופר פארם,62.30,,,רגילה,
```

**`max_sample.csv`** (4 rows): Same structure but with Max-specific column names.

### Test Patterns

```python
# tests/test_parsers.py

class TestVisaParser:
    def test_parse_basic_csv(self, visa_sample_path):
        parser = VisaParser(source_label='visa-mizrahi')
        result = parser.parse(visa_sample_path)
        assert len(result) == 5
        assert result[0]['merchant'] == 'שופרסל דיל 1234'
        assert result[0]['amount_ils'] == 250.00
        assert result[0]['date'] == '2026-03-15'
        assert result[0]['source'] == 'visa-mizrahi'

    def test_parse_installments(self, visa_sample_path):
        parser = VisaParser(source_label='visa-mizrahi')
        result = parser.parse(visa_sample_path)
        insurance = result[3]
        assert insurance['installment_number'] == 3
        assert insurance['installments_total'] == 12
        assert insurance['payment_method'] == 'installments'

    def test_foreign_currency(self, visa_sample_path):
        parser = VisaParser(source_label='visa-mizrahi')
        result = parser.parse(visa_sample_path)
        amazon = result[2]
        assert amazon['amount_original'] == 24.99
        assert amazon['currency_original'] == 'USD'

    def test_diners_uses_same_parser(self, visa_sample_path):
        parser = VisaParser(source_label='diners-el-al')
        result = parser.parse(visa_sample_path)
        assert all(t['source'] == 'diners-el-al' for t in result)

    def test_skips_rows_with_zero_amount(self):
        # CSV with a summary row having amount=0
        ...

    def test_handles_cp1255_encoding(self, cp1255_sample_path):
        parser = VisaParser(source_label='visa-mizrahi')
        result = parser.parse(cp1255_sample_path)
        assert len(result) > 0


# tests/test_categorizer.py

class TestMerchantNormalization:
    def test_strips_store_id(self):
        assert normalize_merchant('שופרסל דיל 1234') == 'שופרסל דיל'

    def test_collapses_spaces(self):
        assert normalize_merchant('רמי   לוי') == 'רמי לוי'

    def test_casefolds_latin(self):
        assert normalize_merchant('AMAZON') == 'amazon'

    def test_preserves_hebrew_punctuation(self):
        assert normalize_merchant('שופר-סל') == 'שופר-סל'


class TestCategorizer:
    def test_uses_cache_when_available(self, db_with_merchant_map):
        # Pre-populate merchant_map with known mapping
        # Verify no API call is made
        ...

    def test_calls_api_for_unknown_merchants(self, mock_anthropic):
        # Mock the API response
        # Verify correct prompt sent
        # Verify result stored in merchant_map
        ...

    def test_handles_api_error_gracefully(self, mock_anthropic_error):
        # Mock API to raise error
        # Verify transactions get 'לא מזוהה' category
        ...


# tests/test_savings.py

class TestBankFeeDetection:
    def test_detects_fee_keyword(self):
        txns = [{'merchant': 'עמלת ניהול חשבון', 'amount_ils': 25.0}]
        alerts = detect_savings(txns)
        assert any('עמלה' in a or 'bank' in a.lower() for a in alerts)

class TestDuplicatePayments:
    def test_detects_same_merchant_same_amount_within_2_days(self):
        txns = [
            {'merchant': 'שופרסל', 'amount_ils': 250.0, 'date': '2026-03-15'},
            {'merchant': 'שופרסל', 'amount_ils': 250.0, 'date': '2026-03-16'},
        ]
        alerts = detect_savings(txns)
        assert len(alerts) >= 1

class TestMicroLeaks:
    def test_detects_small_transactions_totaling_over_threshold(self):
        # 10 transactions of 35 ILS in same category = 350 > 300
        txns = [
            {'merchant': f'store_{i}', 'amount_ils': 35.0, 'category': 'מזון ושוק',
             'date': '2026-03-01'}
            for i in range(10)
        ]
        alerts = detect_savings(txns)
        assert len(alerts) >= 1
```

### Test Fixtures (`conftest.py`)

```python
# tests/conftest.py
import pytest
import sqlite3
from pathlib import Path
from myfinance.db import init_db

@pytest.fixture
def tmp_db(tmp_path):
    """Create a temporary SQLite database with schema initialized."""
    db_path = tmp_path / "test.db"
    conn = sqlite3.connect(str(db_path))
    # Execute schema from init_db logic
    init_db(db_path=db_path)
    yield db_path
    conn.close()

@pytest.fixture
def visa_sample_path():
    return Path(__file__).parent / "sample_data" / "visa_sample.csv"

@pytest.fixture
def max_sample_path():
    return Path(__file__).parent / "sample_data" / "max_sample.csv"
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_parsers.py -v

# Run with coverage
pytest tests/ --cov=myfinance --cov-report=term-missing
```

---

## Design Decision Summary

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Hebrew column handling | Per-parser column map dict + aliases dict | Each source has unique Hebrew column names; keeping the mapping explicit and per-parser is clearest |
| Merchant normalization | Strip trailing store IDs, collapse spaces, casefold Latin | Conservative approach for v1; advanced fuzzy matching in v3 |
| API batching | Batch unique merchants, up to 50 per API call | Minimizes API cost. 100 transactions might have only 30 unique merchants, 20 already cached = 1 API call |
| Dashboard refresh | Synchronous callback — process runs, then refresh | Simple for v1 (< 30s processing). Async deferred to v2 |
| Sensitive data stripping | Regex on merchant name before API send only | Strips card/account numbers embedded in descriptions; original preserved in local DB |
| Backup strategy | Full SQLite copy before each `process` run, keep last 5 | Simple, reliable. 5 backups at ~1MB each is negligible disk usage |
| File dedup (re-drop) | SHA256 of file content in processing_log | Detects same file dropped again under different name |
| Transaction dedup | SHA256 of (date + merchant + amount + source) | No cross-source dedup in v1 (only credit cards, no bank overlap) |
| Storage format | SQLite (not JSON) | Product definition specifies SQLite. Supports concurrent reads from dashboard + CLI. |
| No cross-source dedup | By design in v1 | Only credit card sources in v1 — no bank statements means no overlap risk |
| Parser file naming | `max_parser.py` not `max.py` | Avoids shadowing Python built-in `max()` |
| Dashboard framework | Dash + DMC + ag-grid | Product definition specifies this stack. DMC has native RTL. ag-grid has inline editing. |
| Claude model | claude-sonnet-4-20250514 | Cost-effective for categorization (fast, cheap, accurate enough) |
| Logging | Print statements | v1 simplicity. Python `logging` module in v2. |
