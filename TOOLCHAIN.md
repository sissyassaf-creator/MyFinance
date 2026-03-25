# MyFinance — Toolchain

## Language

- Python 3.11+

## Core Libraries

| Library | Purpose |
|---------|---------|
| dash | Dashboard framework |
| dash-mantine-components | RTL-native UI components |
| dash-ag-grid | High-performance data table with inline editing |
| plotly | Charts (pie, bar) |
| pandas | Data manipulation, CSV/Excel reading |
| openpyxl | Excel export |
| anthropic | Claude API for categorization |
| python-dotenv | Load .env file |

## System Dependencies

- **None** — v1 uses CSV/Excel only (no Poppler, no OCR)

## Environment Setup

```bash
cd ~/claude-code/MyFinance
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | Yes | API key from console.anthropic.com |

Set in `.env` file (gitignored):
```
ANTHROPIC_API_KEY=sk-ant-api03-...
```

## Running

```bash
# Process new files
python -m myfinance.cli process

# Launch dashboard
python -m myfinance.cli dashboard

# Export to Excel
python -m myfinance.cli export --month 2026-03
```

## Cost

- All Python libraries: free, open source
- No system dependencies
- Anthropic API: ~1-3 ILS/month (Sonnet model, merchant cache minimizes calls)
