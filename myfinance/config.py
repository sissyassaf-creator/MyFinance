"""MyFinance v1 — All constants, categories, column mappings, and paths."""

from pathlib import Path

# ── Paths ──────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent.parent
INPUT_DIR = PROJECT_ROOT / "input"
DATA_DIR = PROJECT_ROOT / "data"
BACKUP_DIR = PROJECT_ROOT / "backups"
EXPORT_DIR = PROJECT_ROOT / "exports"
DB_PATH = DATA_DIR / "myfinance.db"

# ── Sources ────────────────────────────────────────────
SOURCES = {
    'visa-mizrahi': 'ויזה מזרחי טפחות',
    'diners-el-al': 'דיינרס אל על',
    'max': 'מקס',
}

# ── Categories ─────────────────────────────────────────
CATEGORIES = [
    'מזון ושוק',
    'מסעדות ובילויים',
    'דלק ותחבורה',
    'בריאות',
    'חינוך וילדים',
    'דיור ובית',
    'ביטוח',
    'התחייבויות קבועות',
    'ביגוד והנעלה',
    'חופשות ונסיעות',
    'העברות ותשלומים',
    'לא מזוהה',
]

UNRECOGNIZED_CATEGORY = 'לא מזוהה'

# ── File Detection ─────────────────────────────────────
SUPPORTED_EXTENSIONS = {'.csv', '.xlsx', '.xls'}

# ── Categorization ─────────────────────────────────────
CLAUDE_MODEL = "claude-sonnet-4-20250514"
CATEGORIZATION_BATCH_SIZE = 50
MAX_TOKENS = 4096

# ── Savings Rules ──────────────────────────────────────
MICRO_LEAK_THRESHOLD = 50           # ILS — individual transaction
MICRO_LEAK_MONTHLY_TOTAL = 300      # ILS — sum in one category
DUPLICATE_PAYMENT_DAYS = 2          # Days window for same merchant+amount

BANK_FEE_KEYWORDS = [
    'עמלה', 'עמלת', 'דמי ניהול', 'דמי כרטיס', 'ריבית',
    'commission', 'fee', 'דמי', 'אגרה',
]

# ── Backup ─────────────────────────────────────────────
MAX_BACKUPS = 5

# ── Dashboard ──────────────────────────────────────────
DASHBOARD_HOST = "127.0.0.1"
DASHBOARD_PORT = 8050
DASHBOARD_DEBUG = False

# ── Sensitive Data Patterns ────────────────────────────
SENSITIVE_PATTERNS = [
    r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',  # Card numbers
    r'\b\d{6,}\b',                                      # Account numbers (6+ digits)
]
