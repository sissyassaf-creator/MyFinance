# MyFinance — Product & Competitive Analysis Report

**Date:** 2026-03-25
**Reviewer Role:** Product Expert, Home Finance & Budgeting Applications

---

## 1. Competitive Landscape Analysis

### 1.1 Israeli Market

#### Caspion (Open-source scraper)
- **What it does:** Open-source project that scrapes Israeli bank and credit card websites directly using browser automation (Puppeteer). Supports Bank Hapoalim, Leumi, Discount, Mizrahi Tefahot, Max, Cal (Visa), Isracard, and more.
- **Key advantage over MyFinance:** Automated data fetching — no manual PDF/Excel downloads needed. Users provide credentials and Caspion pulls transactions automatically.
- **Key disadvantage:** Requires storing bank credentials locally. Fragile when banks change their UI. No categorization, no dashboard — it is purely an extraction tool.
- **What MyFinance is missing:** Automated scraping. Caspion's scraper library (`israeli-bank-scrapers`) is npm-based and could theoretically be wrapped.

#### Heshbonit
- **What it does:** Israeli app focused on receipt scanning and expense tracking for small businesses and freelancers. Handles invoices, receipts, and VAT tracking.
- **Relevance:** Different target audience (business/freelancer vs. household), but its receipt-scanning UX and Hebrew-native category system are worth studying.
- **What MyFinance is missing:** Receipt photo scanning as a separate input channel (not just statement documents).

#### Bank Apps (Hapoalim, Leumi, Mizrahi Tefahot)
- **What they do:** Each bank provides its own app with transaction history, categorization, budgeting tools, and spending insights. Mizrahi Tefahot's app has improved significantly with automatic categorization and monthly summaries.
- **Key limitation:** Siloed — each app only sees its own bank's data. No cross-institution view.
- **What MyFinance is missing:** Push notifications, real-time transaction alerts, biometric authentication.

#### Max / Isracard / Cal Apps
- **What they do:** Credit card company apps with transaction tracking, installment management, benefits/rewards tracking, and spending analytics.
- **Key feature MyFinance lacks:** Rewards/points/miles tracking (especially relevant for Diners El Al with frequent flyer miles).

### 1.2 Global Market

#### Mint (Intuit) — Shut down Jan 2024, migrated to Credit Karma
- **Legacy features worth noting:** Auto-categorization with user override, budget vs. actual tracking, bill reminders, credit score monitoring, net worth tracking.
- **Lesson learned:** Users loved the free model but Mint struggled with monetization. The "set it and forget it" auto-sync was its killer feature.

#### YNAB (You Need A Budget)
- **Philosophy:** Zero-based budgeting — every shekel gets a job. Proactive budgeting, not just tracking.
- **Key features MyFinance lacks:**
  - **Budget envelopes/categories with assigned amounts** — not just tracking what was spent, but planning what SHOULD be spent
  - **Age of money metric** — how long money sits before being spent
  - **Goal tracking** — save for vacation, emergency fund, etc.
  - **Reconciliation workflow** — matching bank statement to tracked transactions
- **Price:** ~$99/year — MyFinance's $0.50/month is a massive advantage.

#### Monarch Money
- **Key features:** Beautiful dashboard, collaborative (multi-user households), investment tracking, net worth, recurring transaction detection, custom categories, Sankey cash flow diagrams.
- **What MyFinance lacks:** Investment/portfolio tracking, net worth tracking, collaborative household access, Sankey/waterfall visualizations.

#### Copilot Money (iOS)
- **Key features:** Clean minimalist UI, AI-powered categorization, subscription tracking, investment overview, rental income tracking.
- **Design lesson:** Less is more. Copilot succeeds with a very focused feature set and exceptional visual design.

#### Rocket Money (formerly Truebill)
- **Key features:** Subscription cancellation service, bill negotiation, spending insights, credit score, net worth.
- **Differentiator:** Actionable savings — not just "here's a suggestion" but "we'll cancel it for you."

---

## 2. UX Best Practices for Finance Dashboards

### What Makes Users Come Back

1. **Immediate value on every visit:** The landing screen must answer "how am I doing?" in under 3 seconds. A single KPI (e.g., "You've spent 72% of your monthly budget") is more effective than 10 charts.

2. **Anxiety reduction, not anxiety creation:** Finance apps that make users feel stressed about their spending get abandoned. Frame insights positively: "You saved 340 ILS vs last month" rather than "You overspent by 500 ILS."

3. **Progressive disclosure:** Show summary first, let users drill down. Don't overwhelm with data on the first screen.

