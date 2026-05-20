"""ClinTrialist Report entry point: fetch -> dedupe -> tag -> build -> write."""

from collections import Counter
from pathlib import Path

from pharma_report.feeds import (
    GENERAL_LIMIT,
    INDUSTRY_FEEDS,
    INDUSTRY_LIMIT,
    JOURNALS,
    PER_AGENCY_LIMIT,
    PER_JOURNAL_LIMIT,
    REGULATORY_AGENCIES,
    REGULATORY_EXCLUDE_TITLES,
    REGULATORY_FEEDS,
)
from pharma_report.fetcher import dedupe, fetch_feed, filter_by_title, latest_n
from pharma_report.html_builder import build_page
from pharma_report.topics import tag_entry


def _fetch_all(feeds: list[dict]) -> list[dict]:
    results: list[dict] = []
    for f in feeds:
        results.extend(fetch_feed(f["name"], f["rss"]))
    return results


def main() -> None:
    print("=== REGULATORY FEEDS ===")
    # Fetch each sub-feed but stamp the source with the agency, not the sub-feed name,
    # so the UI shows e.g. "FDA" rather than "FDA Guidance" for each item.
    regulatory_by_agency: dict[str, list[dict]] = {a: [] for a in REGULATORY_AGENCIES}
    for f in REGULATORY_FEEDS:
        entries = fetch_feed(f["name"], f["rss"])
        for e in entries:
            e["source"] = f["agency"]
        regulatory_by_agency[f["agency"]].extend(entries)
    for agency in REGULATORY_AGENCIES:
        items = filter_by_title(dedupe(regulatory_by_agency[agency]), REGULATORY_EXCLUDE_TITLES)
        items = latest_n(items, PER_AGENCY_LIMIT)
        for e in items:
            tag_entry(e)
        regulatory_by_agency[agency] = items
        print(f"  {agency}: {len(items)} selected")

    print("\n=== INDUSTRY FEEDS ===")
    industry_raw = _fetch_all(INDUSTRY_FEEDS)
    industry_items = latest_n(dedupe(industry_raw), INDUSTRY_LIMIT)
    for e in industry_items:
        tag_entry(e)
    print(f"Industry: {len(industry_raw)} raw -> {len(industry_items)} selected")

    print("\n=== JOURNAL FEEDS ===")
    topic_counter: Counter = Counter()
    for j in JOURNALS:
        raw = fetch_feed(j["name"], j["rss"])
        limit = GENERAL_LIMIT if j["category"] == "general" else PER_JOURNAL_LIMIT
        items = latest_n(dedupe(raw), limit)
        for e in items:
            tags = tag_entry(e)
            for t in tags:
                topic_counter[t] += 1
        j["entries"] = items

    # Add topic counts for regulatory + industry too.
    for agency_items in regulatory_by_agency.values():
        for e in agency_items:
            for t in e.get("topics", []):
                topic_counter[t] += 1
    for e in industry_items:
        for t in e.get("topics", []):
            topic_counter[t] += 1

    print(
        "\nTopics tagged: "
        + ", ".join(f"{n} {key}" for key, n in topic_counter.most_common())
        if topic_counter
        else "Topics tagged: 0"
    )

    html = build_page(regulatory_by_agency, industry_items, JOURNALS)
    out_path = Path(__file__).parent / "docs" / "index.html"
    out_path.parent.mkdir(exist_ok=True)
    out_path.write_text(html, encoding="utf-8")
    print(f"\nWrote {len(html):,} bytes to {out_path}")


if __name__ == "__main__":
    main()
