"""HTML generation: 3-column top section (FDA + 2 stats cols) and collapsible therapeutic panels."""

from datetime import datetime, timezone

from pharma_report.feeds import REGULATORY_AGENCY_HOMES
from pharma_report.topics import TOPIC_ORDER, TOPICS

DEFAULT_LINK_COLOR = "#0000cc"


def _time_ago(published: datetime) -> str:
    now = datetime.now(timezone.utc)
    delta = now - published
    minutes = int(delta.total_seconds() / 60)
    if minutes < 1:
        return "just now"
    if minutes < 60:
        return f"{minutes}m ago"
    hours = minutes // 60
    if hours < 24:
        return f"{hours}h ago"
    days = hours // 24
    return f"{days}d ago"


def _split_list(items: list, n: int) -> list[list]:
    k, m = divmod(len(items), n)
    return [items[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n)]


def _primary_color(topics: list[str]) -> str:
    if not topics:
        return DEFAULT_LINK_COLOR
    return TOPICS[topics[0]]["color"]


def _badges(topics: list[str]) -> str:
    """Render small colored [tag] badges for any secondary topics on an entry."""
    if len(topics) <= 1:
        return ""
    parts = []
    for key in topics[1:]:
        spec = TOPICS[key]
        parts.append(
            f' <font size="1" color="{spec["color"]}"><b>[{spec["label"]}]</b></font>'
        )
    return "".join(parts)


def _article_link(entry: dict) -> str:
    color = _primary_color(entry.get("topics", []))
    return (
        f'<a href="{entry["link"]}" style="color: {color};">'
        f'{entry["title"]}</a>{_badges(entry.get("topics", []))}'
    )


def _fda_block(entry: dict) -> str:
    return (
        '<div style="break-inside: avoid; page-break-inside: avoid; margin-bottom: 6px;">'
        f"<b>{_article_link(entry)}</b>"
        f'<br><font size="1" color="#666666">{entry["source"]} | '
        f"{_time_ago(entry['published'])}</font>"
        "</div>"
    )


def _journal_block(journal: dict) -> str:
    """A journal's header + its latest entries; atomic so multicol won't split it."""
    name = journal["name"]
    home = journal.get("home", "#")
    entries = journal.get("entries") or []
    parts = [
        '<div style="margin-bottom: 8px; break-inside: avoid; page-break-inside: avoid;">',
        f'<font size="3"><b>'
        f'<a href="{home}" style="color: #000000; text-decoration: none;">'
        f'{name}</a></b></font>',
        "<br>",
    ]
    if not entries:
        parts.append('<i><font size="1" color="#888888">No recent articles.</font></i>')
    else:
        for e in entries:
            parts.append(
                f'{_article_link(e)}'
                f'<br><font size="1" color="#666666">{_time_ago(e["published"])}</font>'
                f"<br>"
            )
    parts.append('<hr style="border: none; border-top: 1px dotted #cccccc; margin: 6px 0;">')
    parts.append("</div>")
    return "\n".join(parts)


def _pick_lead(regulatory: dict[str, list[dict]]) -> dict | None:
    """Newest FDA item; falls back to newest regulatory item across all agencies."""
    fda_items = regulatory.get("FDA") or []
    if fda_items:
        return fda_items[0]
    all_items = [e for items in regulatory.values() for e in items]
    if not all_items:
        return None
    all_items.sort(key=lambda e: e["published"], reverse=True)
    return all_items[0]


def _pick_teaser(journals: list[dict]) -> dict | None:
    """Newest article across NEJM / The Lancet / JAMA — Drudge's top-left teaser slot."""
    tier1 = {"NEJM", "The Lancet", "JAMA"}
    candidates = []
    for j in journals:
        if j["name"] in tier1:
            candidates.extend(j.get("entries") or [])
    if not candidates:
        return None
    candidates.sort(key=lambda e: e["published"], reverse=True)
    return candidates[0]


