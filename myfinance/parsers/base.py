"""Base parser ABC for all source parsers."""

from abc import ABC, abstractmethod
from pathlib import Path

import pandas as pd


class BaseParser(ABC):
    """Abstract base for all source parsers."""

    SOURCE_LABEL: str = ""

    @abstractmethod
    def parse(self, file_path: Path) -> list[dict]:
        """Read a CSV/Excel file and return a list of transaction dicts.

        Each dict must have keys matching the transactions table:
            date, charge_date, merchant, raw_description, amount_ils,
            amount_original, currency_original, payment_method,
            installment_number, installments_total, source

        Category, needs_review, and transaction_id are NOT set here.
        """
        ...

    def read_file(self, file_path: Path) -> pd.DataFrame:
        """Read CSV or Excel into a DataFrame. Handles encoding detection."""
        suffix = file_path.suffix.lower()
        if suffix == '.csv':
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

    def _parse_date(self, date_str) -> str | None:
        """Parse various date formats to ISO YYYY-MM-DD."""
        if pd.isna(date_str):
            return None
        # Handle pandas Timestamp objects directly
        if isinstance(date_str, pd.Timestamp):
            return date_str.strftime('%Y-%m-%d')
        date_str = str(date_str).strip()
        if not date_str or date_str == 'nan' or date_str == 'NaT':
            return None
        for fmt in ('%d/%m/%Y', '%d-%m-%Y', '%d.%m.%Y', '%Y-%m-%d', '%Y-%m-%d %H:%M:%S'):
            try:
                return pd.to_datetime(date_str, format=fmt).strftime('%Y-%m-%d')
            except ValueError:
                continue
        # Try pandas auto-detection as fallback
        try:
            return pd.to_datetime(date_str, dayfirst=True).strftime('%Y-%m-%d')
        except (ValueError, TypeError):
            return None

    def _parse_amount(self, value) -> float:
        """Convert amount string to float. Handles Hebrew formatting."""
        if pd.isna(value):
            return 0.0
        if isinstance(value, (int, float)):
            return float(value)
        cleaned = str(value).replace(',', '').replace('₪', '').replace(' ', '').strip()
        if cleaned.startswith('(') and cleaned.endswith(')'):
            cleaned = '-' + cleaned[1:-1]
        if cleaned in ('', '-'):
            return 0.0
        return float(cleaned)
