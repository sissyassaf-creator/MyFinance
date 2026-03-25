# MyFinance — Product Definition

**Date:** 2026-03-25
**Status:** Product Definition Complete — Ready for Architecture

---

## Vision

A local, privacy-first Python application that gives Israeli households a complete
picture of their financial health — tracking expenses, income, budgets, and savings
goals across multiple banks and credit cards, all in Hebrew.

**Tagline:** הכספים שלך, במחשב שלך (Your finances, on your computer)

---

## Target User

- Israeli household (2 adults + 3 children)
- Uses multiple Israeli banks and credit cards
- Privacy-conscious — no cloud, no credential sharing
- Wants practical budgeting without complexity
- Hebrew-speaking

---

## Version Roadmap

### v1 — Working Foundation (Target: 2-3 weeks)
Get end-to-end flow working with minimal scope. Ship it, use it, learn from it.

### v2 — Full Dashboard (Target: 4-6 weeks after v1)
Add trends, budgeting, savings goals, and all categories.

### v3 — Smart & Automated (Target: after 2+ months of using v2)
Add automation, advanced savings detection, and polish.

### v4 — Future (no timeline)
Cloud, collaboration, investment tracking.

---

# v1 — Working Foundation

## Scope Philosophy
The reviewer was right: ship a thin slice that works end-to-end. Use it for real
for 1-2 months before building more. Every feature in v1 must be essential for
the basic flow: import → see transactions → understand where money goes.

## Sources (v1)

| Source | Type | Folder |
|--------|------|--------|
| Visa Mizrahi Tefahot | Credit Card | `input/visa-mizrahi/` |
| Max | Credit Card | `input/max/` |

**Input formats (v1):** Excel/CSV only (most reliable, no OCR issues)

Bank statements and PDF parsing deferred to v2 — credit card statements give
the richest transaction-level data and are available as Excel/CSV downloads
from max.co.il and cal-online.co.il.

## Processing Pipeline (v1)

1. **File Detection** — Identify CSV/Excel and source folder
2. **Extraction** — pandas reads Excel/CSV, normalize column names per source
3. **Deduplication** — SHA256 hash of (date + merchant + amount + source). No cross-source dedup in v1 (only credit cards, no bank overlap).
4. **Categorization** — Claude API classifies into 12 Hebrew categories. Merchant map cache in SQLite. User confirms unrecognized.
5. **Export** — Append to SQLite, basic Excel export

## 12 Categories (v1)

| # | Category | Description |
|---|----------|-------------|
| 1 | מזון ושוק | Groceries and supermarkets |
| 2 | מסעדות ובילויים | Dining and entertainment |
| 3 | דלק ותחבורה | Fuel and transportation |
| 4 | בריאות | Health and medical |
| 5 | חינוך וילדים | Education and children (merged for v1) |
| 6 | דיור ובית | Housing, maintenance, arnona, va'ad bayit (merged for v1) |
| 7 | ביטוח | Insurance |
| 8 | התחייבויות קבועות | Fixed commitments (utilities, phone, internet, subscriptions) |
| 9 | ביגוד והנעלה | Clothing and shoes |
| 10 | חופשות ונסיעות | Vacations and travel |
| 11 | העברות ותשלומים | Transfers, Bit, bank fees |
| 12 | לא מזוהה | Unrecognized — pending user review |

## Transaction Data Model (v1)

| Field | Type | Description |
|-------|------|-------------|
| transaction_id | string | SHA256 hash for deduplication |
| date | date | Transaction date |
| charge_date | date | Billing/charge date |
| merchant | string | Merchant name (as-is from statement) |
| raw_description | string | Original description |
| amount_ils | float | Amount in ILS |
| amount_original | float | Original amount (if foreign currency) |
| currency_original | string | Original currency code |
| payment_method | enum | regular / installments / immediate_debit |
| installment_number | int | Current installment |
| installments_total | int | Total installments |
| category | string | Hebrew category (1 of 12) |
| needs_review | bool | True if unrecognized |
| source | string | Institution name |

