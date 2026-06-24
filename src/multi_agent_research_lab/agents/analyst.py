"""Analyst agent."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.schemas import AgentName, AgentResult
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.observability.tracing import trace_span
from multi_agent_research_lab.services.llm_client import LLMClient


class AnalystAgent(BaseAgent):
    """Turns research notes into structured insights."""

    name = "analyst"

    def __init__(self, llm: LLMClient | None = None) -> None:
        self._llm = llm or LLMClient()

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.analysis_notes`."""

        notes = state.research_notes or "No research notes available."

        with trace_span("analyst.analyze") as span:
            response = self._llm.complete(
                system_prompt=(
                    "You are an analyst. Extract key claims, compare viewpoints, flag weak "
                    "evidence, and note open questions. Use bullet points."
                ),
                user_prompt=(
                    f"Original query: {state.request.query}\n\nResearch notes:\n{notes}"
                ),
            )
            state.analysis_notes = response.content
            span["attributes"]["output_tokens"] = response.output_tokens

        state.agent_results.append(
            AgentResult(
                agent=AgentName.ANALYST,
                content=state.analysis_notes,
                metadata={
                    "input_tokens": response.input_tokens,
                    "output_tokens": response.output_tokens,
                    "cost_usd": response.cost_usd,
                },
            )
        )
        state.add_trace_event("analyst.done", {})
        return state
