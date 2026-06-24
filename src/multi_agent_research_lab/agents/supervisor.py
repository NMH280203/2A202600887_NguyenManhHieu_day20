"""Supervisor / router agent."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.config import Settings, get_settings
from multi_agent_research_lab.core.schemas import AgentName, AgentResult
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.observability.tracing import trace_span


class SupervisorAgent(BaseAgent):
    """Decides which worker should run next and when to stop."""

    name = "supervisor"

    def run(self, state: ResearchState) -> ResearchState:
        """Update `state.route_history` with the next route."""

        settings = get_settings()

        with trace_span("supervisor.route", {"iteration": state.iteration}) as span:
            if state.iteration >= settings.max_iterations:
                next_route = "done"
                if not state.final_answer:
                    state.final_answer = (
                        state.analysis_notes
                        or state.research_notes
                        or "Stopped: max iterations reached without a final answer."
                    )
                    state.errors.append("max_iterations_reached")
            elif not state.sources or not state.research_notes:
                next_route = "researcher"
            elif not state.analysis_notes:
                next_route = "analyst"
            elif not state.final_answer:
                next_route = "writer"
            elif settings.use_critic and not state.critic_reviewed:
                next_route = "critic"
            elif self._needs_writer_revision(state, settings):
                next_route = "writer"
            else:
                next_route = "done"

            state.record_route(next_route)
            span["attributes"]["next_route"] = next_route
            span["attributes"]["citation_coverage"] = state.citation_coverage
            state.add_trace_event(
                "supervisor.route",
                {
                    "next": next_route,
                    "iteration": state.iteration,
                    "citation_coverage": state.citation_coverage,
                    "writer_revisions": state.writer_revisions,
                },
            )
            state.agent_results.append(
                AgentResult(
                    agent=AgentName.SUPERVISOR,
                    content=f"Routing to {next_route}",
                    metadata={
                        "next_route": next_route,
                        "citation_coverage": state.citation_coverage,
                    },
                )
            )

        return state

    @staticmethod
    def _needs_writer_revision(state: ResearchState, settings: Settings) -> bool:
        if not settings.use_critic:
            return False
        if state.citation_coverage is None:
            return False
        if state.writer_revisions >= settings.max_writer_revisions:
            if state.citation_coverage < settings.min_citation_coverage:
                state.errors.append("citation_coverage_below_threshold")
            return False
        return state.citation_coverage < settings.min_citation_coverage