## Savings Detection (v1 — 3 rules only)

| # | Rule | Trigger |
|---|------|---------|
| 1 | Bank fees | Any charge with fee/commission keywords |
| 2 | Duplicate payments | Same merchant + same amount within 1-2 days |
| 3 | Micro leaks | Transactions <50 ILS in one category totaling >300 ILS/month |

Only rules that work with a single month of data. Rules requiring history (spikes,
trends, unused subscriptions) deferred to v2.

## Dashboard (v1 — Plotly Dash, Hebrew RTL, 2 tabs)

**Framework:** Plotly Dash with Dash Mantine Components (native RTL via `dir="rtl"`)
and dash-ag-grid for tables.

**Tab 1: סקירה כללית (Overview)**
- Total spend this month
- Pie chart by category
- Bar chart: spend per category
- Pending review count (red badge — click to jump to review)
- Top 5 merchants
- Foreign currency summary (if any)

**Tab 2: פירוט עסקאות (Transactions)**
- Full transaction table (dash-ag-grid): search, filter, sort
- Inline category editor for unrecognized transactions
- Filter by: date range, category, source, amount range

**Sidebar:**
- Process new files button
- Last run timestamp
- File count per source folder
- Total transactions in database

## Data Storage (v1 — SQLite)

| Table | Description |
|-------|-------------|
| transactions | All transactions (append-only) |
| merchant_map | User-confirmed category mappings cache |
| processing_log | Which files were processed and when |

**Backups:** Copy SQLite file before each processing run → `backups/myfinance_YYYYMMDD_HHMMSS.db`
**Retention:** Keep last 5 backups, delete older ones.

## Excel Export (v1)

Monthly file: `הוצאות_YYYY_MM.xlsx`
- Sheet 1: עסקאות (all transactions)

## Tech Stack (v1)

| Component | Technology |
|-----------|-----------|
| Language | Python 3.11+ |
| Dashboard | Plotly Dash + Dash Mantine Components + dash-ag-grid |
| Data | pandas, SQLite |
| Excel export | openpyxl |
| AI | anthropic (Claude API) |
| System dep | None (CSV/Excel only, no Poppler needed) |

## Security (v1)

- API key from .env (gitignored)
- No bank credentials — manual file download only
- Sensitive data stripped before API calls (account numbers, card numbers)
- User confirmation before first API call
- Automatic backup before processing

## Cost (v1)

| Item | Cost |
|------|------|
| Python libraries | Free |
| Anthropic API | ~$1-3 first month, ~$0.50-1/month ongoing |
| **Total** | **~2-10 ILS/month** |

---

# v2 — Full Dashboard

**Prerequisite:** v1 used successfully for 1-2 months with real data.

## What v2 Adds

### Additional Sources
| Source | Type | Folder |
|--------|------|--------|
| Bank Mizrahi Tefahot | Bank | `input/bank-mizrahi/` |
| Diners El Al | Credit Card | `input/diners-el-al/` |

### PDF Parsing
- Text PDF extraction via pdfplumber (or pymupdf4llm for better RTL)
- Scanned PDF / image extraction via Claude Vision
- Requires Poppler system dependency

### Expand to 22 Categories

#### Expense Categories (18)
| # | Category | Description |
|---|----------|-------------|
| 1 | מזון ושוק | Groceries and supermarkets |
| 2 | מסעדות ובילויים | Dining and entertainment |
| 3 | דלק ותחבורה | Fuel and transportation |
| 4 | בריאות | Health and medical |
| 5 | חינוך | Education |
| 6 | ילדים ומשפחה | Children — daycare, activities, camps, supplies |
| 7 | דיור | Housing — mortgage or rent |
| 8 | תחזוקת בית | Home maintenance and repairs |
| 9 | ארנונה ומיסים | Municipal tax and government fees |
| 10 | ועד בית | Building maintenance fee |
| 11 | ביטוח | Insurance — health, car, home, life, mortgage |
| 12 | התחייבויות קבועות | Fixed commitments (utilities, phone, internet) |
| 13 | מנויים ודיגיטל | Subscriptions and digital services |
| 14 | ביגוד והנעלה | Clothing and shoes |
| 15 | חיות מחמד | Pets |
| 16 | חופשות ונסיעות | Vacations and travel |
| 17 | תרומות | Donations (flag Section 46 eligible) |
| 18 | קניות אונליין | Online shopping |

