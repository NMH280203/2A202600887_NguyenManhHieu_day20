"""Benchmark report rendering."""

from multi_agent_research_lab.core.schemas import BenchmarkMetrics


def render_markdown_report(metrics: list[BenchmarkMetrics]) -> str:
    """Render benchmark metrics to markdown with summary analysis."""

    lines = [
        "# Benchmark Report",
        "",
        "Comparison of single-agent baseline vs multi-agent workflow.",
        "",
        "| Run | Latency (s) | Cost (USD) | Quality | Notes |",
        "|---|---:|---:|---:|---|",
    ]

    for item in metrics:
        cost = "" if item.estimated_cost_usd is None else f"{item.estimated_cost_usd:.4f}"
        quality = "" if item.quality_score is None else f"{item.quality_score:.1f}"
        lines.append(
            f"| {item.run_name} | {item.latency_seconds:.2f} | {cost} | {quality} | {item.notes} |"
        )

    if len(metrics) >= 2:
        baseline = metrics[0]
        multi = metrics[1]
        lines.extend(
            [
                "",
                "## Analysis",
                "",
                f"- **Latency delta**: multi-agent took "
                f"{multi.latency_seconds - baseline.latency_seconds:+.2f}s vs baseline.",
            ]
        )
        if baseline.estimated_cost_usd and multi.estimated_cost_usd:
            lines.append(
                f"- **Cost delta**: multi-agent cost "
                f"${multi.estimated_cost_usd - baseline.estimated_cost_usd:+.4f} vs baseline."
            )
        if baseline.quality_score is not None and multi.quality_score is not None:
            lines.append(
                f"- **Quality delta**: multi-agent scored "
                f"{multi.quality_score - baseline.quality_score:+.1f} vs baseline."
            )
        lines.extend(
            [
                "",
                "## Failure Modes",
                "",
                "- **Max iterations**: supervisor stops early; fix by raising `MAX_ITERATIONS` or "
                "simplifying agent prompts.",
                "- **Search/API errors**: Researcher falls back to mock sources; fix API keys or "
                "add retry with alternate provider.",
                "- **Low citation coverage**: Writer omits `[n]` refs; tighten writer "
                "prompt or add Critic agent loop.",
                "",
                "## Trace",
                "",
                "See exported artifacts under `reports/traces/` (latest.json, latest.md).",
                "Per-prompt traces: `reports/prompt_evaluations/traces/`.",
            ]
        )

    return "\n".join(lines) + "\n"
