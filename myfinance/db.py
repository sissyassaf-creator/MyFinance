"""MyFinance v1 — SQLite database: connection, schema, CRUD, backups."""

import shutil
import sqlite3
from datetime import datetime
from pathlib import Path

from myfinance.config import BACKUP_DIR, DATA_DIR, DB_PATH, MAX_BACKUPS

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id    TEXT PRIMARY KEY,
    date              TEXT NOT NULL,
    charge_date       TEXT,
    merchant          TEXT NOT NULL,
    raw_description   TEXT,
    amount_ils        REAL NOT NULL,
    amount_original   REAL,
    currency_original TEXT,
    payment_method    TEXT DEFAULT 'regular',
    installment_number INTEGER,
    installments_total INTEGER,
    category          TEXT NOT NULL DEFAULT 'לא מזוהה',
    needs_review      INTEGER NOT NULL DEFAULT 1,
    source            TEXT NOT NULL,
    created_at        TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);

CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(date);
CREATE INDEX IF NOT EXISTS idx_transactions_category ON transactions(category);
CREATE INDEX IF NOT EXISTS idx_transactions_source ON transactions(source);
CREATE INDEX IF NOT EXISTS idx_transactions_merchant ON transactions(merchant);
CREATE INDEX IF NOT EXISTS idx_transactions_needs_review ON transactions(needs_review);