#### Financial Categories (3)
| # | Category | Description |
|---|----------|-------------|
| 19 | ביט והעברות | Bit payments and transfers |
| 20 | עמלות בנקאיות | Bank fees and commissions |
| 21 | חיסכון והשקעות | Savings, pension, keren hishtalmut |

#### System (1)
| # | Category | Description |
|---|----------|-------------|
| 22 | לא מזוהה | Unrecognized — pending review |

#### Income Categories
| Category | Description |
|----------|-------------|
| משכורת | Salary |
| קצבאות | Government allowances |
| הכנסה מעסק | Freelance / business income |
| הכנסה מהשקעות | Investment income |
| הכנסה אחרת | Other income |

### Income Tracking
- Detect income from bank statements (credit entries)
- Income categories (salary, allowances, etc.)
- Savings rate KPI: (Income - Expenses) / Income

### Budgeting
- Simple per-category monthly limits
- Progress bars: green (<70%), yellow (70-90%), red (>90%)
- Alert at 80% threshold
- Budget vs. actual comparison
- Annual view for quarterly/annual expenses

### Savings Goals
- Multiple simultaneous goals (emergency fund, vacation, purchase, general)
- Progress bar per goal
- Projected completion date
- Monthly contribution needed

### Cross-Source Deduplication
- Fuzzy matching: merchant + amount (±1 ILS) + billing cycle awareness
- Source priority: credit card statement as truth for card transactions,
  bank statement as truth for direct debits
- User confirmation on first match, then learn

### Dashboard Expands to 5 Tabs
1. **סקירה כללית** — Overview + KPIs + budget status + savings goals + pending banner
2. **פירוט עסקאות** — Transaction table with search/filters/inline editing
3. **מגמות** — Multi-month trends, rolling averages, YoY comparison, spending velocity
4. **התחייבויות ומנויים** — Recurring charges, installments, future liability
5. **הצעות חיסכון** — Savings suggestions + goals management

### Additional KPIs
| KPI | Formula |
|-----|---------|
| Savings rate | (Income - Expenses) / Income |
| Housing cost ratio | Housing / Income (target: <30%) |
| Fixed vs. variable | Fixed / Total (target: <50%) |
| Installment burden | Installments / Income (alert >15%) |
| Month-over-month | % change vs. last month |
| Expense per day | Spend / Days elapsed |
| Days until billing | Per credit card |

### More Savings Rules (expand to 10)
Add to v1's 3 rules:
| # | Rule |
|---|------|
| 4 | Category spikes (>150% of 3-month rolling average) |
| 5 | Unused subscriptions (no merchant activity in 3 months) |
| 6 | Duplicate-purpose subscriptions |
| 7 | Subscription price creep |
| 8 | Installment burden alert (>15% of income) |
| 9 | Foreign currency conversion waste (>2.5% spread) |
| 10 | Cash withdrawal pattern (>2,000 ILS/month) |

### macOS Notifications
- Processing complete
- Budget threshold reached
- Monthly summary ready
- New files detected

### Parser Plugin Architecture
Each source gets a parser class with a common interface for easy expansion:
```
class SourceParser:
    def detect(self, file) -> bool
    def extract(self, file) -> list[Transaction]
```

---

# v3 — Smart & Automated

**Prerequisite:** v2 used for 2+ months. Enough historical data for trend analysis.

