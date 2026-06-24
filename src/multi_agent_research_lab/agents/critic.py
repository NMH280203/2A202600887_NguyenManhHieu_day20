"""Optional critic agent for fact-checking and safety review."""

import re

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.config import get_settings
from multi_agent_research_lab.core.schemas import AgentName, AgentResult
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.observability.tracing import trace_span
from multi_agent_research_lab.services.llm_client import LLMClient


class CriticAgent(BaseAgent):
    """Optional fact-checking and safety-review agent."""

    name = "critic"

    def __init__(self, llm: LLMClient | None = None) -> None:
        self._llm = llm or LLMClient()

    def run(self, state: ResearchState) -> ResearchState:
        """Validate final answer and append findings."""

        settings = get_settings()
        answer = state.final_answer or ""
        source_count = len(state.sources)
        citation_refs = set(re.findall(r"\[(\d+)\]", answer))
        coverage = len(citation_refs) / max(source_count, 1) if source_count else 0.0

        with trace_span("critic.review", {"citation_coverage": coverage}) as span:
            response = self._llm.complete(
                system_prompt=(
                    "You are a critic reviewing a research answer. Check unsupported claims, "
                    "missing citations, and hallucinations. End with PASS or FAIL and concrete "
                    "fixes for the writer."
                ),
                user_prompt=(
                    f"Query: {state.request.query}\n\n"
                    f"Answer:\n{answer}\n\n"
                    f"Sources available: {source_count}\n"
                    f"Citation refs found: {sorted(citation_refs)}\n"
                    f"Citation coverage ratio: {coverage:.2f}\n"
                    f"Minimum required: {settings.min_citation_coverage:.2f}"
                ),
            )
            span["attributes"]["citation_coverage"] = coverage

        state.citation_coverage = coverage
        state.critic_feedback = response.content
        state.critic_reviewed = True

        state.agent_results.append(
            AgentResult(
                agent=AgentName.CRITIC,
                content=response.content,
                metadata={
                    "citation_coverage": coverage,
                    "passed": coverage >= settings.min_citation_coverage,
                    "input_tokens": response.input_tokens,
                    "output_tokens": response.output_tokens,
                    "cost_usd": response.cost_usd,
                },
            )
        )
        state.add_trace_event(
            "critic.done",
            {"citation_coverage": coverage, "passed": coverage >= settings.min_citation_coverage},
        )
        return state
