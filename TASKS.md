# MyFinance — Tasks (v1)

## Phase 1: Project Setup
- [x] Create project directory and GitHub repo
- [x] Create documentation files (DESIGN, ARCHITECTURE, TOOLCHAIN, TASKS, PROGRESS)
- [x] Create directory structure (input/, data/, backups/)
- [x] Write detailed v1 architecture
- [ ] Create requirements.txt with pinned dependencies
- [ ] Create pyproject.toml with entry points
- [ ] Create .env.example
- [ ] Create .gitignore (complete version)
- [ ] Create myfinance/ package skeleton (__init__.py, config.py)

## Phase 2: Database & Core
- [ ] db.py — SQLite connection, init_db(), backup_db(), CRUD functions
- [ ] config.py — all constants, categories, paths, column mappings

## Phase 3: Parsers
- [ ] parsers/base.py — BaseParser ABC with read_file, _parse_date, _parse_amount
- [ ] parsers/visa.py — VisaParser with column mapping + installment parsing
- [ ] parsers/max_parser.py — MaxParser with column mapping
- [ ] parsers/__init__.py — PARSER_REGISTRY
- [ ] Unit tests for both parsers with sample CSV files

## Phase 4: Processing Pipeline
- [ ] processing/dedup.py — SHA256 hash generation, duplicate check
- [ ] processing/categorizer.py — Claude API integration, merchant cache, batch logic
- [ ] processing/savings.py — 3 savings rules (bank fees, duplicates, micro leaks)
- [ ] processing/pipeline.py — orchestrator (detect → parse → dedup → categorize → store)
- [ ] Unit tests for dedup, categorizer (mocked), savings

## Phase 5: CLI
- [ ] cli.py — process, dashboard, export commands with argparse
- [ ] Integration test: end-to-end pipeline with sample data

## Phase 6: Dashboard
- [ ] dashboard/app.py — Dash app factory with MantineProvider RTL
- [ ] dashboard/sidebar.py — process button, stats, last run
- [ ] dashboard/tab_overview.py — pie chart, bar chart, stats cards, top merchants
- [ ] dashboard/tab_transactions.py — ag-grid with filters and inline category editing
- [ ] dashboard/callbacks.py — all callback registrations
- [ ] Manual testing with real data

## Phase 7: Export & Polish
- [ ] export.py — monthly Excel export
- [ ] Error handling review (all error matrix cases)
- [ ] User confirmation before first API call
- [ ] End-to-end test with real credit card files
- [ ] Tag v1.0.0
