"""Savings detection rules (v1: 3 rules)."""

from collections import defaultdict
from datetime import datetime, timedelta

from myfinance.config import (
    BANK_FEE_KEYWORDS,
    DUPLICATE_PAYMENT_DAYS,
    MICRO_LEAK_THRESHOLD,
    MICRO_LEAK_MONTHLY_TOTAL,
)


def detect_savings(transactions: list[dict]) -> list[dict]:
    """Run all savings rules on transactions. Returns list of alert dicts."""
    alerts = []
    alerts.extend(_check_bank_fees(transactions))
    alerts.extend(_check_duplicate_payments(transactions))
    alerts.extend(_check_micro_leaks(transactions))
    return alerts


def _check_bank_fees(transactions: list[dict]) -> list[dict]:
    """Rule 1: Flag any charge containing fee/commission keywords."""
    alerts = []
    for txn in transactions:
        merchant_lower = txn['merchant'].lower()
        desc_lower = (txn.get('raw_description') or '').lower()
        combined = merchant_lower + ' ' + desc_lower

        for keyword in BANK_FEE_KEYWORDS:
            if keyword in combined:
                alerts.append({
                    'rule': 'bank_fee',
                    'title': 'עמלה בנקאית',
                    'description': f"עמלה: {txn['merchant']} — ₪{txn['amount_ils']:.2f}",
                    'amount': txn['amount_ils'],
                    'transaction_id': txn.get('transaction_id'),
                })
                break
    return alerts


def _check_duplicate_payments(transactions: list[dict]) -> list[dict]:
    """Rule 2: Same merchant + same amount within N days."""
    alerts = []
    # Group by (merchant, amount)
    groups: dict[tuple, list] = defaultdict(list)
    for txn in transactions:
        key = (txn['merchant'].strip(), f"{txn['amount_ils']:.2f}")
        groups[key].append(txn)

    for (merchant, amount_str), txns in groups.items():
        if len(txns) < 2:
            continue
        # Sort by date and check consecutive pairs
        sorted_txns = sorted(txns, key=lambda t: t['date'])
        for i in range(len(sorted_txns) - 1):
            try:
                d1 = datetime.strptime(sorted_txns[i]['date'], '%Y-%m-%d')
                d2 = datetime.strptime(sorted_txns[i + 1]['date'], '%Y-%m-%d')
                if (d2 - d1).days <= DUPLICATE_PAYMENT_DAYS:
                    alerts.append({
                        'rule': 'duplicate_payment',
                        'title': 'חיוב כפול אפשרי',
                        'description': (
                            f"{merchant} — ₪{amount_str} "
                            f"בתאריכים {sorted_txns[i]['date']} ו-{sorted_txns[i+1]['date']}"
                        ),
                        'amount': float(amount_str),
                        'transaction_id': sorted_txns[i + 1].get('transaction_id'),
                    })
            except (ValueError, TypeError):
                continue
    return alerts


def _check_micro_leaks(transactions: list[dict]) -> list[dict]:
    """Rule 3: Small transactions (<50 ILS) in one category totaling >300 ILS/month."""
    alerts = []
    # Group by (month, category)
    monthly_category: dict[tuple, list] = defaultdict(list)
    for txn in transactions:
        if txn['amount_ils'] < MICRO_LEAK_THRESHOLD:
            month = txn['date'][:7]  # YYYY-MM
            monthly_category[(month, txn.get('category', ''))].append(txn)

    for (month, category), txns in monthly_category.items():
        total = sum(t['amount_ils'] for t in txns)
        if total > MICRO_LEAK_MONTHLY_TOTAL:
            alerts.append({
                'rule': 'micro_leak',
                'title': 'דליפת מיקרו',
                'description': (
                    f"{len(txns)} עסקאות קטנות בקטגוריה '{category}' "
                    f"בחודש {month}: סה״כ ₪{total:.2f}"
                ),
                'amount': total,
                'transaction_id': None,
            })
    return alerts
