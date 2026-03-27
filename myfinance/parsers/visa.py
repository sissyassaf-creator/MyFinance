"""Parser for Visa Mizrahi Tefahot / Cal / Diners El Al credit card statements.

Real file format (as of March 2026):
- Row 0: Account info header ("פירוט עסקאות לסיסי...")
- Row 1: Column names (with newlines in them: "תאריך\nעסקה")
- Rows 2+: Transactions
- Last rows: Footer with totals and disclaimer
- Multiple cards in one file (כרטיס column: "ויזה 9614", "דיינרס מסטרקארד 8656")
- No separate installment column — info may be in הערות
- No original currency/amount columns — just סכום בש"ח
"""

import re
from pathlib import Path

import pandas as pd

from myfinance.parsers.base import BaseParser

# Column names as they appear in the real Excel file (with newlines)
VISA_COLUMN_MAP = {
    'תאריך\nעסקה': 'date',
    'שם בית עסק': 'merchant',
    'סכום\nבש"ח': 'amount_ils',
    'כרטיס': 'card',
    'מועד\nחיוב': 'charge_date',
    'סוג\nעסקה': 'payment_method',
    'מזהה כרטיס\nבארנק דיגילטי': 'digital_wallet_id',
    'הערות': 'raw_description',
}

# Alternate column names (different statement versions / CSV exports)
VISA_COLUMN_ALIASES = {
    'תאריך עסקה': 'date',
    'תאריך חיוב': 'charge_date',
    'שם בית העסק': 'merchant',
    'סכום חיוב': 'amount_ils',
    'סכום בש"ח': 'amount_ils',
    'סכום עסקה מקורי': 'amount_original',
    'מטבע מקור': 'currency_original',
    'סוג עסקה': 'payment_method',
    'מספר תשלום': 'installment_info',
    'פירוט נוסף': 'raw_description',
    'תאריך העסקה': 'date',
    'תאריך החיוב': 'charge_date',
    'סכום החיוב': 'amount_ils',
    'סכום מקורי': 'amount_original',
    'מועד חיוב': 'charge_date',
}

PAYMENT_METHOD_MAP = {
    'רגילה': 'regular',
    'רכישה רגילה': 'regular',
    'תשלומים': 'installments',
    'חיוב מיידי': 'immediate_debit',
    'הוראת קבע': 'regular',
    'שרותים': 'regular',
}

# Map card name prefix to source label
CARD_SOURCE_MAP = {
    'ויזה': 'visa-mizrahi',
    'דיינרס': 'diners-el-al',
    'מסטרקארד': 'diners-el-al',
}


class VisaParser(BaseParser):
    """Parser for Visa Mizrahi / Cal / Diners El Al credit card statements.

    Handles the real Excel format where:
    - Row 0 is account info (header=1 needed)
    - Column names contain newlines
    - Multiple cards in one file
    - Footer rows with totals
    """

    def __init__(self, source_label: str):
        self.SOURCE_LABEL = source_label

    def read_file(self, file_path: Path) -> pd.DataFrame:
        """Override to handle the header row in real Visa files."""
        suffix = file_path.suffix.lower()

        if suffix in ('.xlsx', '.xls'):
            # Try header=1 first (real Visa format with account info in row 0)
            df = pd.read_excel(file_path, header=0)
            first_col = str(df.columns[0])

            if 'פירוט עסקאות' in first_col or 'לחשבון' in first_col:
                # Real Visa format — actual columns are in row 0
                df = pd.read_excel(file_path, header=1)
            return df

        elif suffix == '.csv':
            # Try CSV with encoding detection
            for encoding in ['utf-8-sig', 'cp1255', 'utf-8', 'iso-8859-8']:
                try:
                    df = pd.read_csv(file_path, encoding=encoding)
                    first_col = str(df.columns[0])
                    if 'פירוט עסקאות' in first_col or 'לחשבון' in first_col:
                        df = pd.read_csv(file_path, encoding=encoding, header=1)
                    return df
                except (UnicodeDecodeError, UnicodeError):
                    continue
            raise ValueError(f"Cannot decode CSV file: {file_path}")
        else:
            raise ValueError(f"Unsupported file type: {suffix}")

    def parse(self, file_path: Path) -> list[dict]:
        df = self.read_file(file_path)
        df = self._normalize_columns(df)
        transactions = []

        for _, row in df.iterrows():
            date_val = row.get('date')
            if date_val is None or pd.isna(date_val):
                continue

            parsed_date = self._parse_date(date_val)
            if not parsed_date:
                continue

            amount = self._parse_amount(row.get('amount_ils', 0))
            if amount == 0.0:
                continue

            merchant = str(row.get('merchant', '')).strip()
            if not merchant or merchant == 'nan' or 'סה"כ' in merchant:
                continue

            # Detect source from card column if available
            source = self._detect_source(row.get('card', ''))

            installment_number, installments_total = self._parse_installments(
                row.get('installment_info', ''),
                row.get('raw_description', ''),
            )

            txn = {
                'date': parsed_date,
                'charge_date': self._parse_date(row.get('charge_date')),
                'merchant': merchant,
                'raw_description': self._clean_str(row.get('raw_description', '')),
                'amount_ils': amount,
                'amount_original': self._parse_amount(row.get('amount_original')),
                'currency_original': self._clean_currency(row.get('currency_original')),
                'payment_method': self._map_payment_method(row.get('payment_method', '')),
                'installment_number': installment_number,
                'installments_total': installments_total,
                'source': source,
            }
            transactions.append(txn)

        return transactions

    def _normalize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Map Hebrew column names (including ones with newlines) to standard names."""
        col_map = {**VISA_COLUMN_MAP, **VISA_COLUMN_ALIASES}
        rename = {}
        for orig_col in df.columns:
            cleaned = str(orig_col).strip()
            if cleaned in col_map:
                rename[orig_col] = col_map[cleaned]
            # Also try with newlines removed
            no_newline = cleaned.replace('\n', ' ')
            if no_newline in col_map:
                rename[orig_col] = col_map[no_newline]
        return df.rename(columns=rename)

    def _detect_source(self, card_str) -> str:
        """Detect source label from the card column (e.g., 'ויזה 9614' → 'visa-mizrahi')."""
        if pd.isna(card_str):
            return self.SOURCE_LABEL
        card_str = str(card_str).strip()
        for prefix, source in CARD_SOURCE_MAP.items():
            if prefix in card_str:
                return source
        return self.SOURCE_LABEL

    def _parse_installments(self, info, description) -> tuple[int | None, int | None]:
        """Parse installment info from dedicated column or description/notes."""
        # Try dedicated installment column
        for text in [info, description]:
            if not text or str(text).strip() in ('', 'nan'):
                continue
            text = str(text)
            # Match "3 מתוך 12" or "תשלום 3 מ-12" or "3/12"
            match = re.search(r'(\d+)\s*(?:מתוך|מ-|/)\s*(\d+)', text)
            if match:
                return int(match.group(1)), int(match.group(2))
        return None, None

    def _map_payment_method(self, method_str: str) -> str:
        if pd.isna(method_str):
            return 'regular'
        return PAYMENT_METHOD_MAP.get(str(method_str).strip(), 'regular')

    def _clean_currency(self, val) -> str | None:
        if val is None or pd.isna(val) or str(val).strip() in ('', '₪', 'ILS', 'ש"ח', 'nan'):
            return None
        return str(val).strip().upper()

    def _clean_str(self, val) -> str:
        if val is None or pd.isna(val):
            return ''
        return str(val).strip()