## What v3 Adds

### Automated Data Fetching (Optional)
- Integration with Caspion / israeli-bank-scrapers
- User chooses: manual upload OR automated scraping
- Credentials stored encrypted in OS keychain (never plain text)
- Fully optional — manual mode always available

### Additional Savings Rules (expand to 14)
| # | Rule |
|---|------|
| 11 | Insurance renewal alert |
| 12 | Arnona discount eligibility check |
| 13 | Recurring charge after user cancellation |
| 14 | Weekend/night impulse spending patterns |

### Advanced Analytics
- Cash flow forecasting (projected balance at month-end)
- Seasonal awareness (Israeli holidays spending patterns)
- Year-over-year inflation impact
- Merchant normalization ("שופרסל דיל" = "שופר-סל" = "שופרסל")

### Onboarding Wizard
5-step wizard for first-time users:
1. Welcome + privacy assurance
2. API key setup with validation
3. Source selection
4. First document processing
5. Dashboard tour

### Additional Banks/Cards
- Plugin parsers for: Hapoalim, Leumi, Cal (Visa Cal), Isracard, Discount
- Auto-detection by document content (not just folder)

### Enhanced Export
- Monthly Excel with 3 sheets: עסקאות, הצעות חיסכון, תקציב מול ביצוע
- Annual summary report
- Tax-relevant expense summary (Section 46 donations)

---

# v4 — Future (No Timeline)

- Cloud deployment option
- Local LLM fallback (Ollama) for zero external calls
- Net worth tracking
- Investment portfolio tracking
- WhatsApp/Telegram bot ("how much did I spend on food?")
- Collaborative household mode (shared dashboard, per-user views)
- Receipt photo scanning
- VAT toggle for freelancers
- El Al miles/rewards tracking
- Family member transaction tagging and splitting

---

## Full Transaction Data Model (Target — v2+)

| Field | Type | Description |
|-------|------|-------------|
| transaction_id | string | SHA256 hash for deduplication |
| date | date | Transaction date |
| charge_date | date | Billing/charge date |
| merchant | string | Normalized merchant name |
| raw_description | string | Original description from statement |
| amount_ils | float | Amount in ILS |
| amount_original | float | Original amount (if foreign currency) |
| currency_original | string | Original currency code |
| payment_method | enum | regular / credit / installments / immediate_debit / standing_order |
| installment_number | int | Current installment number |
| installments_total | int | Total installments |
| transaction_type | enum | one_time / recurring / transfer |
| category | string | Hebrew category |
| is_income | bool | True if income transaction |
| needs_review | bool | True if category unrecognized |
| source | string | Institution name |
| family_member | string | Optional tag by family member |

---

## Security & Privacy (All Versions)

- API key from environment variable only (.env, gitignored)
- No bank credentials stored (v1-v2). Optional encrypted storage in v3.
- Sensitive data (account numbers, card numbers) stripped before API calls
- API call log viewable by user
- User confirmation required before first API call
- Automatic backup before every processing run
- All data in local SQLite — no cloud, no external services except Anthropic API
- **Privacy positioning:** הכספים שלך, במחשב שלך

---

## Competitive Context

| Alternative | Price | Pros | Cons | MyFinance Advantage |
|------------|-------|------|------|---------------------|
| Bank apps | Free | Real-time, on phone | Siloed (one bank only) | Cross-institution view |
| Riseup | 45 NIS/mo | Full automation, coaching | Cloud, expensive | Free, private, local |
| Finanda | 16 NIS/mo | Automated, free tier | Cloud-based | No cloud dependency |
| Caspion | Free | Auto-fetches | No dashboard, no categorization | AI categorization + dashboard |
| YNAB | $99/year | Great budgeting | No Israeli bank support, cloud | Hebrew, Israeli sources, local |
| Spreadsheet | Free | Flexible | Manual, no insights | Automated categorization + savings detection |
