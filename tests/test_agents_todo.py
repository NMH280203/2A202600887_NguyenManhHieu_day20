from multi_agent_research_lab.agents import SupervisorAgent
from multi_agent_research_lab.core.schemas import ResearchQuery, SourceDocument
from multi_agent_research_lab.core.state import ResearchState


def test_supervisor_routes_to_researcher_first() -> None:
    state = ResearchState(request=ResearchQuery(query="Explain multi-agent systems"))
    result = SupervisorAgent().run(state)
    assert result.route_history[-1] == "researcher"
    assert result.iteration == 1


def test_supervisor_routes_to_analyst_after_research() -> None:
    state = ResearchState(
        request=ResearchQuery(query="Explain multi-agent systems"),
        research_notes="Some notes",
        sources=[SourceDocument(title="t", snippet="s")],
    )
    result = SupervisorAgent().run(state)
    assert result.route_history[-1] == "analyst"


def test_supervisor_routes_to_critic_before_done() -> None:
    state = ResearchState(
        request=ResearchQuery(query="Explain multi-agent systems"),
        research_notes="notes",
        analysis_notes="analysis",
        final_answer="answer with citation [1]",
        sources=[SourceDocument(title="t", snippet="s")],
    )
    result = SupervisorAgent().run(state)
    assert result.route_history[-1] == "critic"


def test_supervisor_routes_to_done_when_complete() -> None:
    state = ResearchState(
        request=ResearchQuery(query="Explain multi-agent systems"),
        research_notes="notes",
        analysis_notes="analysis",
        final_answer="answer with citation [1]",
        sources=[SourceDocument(title="t", snippet="s")],
        critic_reviewed=True,
        citation_coverage=1.0,
    )
    result = SupervisorAgent().run(state)
    assert result.route_history[-1] == "done"
