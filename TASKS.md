# MyFinance — Tasks (v1)

## Phase 1: Project Setup
- [x] Create project directory and GitHub repo
- [x] Create documentation files (DESIGN, ARCHITECTURE, TOOLCHAIN, TASKS, PROGRESS)
- [x] Create directory structure (input/, data/, backups/)
- [x] Write detailed v1 architecture
- [x] Create requirements.txt with pinned dependencies
- [x] Create pyproject.toml with entry points
- [x] Create .env.example
- [x] Create .gitignore (complete version)
- [x] Create myfinance/ package skeleton (__init__.py, config.py)

## Phase 2: Database & Core
- [x] db.py — SQLite connection, init_db(), backup_db(), CRUD functions
- [x] config.py — all constants, categories, paths, column mappings

## Phase 3: Parsers
- [x] parsers/base.py — BaseParser ABC with read_file, _parse_date, _parse_amount
- [x] parsers/visa.py — VisaParser with column mapping + installment parsing
- [x] parsers/max_parser.py — MaxParser with column mapping
- [x] parsers/__init__.py — PARSER_REGISTRY
- [x] Unit tests for both parsers with sample CSV files

## Phase 4: Processing Pipeline
- [x] processing/dedup.py — SHA256 hash generation, duplicate check
- [x] processing/categorizer.py — Claude API integration, merchant cache, batch logic
- [x] processing/savings.py — 3 savings rules (bank fees, duplicates, micro leaks)
- [x] processing/pipeline.py — orchestrator (detect → parse → dedup → categorize → store)
- [x] Unit tests for dedup, categorizer (mocked), savings

## Phase 5: CLI
- [x] cli.py — process, dashboard, export commands with argparse
- [x] Integration test: end-to-end pipeline with sample data

## Phase 6: Dashboard
- [x] dashboard/app.py — Dash app factory with MantineProvider RTL
- [x] dashboard/sidebar.py — process button, stats, last run
- [x] dashboard/tab_overview.py — pie chart, bar chart, stats cards, top merchants
- [x] dashboard/tab_transactions.py — ag-grid with filters and inline category editing
- [x] dashboard/callbacks.py — all callback registrations

## Phase 7: Export & Polish
- [x] export.py — monthly Excel export
- [x] User confirmation before first API call
- [x] 31 unit tests passing (parsers, db, dedup, categorizer, savings)
- [x] Tag v1.0.0
- [ ] End-to-end test with real credit card files
