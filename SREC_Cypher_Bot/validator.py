"""Context validator to remove confidential content from retrieval results."""

from typing import Dict, List

CONFIDENTIAL_TAG = "[TAG:CONFIDENTIAL]"


def filter_safe_documents(documents: List[Dict]) -> List[Dict]:
    """Keep only documents that are not confidential."""
    safe_docs: List[Dict] = []
    for doc in documents:
        text = doc.get("text", "")
        if CONFIDENTIAL_TAG not in text:
            safe_docs.append(doc)
    return safe_docs
