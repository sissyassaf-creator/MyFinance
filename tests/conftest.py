"""Shared test fixtures."""

import sqlite3
import tempfile
from pathlib import Path

import pytest

from myfinance.db import SCHEMA_SQL


@pytest.fixture
def tmp_db(tmp_path, monkeypatch):
    """Create a temporary SQLite database for testing."""
    db_path = tmp_path / "test.db"
    monkeypatch.setattr("myfinance.config.DB_PATH", db_path)
    monkeypatch.setattr("myfinance.config.DATA_DIR", tmp_path)
    monkeypatch.setattr("myfinance.config.BACKUP_DIR", tmp_path / "backups")

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA_SQL)
    yield conn
    conn.close()


@pytest.fixture
def sample_data_dir():
    """Path to test sample data files."""
    return Path(__file__).parent / "sample_data"


@pytest.fixture
def sample_transactions():
    """A list of sample transaction dicts."""
    return [
        {
            'transaction_id': 'abc123',
            'date': '2026-03-05',
            'charge_date': '2026-04-10',
            'merchant': 'שופרסל דיל 1234',
            'raw_description': 'קניות',
            'amount_ils': 350.00,
            'amount_original': None,
            'currency_original': None,
            'payment_method': 'regular',
            'installment_number': None,
            'installments_total': None,
            'category': 'מזון ושוק',
            'needs_review': 0,
            'source': 'visa-mizrahi',
        },
        {
            'transaction_id': 'def456',
            'date': '2026-03-07',
            'charge_date': '2026-04-10',
            'merchant': 'פיצה האט תל אביב',
            'raw_description': '',
            'amount_ils': 89.90,
            'amount_original': None,
            'currency_original': None,
            'payment_method': 'regular',
            'installment_number': None,
            'installments_total': None,
            'category': 'מסעדות ובילויים',
            'needs_review': 0,
            'source': 'visa-mizrahi',
        },
    ]
