# MyFinance — Progress

## 2026-03-25

### Session 1 — Project Initialization
- Created project directory at `~/claude-code/MyFinance/`
- Initialized git repo with .gitignore
- Created initial documentation files
- Wrote PRODUCT_DEFINITION.md covering v1 through v4

### Session 2 — v1 Architecture Design
- Rewrote ARCHITECTURE.md with complete v1 technical architecture covering:
  - Project file structure (every file and folder)
  - Module architecture with dependency graph
  - Data flow diagram (file drop → dashboard)
  - SQLite schema (3 tables with exact CREATE TABLE statements)
  - Parser interface (BaseParser ABC + VisaParser + MaxParser)
  - Categorization module (Claude API batching, merchant cache, prompt design)
  - Dashboard layout (Dash + DMC + ag-grid, 2 tabs, component hierarchy)
  - Configuration split (.env vs config.py)
  - CLI entry points (process, dashboard, export)
  - Error handling matrix (15 error types with handling strategy)
  - Testing strategy (unit + integration, sample data approach)
- Updated DESIGN.md, TOOLCHAIN.md, TASKS.md to align with v1 scope
- Key decisions documented: batch by unique merchant, conservative normalization,
  synchronous dashboard refresh, SQLite with ISO date strings
- **Next step:** Create requirements.txt and package skeleton, then start Phase 2 (db.py + config.py)
