"""Processing pipeline orchestrator: detect → parse → dedup → categorize → store."""

from pathlib import Path

from myfinance.config import INPUT_DIR, SOURCES, SUPPORTED_EXTENSIONS
from myfinance.db import (
    file_already_processed,
    get_connection,
    insert_transactions,
    log_processing,
)
from myfinance.parsers import PARSER_REGISTRY
from myfinance.processing.categorizer import categorize_transactions
from myfinance.processing.dedup import compute_file_hash, compute_transaction_hash
from myfinance.processing.savings import detect_savings


def run_pipeline(
    source_filter: str | None = None,
    dry_run: bool = False,
    skip_api: bool = False,
) -> dict:
    """Run the full processing pipeline.

    Args:
        source_filter: Process only this source (e.g. 'visa-mizrahi'), or None for all.
        dry_run: Parse and show results without writing to DB.
        skip_api: Skip Claude API calls, mark all as unrecognized.

    Returns:
        Summary dict with counts and savings alerts.
    """
    conn = get_connection()
    result = {
        'files_processed': 0,
        'new_transactions': 0,
        'duplicates_skipped': 0,
        'errors': [],
        'savings_alerts': [],
    }

    sources = {source_filter: SOURCES[source_filter]} if source_filter else SOURCES

    all_new_transactions = []

    for source_key in sources:
        source_dir = INPUT_DIR / source_key
        if not source_dir.exists():
            continue

        parser = PARSER_REGISTRY.get(source_key)
        if not parser:
            result['errors'].append(f"No parser for source: {source_key}")
            continue

        # Find files to process
        files = [
            f for f in source_dir.iterdir()
            if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS
        ]

        for file_path in files:
            try:
                file_hash = compute_file_hash(file_path)

                # Skip already-processed files
                if file_already_processed(conn, file_hash):
                    print(f"  דילוג (כבר עובד): {file_path.name}")
                    continue

                print(f"  מעבד: {file_path.name} [{source_key}]")

                # Parse
                raw_transactions = parser.parse(file_path)
                rows_total = len(raw_transactions)

                if rows_total == 0:
                    print(f"    אין עסקאות בקובץ")
                    log_processing(
                        conn, str(file_path.relative_to(INPUT_DIR.parent)),
                        file_hash, source_key, 0, 0, 0, 'success',
                    )
                    result['files_processed'] += 1
                    continue

                # Dedup — compute hashes and filter existing
                new_transactions = []
                duplicates = 0
                for txn in raw_transactions:
                    txn['transaction_id'] = compute_transaction_hash(txn)
                    from myfinance.db import transaction_exists
                    if transaction_exists(conn, txn['transaction_id']):
                        duplicates += 1
                    else:
                        new_transactions.append(txn)

                if dry_run:
                    print(f"    [DRY RUN] {len(new_transactions)} חדשות, {duplicates} כפילויות")
                    result['files_processed'] += 1
                    result['new_transactions'] += len(new_transactions)
                    result['duplicates_skipped'] += duplicates
                    continue

                # Categorize
                if new_transactions:
                    categorize_transactions(new_transactions, conn, skip_api=skip_api)

                    # Store
                    inserted = insert_transactions(conn, new_transactions)
                    all_new_transactions.extend(new_transactions)
                else:
                    inserted = 0

                # Log
                log_processing(
                    conn, str(file_path.relative_to(INPUT_DIR.parent)),
                    file_hash, source_key, rows_total, inserted, duplicates, 'success',
                )

                result['files_processed'] += 1
                result['new_transactions'] += inserted
                result['duplicates_skipped'] += duplicates

                print(f"    ✓ {inserted} חדשות, {duplicates} כפילויות")

            except Exception as e:
                error_msg = f"Error processing {file_path.name}: {e}"
                print(f"    ✗ {error_msg}")
                result['errors'].append(error_msg)
                try:
                    log_processing(
                        conn, str(file_path.name), '', source_key, 0, 0, 0, 'error',
                    )
                except Exception:
                    pass

    # Run savings detection on all new transactions
    if all_new_transactions and not dry_run:
        result['savings_alerts'] = detect_savings(all_new_transactions)

    conn.close()
    return result
