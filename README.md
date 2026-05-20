# ClinTrialist Report

A Drudge-style aggregator for pharma clinical statisticians.

Top section (3 balanced CSS columns):
- **Stats & Trial Methods** journals (alphabetical) flow across all three columns
- **Industry** trade press (Fierce Pharma / Fierce Biotech) follows the last stats journal

Below, collapsible panels:
- **Regulatory Watch** (default open) - FDA, EMA, Health Canada, PMDA - guidance, approvals, workshops
- **General Medical** - NEJM, The Lancet, JAMA, BMJ
- **Gastroenterology**, **Immunology**, **Oncology**, **Neuroscience**

Title links are color-coded by topic:
- Purple = AI / ML
- Orange = Adaptive designs
- Teal = Causal inference

Built on the same pattern as the sibling `GRUDGE` project. Daily GitHub Actions cron at 17:00 UTC rebuilds `docs/index.html` and publishes via GitHub Pages.

Contact: clintrialist@gmail.com

## Local development

```bash
python -m venv .venv
.venv/Scripts/python.exe -m pip install -e ".[dev]"
.venv/Scripts/python.exe run.py
# open docs/index.html
```

## Tests

```bash
.venv/Scripts/python.exe -m pytest tests/ -q
```
