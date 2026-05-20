"""Topic tagging assertions."""

from pharma_report.topics import tag_entry


def _entry(title: str, summary: str = "") -> dict:
    return {"title": title, "summary": summary}


def test_causal_tag():
    e = _entry("A causal forest approach to estimating treatment effects")
    assert tag_entry(e) == ["ai_ml", "causal"] or "causal" in e["topics"]
    assert "causal" in e["topics"]


def test_ai_ml_tag():
    e = _entry("Deep learning models for clinical trial enrichment")
    assert tag_entry(e) == ["ai_ml"]


def test_adaptive_tag():
    e = _entry("Bayesian adaptive design for dose finding")
    assert "adaptive" in tag_entry(e)


def test_estimand_tags_causal():
    e = _entry("Estimands and intercurrent events in oncology trials")
    assert "causal" in tag_entry(e)


def test_no_tag_for_plain_title():
    e = _entry("A new estimator for clinical trials with missing data")
    # 'estimator' must NOT match 'estimand'
    assert tag_entry(e) == []


def test_multiple_tags():
    e = _entry("Machine learning for causal inference in observational data")
    tags = tag_entry(e)
    assert "ai_ml" in tags
    assert "causal" in tags


def test_topics_field_set():
    e = _entry("Adaptive platform trial design")
    tag_entry(e)
    assert e["topics"] == ["adaptive"]