4. **Habit hooks:**
   - Weekly email/notification summary
   - Monthly "financial health report"
   - Streaks (e.g., "3 months under budget in Food")
   - Celebration of milestones

5. **Low friction data entry:** Every manual step is a churn risk. The more automated the data ingestion, the higher the retention.

6. **Personalization over time:** The app should get smarter — better categorization, more relevant savings tips, personalized benchmarks.

### Visual Design Principles for Finance

- **Use color meaningfully:** Green = under budget/positive, Red = over budget/negative, Amber = warning. Do not use color decoratively.
- **Round numbers for summaries, exact for details:** Show "~12,500 ILS" in the overview, "12,487.32 ILS" in the transaction table.
- **Trend arrows matter more than absolute numbers:** "Food spending DOWN 12%" is more useful than "Food: 3,200 ILS."
- **Whitespace is critical in Hebrew RTL:** Dense Hebrew text in financial tables becomes unreadable quickly. Generous spacing is essential.

---

## 3. Dashboard Structure Critique

### Current 5-Tab Structure Assessment

| Tab | Verdict | Notes |
|-----|---------|-------|
| 1. סקירה חודשית (Monthly Overview) | **Keep — this is correct** | Good as landing page. Needs enhancement (see below). |
| 2. פירוט עסקאות (Transaction Details) | **Keep** | Core feature, essential. |
| 3. התחייבויות קבועות (Recurring Charges) | **Keep but merge consideration** | Could be a section within Monthly Overview rather than its own tab, unless the data is substantial. |
| 4. הצעות חיסכון (Savings Suggestions) | **Keep but rethink UX** | Should be more prominent — consider inline alerts rather than a separate tab users must visit. |
| 5. ממתינים לאישורך (Pending Review) | **Rethink** | This should NOT be a separate tab. It is a workflow blocker that should appear as a persistent banner/badge on the main screen. |

### Recommended Changes

#### Change 1: Make "Pending Review" a modal/banner, not a tab
Users will forget to check tab 5. Unreviewed transactions should surface as:
- A red badge counter in the sidebar (e.g., "7 ממתינים")
- A dismissible banner at the top of the Monthly Overview tab
- A blocking step during processing: "We found 7 new transactions we couldn't categorize. Review them now?"

#### Change 2: Add a "Trends" tab (or section)
The biggest gap in the current design is **multi-month trend analysis**. Users need to see:
- Month-over-month spending by category (line chart)
- 3-month rolling average vs. current month
- Year-over-year comparison
- "Your spending pattern" insights

#### Change 3: Promote savings suggestions
Instead of hiding savings in tab 4, surface the top 1-2 suggestions as cards on the Monthly Overview. The dedicated tab can have the full list.

#### Recommended Tab Structure (revised)

1. **סקירה כללית** (Overview) — KPIs, top insights, top savings tip, pending review banner, pie chart
2. **פירוט עסקאות** (Transactions) — Full table with filters
3. **מגמות** (Trends) — Multi-month analysis, category trends, forecasting
4. **התחייבויות ומנויים** (Commitments & Subscriptions) — Recurring charges, installments, subscription management
5. **הצעות חיסכון** (Savings) — Full savings suggestions with action tracking

---

## 4. Onboarding Experience

### Current Gap
The current design has no defined onboarding flow. This is critical — a confusing first experience will kill adoption.

### Recommended First-Time Setup Flow

#### Step 1: Welcome & Privacy Assurance (30 seconds)
- Welcome screen explaining: "Your data never leaves your computer. Only categorization requests go to Anthropic's API."
- Show a simple diagram: Documents -> Your Computer -> Dashboard
- Single CTA: "Let's get started"

#### Step 2: API Key Setup (1 minute)
- Clear instructions: "Create an Anthropic API key at console.anthropic.com"
- Input field with validation (test the key immediately)
- Show estimated cost: "This typically costs less than 2 ILS per month"

#### Step 3: Source Selection (30 seconds)
- Checkboxes for which sources the user has:
  - [ ] Bank Mizrahi Tefahot
  - [ ] Visa Mizrahi Tefahot
  - [ ] Diners El Al
  - [ ] Max
- Only show relevant input folders for selected sources

#### Step 4: First Document Upload (2 minutes)
- Guided upload: "Drop your most recent bank statement here"
- Process it immediately and show results
- Let the user see the categorization in action
- Ask user to confirm/correct 3-5 categories to train the system

#### Step 5: Dashboard Tour (1 minute)
- Brief guided tour highlighting each tab
- Point out the "Process New Files" button in the sidebar
- Explain the pending review workflow

