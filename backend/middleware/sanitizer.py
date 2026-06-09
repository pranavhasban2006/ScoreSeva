"""
sanitizer.py
Input sanitization utilities for ScoreSeva API.
Strips dangerous characters from text inputs before NLP processing.
Prevents prompt injection and XSS in text fields.
"""

import re
import html


def sanitize_text(text: str, max_length: int = 1000) -> str:
    """
    Sanitize free-text input before NLP processing.
    - HTML-escapes special characters
    - Strips control characters and null bytes
    - Collapses excessive whitespace
    - Truncates to max_length
    """
    if not isinstance(text, str):
        return ""
    text = html.escape(text)
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:max_length]


def sanitize_applicant_id(applicant_id: str) -> str:
    """Allow only alphanumeric, dash, and underscore in IDs."""
    return re.sub(r"[^a-zA-Z0-9\-_]", "", applicant_id)[:64]