def _lead_block(entry: dict | None) -> str:
    if not entry:
        return ""
    color = _primary_color(entry.get("topics", []))
    # Drudge-style: huge italic bold red, centered.
    return (
        '<div style="text-align: center; padding: 4px 30px 10px 30px;">'
        f'<a href="{entry["link"]}" '
        f'style="color: #cc0000; text-decoration: none; '
        f'font-size: 2.1em; font-weight: bold; font-style: italic; '
        f'text-shadow: 1px 1px 2px #cccccc;">'
        f'{entry["title"]}</a>'
        f'<br><font size="1" color="#666666">{entry["source"]} | '
        f'{_time_ago(entry["published"])}</font>'
        f'<span style="color:{color};">{_badges(entry.get("topics", []))}</span>'
        "</div>"
    )


def _teaser_block(entry: dict | None) -> str:
    if not entry:
        return ""
    return (
        '<div style="font-size: 12px; padding: 4px 8px; line-height: 1.3;">'
        f'<font size="1" color="#777777"><b>{entry["source"]}</b> &middot; '
        f'{_time_ago(entry["published"])}</font><br>'
        f'<i><a href="{entry["link"]}" style="color: #000088; text-decoration: none;">'
        f'{entry["title"]}</a></i>'
        "</div>"
    )


def _legend() -> str:
    swatches = []
    for key in TOPIC_ORDER:
        spec = TOPICS[key]
        swatches.append(
            f'<font color="{spec["color"]}"><b>&#9632; {spec["label"]}</b></font>'
        )
    return (
        '<div style="text-align: center; padding: 6px; font-size: 12px; '
        'background-color: #f7f7f7;">'
        '<b>TOPIC COLORS:</b> &nbsp; '
        + " &nbsp; ".join(swatches)
        + " &nbsp; <i>(uncolored = no tag)</i></div>"
    )


