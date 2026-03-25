"""Tests for deduplication logic."""

from myfinance.processing.dedup import compute_file_hash, compute_transaction_hash


def test_same_transaction_same_hash():
    txn = {'date': '2026-03-05', 'merchant': 'שופרסל', 'amount_ils': 350.0, 'source': 'visa-mizrahi'}
    h1 = compute_transaction_hash(txn)
    h2 = compute_transaction_hash(txn)
    assert h1 == h2


def test_different_amount_different_hash():
    txn1 = {'date': '2026-03-05', 'merchant': 'שופרסל', 'amount_ils': 350.0, 'source': 'visa-mizrahi'}
    txn2 = {'date': '2026-03-05', 'merchant': 'שופרסל', 'amount_ils': 351.0, 'source': 'visa-mizrahi'}
    assert compute_transaction_hash(txn1) != compute_transaction_hash(txn2)


def test_different_source_different_hash():
    txn1 = {'date': '2026-03-05', 'merchant': 'שופרסל', 'amount_ils': 350.0, 'source': 'visa-mizrahi'}
    txn2 = {'date': '2026-03-05', 'merchant': 'שופרסל', 'amount_ils': 350.0, 'source': 'max'}
    assert compute_transaction_hash(txn1) != compute_transaction_hash(txn2)


def test_file_hash(tmp_path):
    f1 = tmp_path / "a.csv"
    f2 = tmp_path / "b.csv"
    f1.write_text("hello")
    f2.write_text("hello")
    assert compute_file_hash(f1) == compute_file_hash(f2)

    f2.write_text("world")
    assert compute_file_hash(f1) != compute_file_hash(f2)
