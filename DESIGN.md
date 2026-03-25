# MyFinance — Design Document

## Goal

A local, privacy-first Python application for Israeli households that imports
credit card transactions from CSV/Excel files, categorizes them with Claude AI,
and presents everything in a Hebrew RTL dashboard with savings detection.

**Tagline:** הכספים שלך, במחשב שלך (Your finances, on your computer)

## Key Principles

- **Privacy first**: All data stays on the local machine. Only merchant names (stripped of sensitive info) are sent to Anthropic API.
- **Minimal cost**: Claude Sonnet for categorization, merchant cache avoids repeat calls. ~1-3 ILS/month.
- **Hebrew native**: All categories, UI labels, and exports are in Hebrew with RTL layout.
- **Append-only data**: Transactions are never deleted, only appended and deduplicated.
- **User confirmation**: Unrecognized categories require user approval before being finalized.
- **Thin v1 slice**: Ship end-to-end flow, use with real data for 1-2 months, then build more.

## Constraints

- v1 supports CSV/Excel only (no PDF, no images, no OCR)
- 3 credit card sources (Visa Mizrahi, Diners El Al, Max) — no bank statements
- 2 parsers: Visa parser (covers Visa Mizrahi + Diners El Al), Max parser
- 12 Hebrew categories
- SQLite storage (3 tables)
- macOS local app, Python 3.11+
- No cross-source deduplication (only credit cards, no overlap risk)

## Sources (v1)

| Source | Folder | Parser |
|--------|--------|--------|
| Visa Mizrahi Tefahot | `input/visa-mizrahi/` | VisaParser |
| Diners El Al | `input/diners-el-al/` | VisaParser (same format) |
| Max | `input/max/` | MaxParser |

## Output

- Plotly Dash dashboard on localhost:8050 (RTL, 2 tabs)
- Monthly Excel export: `הוצאות_YYYY_MM.xlsx`
