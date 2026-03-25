"""Excel export — monthly transaction report."""

from pathlib import Path

import pandas as pd

from myfinance.config import EXPORT_DIR
from myfinance.db import get_connection, get_transactions


def export_month(month: str) -> Path | None:
    """Export transactions for a given month to Excel.

    Args:
        month: YYYY-MM format string

    Returns:
        Path to the created file, or None if no transactions.
    """
    conn = get_connection()
    transactions = get_transactions(conn, month=month)
    conn.close()

    if not transactions:
        return None

    EXPORT_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.DataFrame(transactions)

    # Select and rename columns for Hebrew export
    export_columns = {
        'date': 'תאריך',
        'charge_date': 'תאריך חיוב',
        'merchant': 'בית עסק',
        'amount_ils': 'סכום (₪)',
        'amount_original': 'סכום מקורי',
        'currency_original': 'מטבע',
        'category': 'קטגוריה',
        'payment_method': 'אופן תשלום',
        'installment_number': 'תשלום',
        'installments_total': 'מתוך',
        'source': 'מקור',
        'raw_description': 'תיאור מקורי',
    }

    # Only include columns that exist
    cols = [c for c in export_columns if c in df.columns]
    df_export = df[cols].rename(columns=export_columns)

    # Sort by date
    df_export = df_export.sort_values('תאריך')

    filename = f"הוצאות_{month.replace('-', '_')}.xlsx"
    output_path = EXPORT_DIR / filename

    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        df_export.to_excel(writer, sheet_name='עסקאות', index=False)

        # Auto-adjust column widths
        worksheet = writer.sheets['עסקאות']
        for i, col in enumerate(df_export.columns, 1):
            max_len = max(
                df_export[col].astype(str).map(len).max(),
                len(col),
            )
            worksheet.column_dimensions[
                worksheet.cell(row=1, column=i).column_letter
            ].width = min(max_len + 2, 40)

    return output_path
