import re
from typing import Dict, List

SENSITIVE_PATTERNS: Dict[str, re.Pattern] = {
    "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    "phone": re.compile(r"\b(\+?1?\d{10,14})\b"),
    "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "credit_card": re.compile(r"\b(?:\d[ -]*?){13,16}\b"),
}

def detect_sensitive_data(text: str) -> List[str]:
    found = []
    for label, pattern in SENSITIVE_PATTERNS.items():
        if pattern.search(text or ""):
            found.append(label)
    return found

def sanitize_text(text: str) -> str:
    for label, pattern in SENSITIVE_PATTERNS.items():
        text = pattern.sub(f"[REDACTED_{label.upper()}]", text or "")
    return text
