"""Command-line entrypoint for the lab."""

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel

from multi_agent_research_lab.core.config import get_settings
from multi_agent_research_lab.core.schemas import AgentName, AgentResult, ResearchQuery
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.evaluation.benchmark import run_benchmark
from multi_agent_research_lab.evaluation.report import render_markdown_report
from multi_agent_research_lab.graph.workflow import MultiAgentWorkflow
from multi_agent_research_lab.observability.logging import configure_logging
from multi_agent_research_lab.observability.trace_export import export_trace
from multi_agent_research_lab.observability.tracing import (
    clear_trace_buffer,
    configure_tracing,
    get_trace_buffer,
)
from multi_agent_research_lab.services.llm_client import LLMClient
from multi_agent_research_lab.utils.timer import elapsed_timer

app = typer.Typer(help="Multi-Agent Research Lab CLI")
console = Console()


def _init() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)
    configure_tracing()


def _run_baseline(query: str) -> ResearchState:
    request = ResearchQuery(query=query)
    state = ResearchState(request=request)
    llm = LLMClient()

    with elapsed_timer() as timer:
        response = llm.complete(
            system_prompt=(
                "You are a research assistant. Search your knowledge, analyze the topic, and "
                "write a clear technical summary with key points."
            ),
            user_prompt=query,
        )
        state.final_answer = response.content
        latency = timer()

    state.agent_results.append(
        AgentResult(
            agent=AgentName.WRITER,
            content=state.final_answer or "",
            metadata={
                "input_tokens": response.input_tokens,
                "output_tokens": response.output_tokens,
                "cost_usd": response.cost_usd,
            },
        )
    )
    state.add_trace_event("baseline.complete", {"latency_seconds": latency})
    return state


def _run_multi_agent(query: str) -> ResearchState:
    clear_trace_buffer()
    state = ResearchState(request=ResearchQuery(query=query))
    workflow = MultiAgentWorkflow()
    return workflow.run(state)


def _export_run_trace(
    state: ResearchState,
    run_name: str,
    output_dir: Path,
) -> tuple[Path, Path] | None:
    spans = get_trace_buffer()
    if not spans and not state.trace:
        return None
    return export_trace(state, output_dir=output_dir, run_name=run_name)


@app.command()
def baseline(
    query: Annotated[str, typer.Option("--query", "-q", help="Research query")],
) -> None:
    """Run a single-agent baseline using one LLM call."""

    _init()
    state = _run_baseline(query)
    console.print(Panel.fit(state.final_answer or "(empty)", title="Single-Agent Baseline"))


@app.command("multi-agent")
def multi_agent(
    query: Annotated[str, typer.Option("--query", "-q", help="Research query")],
    trace_dir: Annotated[
        Path,
        typer.Option("--trace-dir", help="Directory for trace export"),
    ] = Path("reports/traces"),
    no_export_trace: Annotated[
        bool,
        typer.Option("--no-export-trace", help="Skip writing trace JSON/Markdown"),
    ] = False,
) -> None:
    """Run the multi-agent LangGraph workflow."""

    _init()
    result = _run_multi_agent(query)
    console.print(Panel.fit(result.final_answer or "(empty)", title="Multi-Agent Answer"))
    console.print(f"\nRoutes: {' -> '.join(result.route_history)}")
    if result.citation_coverage is not None:
        console.print(f"Citation coverage: {result.citation_coverage:.2f}")
    if result.writer_revisions:
        console.print(f"Writer revisions: {result.writer_revisions}")
    if result.errors:
        console.print(f"Errors: {result.errors}")

    if not no_export_trace:
        paths = _export_run_trace(result, "multi-agent", trace_dir)
        if paths:
            json_path, md_path = paths
            console.print(f"Trace JSON: {json_path}")
            console.print(f"Trace report: {md_path}")
        else:
            console.print("No trace data to export.")


@app.command()
def benchmark(
    query: Annotated[
        str,
        typer.Option(
            "--query",
            "-q",
            help="Research query",
        ),
    ] = "Research GraphRAG state-of-the-art and write a 500-word summary",
    output: Annotated[
        Path,
        typer.Option("--output", "-o", help="Markdown report path"),
    ] = Path("reports/benchmark_report.md"),
) -> None:
    """Benchmark single-agent vs multi-agent and write a markdown report."""

    _init()
    console.print(f"Running benchmark for: {query}")

    _, baseline_metrics = run_benchmark("single-agent", query, _run_baseline)
    console.print(
        f"Baseline: {baseline_metrics.latency_seconds:.2f}s, "
        f"quality={baseline_metrics.quality_score}"
    )

    multi_state, multi_metrics = run_benchmark("multi-agent", query, _run_multi_agent)
    console.print(
        f"Multi-agent: {multi_metrics.latency_seconds:.2f}s, "
        f"quality={multi_metrics.quality_score}"
    )

    trace_paths = _export_run_trace(multi_state, "benchmark-multi-agent", Path("reports/traces"))

    report = render_markdown_report([baseline_metrics, multi_metrics])
    if trace_paths:
        json_path, md_path = trace_paths
        report += (
            f"\n## Trace export\n\n"
            f"- Markdown: `{md_path}`\n"
            f"- JSON: `{json_path}`\n"
        )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(report, encoding="utf-8")
    console.print(Panel.fit(f"Report written to {output}", title="Benchmark Complete"))


if __name__ == "__main__":
    app()
