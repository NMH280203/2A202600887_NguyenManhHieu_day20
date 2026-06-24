"""Writer agent."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.schemas import AgentName, AgentResult
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.observability.tracing import trace_span
from multi_agent_research_lab.services.llm_client import LLMClient


class WriterAgent(BaseAgent):
    """Produces final answer from research and analysis notes."""

    name = "writer"

    def __init__(self, llm: LLMClient | None = None) -> None:
        self._llm = llm or LLMClient()

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.final_answer`."""

        citations = "\n".join(
            f"- [{i + 1}] {src.title} ({src.url or 'no url'})"
            for i, src in enumerate(state.sources)
        )
        is_revision = bool(state.critic_feedback and state.critic_reviewed)

        revision_block = ""
        if is_revision:
            revision_block = (
                f"\n\nPrevious draft:\n{state.final_answer or 'n/a'}\n\n"
                f"Critic feedback:\n{state.critic_feedback}\n\n"
                "Revise the answer. Add inline citations like [1], [2] for every major claim."
            )

        with trace_span(
            "writer.compose",
            {"revision": is_revision, "writer_revisions": state.writer_revisions},
        ) as span:
            response = self._llm.complete(
                system_prompt=(
                    "You are a technical writer. Synthesize a clear, well-structured answer for "
                    f"the audience: {state.request.audience}. Include inline citations like [1], "
                    "[2] referencing the source list for each major claim."
                ),
                user_prompt=(
                    f"Query: {state.request.query}\n\n"
                    f"Research notes:\n{state.research_notes or 'n/a'}\n\n"
                    f"Analysis:\n{state.analysis_notes or 'n/a'}\n\n"
                    f"Available sources:\n{citations}"
                    f"{revision_block}"
                ),
            )
            state.final_answer = response.content
            span["attributes"]["output_tokens"] = response.output_tokens

        if is_revision:
            state.writer_revisions += 1
            state.critic_reviewed = False

        state.agent_results.append(
            AgentResult(
                agent=AgentName.WRITER,
                content=state.final_answer,
                metadata={
                    "revision": is_revision,
                    "writer_revisions": state.writer_revisions,
                    "input_tokens": response.input_tokens,
                    "output_tokens": response.output_tokens,
                    "cost_usd": response.cost_usd,
                },
            )
        )
        state.add_trace_event(
            "writer.done",
            {"revision": is_revision, "writer_revisions": state.writer_revisions},
        )
        return state
