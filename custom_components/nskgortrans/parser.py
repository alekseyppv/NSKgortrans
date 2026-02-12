"""Helpers for parsing NSK Gortrans stop page HTML."""

from __future__ import annotations

import html
import re
from typing import Iterable

ROUTE_FIX_TRANSLATION = str.maketrans({
    "a": "а",
    "b": "в",
    "c": "с",
    "e": "е",
    "h": "н",
    "k": "к",
    "m": "м",
    "o": "о",
    "p": "р",
    "t": "т",
    "x": "х",
    "y": "у",
})

MINUTES_RE = re.compile(r"(\d+)\s*(?:мин\.?|min)?", re.IGNORECASE)
TAG_RE = re.compile(r"<[^>]+>")
SCRIPT_RE = re.compile(r"<(script|style)\b[^>]*>.*?</\1>", re.IGNORECASE | re.DOTALL)
ROW_RE = re.compile(r"<tr\b[^>]*>(.*?)</tr>", re.IGNORECASE | re.DOTALL)


def normalize_route(value: str) -> str:
    """Normalize route value for robust matching."""
    value = value.strip().lower().replace(" ", "")
    return value.translate(ROUTE_FIX_TRANSLATION)


def _plain_text_from_html(html_content: str) -> str:
    cleaned = SCRIPT_RE.sub(" ", html_content)
    cleaned = TAG_RE.sub(" ", cleaned)
    cleaned = html.unescape(cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip().lower()


def _extract_rows(html_content: str) -> Iterable[str]:
    rows = ROW_RE.findall(html_content)
    if not rows:
        return (_plain_text_from_html(html_content),)

    return tuple(_plain_text_from_html(row) for row in rows)


def extract_minutes(html_content: str, route: str, transport_type_ru: str) -> int | None:
    """Extract minutes for specific route and transport type.

    Returns None when route/type were not found.
    """
    route_norm = normalize_route(route)
    transport_norm = transport_type_ru.strip().lower()

    candidates: list[int] = []
    for row in _extract_rows(html_content):
        if transport_norm not in row:
            continue

        row_tokens = [normalize_route(token) for token in row.split()]
        if route_norm not in row_tokens and route_norm not in normalize_route(row):
            continue

        for match in MINUTES_RE.finditer(row):
            minute_value = int(match.group(1))
            if 0 <= minute_value <= 240:
                candidates.append(minute_value)

    if not candidates:
        return None

    return min(candidates)
