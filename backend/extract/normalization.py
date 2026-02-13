from __future__ import annotations

import re
from typing import Optional


def normalize_decimal_separator(raw_price: str) -> Optional[float]:
    """Normalize prices using commas or periods as decimal separators."""

    cleaned = re.sub(r"[^\d,.-]", "", raw_price).strip()
    if not cleaned:
        return None

    if "," in cleaned and "." in cleaned:
        cleaned = cleaned.replace(".", "").replace(",", ".")
    elif "," in cleaned:
        cleaned = cleaned.replace(",", ".")

    try:
        return float(cleaned)
    except ValueError:
        return None


def normalize_product_name(name: str) -> str:
    """Standardize whitespace/casing in product names."""

    name = re.sub(r"\s+", " ", name).strip()
    return name.title()
