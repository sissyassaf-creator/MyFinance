# MyFinance — Tasks

## Phase 1: Project Setup
- [x] Create project directory and GitHub repo
- [x] Create documentation files (DESIGN, ARCHITECTURE, TOOLCHAIN, TASKS, PROGRESS)
- [ ] Create requirements.txt
- [ ] Create directory structure (input/, data/, backups/)
- [ ] Create .env template

## Phase 2: Core Pipeline
- [ ] File detection module (identify type and source)
- [ ] Text PDF extraction (pdfplumber)
- [ ] Scanned PDF / image extraction (Claude Vision)
- [ ] Excel/CSV extraction (pandas)
- [ ] Transaction data model and validation
- [ ] Deduplication logic (SHA256 + 3-day window)
- [ ] Categorization via Claude API
- [ ] Merchant map cache (merchant_map.json)
- [ ] Savings detection (5 checks)
- [ ] Excel export

## Phase 3: Dashboard
- [ ] Streamlit app scaffold with Hebrew RTL
- [ ] Tab 1: סקירה חודשית (monthly overview)
- [ ] Tab 2: פירוט עסקאות (transaction details)
- [ ] Tab 3: התחייבויות קבועות (recurring charges)
- [ ] Tab 4: הצעות חיסכון (savings suggestions)
- [ ] Tab 5: ממתינים לאישורך (pending review)
- [ ] Sidebar: processing trigger, stats

## Phase 4: Polish
- [ ] Automatic backup before writes
- [ ] User confirmation on first API call
- [ ] Error handling for malformed documents
- [ ] End-to-end testing with sample documents
