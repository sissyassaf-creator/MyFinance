"""Tests for categorization logic (API mocked)."""

from unittest.mock import MagicMock, patch

from myfinance.processing.categorizer import (
    normalize_merchant,
    strip_sensitive,
)


def test_normalize_removes_store_id():
    assert normalize_merchant('שופרסל דיל 1234') == 'שופרסל דיל'
    assert normalize_merchant('רמי לוי שיווק 567') == 'רמי לוי שיווק'


def test_normalize_preserves_short_numbers():
    # Single digits should not be removed
    assert normalize_merchant('סופר 7') == 'סופר 7'


def test_normalize_collapses_spaces():
    assert normalize_merchant('שופרסל   דיל') == 'שופרסל דיל'


def test_normalize_casefolds_latin():
    assert normalize_merchant('AMAZON.COM') == 'amazon.com'
    assert normalize_merchant('Netflix') == 'netflix'


def test_strip_sensitive_card_numbers():
    assert '****' in strip_sensitive('משכורת 1234-5678-9012-3456')
    assert '****' in strip_sensitive('חשבון 123456789')


def test_strip_sensitive_preserves_short():
    assert strip_sensitive('שופרסל 123') == 'שופרסל 123'


def test_categorize_with_cache(tmp_db):
    """Test that cached merchants don't trigger API calls."""
    from myfinance.db import upsert_merchant_map
    from myfinance.processing.categorizer import categorize_transactions

    # Pre-cache a merchant
    upsert_merchant_map(tmp_db, 'שופרסל דיל', 'מזון ושוק', 'user')

    txns = [
        {'merchant': 'שופרסל דיל 1234', 'amount_ils': 350.0},
    ]

    with patch('myfinance.processing.categorizer._categorize_via_api') as mock_api:
        categorize_transactions(txns, tmp_db, skip_api=False)
        mock_api.assert_not_called()

    assert txns[0]['category'] == 'מזון ושוק'
    assert txns[0]['needs_review'] == 0
