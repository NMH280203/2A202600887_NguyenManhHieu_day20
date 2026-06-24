"""Search client abstraction for ResearcherAgent."""

import json
import logging
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from multi_agent_research_lab.core.config import Settings, get_settings
from multi_agent_research_lab.core.schemas import SourceDocument
from multi_agent_research_lab.utils.query import extract_search_query

logger = logging.getLogger(__name__)


class SearchClient:
    """Provider-agnostic search client with Tavily and mock fallback."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()

    def search(self, query: str, max_results: int = 5) -> list[SourceDocument]:
        """Search for documents relevant to a query."""

        max_len = self._settings.tavily_max_query_length
        search_query = extract_search_query(query, max_length=max_len)
        if search_query != query.strip():
            logger.info(
                "Shortened search query from %d to %d chars",
                len(query),
                len(search_query),
            )

        if self._settings.tavily_api_key:
            try:
                return self._search_tavily(search_query, max_results)
            except (HTTPError, URLError, TimeoutError, ValueError) as exc:
                body = ""
                if isinstance(exc, HTTPError):
                    body = exc.read().decode(errors="replace")[:300]
                logger.warning("Tavily search failed, falling back to mock: %s %s", exc, body)

        return self._mock_search(search_query, max_results)

    def _search_tavily(self, query: str, max_results: int) -> list[SourceDocument]:
        if len(query) > 400:
            raise ValueError(f"Tavily query too long: {len(query)} chars (max 400)")

        payload = json.dumps(
            {
                "api_key": self._settings.tavily_api_key,
                "query": query,
                "max_results": min(max_results, 20),
                "include_answer": False,
                "search_depth": "basic",
            }
        ).encode()
        request = Request(
            "https://api.tavily.com/search",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(request, timeout=float(self._settings.timeout_seconds)) as response:
            data = json.loads(response.read().decode())

        results: list[SourceDocument] = []
        for item in data.get("results", [])[:max_results]:
            results.append(
                SourceDocument(
                    title=item.get("title", "Untitled"),
                    url=item.get("url"),
                    snippet=item.get("content", "")[:500],
                    metadata={"score": item.get("score")},
                )
            )
        if not results:
            raise ValueError("Tavily returned no results")
        return results

    @staticmethod
    def _mock_search(query: str, max_results: int) -> list[SourceDocument]:
        topics = query.split()[:6] or ["research"]
        topic = " ".join(topics)
        return [
            SourceDocument(
                title=f"Overview of {topic}",
                url=f"https://example.com/{i + 1}",
                snippet=(
                    f"Source {i + 1} discusses {topic}: background, methods, and recent advances "
                    "relevant to the query."
                ),
            )
            for i in range(min(max_results, 3))
        ]
