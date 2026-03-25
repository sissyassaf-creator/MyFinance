"""Claude API categorization with merchant map cache."""

import json
import re

import anthropic

from myfinance.config import (
    CATEGORIES,
    CATEGORIZATION_BATCH_SIZE,
    CLAUDE_MODEL,
    MAX_TOKENS,
    SENSITIVE_PATTERNS,
    UNRECOGNIZED_CATEGORY,
)
from myfinance.db import get_merchant_category, upsert_merchant_map

CATEGORIZATION_SYSTEM_PROMPT = """You are a financial transaction categorizer for an Israeli household.
You will receive a list of merchant names from Israeli credit card statements.
For each merchant, assign exactly one category from the following list:

1. מזון ושוק — Groceries and supermarkets
2. מסעדות ובילויים — Dining and entertainment
3. דלק ותחבורה — Fuel and transportation
4. בריאות — Health and medical
5. חינוך וילדים — Education and children
6. דיור ובית — Housing, maintenance, arnona, va'ad bayit
7. ביטוח — Insurance
8. התחייבויות קבועות — Fixed commitments (utilities, phone, internet, subscriptions)
9. ביגוד והנעלה — Clothing and shoes
10. חופשות ונסיעות — Vacations and travel
11. העברות ותשלומים — Transfers, Bit, bank fees
12. לא מזוהה — Use ONLY if you truly cannot determine the category

Rules:
- Return ONLY valid JSON: a list of objects with "merchant" and "category" keys
- "category" must be the exact Hebrew string from the list above
- Use "לא מזוהה" sparingly — most Israeli merchants are recognizable
- Do NOT include any explanation, just the JSON array
"""


def normalize_merchant(name: str) -> str:
    """Normalize merchant name for cache matching."""
    name = str(name).strip()
    name = re.sub(r'\s+\d{2,}$', '', name)  # Remove trailing store IDs
    name = re.sub(r'\s+', ' ', name)  # Collapse spaces
    name = name.casefold()  # Lowercase Latin
    return name


def strip_sensitive(merchant_name: str) -> str:
    """Remove card/account numbers before sending to API."""
    cleaned = merchant_name
    for pattern in SENSITIVE_PATTERNS:
        cleaned = re.sub(pattern, '****', cleaned)
    return cleaned


def categorize_transactions(transactions: list[dict], db_conn, skip_api: bool = False) -> list[dict]:
    """Categorize transactions using merchant cache + Claude API.

    Modifies transactions in-place, adding 'category' and 'needs_review' keys.
    Returns the same list.
    """
    # Collect unique merchants
    unique_merchants = set()
    for txn in transactions:
        normalized = normalize_merchant(txn['merchant'])
        unique_merchants.add(normalized)

    # Check cache for each
    cached = {}
    uncached = []
    for merchant in unique_merchants:
        category = get_merchant_category(db_conn, merchant)
        if category:
            cached[merchant] = category
        else:
            uncached.append(merchant)

    # Call Claude API for uncached merchants
    api_results = {}
    if uncached and not skip_api:
        api_results = _categorize_via_api(uncached)
        # Save new mappings to cache
        for merchant, category in api_results.items():
            upsert_merchant_map(db_conn, merchant, category, confirmed_by='api')

    # Apply categories to all transactions
    all_mappings = {**cached, **api_results}
    for txn in transactions:
        normalized = normalize_merchant(txn['merchant'])
        category = all_mappings.get(normalized, UNRECOGNIZED_CATEGORY)
        # Validate category
        if category not in CATEGORIES:
            category = UNRECOGNIZED_CATEGORY
        txn['category'] = category
        txn['needs_review'] = 1 if category == UNRECOGNIZED_CATEGORY else 0

    return transactions


def _categorize_via_api(merchants: list[str]) -> dict[str, str]:
    """Call Claude API to categorize merchants in batches."""
    all_results = {}

    for i in range(0, len(merchants), CATEGORIZATION_BATCH_SIZE):
        batch = merchants[i:i + CATEGORIZATION_BATCH_SIZE]
        # Strip sensitive data before sending
        safe_batch = [strip_sensitive(m) for m in batch]

        try:
            client = anthropic.Anthropic()
            merchants_json = json.dumps(safe_batch, ensure_ascii=False)

            response = client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=MAX_TOKENS,
                system=CATEGORIZATION_SYSTEM_PROMPT,
                messages=[{
                    "role": "user",
                    "content": f"Categorize these merchants:\n{merchants_json}",
                }],
            )

            result_text = response.content[0].text
            # Extract JSON from response (handle markdown code blocks)
            json_match = re.search(r'\[.*\]', result_text, re.DOTALL)
            if json_match:
                results = json.loads(json_match.group())
            else:
                results = json.loads(result_text)

            # Map back to original (non-stripped) merchant names
            api_map = {item['merchant']: item['category'] for item in results}
            for orig, safe in zip(batch, safe_batch):
                category = api_map.get(safe, UNRECOGNIZED_CATEGORY)
                all_results[orig] = category

        except (anthropic.APIError, json.JSONDecodeError, KeyError) as e:
            print(f"API error during categorization: {e}")
            # Mark all in this batch as unrecognized
            for merchant in batch:
                all_results[merchant] = UNRECOGNIZED_CATEGORY

    return all_results
