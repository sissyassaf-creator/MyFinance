# MyFinance — Design Document

## Goal

A local Python agent that reads financial documents from four Israeli sources
(Bank Mizrahi Tefahot, Visa Mizrahi Tefahot, Diners El Al, Max),
extracts all transactions, categorizes them, detects savings opportunities,
and presents everything in a dynamic Hebrew RTL dashboard with Excel export.

## Key Principles

- **Privacy first**: All data stays on the local machine. The only external
  connection is to the Anthropic API for document parsing and categorization.
- **Minimal cost**: Estimated under $0.50 per monthly run via Anthropic API.
- **Hebrew native**: All categories, UI labels, and exports are in Hebrew with RTL layout.
- **Append-only data**: Transactions are never deleted, only appended and deduplicated.
- **User confirmation**: Unrecognized categories require user approval before being finalized.

## Constraints

- Must support PDF (text and scanned), images (jpg/png), and Excel/CSV inputs.
- Deduplication uses a 3-day date window to handle overlapping bank/card statements.
- Merchant category cache avoids redundant API calls.
- Automatic backup before every write operation.
- API key loaded from environment variable only, never hardcoded.

## Sources

| Source | Folder |
|--------|--------|
| Bank Mizrahi Tefahot | `input/bank-mizrahi/` |
| Visa Mizrahi Tefahot | `input/visa-mizrahi/` |
| Diners El Al | `input/diners-el-al/` |
| Max | `input/max/` |

## Output

- Streamlit dashboard on localhost
- Monthly Excel export: `הוצאות_YYYY_MM.xlsx` with sheets for transactions and savings suggestions
