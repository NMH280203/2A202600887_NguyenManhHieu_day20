"""Researcher agent."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.errors import AgentExecutionError
from multi_agent_research_lab.core.schemas import AgentName, AgentResult
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.observability.tracing import trace_span
from multi_agent_research_lab.services.llm_client import LLMClient
from multi_agent_research_lab.services.search_client import SearchClient


class ResearcherAgent(BaseAgent):
    """Collects sources and creates concise research notes."""

    name = "researcher"

    def __init__(
        self,
        llm: LLMClient | None = None,
        search: SearchClient | None = None,
    ) -> None:
        self._llm = llm or LLMClient()
        self._search = search or SearchClient()

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.sources` and `state.research_notes`."""

        query = state.request.query
        max_sources = state.request.max_sources

        with trace_span("researcher.search", {"query": query}) as span:
            try:
                sources = self._search.search(query, max_results=max_sources)
                state.sources = sources
                span["attributes"]["source_count"] = len(sources)
            except Exception as exc:
                state.errors.append(f"researcher_search_failed: {exc}")
                raise AgentExecutionError("Researcher search failed") from exc

        source_block = "\n\n".join(
            f"[{i + 1}] {src.title}\nURL: {src.url or 'n/a'}\n{src.snippet}"
            for i, src in enumerate(state.sources)
        )

        with trace_span("researcher.summarize") as span:
            response = self._llm.complete(
                system_prompt=(
                    "You are a research assistant. Summarize the provided sources into concise "
                    "research notes with numbered citations matching source indices."
                ),
                user_prompt=f"Query: {query}\n\nSources:\n{source_block}",
            )
            state.research_notes = response.content
            span["attributes"]["output_tokens"] = response.output_tokens

        state.agent_results.append(
            AgentResult(
                agent=AgentName.RESEARCHER,
                content=state.research_notes,
                metadata={
                    "source_count": len(state.sources),
                    "input_tokens": response.input_tokens,
                    "output_tokens": response.output_tokens,
                    "cost_usd": response.cost_usd,
                },
            )
        )
        state.add_trace_event("researcher.done", {"source_count": len(state.sources)})
        return state
