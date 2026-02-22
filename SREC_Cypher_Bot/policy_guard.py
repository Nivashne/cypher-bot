"""Policy guard for sensitive cybersecurity/privacy prompts."""

from typing import Tuple

BLOCKED_KEYWORDS = {
    "salary",
    "turnover",
    "budget",
    "confidential",
    "internal database",
    "staff details",
}


def is_query_allowed(query: str) -> Tuple[bool, str]:
    """Return whether a query is policy-compliant.

    Returns:
        (allowed, reason)
    """
    normalized = query.lower()
    for keyword in BLOCKED_KEYWORDS:
        if keyword in normalized:
            return False, f"Blocked by policy keyword: '{keyword}'"
    return True, "ALLOWED"
