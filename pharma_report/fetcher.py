"""RSS feed fetching, normalization, dedupe, and recency selection.

Ported from GRUDGE's grudge/feeds.py with the drama-scoring removed.
"""

from datetime import datetime, timezone

import feedparser


def _parse_date(entry: dict) -> datetime:
    for field in ("published_parsed", "updated_parsed"):
        parsed = entry.get(field)
        if parsed:
            try:
                from time import mktime

                return datetime.fromtimestamp(mktime(parsed), tz=timezone.utc)
            except (ValueError, OverflowError, OSError):
                pass
    return datetime.now(timezone.utc)


def _normalize_entry(entry: dict, source: str) -> dict | None:
    title = entry.get("title", "").strip()
    link = entry.get("link", "").strip()
    if not title or not link:
        return None
    return {
        "title": title,
        "link": link,
        "published": _parse_date(entry),
        "source": source,
        "summary": entry.get("summary", ""),
    }


def fetch_feed(name: str, url: str, timeout: int = 10) -> list[dict]:
    """Fetch and normalize one RSS feed. Logs OK/SKIP/FAIL line."""
    try:
        feed = feedparser.parse(url, request_headers={"User-Agent": "PharmaReport/0.1"})
        if feed.bozo and not feed.entries:
            print(f"  [SKIP] {name}: feed error")
            return []
        results = []
        for entry in feed.entries:
            normalized = _normalize_entry(entry, name)
            if normalized:
                results.append(normalized)
        print(f"  [OK]   {name}: {len(results)} items")
        return results
    except Exception as e:
        print(f"  [FAIL] {name}: {e}")
        return []


def filter_by_title(entries: list[dict], exclude_substrings: list[str]) -> list[dict]:
    """Drop entries whose titles contain any banned substring (case-insensitive)."""
    bans = [s.lower() for s in exclude_substrings]
    return [e for e in entries if not any(b in e["title"].lower() for b in bans)]


def dedupe(entries: list[dict]) -> list[dict]:
    """Drop duplicate titles, keeping first occurrence."""
    seen: set[str] = set()
    unique: list[dict] = []
    for e in entries:
        key = e["title"].lower().strip()
        if key not in seen:
            seen.add(key)
            unique.append(e)
    return unique


def latest_n(entries: list[dict], n: int) -> list[dict]:
    """Sort by publish date descending, return first n."""
    entries.sort(key=lambda e: e["published"], reverse=True)
    return entries[:n]
