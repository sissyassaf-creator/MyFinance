"""Parser for Max credit card statements."""

import re
from pathlib import Path

import pandas as pd

from myfinance.parsers.base import BaseParser

MAX_COLUMN_MAP = {
    'תאריך עסקה': 'date',
    'תאריך חיוב': 'charge_date',
    'שם בית העסק': 'merchant',
    'סכום חיוב': 'amount_ils',
    'סכום מקורי': 'amount_original',
    'מטבע': 'currency_original',
    'הערות': 'raw_description',
    'סוג עסקה': 'payment_method',
    'מספר תשלומים': 'installment_info',
    'תשלום': 'installment_current',
}

MAX_COLUMN_ALIASES = {
    'תאריך': 'date',
    'סכום': 'amount_ils',
    'סכום העסקה': 'amount_original',
    'תיאור': 'raw_description',
    'פירוט': 'raw_description',
    'שם בית עסק': 'merchant',
}

PAYMENT_METHOD_MAP = {
    'רגילה': 'regular',
    'תשלומים': 'installments',
    'חיוב מיידי': 'immediate_debit',
    'קרדיט': 'regular',
}


class MaxParser(BaseParser):
    """Parser for Max credit card statements."""

    SOURCE_LABEL = 'max'

    def parse(self, file_path: Path) -> list[dict]:
        df = self.read_file(file_path)
        df = self._normalize_columns(df)
        transactions = []

        for _, row in df.iterrows():
            date_val = row.get('date')
            if not date_val or str(date_val).strip() == '' or pd.isna(date_val):
                continue

            parsed_date = self._parse_date(date_val)
            if not parsed_date:
                continue

            installment_number, installments_total = self._parse_installments(row)

            amount = self._parse_amount(row.get('amount_ils', 0))
            if amount == 0.0:
                continue

            txn = {
                'date': parsed_date,
                'charge_date': self._parse_date(row.get('charge_date')),
                'merchant': str(row.get('merchant', '')).strip(),
                'raw_description': str(row.get('raw_description', '')).strip(),
                'amount_ils': amount,
                'amount_original': self._parse_amount(row.get('amount_original')),
                'currency_original': self._clean_currency(row.get('currency_original')),
                'payment_method': self._map_payment_method(row.get('payment_method', '')),
                'installment_number': installment_number,
                'installments_total': installments_total,
                'source': self.SOURCE_LABEL,
            }
            transactions.append(txn)

        return transactions

    def _normalize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        col_map = {**MAX_COLUMN_MAP, **MAX_COLUMN_ALIASES}
        rename = {}
        for orig_col in df.columns:
            cleaned = str(orig_col).strip()
            if cleaned in col_map:
                rename[orig_col] = col_map[cleaned]
        return df.rename(columns=rename)

    def _parse_installments(self, row) -> tuple[int | None, int | None]:
        """Max may store installment info in separate columns or combined."""
        # Try combined format
        info = row.get('installment_info', '')
        if info and str(info).strip() not in ('', 'nan'):
            match = re.search(r'(\d+)\s*(?:מתוך|/)\s*(\d+)', str(info))
            if match:
                return int(match.group(1)), int(match.group(2))
        # Try separate columns
        current = row.get('installment_current')
        total = row.get('installments_total')
        if current and total:
            try:
                return int(current), int(total)
            except (ValueError, TypeError):
                pass
        return None, None

    def _map_payment_method(self, method_str: str) -> str:
        return PAYMENT_METHOD_MAP.get(str(method_str).strip(), 'regular')

    def _clean_currency(self, val) -> str | None:
        if pd.isna(val) or str(val).strip() in ('', '₪', 'ILS', 'ש"ח'):
            return None
        return str(val).strip().upper()