def build_page(
    regulatory: dict[str, list[dict]],
    industry_items: list[dict],
    journals: list[dict],
) -> str:
    now = datetime.now(timezone.utc).strftime("%A, %B %d, %Y %H:%M UTC")

    stats_journals = sorted(
        [j for j in journals if j["category"] == "stats"], key=lambda j: j["name"].lower()
    )

    general_journals = sorted(
        [j for j in journals if j["category"] == "general"], key=lambda j: j["name"].lower()
    )

    lead = _pick_lead(regulatory)
    teaser = _pick_teaser(journals)

    lines = [
        "<!DOCTYPE html>",
        "<html>",
        "<head>",
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        "<title>ClinTrialist Report</title>",
        '<base target="_blank" rel="noopener noreferrer">',
        "</head>",
        '<body style="font-family: \'Times New Roman\', Times, serif; '
        "margin: 0; padding: 0; background-color: #ffffff;\">",
        "",
        "<!-- HEADER: top-left teaser + centered lead story above the brand -->",
        '<table width="100%" cellpadding="6" cellspacing="0" border="0">',
        '<tr valign="top">',
        '<td width="25%" align="left">',
        _teaser_block(teaser),
        "</td>",
        '<td width="50%" align="center">',
        _lead_block(lead),
        "</td>",
        '<td width="25%"></td>',
        "</tr>",
        "</table>",
        "",
        "<!-- BRAND -->",
        '<div style="text-align: center; padding: 6px 0 10px 0;">',
        '<div style="display: flex; justify-content: center; align-items: center; '
        'gap: 14px; flex-wrap: wrap;">',
        # Logo: bell curve (AI/ML purple) over a forest-plot CI bar (Causal teal)
        # with point estimate (Adaptive orange) just right of a dashed null line.
        '<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" '
        'viewBox="0 0 48 48" role="img" '
        'aria-label="ClinTrialist Report logo: bell curve over a forest plot">'
        '<line x1="24" y1="4" x2="24" y2="46" stroke="#cccccc" '
        'stroke-width="0.6" stroke-dasharray="2,2"/>'
        '<path d="M 4 30 C 14 30, 18 10, 24 10 C 30 10, 34 30, 44 30" '
        'fill="none" stroke="#6a1b9a" stroke-width="2.4" stroke-linecap="round"/>'
        '<line x1="10" y1="40" x2="38" y2="40" stroke="#00695c" '
        'stroke-width="2.4" stroke-linecap="round"/>'
        '<line x1="10" y1="36.5" x2="10" y2="43.5" stroke="#00695c" stroke-width="2"/>'
        '<line x1="38" y1="36.5" x2="38" y2="43.5" stroke="#00695c" stroke-width="2"/>'
        '<circle cx="26" cy="40" r="3.2" fill="#e65100"/>'
        '</svg>',
        '<h1 style="'
        "font-family: 'Times New Roman', Times, serif; "
        "font-size: 4.2em; font-weight: bold; font-style: italic; "
        "margin: 0; letter-spacing: 1px; "
        "text-shadow: 3px 3px 4px #aaaaaa; color: #000000;"
        '">ClinTrialist Report</h1>',
        "</div>",
        '<font size="2" color="#333333"><i>FDA news + clinical/pharma stats journals</i></font>',
        f'<br><font size="2" color="#555555">{now}</font>',
        "</div>",
        _legend(),
        "<hr>",
        "",
        "<!-- TOP SECTION: Stats journals then Industry, flowing across 3 balanced CSS columns -->",
        '<div style="column-count: 3; column-gap: 20px; '
        'column-rule: 1px solid #cccccc; padding: 8px 16px; font-size: 14px;">',
        "",
        '<!-- Stats banner leads, journals flow across columns -->',
        '<div style="break-inside: avoid; page-break-inside: avoid; margin-bottom: 8px;">',
        '<div style="text-align: center; padding: 4px 0; background-color: #e5f0ff;">',
        '<font size="3"><b>STATS &amp; TRIAL METHODS</b></font><br>',
        '<font size="1" color="#555555">Pharma / clinical statistics journals</font>',
        "</div>",
        '<hr style="margin: 6px 0;">',
        "</div>",
    ]

    # All stats journals (single alphabetical list). Each block is atomic; multicol balances.
    for j in stats_journals:
        lines.append(_journal_block(j))

    lines.extend([
        "",
        '<!-- Industry follows the last stats journal -->',
        '<div style="break-inside: avoid; page-break-inside: avoid; '
        'margin-top: 12px; margin-bottom: 8px;">',
        '<div style="text-align: center; padding: 4px 0; background-color: #fff4e5;">',
        '<font size="3"><b>INDUSTRY</b></font><br>',
        '<font size="1" color="#555555">Fierce Pharma, Fierce Biotech</font>',
        "</div>",
        '<hr style="margin: 6px 0;">',
        "</div>",
    ])

    if industry_items:
        for e in industry_items:
            lines.append(_fda_block(e))
    else:
        lines.append("<i>No industry items.</i>")

    lines.extend([
        "</div>",   # close multicol container
        "",
        "<hr>",
    ])

    # Regulatory Watch collapsible (default open) -- 4 sub-columns: FDA / EMA / Health Canada / PMDA.
    _AGENCY_ORDER = ["FDA", "EMA", "Health Canada", "PMDA"]
    if any(regulatory.get(a) for a in _AGENCY_ORDER):
        lines.extend([
            "",
            '<details open style="margin: 8px;">',
            '<summary style="cursor: pointer; padding: 10px; background-color: #ffe5e5; '
            'font-size: 1.3em;"><b>REGULATORY WATCH</b> '
            '<font size="2" color="#555555">&mdash; guidance, approvals, workshops</font>'
            '</summary>',
            '<table width="100%" cellpadding="10" cellspacing="0" border="0">',
            '<tr valign="top">',
        ])
        for i, agency in enumerate(_AGENCY_ORDER):
            border = ' style="border-right: 1px solid #cccccc; padding: 8px; font-size: 13px;"' \
                if i < len(_AGENCY_ORDER) - 1 else ' style="padding: 8px; font-size: 13px;"'
            lines.append(f'<td width="25%"{border}>')
            home = REGULATORY_AGENCY_HOMES.get(agency, "#")
            lines.append(
                '<div style="text-align: center; padding: 4px 0; background-color: #f7e9e9;">'
                f'<font size="3"><b>'
                f'<a href="{home}" style="color: #000000; text-decoration: none;" target="_blank" '
                f'rel="noopener">{agency}</a>'
                f'</b></font></div><hr>'
            )
            agency_items = regulatory.get(agency) or []
            if agency_items:
                for e in agency_items:
                    lines.append(_fda_block(e))
            else:
                lines.append('<i><font size="1" color="#888888">No items.</font></i>')
            lines.append("</td>")
        lines.extend(["</tr>", "</table>", "</details>"])

    # General Medical collapsible panel -- 2 columns of NEJM/Lancet/JAMA/BMJ.
    if general_journals:
        gen_split = _split_list(general_journals, 2)
        lines.extend([
            "",
            '<details style="margin: 8px;">',
            '<summary style="cursor: pointer; padding: 10px; background-color: #eee5ff; '
            'font-size: 1.3em;"><b>GENERAL MEDICAL</b></summary>',
            '<table width="100%" cellpadding="10" cellspacing="0" border="0">',
            '<tr valign="top">',
        ])
        for i, col in enumerate(gen_split):
            border = ' style="border-right: 1px solid #cccccc; padding: 8px; font-size: 14px;"' \
                if i == 0 else ' style="padding: 8px; font-size: 14px;"'
            lines.append(f'<td width="50%"{border}>')
            for j in col:
                lines.append(_journal_block(j))
            lines.append("</td>")
        lines.extend(["</tr>", "</table>", "</details>"])

    # Collapsible therapeutic panels (default collapsed).
    therapeutic_keys = ["gi", "immuno", "onc", "neuro"]
    therapeutic_labels = {
        "gi":     "GASTROENTEROLOGY",
        "immuno": "IMMUNOLOGY",
        "onc":    "ONCOLOGY",
        "neuro":  "NEUROSCIENCE",
    }
    for cat in therapeutic_keys:
        cat_journals = sorted(
            [j for j in journals if j["category"] == cat], key=lambda j: j["name"].lower()
        )
        if not cat_journals:
            continue
        cat_split = _split_list(cat_journals, 3)
        lines.extend([
            "",
            '<details style="margin: 8px;">',
            f'<summary style="cursor: pointer; padding: 10px; background-color: #f0f0f0; '
            'font-size: 1.3em;"><b>'
            + therapeutic_labels[cat]
            + "</b></summary>",
            '<table width="100%" cellpadding="10" cellspacing="0" border="0">',
            '<tr valign="top">',
        ])
        widths = ["33%", "33%", "34%"]
        for i, col in enumerate(cat_split):
            border = ' style="border-right: 1px solid #cccccc; padding: 8px; font-size: 14px;"' \
                if i < 2 else ' style="padding: 8px; font-size: 14px;"'
            lines.append(f'<td width="{widths[i]}"{border}>')
            for j in col:
                lines.append(_journal_block(j))
            lines.append("</td>")
        lines.extend([
            "</tr>",
            "</table>",
            "</details>",
        ])

    lines.extend([
        "",
        "<hr>",
        '<p style="text-align: center; font-size: 11px; color: #999999;">',
        "ClinTrialist Report &copy; 2025-2026. Article links property of their respective publishers.",
        "<br>Aggregated by robots. Read by statisticians.",
        '<br>Contact: <a href="mailto:clintrialist@gmail.com" '
        'style="color: #555555;">clintrialist@gmail.com</a>',
        '<br><br><img src="https://hits.sh/clintrialist.gcicc.github.io.svg?'
        'style=flat-square&label=page%20views&color=2a4d6f" alt="page views">',
        "</p>",
        "</body>",
        "</html>",
    ])

    return "\n".join(lines)
