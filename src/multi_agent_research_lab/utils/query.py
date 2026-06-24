"""Query helpers for search and retrieval."""

import re


def extract_search_query(text: str, max_length: int = 380) -> str:
    """Reduce a long research prompt to a Tavily-compatible search query.

    Tavily rejects queries longer than 400 characters. This helper prefers quoted
    topics, explicit research questions, and the first substantive line.
    """

    stripped = text.strip()
    if len(stripped) <= max_length:
        return stripped

    quoted = re.findall(r'"([^"]{10,})"', stripped)
    if quoted:
        return quoted[0][:max_length]

    topic_match = re.search(
        r"(?:topic|title)\s*:\s*(.+?)(?:\n|$)",
        stripped,
        flags=re.IGNORECASE,
    )
    if topic_match:
        return topic_match.group(1).strip()[:max_length]

    question_match = re.search(r"([^\n?]{10,}\?)", stripped)
    if question_match:
        return question_match.group(1).strip()[:max_length]

    first_line = next((line.strip() for line in stripped.splitlines() if line.strip()), stripped)
    if len(first_line) <= max_length:
        return first_line

    truncated = first_line[:max_length]
    if " " in truncated:
        truncated = truncated.rsplit(" ", 1)[0]
    return truncated
