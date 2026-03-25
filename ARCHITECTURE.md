# MyFinance — Architecture

## System Overview

```
input/          Processing Pipeline         Data Layer          Dashboard
───────────     ──────────────────         ──────────          ─────────
bank-mizrahi/                              transactions.json
visa-mizrahi/   detect → extract →         processed_log.json   Streamlit
diners-el-al/   dedup → categorize →       merchant_map.json    (5 tabs)
max/            savings → export           savings.json         Excel
```

## Processing Pipeline (6 stages)

1. **File Detection**: Identify file type (PDF/image/Excel/CSV) and source folder
2. **Extraction**: pdfplumber for text PDFs, Claude Vision for scanned PDFs and images, pandas for Excel/CSV
3. **Deduplication**: SHA256 hash per transaction, 3-day date window matching for cross-source dedup
4. **Categorization**: Claude API classifies into 15 Hebrew categories; merchant_map.json caches confirmed mappings
5. **Savings Detection**: 5 rule-based checks (duplicate subscriptions, bank fees, category spikes, unused subscriptions, micro leaks)
6. **Export**: Append to transactions.json, generate monthly Excel, update dashboard data

## Transaction Data Model

| Field | Type | Description |
|-------|------|-------------|
| date | date | Transaction date |
| charge_date | date | Charge/billing date |
| merchant | string | Merchant name |
| raw_description | string | Original description from statement |
| amount_ils | float | Amount in ILS |
| amount_original | float | Original amount (if foreign currency) |
| currency_original | string | Original currency code |
| payment_method | enum | regular / credit / installments / immediate_debit |
| installment_number | int | Current installment number |
| installments_total | int | Total installments |
| transaction_type | enum | one_time / recurring |
| category | string | Hebrew category (1 of 15) |
| needs_review | bool | True if category unrecognized |
| source | string | Institution name |
| transaction_id | string | SHA256 hash for deduplication |

## 15 Categories (Hebrew)

מזון ושוק, מסעדות ובילויים, דלק ותחבורה, בריאות, חינוך,
תחזוקת בית, התחייבויות קבועות, מנויים ודיגיטל, ביגוד והנעלה,
חיות מחמד, חופשות ונסיעות, תרומות, ביט והעברות,
קניות אונליין, לא מזוהה

## Savings Detection Rules

1. **Duplicate subscriptions**: ≥3 active recurring subscriptions in the same month
2. **Bank fees**: Any charge containing fee/commission keywords
3. **Category spikes**: Category exceeds 150% of its monthly average
4. **Unused subscriptions**: Recurring charge with no other activity from same merchant in 3 months
5. **Micro leaks**: Transactions <50 ILS in one category totaling >300 ILS/month

## Dashboard (Streamlit, 5 tabs)

1. **סקירה חודשית** — Monthly overview: pie chart, bar chart, KPIs, foreign currency summary
2. **פירוט עסקאות** — Full transaction table with filters, inline category editor
3. **התחייבויות קבועות** — Recurring charges and installments, monthly/annual totals
4. **הצעות חיסכון** — Savings suggestion cards with dismiss/acted actions
5. **ממתינים לאישורך** — Unrecognized transactions pending user category confirmation

Sidebar: processing trigger button, last run timestamp, pending file count, DB stats.

## Data Files

| File | Purpose |
|------|---------|
| `data/transactions.json` | Append-only transaction database |
| `data/processed_log.json` | Processing history |
| `data/merchant_map.json` | User-confirmed category mappings cache |
| `data/savings_suggestions.json` | Savings suggestions with status |
| `backups/` | Timestamped backups before every write |
