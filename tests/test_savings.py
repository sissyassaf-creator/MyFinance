"""Tests for savings detection rules."""

from myfinance.processing.savings import detect_savings


def test_bank_fee_detection():
    txns = [
        {'merchant': 'עמלת כרטיס אשראי', 'raw_description': '', 'amount_ils': 12.90,
         'date': '2026-03-25', 'category': 'העברות ותשלומים', 'transaction_id': 'x1'},
        {'merchant': 'שופרסל', 'raw_description': '', 'amount_ils': 350.0,
         'date': '2026-03-05', 'category': 'מזון ושוק', 'transaction_id': 'x2'},
    ]
    alerts = detect_savings(txns)
    fee_alerts = [a for a in alerts if a['rule'] == 'bank_fee']
    assert len(fee_alerts) == 1
    assert fee_alerts[0]['amount'] == 12.90


def test_duplicate_payment_detection():
    txns = [
        {'merchant': 'בית מרקחת', 'raw_description': '', 'amount_ils': 28.0,
         'date': '2026-03-24', 'category': 'בריאות', 'transaction_id': 'x1'},
        {'merchant': 'בית מרקחת', 'raw_description': '', 'amount_ils': 28.0,
         'date': '2026-03-24', 'category': 'בריאות', 'transaction_id': 'x2'},
    ]
    alerts = detect_savings(txns)
    dup_alerts = [a for a in alerts if a['rule'] == 'duplicate_payment']
    assert len(dup_alerts) == 1


def test_no_duplicate_for_different_amounts():
    txns = [
        {'merchant': 'שופרסל', 'raw_description': '', 'amount_ils': 350.0,
         'date': '2026-03-05', 'category': 'מזון ושוק', 'transaction_id': 'x1'},
        {'merchant': 'שופרסל', 'raw_description': '', 'amount_ils': 280.0,
         'date': '2026-03-06', 'category': 'מזון ושוק', 'transaction_id': 'x2'},
    ]
    alerts = detect_savings(txns)
    dup_alerts = [a for a in alerts if a['rule'] == 'duplicate_payment']
    assert len(dup_alerts) == 0


def test_micro_leak_detection():
    txns = [
        {'merchant': f'חנות {i}', 'raw_description': '', 'amount_ils': 40.0,
         'date': '2026-03-01', 'category': 'מזון ושוק', 'transaction_id': f'x{i}'}
        for i in range(10)
    ]  # 10 x 40 = 400 > 300 threshold
    alerts = detect_savings(txns)
    leak_alerts = [a for a in alerts if a['rule'] == 'micro_leak']
    assert len(leak_alerts) == 1
    assert leak_alerts[0]['amount'] == 400.0


def test_no_micro_leak_below_threshold():
    txns = [
        {'merchant': f'חנות {i}', 'raw_description': '', 'amount_ils': 40.0,
         'date': '2026-03-01', 'category': 'מזון ושוק', 'transaction_id': f'x{i}'}
        for i in range(5)
    ]  # 5 x 40 = 200 < 300 threshold
    alerts = detect_savings(txns)
    leak_alerts = [a for a in alerts if a['rule'] == 'micro_leak']
    assert len(leak_alerts) == 0
