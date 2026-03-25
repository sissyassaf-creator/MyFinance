"""CLI entry points: process, dashboard, export."""

import argparse
import sys


def main():
    parser = argparse.ArgumentParser(
        prog='myfinance',
        description='MyFinance — הכספים שלך, במחשב שלך',
    )
    subparsers = parser.add_subparsers(dest='command', required=True)

    # ── process ─────────────────────────────────────
    proc_parser = subparsers.add_parser('process', help='Process new files from input folders')
    proc_parser.add_argument(
        '--source', choices=['visa-mizrahi', 'diners-el-al', 'max'],
        help='Process only a specific source (default: all)',
    )
    proc_parser.add_argument(
        '--dry-run', action='store_true',
        help='Parse and show results without writing to DB',
    )
    proc_parser.add_argument(
        '--no-api', action='store_true',
        help='Skip Claude API categorization (mark all as unrecognized)',
    )

    # ── dashboard ───────────────────────────────────
    dash_parser = subparsers.add_parser('dashboard', help='Launch the dashboard')
    dash_parser.add_argument('--port', type=int, default=8050, help='Port (default: 8050)')
    dash_parser.add_argument('--debug', action='store_true', help='Enable Dash debug mode')

    # ── export ──────────────────────────────────────
    export_parser = subparsers.add_parser('export', help='Export transactions to Excel')
    export_parser.add_argument(
        '--month', type=str,
        help='Month in YYYY-MM format (default: current month)',
    )

    args = parser.parse_args()

    if args.command == 'process':
        _run_process(args)
    elif args.command == 'dashboard':
        _run_dashboard(args)
    elif args.command == 'export':
        _run_export(args)


def _run_process(args):
    from dotenv import load_dotenv
    load_dotenv()

    from myfinance.db import backup_db, init_db
    from myfinance.processing.pipeline import run_pipeline

    init_db()
    backup_db()

    print("\n🔄 מעבד קבצים חדשים...\n")

    result = run_pipeline(
        source_filter=args.source,
        dry_run=args.dry_run,
        skip_api=args.no_api,
    )

    print(f"\n{'=' * 40}")
    if args.dry_run:
        print("  [DRY RUN — לא נשמר לבסיס נתונים]")
    print(f"  קבצים שעובדו: {result['files_processed']}")
    print(f"  עסקאות חדשות: {result['new_transactions']}")
    print(f"  כפילויות שדולגו: {result['duplicates_skipped']}")
    if result['errors']:
        print(f"\n  שגיאות:")
        for err in result['errors']:
            print(f"    ✗ {err}")
    if result.get('savings_alerts'):
        print(f"\n  הצעות חיסכון:")
        for alert in result['savings_alerts']:
            print(f"    💡 {alert['title']}: {alert['description']}")
    print(f"{'=' * 40}\n")


def _run_dashboard(args):
    from dotenv import load_dotenv
    load_dotenv()

    from myfinance.db import init_db
    init_db()

    from myfinance.dashboard.app import create_app

    app = create_app()
    print(f"\n🚀 Dashboard running at http://127.0.0.1:{args.port}\n")
    app.run(host="127.0.0.1", port=args.port, debug=args.debug)


def _run_export(args):
    from dotenv import load_dotenv
    load_dotenv()

    from datetime import datetime

    from myfinance.db import init_db
    init_db()

    month = args.month or datetime.now().strftime('%Y-%m')
    from myfinance.export import export_month
    output_path = export_month(month)
    if output_path:
        print(f"\n✓ Exported to: {output_path}\n")
    else:
        print(f"\nאין עסקאות לחודש {month}\n")


if __name__ == '__main__':
    main()