CREATE TABLE IF NOT EXISTS merchant_map (
    merchant_name     TEXT PRIMARY KEY,
    category          TEXT NOT NULL,
    confirmed_by      TEXT NOT NULL DEFAULT 'api',
    created_at        TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    updated_at        TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS processing_log (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path         TEXT NOT NULL,
    file_hash         TEXT NOT NULL,
    source            TEXT NOT NULL,
    rows_total        INTEGER NOT NULL,
    rows_new          INTEGER NOT NULL,
    rows_duplicate    INTEGER NOT NULL,
    processed_at      TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    status            TEXT NOT NULL DEFAULT 'success'
);

CREATE INDEX IF NOT EXISTS idx_processing_log_file_hash ON processing_log(file_hash);
"""


def get_connection() -> sqlite3.Connection:
    """Get a SQLite connection with row factory enabled."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    """Create tables and indexes if they don't exist."""
    conn = get_connection()
    conn.executescript(SCHEMA_SQL)
    conn.close()


def backup_db():
    """Copy the database file to backups/ with a timestamp. Prune old backups."""
    if not DB_PATH.exists():
        return

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUP_DIR / f"myfinance_{timestamp}.db"
    shutil.copy2(str(DB_PATH), str(backup_path))

    # Prune old backups, keep last MAX_BACKUPS
    backups = sorted(BACKUP_DIR.glob("myfinance_*.db"), key=lambda p: p.name)
    while len(backups) > MAX_BACKUPS:
        backups.pop(0).unlink()


# ── Transaction CRUD ───────────────────────────────────

def insert_transactions(conn: sqlite3.Connection, transactions: list[dict]) -> int:
    """Insert transactions, skipping duplicates. Returns count of new rows."""
    inserted = 0
    for txn in transactions:
        try:
            conn.execute(
                """INSERT INTO transactions
                   (transaction_id, date, charge_date, merchant, raw_description,
                    amount_ils, amount_original, currency_original, payment_method,
                    installment_number, installments_total, category, needs_review, source)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    txn['transaction_id'],
                    txn['date'],
                    txn.get('charge_date'),
                    txn['merchant'],
                    txn.get('raw_description', ''),
                    txn['amount_ils'],
                    txn.get('amount_original'),
                    txn.get('currency_original'),
                    txn.get('payment_method', 'regular'),
                    txn.get('installment_number'),
                    txn.get('installments_total'),
                    txn.get('category', 'לא מזוהה'),
                    txn.get('needs_review', 1),
                    txn['source'],
                ),
            )
            inserted += 1
        except sqlite3.IntegrityError:
            # Duplicate transaction_id — skip
            pass
    conn.commit()
    return inserted


def transaction_exists(conn: sqlite3.Connection, transaction_id: str) -> bool:
    """Check if a transaction already exists by its hash."""
    row = conn.execute(
        "SELECT 1 FROM transactions WHERE transaction_id = ?",
        (transaction_id,),
    ).fetchone()
    return row is not None


def get_transactions(
    conn: sqlite3.Connection,
    month: str | None = None,
    category: str | None = None,
    source: str | None = None,
    needs_review: bool | None = None,
    min_amount: float | None = None,
    max_amount: float | None = None,
) -> list[dict]:
    """Query transactions with optional filters. Returns list of dicts."""
    query = "SELECT * FROM transactions WHERE 1=1"
    params: list = []

    if month:
        query += " AND strftime('%Y-%m', date) = ?"
        params.append(month)
    if category:
        query += " AND category = ?"
        params.append(category)
    if source:
        query += " AND source = ?"
        params.append(source)
    if needs_review is not None:
        query += " AND needs_review = ?"
        params.append(1 if needs_review else 0)
    if min_amount is not None:
        query += " AND amount_ils >= ?"
        params.append(min_amount)
    if max_amount is not None:
        query += " AND amount_ils <= ?"
        params.append(max_amount)

    query += " ORDER BY date DESC"
    rows = conn.execute(query, params).fetchall()
    return [dict(row) for row in rows]


def update_transaction_category(
    conn: sqlite3.Connection, transaction_id: str, category: str
):
    """Update a transaction's category and mark as reviewed."""
    conn.execute(
        "UPDATE transactions SET category = ?, needs_review = 0 WHERE transaction_id = ?",
        (category, transaction_id),
    )
    conn.commit()


# ── Merchant Map CRUD ──────────────────────────────────

def get_merchant_category(conn: sqlite3.Connection, merchant_name: str) -> str | None:
    """Look up cached category for a normalized merchant name."""
    row = conn.execute(
        "SELECT category FROM merchant_map WHERE merchant_name = ?",
        (merchant_name,),
    ).fetchone()
    return row['category'] if row else None


def upsert_merchant_map(
    conn: sqlite3.Connection,
    merchant_name: str,
    category: str,
    confirmed_by: str = 'api',
):
    """Insert or update a merchant → category mapping."""
    conn.execute(
        """INSERT INTO merchant_map (merchant_name, category, confirmed_by, updated_at)
           VALUES (?, ?, ?, datetime('now', 'localtime'))
           ON CONFLICT(merchant_name) DO UPDATE SET
               category = excluded.category,
               confirmed_by = excluded.confirmed_by,
               updated_at = datetime('now', 'localtime')""",
        (merchant_name, category, confirmed_by),
    )
    conn.commit()


def get_all_merchant_mappings(conn: sqlite3.Connection) -> dict[str, str]:
    """Return full merchant map as {merchant_name: category}."""
    rows = conn.execute("SELECT merchant_name, category FROM merchant_map").fetchall()
    return {row['merchant_name']: row['category'] for row in rows}


# ── Processing Log CRUD ────────────────────────────────

def file_already_processed(conn: sqlite3.Connection, file_hash: str) -> bool:
    """Check if a file with this content hash was already processed."""
    row = conn.execute(
        "SELECT 1 FROM processing_log WHERE file_hash = ? AND status = 'success'",
        (file_hash,),
    ).fetchone()
    return row is not None


def log_processing(
    conn: sqlite3.Connection,
    file_path: str,
    file_hash: str,
    source: str,
    rows_total: int,
    rows_new: int,
    rows_duplicate: int,
    status: str = 'success',
):
    """Record a file processing event."""
    conn.execute(
        """INSERT INTO processing_log
           (file_path, file_hash, source, rows_total, rows_new, rows_duplicate, status)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (file_path, file_hash, source, rows_total, rows_new, rows_duplicate, status),
    )
    conn.commit()


# ── Stats ──────────────────────────────────────────────

def get_stats(conn: sqlite3.Connection) -> dict:
    """Get database stats for the sidebar."""
    total = conn.execute("SELECT COUNT(*) as c FROM transactions").fetchone()['c']
    pending = conn.execute(
        "SELECT COUNT(*) as c FROM transactions WHERE needs_review = 1"
    ).fetchone()['c']

    date_range = conn.execute(
        "SELECT MIN(date) as min_date, MAX(date) as max_date FROM transactions"
    ).fetchone()

    last_run = conn.execute(
        "SELECT processed_at FROM processing_log ORDER BY id DESC LIMIT 1"
    ).fetchone()

    return {
        'total_transactions': total,
        'pending_review': pending,
        'min_date': date_range['min_date'],
        'max_date': date_range['max_date'],
        'last_run': last_run['processed_at'] if last_run else None,
    }