### Key Onboarding Principles
- **Time to first value < 5 minutes:** User should see their transactions categorized within 5 minutes of starting
- **Don't require all sources at once:** Let users start with one source and add more later
- **Celebrate the first insight:** After processing, show something like "Your top spending category is מזון ושוק at 3,200 ILS this month"

---

## 5. Notifications & Alerts

### Critical Gap
The current design has ZERO notification/alert capability. For a local app, this is understandable but solvable.

### Recommended Alert System

#### Tier 1: In-Dashboard Alerts (Must Have)
These appear when the user opens the dashboard:
- **New files detected:** "3 new files found in input folders. Process now?"
- **Budget threshold alerts:** "Food spending has reached 80% of last month's total with 10 days remaining"
- **Unusual transactions:** Transactions that are significantly larger than the merchant's average
- **Pending reviews:** Count of uncategorized transactions

#### Tier 2: System Notifications (Should Have)
Using Python's `plyer` or native macOS notifications:
- **Processing complete:** "12 new transactions processed, 3 need your review"
- **Monthly summary ready:** On the 1st of each month, generate and notify
- **Savings alert:** "New savings opportunity detected: possible duplicate subscription"

#### Tier 3: Scheduled Reports (Nice to Have)
- **Weekly email digest** (via local SMTP or a simple email API)
- **Monthly PDF report** auto-generated and saved
- **Bill reminders:** "Credit card payment due in 3 days: estimated 8,500 ILS"

### Spending Limits System
Allow users to set per-category monthly limits:
```
מזון ושוק: 4,000 ILS
מסעדות ובילויים: 2,000 ILS
```
Alert at 80% and 100% thresholds. Show progress bars on the overview tab.

---

## 6. Multi-Source Problem (Israeli Market Specific)

### The Core Challenge
Israeli households typically have:
- 1-2 bank accounts
- 2-4 credit cards (often from different companies)
- Overlap: credit card charges appear on both the card statement AND the bank statement
- Timing differences: card transaction date vs. bank charge date can differ by weeks
- Installments: a single purchase becomes multiple monthly charges

### How Competitors Handle It

#### Bank Apps: They don't
Each bank/card app is siloed. Users must mentally aggregate across apps.

#### Caspion: Scrape everything, dump to spreadsheet
Caspion pulls from all sources but does minimal deduplication. Users must handle overlaps.

#### MyFinance's Current Approach
The 3-day window dedup with SHA256 hash is a good start, but needs enhancement:

### Recommendations

1. **Smart Deduplication Engine (Must Have Enhancement)**
   - Current 3-day window is too narrow for Israeli credit cards where the charge date can be 30+ days after transaction date
   - Implement fuzzy matching: same merchant + similar amount (within 1 ILS for rounding) + date within the billing cycle
   - Mark dedup matches for user confirmation on first occurrence, then learn

2. **Source Priority System**
   - Credit card statement should be the "source of truth" for card transactions (it has the merchant name)
   - Bank statement should be the source of truth for direct debits, transfers, and standing orders
   - When both exist, prefer the one with richer data and link them

3. **Billing Cycle Awareness**
   - Each credit card has a specific billing cycle (e.g., 2nd of each month)
   - The system should know these cycles to correctly attribute transactions to months
   - This is CRITICAL for Israeli finance because a transaction on March 25 might be charged to April's bill

4. **Installment Tracking**
   - Israeli consumers heavily use installment payments (תשלומים)
   - Each installment should link back to the original purchase
   - Show both: "Original purchase: 6,000 ILS" and "Monthly charge: 1,000 ILS x 6"
   - Track remaining installment obligations as a "future committed spending" metric

---

## 7. Privacy/Local Competitive Advantage

### Why This Matters in Israel
- Israeli consumers are highly privacy-conscious about financial data after several data breaches
- Bank credential sharing (required by Caspion) makes many users uncomfortable
- Cloud-based finance apps require trusting a third party with complete financial history
- Israeli data protection regulations (Privacy Protection Law 5741-1981) add compliance burden for cloud services

### MyFinance's Privacy Positioning

#### Strengths
- **No credentials stored:** Users export their own documents — no screen scraping
- **No cloud storage:** Transaction data never leaves the machine
- **Minimal API exposure:** Only merchant names and amounts go to Anthropic for categorization (not account numbers, not personal details)
- **Auditable:** Users can inspect exactly what data is sent via the API

#### How to Strengthen This Advantage
1. **Show users exactly what goes to the API:** Add a "View API Request" button so users can see the data being sent to Claude before it goes
2. **Redact sensitive data before API calls:** Strip account numbers, card numbers, and personal identifiers before sending to the categorization API
3. **Offer a "fully offline" mode:** Use a local LLM (e.g., Ollama with a small model) for categorization — slower and less accurate but zero external calls
4. **API call log:** Maintain a viewable log of all external API calls with timestamps and data sent

