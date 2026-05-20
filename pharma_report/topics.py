"""Topic tagging: regex-match article titles to AI/ML, Adaptive designs, Causal inference."""

import re

TOPICS: dict[str, dict] = {
    "ai_ml": {
        "label": "AI/ML",
        "color": "#6a1b9a",
        "patterns": [
            r"\bmachine learning\b",
            r"\bdeep learning\b",
            r"\bneural network",
            r"\bartificial intelligence\b",
            r"\b(AI|ML)\b",
            r"\btransformer\b",
            r"\bLLM\b",
            r"\blarge language model",
            r"\breinforcement learning\b",
            r"\brandom forest",
            r"\bgradient boost",
            r"\bxgboost\b",
        ],
    },
    "adaptive": {
        "label": "Adaptive",
        "color": "#e65100",
        "patterns": [
            r"\badaptive\b",
            r"\bgroup sequential\b",
            r"\bplatform trial",
            r"\bbasket trial",
            r"\bumbrella trial",
            r"\bsample size re-?estimation\b",
            r"\bresponse-?adaptive\b",
            r"\bseamless\b.{0,20}(phase|design)",
            r"\bMAMS\b",
        ],
    },
    "causal": {
        "label": "Causal",
        "color": "#00695c",
        "patterns": [
            r"\bcausal\b",
            r"\bcounterfactual\b",
            r"\bconfound",
            r"\bpropensity score\b",
            r"\binstrumental variable\b",
            r"\bg-?(computation|formula|methods?)\b",
            r"\bmarginal structural\b",
            r"\bDAG\b",
            r"\bdo-calculus\b",
            r"\bintercurrent\b",
            r"\bestimand\b",
        ],
    },
}

# Pre-compile patterns for speed.
_COMPILED = {
    key: [re.compile(p, re.IGNORECASE) for p in spec["patterns"]]
    for key, spec in TOPICS.items()
}

# Stable display order: ai_ml first, then adaptive, then causal.
TOPIC_ORDER = ["ai_ml", "adaptive", "causal"]


def tag_entry(entry: dict) -> list[str]:
    """Return list of topic keys whose patterns match the title or summary."""
    text = f"{entry.get('title', '')} {entry.get('summary', '')}"
    tags: list[str] = []
    for key in TOPIC_ORDER:
        if any(p.search(text) for p in _COMPILED[key]):
            tags.append(key)
    entry["topics"] = tags
    return tags
