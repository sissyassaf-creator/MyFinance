# MyFinance — Toolchain

## Language

- Python 3.11+

## Core Libraries

| Library | Purpose |
|---------|---------|
| streamlit | Dashboard UI (Hebrew, RTL) |
| pandas | Data manipulation, CSV/Excel reading |
| openpyxl | Excel export |
| anthropic | Claude API for document parsing and categorization |
| Pillow | Image handling |
| pdfplumber | Text-based PDF extraction |
| pdf2image | Convert scanned PDF pages to images for Claude Vision |

## System Dependencies

- **Poppler**: Required by pdf2image for PDF-to-image conversion (free, open source)
  - macOS: `brew install poppler`
  - Ubuntu: `apt-get install poppler-utils`

## Environment Setup

```bash
cd ~/claude-code/MyFinance
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | Yes | API key from console.anthropic.com |

Set in `.env` file (gitignored):
```
ANTHROPIC_API_KEY=sk-ant-...
```

## Running

```bash
# Process new documents
python main.py process

# Launch dashboard
streamlit run dashboard.py
```

## Cost

- All Python libraries: free, open source
- Poppler: free, open source
- Anthropic API: pay per use, estimated under $0.50 per monthly run
