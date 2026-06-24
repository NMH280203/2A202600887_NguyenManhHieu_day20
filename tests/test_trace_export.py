from multi_agent_research_lab.core.schemas import ResearchQuery
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.observability.trace_export import (
    build_trace_payload,
    export_trace,
    render_trace_markdown,
)
from multi_agent_research_lab.observability.tracing import clear_trace_buffer, trace_span


def test_build_trace_payload_merges_spans_and_events() -> None:
    clear_trace_buffer()
    with trace_span("test.span", {"step": 1}):
        pass

    state = ResearchState(request=ResearchQuery(query="Explain multi-agent systems"))
    state.record_route("researcher")
    state.add_trace_event("researcher.done", {"source_count": 3})

    payload = build_trace_payload(state, run_name="test")
    assert payload["query"] == "Explain multi-agent systems"
    assert payload["summary"]["routes"] == ["researcher"]
    assert payload["summary"]["span_count"] == 1
    assert payload["summary"]["event_count"] == 1
    assert payload["spans"][0]["name"] == "test.span"


def test_export_trace_writes_json_and_markdown(tmp_path) -> None:
    clear_trace_buffer()
    state = ResearchState(request=ResearchQuery(query="GraphRAG overview"))
    state.record_route("writer")
    state.add_trace_event("writer.done", {})

    json_path, md_path = export_trace(state, output_dir=tmp_path, run_name="unit-test")
    assert json_path.exists()
    assert md_path.exists()
    assert (tmp_path / "latest.json").exists()
    assert (tmp_path / "latest.md").exists()
    md = render_trace_markdown(build_trace_payload(state))
    assert "Workflow Trace Report" in md
    assert "writer" in md
