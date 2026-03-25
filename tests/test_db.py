"""Tests for database CRUD operations."""

from myfinance.db import (
    file_already_processed,
    get_merchant_category,
    get_stats,
    get_transactions,
    insert_transactions,
    log_processing,
    transaction_exists,
    update_transaction_category,
    upsert_merchant_map,
)


def test_insert_and_query(tmp_db, sample_transactions):
    inserted = insert_transactions(tmp_db, sample_transactions)
    assert inserted == 2

    txns = get_transactions(tmp_db)
    assert len(txns) == 2


def test_insert_skips_duplicates(tmp_db, sample_transactions):
    insert_transactions(tmp_db, sample_transactions)
    inserted_again = insert_transactions(tmp_db, sample_transactions)
    assert inserted_again == 0


def test_transaction_exists(tmp_db, sample_transactions):
    insert_transactions(tmp_db, sample_transactions)
    assert transaction_exists(tmp_db, 'abc123') is True
    assert transaction_exists(tmp_db, 'nonexistent') is False


def test_update_category(tmp_db, sample_transactions):
    insert_transactions(tmp_db, sample_transactions)
    update_transaction_category(tmp_db, 'abc123', 'דלק ותחבורה')

    txns = get_transactions(tmp_db)
    txn = [t for t in txns if t['transaction_id'] == 'abc123'][0]
    assert txn['category'] == 'דלק ותחבורה'
    assert txn['needs_review'] == 0


def test_merchant_map(tmp_db):
    assert get_merchant_category(tmp_db, 'שופרסל') is None

    upsert_merchant_map(tmp_db, 'שופרסל', 'מזון ושוק', 'api')
    assert get_merchant_category(tmp_db, 'שופרסל') == 'מזון ושוק'

    upsert_merchant_map(tmp_db, 'שופרסל', 'קניות אונליין', 'user')
    assert get_merchant_category(tmp_db, 'שופרסל') == 'קניות אונליין'


def test_processing_log(tmp_db):
    assert file_already_processed(tmp_db, 'hash123') is False

    log_processing(tmp_db, 'test.csv', 'hash123', 'visa-mizrahi', 10, 8, 2)
    assert file_already_processed(tmp_db, 'hash123') is True


def test_filter_by_month(tmp_db, sample_transactions):
    insert_transactions(tmp_db, sample_transactions)
    txns = get_transactions(tmp_db, month='2026-03')
    assert len(txns) == 2

    txns = get_transactions(tmp_db, month='2026-04')
    assert len(txns) == 0


def test_stats(tmp_db, sample_transactions):
    insert_transactions(tmp_db, sample_transactions)
    stats = get_stats(tmp_db)
    assert stats['total_transactions'] == 2
    assert stats['pending_review'] == 0
