"""Deduplication logic using SHA256 hashing."""

import hashlib


def compute_transaction_hash(txn: dict) -> str:
    """Compute a SHA256 hash for deduplication.

    Hash is based on: date + merchant + amount + source.
    This ensures the same transaction from the same source is not imported twice.
    """
    raw = f"{txn['date']}|{txn['merchant']}|{txn['amount_ils']:.2f}|{txn['source']}"
    return hashlib.sha256(raw.encode('utf-8')).hexdigest()


def compute_file_hash(file_path) -> str:
    """Compute SHA256 of file content to detect re-drops."""
    h = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()