### Marketing Angle
Position as: **"הכספים שלך, במחשב שלך"** (Your finances, on your computer)
- Emphasize: No login, no cloud, no credentials, no subscription
- Compare: "Unlike bank apps that track you, MyFinance tracks FOR you"

---

## 8. Feature Priority Tiers

### MUST HAVE (Launch Blockers)

| Feature | Rationale |
|---------|-----------|
| Reliable PDF extraction for all 4 sources | Core functionality — if extraction fails, nothing works |
| Accurate deduplication across sources | Wrong totals = zero trust = abandoned product |
| Hebrew RTL dashboard that actually works | Broken RTL is immediately visible and feels amateurish |
| Category confirmation workflow (current tab 5) | Without this, categorization accuracy degrades |
| Monthly overview with accurate totals | The #1 reason users open a finance app |
| Excel export | Many Israeli users want to keep records in Excel |
| Onboarding flow | Without it, technical users might figure it out; everyone else bounces |
| Error handling for malformed documents | Real-world documents are messy — graceful failures are essential |
| Installment tracking | Central to Israeli consumer finance; cannot be an afterthought |
| Per-category spending limits with alerts | Table stakes for any budgeting tool |

### SHOULD HAVE (v1.1 — First Month After Launch)

| Feature | Rationale |
|---------|-----------|
| Multi-month trend analysis | Users need context — "is this month normal?" |
| Smarter dedup (fuzzy matching, billing cycle awareness) | 3-day window will produce false positives/negatives |
| System notifications (macOS native) | Keeps users engaged without opening the dashboard |
| Budget vs. actual tracking | Moves from passive tracking to active budgeting |
| Receipt/invoice photo scanning | Additional input channel beyond statements |
| Search across all transactions | "Where did I buy that thing last month?" |
| Merchant name normalization | "SUPER PHARM RAANANA" and "SUPER-PHARM RA'ANANA" should merge |
| Data backup/restore UI | Users need confidence their data is safe |
| CSV import/export | For users migrating from spreadsheets |

### NICE TO HAVE (v2.0 — Differentiators)

| Feature | Rationale |
|---------|-----------|
| Cash flow forecasting | "Will I have enough money at end of month?" |
| Goal tracking (savings goals) | Emotional engagement — saving for vacation, emergency fund |
| Family member transaction splitting | "This is Avi's expense, this is Dana's" |
| Support for additional banks (Hapoalim, Leumi, Discount) | Expands addressable market significantly |
| Local LLM fallback (Ollama) | Ultimate privacy — zero external calls |
| Rewards/miles tracking (Diners El Al) | High value for that specific user segment |
| Net worth tracking | Holistic financial picture |
| Annual financial summary report | Tax season helper |
| Collaborative household mode | Multiple users, shared dashboard |
| WhatsApp/Telegram bot integration | Quick queries: "How much did I spend on food this month?" |
| Automated document fetching (Caspion integration) | Reduces manual effort to near zero |
| Investment portfolio tracking | Full financial picture |

---

## 9. Advanced Features Analysis

### 9.1 Trend Analysis Over Months
**Priority: SHOULD HAVE**

Implementation recommendations:
- **Minimum 3 months of data before showing trends** — trends with 1-2 data points are misleading
- **Seasonal awareness:** Israeli spending spikes around holidays (Rosh Hashana, Pesach, Hanukkah). The system should mark these periods rather than flagging them as anomalies.
- **Rolling averages:** Show 3-month rolling average as the "normal" baseline, not just last month
- **Year-over-year:** Once 12+ months of data exist, show YoY comparison
- **Inflation adjustment:** With Israeli CPI data, show real vs. nominal spending changes

### 9.2 Family Member Splitting
**Priority: NICE TO HAVE**

Complexity is high, value is moderate:
- Allow tagging transactions with a family member name
- Split view: "Household total vs. per-person breakdown"
- Useful for: shared vs. personal expenses, child-related expenses
- **Simpler alternative for v1:** Tag categories as "shared" vs. "personal" rather than per-person

### 9.3 Goal Tracking
**Priority: NICE TO HAVE (but high emotional value)**

- Allow users to set savings goals: "Save 10,000 ILS for vacation by August"
- Show progress bar on overview tab
- Calculate: "At your current savings rate, you'll reach this goal by [date]"
- This is what makes YNAB sticky — the emotional connection to goals

### 9.4 Cash Flow Forecasting
**Priority: SHOULD HAVE**

