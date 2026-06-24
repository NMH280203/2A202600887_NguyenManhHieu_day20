"""LangGraph workflow for the multi-agent research system."""

from __future__ import annotations

import logging
from typing import Literal

from langgraph.graph import END, StateGraph

from multi_agent_research_lab.agents.analyst import AnalystAgent
from multi_agent_research_lab.agents.critic import CriticAgent
from multi_agent_research_lab.agents.researcher import ResearcherAgent
from multi_agent_research_lab.agents.supervisor import SupervisorAgent
from multi_agent_research_lab.agents.writer import WriterAgent
from multi_agent_research_lab.core.config import get_settings
from multi_agent_research_lab.core.errors import AgentExecutionError
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.observability.tracing import trace_span

logger = logging.getLogger(__name__)

Route = Literal["researcher", "analyst", "writer", "critic", "done"]


class MultiAgentWorkflow:
    """Builds and runs the multi-agent graph.

    Keep orchestration here; keep agent internals in `agents/`.
    """

    def __init__(
        self,
        supervisor: SupervisorAgent | None = None,
        researcher: ResearcherAgent | None = None,
        analyst: AnalystAgent | None = None,
        writer: WriterAgent | None = None,
        critic: CriticAgent | None = None,
        use_critic: bool | None = None,
    ) -> None:
        settings = get_settings()
        self._use_critic = settings.use_critic if use_critic is None else use_critic
        self._supervisor = supervisor or SupervisorAgent()
        self._researcher = researcher or ResearcherAgent()
        self._analyst = analyst or AnalystAgent()
        self._writer = writer or WriterAgent()
        self._critic = critic or CriticAgent()
        self._graph = self.build()

    def build(self) -> object:
        """Create a LangGraph graph with supervisor routing and worker nodes."""

        graph: StateGraph = StateGraph(ResearchState)

        graph.add_node("supervisor", self._supervisor_node)
        graph.add_node("researcher", self._researcher_node)
        graph.add_node("analyst", self._analyst_node)
        graph.add_node("writer", self._writer_node)
        if self._use_critic:
            graph.add_node("critic", self._critic_node)

        graph.set_entry_point("supervisor")
        routes: dict[str, str] = {
            "researcher": "researcher",
            "analyst": "analyst",
            "writer": "writer",
            "done": END,
        }
        if self._use_critic:
            routes["critic"] = "critic"

        graph.add_conditional_edges("supervisor", self._route_after_supervisor, routes)
        graph.add_edge("researcher", "supervisor")
        graph.add_edge("analyst", "supervisor")
        graph.add_edge("writer", "supervisor")
        if self._use_critic:
            graph.add_edge("critic", "supervisor")

        return graph.compile()

    def run(self, state: ResearchState) -> ResearchState:
        """Execute the graph and return final state."""

        settings = get_settings()
        with trace_span("workflow.run", {"query": state.request.query}) as span:
            try:
                result = self._graph.invoke(  # type: ignore[attr-defined]
                    state,
                    config={"recursion_limit": settings.max_iterations * 3},
                )
            except AgentExecutionError as exc:
                state.errors.append(str(exc))
                span["attributes"]["error"] = str(exc)
                return state

            if isinstance(result, ResearchState):
                final_state = result
            else:
                final_state = ResearchState.model_validate(result)

            span["attributes"]["routes"] = final_state.route_history
            span["attributes"]["errors"] = final_state.errors
            span["attributes"]["citation_coverage"] = final_state.citation_coverage
            return final_state

    def _supervisor_node(self, state: ResearchState) -> ResearchState:
        return self._supervisor.run(state)

    def _researcher_node(self, state: ResearchState) -> ResearchState:
        try:
            return self._researcher.run(state)
        except AgentExecutionError:
            state.errors.append("researcher_failed")
            return state

    def _analyst_node(self, state: ResearchState) -> ResearchState:
        return self._analyst.run(state)

    def _writer_node(self, state: ResearchState) -> ResearchState:
        return self._writer.run(state)

    def _critic_node(self, state: ResearchState) -> ResearchState:
        return self._critic.run(state)

    @staticmethod
    def _route_after_supervisor(state: ResearchState) -> Route:
        if not state.route_history:
            return "researcher"
        last = state.route_history[-1]
        if last in {"researcher", "analyst", "writer", "critic", "done"}:
            return last  # type: ignore[return-value]
        return "done"
