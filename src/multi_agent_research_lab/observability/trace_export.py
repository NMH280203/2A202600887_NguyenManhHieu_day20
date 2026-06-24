"""Export workflow traces to JSON and Markdown artifacts."""

from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.observability.tracing import get_trace_buffer


def _slugify(text: str, max_len: int = 48) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", text.strip().lower()).strip("-")
    return (slug[:max_len] or "run").rstrip("-")


def build_trace_payload(state: ResearchState, run_name: str = "multi-agent") -> dict[str, Any]:
    """Combine span buffer and state events into one exportable document."""

    spans = get_trace_buffer()
    total_duration = sum(s.get("duration_seconds") or 0.0 for s in spans)

    return {
        "exported_at": datetime.now(UTC).isoformat(),
        "run_name": run_name,
        "query": state.request.query,
        "summary": {
            "routes": state.route_history,
            "route_string": " -> ".join(state.route_history),
            "iteration_count": state.iteration,
            "span_count": len(spans),
            "event_count": len(state.trace),
            "total_span_duration_seconds": round(total_duration, 4),
            "citation_coverage": state.citation_coverage,
            "writer_revisions": state.writer_revisions,
            "source_count": len(state.sources),
            "errors": state.errors,
            "langsmith_enabled": bool(
                __import__("os").environ.get("LANGCHAIN_TRACING_V2") == "true"
            ),
        },
        "spans": spans,
        "events": state.trace,
        "agent_results": [
            {
                "agent": r.agent.value,
                "metadata": r.metadata,
                "content_preview": (r.content[:200] + "…") if len(r.content) > 200 else r.content,
            }
            for r in state.agent_results
        ],
    }


def render_trace_markdown(payload: dict[str, Any]) -> str:
    """Render a human-readable trace report."""

    summary = payload["summary"]
    lines = [
        "# Workflow Trace Report",
        "",
        f"- **Run:** {payload['run_name']}",
        f"- **Exported:** {payload['exported_at']}",
        f"- **Query:** {payload['query'][:200]}{'…' if len(payload['query']) > 200 else ''}",
        "",
        "## Summary",
        "",
        f"- **Routes:** `{summary['route_string']}`",
        f"- **Total span duration:** {summary['total_span_duration_seconds']:.3f}s",
        f"- **Spans:** {summary['span_count']} | **Events:** {summary['event_count']}",
        f"- **Citation coverage:** {summary.get('citation_coverage')}",
        f"- **Writer revisions:** {summary.get('writer_revisions')}",
        f"- **Errors:** {summary['errors'] or 'none'}",
        "",
        "## Spans (timing)",
        "",
        "| Span | Duration (s) | Attributes |",
        "|---|---:|---|",
    ]

    for span in payload["spans"]:
        attrs = json.dumps(span.get("attributes") or {}, ensure_ascii=False)
        if len(attrs) > 80:
            attrs = attrs[:77] + "…"
        duration = span.get("duration_seconds")
        dur_str = f"{duration:.3f}" if isinstance(duration, (int, float)) else ""
        lines.append(f"| `{span.get('name', '')}` | {dur_str} | {attrs} |")

    lines.extend(["", "## State events", ""])
    for event in payload["events"]:
        name = event.get("name", "")
        payload_str = json.dumps(event.get("payload") or {}, ensure_ascii=False)
        lines.append(f"- **{name}:** {payload_str}")

    lines.extend(["", "## Agent results", ""])
    for result in payload["agent_results"]:
        lines.append(f"- **{result['agent']}:** {result['content_preview'][:120]}")

    if summary.get("langsmith_enabled"):
        lines.extend(
            [
                "",
                "## LangSmith",
                "",
                "Tracing was enabled. Open your LangSmith project for the full UI trace.",
            ]
        )

    return "\n".join(lines) + "\n"


def export_trace(
    state: ResearchState,
    output_dir: Path | str = "reports/traces",
    run_name: str = "multi-agent",
    slug: str | None = None,
) -> tuple[Path, Path]:
    """Write JSON and Markdown trace files; return both paths."""

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    payload = build_trace_payload(state, run_name=run_name)
    name_slug = slug or _slugify(state.request.query)
    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    base = f"{timestamp}_{name_slug}"

    json_path = out / f"{base}.json"
    md_path = out / f"{base}.md"
    latest_json = out / "latest.json"
    latest_md = out / "latest.md"

    json_text = json.dumps(payload, indent=2, ensure_ascii=False)
    md_text = render_trace_markdown(payload)

    json_path.write_text(json_text, encoding="utf-8")
    md_path.write_text(md_text, encoding="utf-8")
    latest_json.write_text(json_text, encoding="utf-8")
    latest_md.write_text(md_text, encoding="utf-8")

    return json_path, md_path
