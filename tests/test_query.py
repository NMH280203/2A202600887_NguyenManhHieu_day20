"""Tests for search query extraction."""

from multi_agent_research_lab.utils.query import extract_search_query


def test_extract_search_query_uses_quoted_topic() -> None:
    prompt = (
        'You are helping prepare a briefing on the topic:\n\n'
        '"Do multi-agent LLM systems outperform single-agent systems?"\n\n'
        + "x" * 500
    )
    result = extract_search_query(prompt)
    assert "multi-agent LLM" in result
    assert len(result) <= 380


def test_extract_search_query_short_passthrough() -> None:
    query = "What is GraphRAG?"
    assert extract_search_query(query) == query