Critical for Israeli households managing installments:
- **Known future charges:** Sum of remaining installments + recurring subscriptions + standing orders
- **Predicted spending:** Based on historical average per category
- **Income estimation:** If bank statements show salary deposits, project income
- **Output:** "Projected balance at end of month: X ILS" with confidence range
- **Red alert:** "Based on current spending pace, you may exceed your income by 2,000 ILS this month"

---

## 10. Expanding Bank/Card Support

### Current Support (4 sources)
Bank Mizrahi Tefahot, Visa Mizrahi Tefahot, Diners El Al, Max

### Expansion Priority

| Priority | Source | Market Share / Rationale |
|----------|--------|--------------------------|
| **HIGH** | Bank Hapoalim | Largest bank in Israel (~30% market share) |
| **HIGH** | Bank Leumi | Second largest bank (~25% market share) |
| **HIGH** | Cal (Visa Cal) | Major credit card company |
| **MEDIUM** | Isracard | Significant credit card market share |
| **MEDIUM** | Bank Discount | Third largest bank |
| **MEDIUM** | Bank International (FIBI) | Growing market share |
| **LOW** | Bank Yahav | Government employee bank |
| **LOW** | Bank Mercantile | Smaller player |
| **LOW** | PayPal / Bit / Paybox | Digital payment platforms |

### Architecture Recommendation for Extensibility
The current design maps sources to folders, which is correct. To make expansion easy:

1. **Create a parser plugin system:** Each source gets its own parser class implementing a common interface:
   ```
   class SourceParser:
       def detect(self, file) -> bool
       def extract(self, file) -> list[Transaction]
   ```
2. **Auto-detection by content:** Instead of relying solely on folder placement, analyze the document content to identify the source (each Israeli bank has distinctive statement formatting).
3. **Community contribution path:** Make it easy for users to contribute new parsers. Document the parser interface clearly.
4. **Parser versioning:** Banks change their statement formats periodically. Each parser should have a format version and gracefully handle format changes.

---

## 11. Additional Recommendations

### 11.1 Data Model Enhancements
The current 15-category system is good but consider:
- **Sub-categories:** "מזון ושוק" (Food & Grocery) could split into "סופרמרקט" (Supermarket), "מכולת" (Corner store), "שוק" (Market)
- **Custom categories:** Let users create their own beyond the 15
- **Category rules:** "If merchant contains 'שופרסל' then always categorize as מזון ושוק" — user-definable rules that override AI

### 11.2 Missing Category: Income
The current 15 categories are all expense categories. Consider adding:
- **Income categories:** Salary, freelance, rental income, government benefits, tax refunds
- **This enables:** Net income tracking, savings rate calculation, cash flow analysis

### 11.3 Missing Category: Transfers
"ביט והעברות" exists but should be refined:
- Transfers between own accounts should not count as expenses
- Bit payments to individuals vs. businesses should be distinguished
- Standing orders (הוראות קבע) need their own handling

### 11.4 Performance Consideration
As transaction data grows (12+ months = 1000+ transactions), JSON files will become slow:
- Consider SQLite as the storage backend instead of JSON files
- SQLite is still local, single-file, and requires no server
- Dramatically faster for queries, filtering, and aggregations
- Easy to backup (single file copy)

### 11.5 Accessibility
- Support high-contrast mode for visually impaired users
- Ensure all charts have text alternatives
- Keyboard navigation for the dashboard
- Font size controls (many Israeli finance users are older adults)

---

## 12. Summary of Top 10 Actionable Recommendations

| # | Recommendation | Priority | Effort |
|---|---------------|----------|--------|
| 1 | Redesign "Pending Review" from tab to persistent banner/modal | Must Have | Low |
| 2 | Build onboarding flow (5-step wizard) | Must Have | Medium |
| 3 | Add per-category spending limits with visual progress bars | Must Have | Medium |
| 4 | Enhance dedup with fuzzy matching and billing cycle awareness | Must Have | High |
| 5 | Add income tracking to enable net savings calculation | Should Have | Medium |
| 6 | Add multi-month trend analysis tab | Should Have | Medium |
| 7 | Implement cash flow forecasting based on recurring + installments | Should Have | High |
| 8 | Switch from JSON to SQLite for data storage | Should Have | Medium |
| 9 | Add macOS native notifications for key events | Should Have | Low |
| 10 | Design parser plugin system for easy bank/card expansion | Nice to Have | Medium |

---

*This review is based on domain expertise in Israeli and global personal finance applications. For the most current competitive data, a web search for recent product updates from Caspion, Monarch Money, and Israeli bank apps is recommended.*
