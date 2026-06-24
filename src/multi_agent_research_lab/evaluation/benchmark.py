"""Benchmark utilities for single-agent vs multi-agent."""

import re
from collections.abc import Callable
from time import perf_counter

from multi_agent_research_lab.core.schemas import BenchmarkMetrics
from multi_agent_research_lab.core.state import ResearchState

Runner = Callable[[str], ResearchState]


def _estimate_cost(state: ResearchState) -> float:
    total = 0.0
    for result in state.agent_results:
        cost = result.metadata.get("cost_usd")
        if isinstance(cost, (int, float)):
            total += float(cost)
    return total


def _citation_coverage(state: ResearchState) -> float:
    answer = state.final_answer or ""
    refs = set(re.findall(r"\[(\d+)\]", answer))
    if not state.sources:
        return 1.0 if not refs else 0.5
    return min(len(refs) / len(state.sources), 1.0)


def _quality_score(state: ResearchState) -> float:
    """Heuristic 0-10 score based on completeness, length, citations, and errors."""

    score = 0.0
    if state.final_answer:
        score += 3.0
        word_count = len(state.final_answer.split())
        score += min(word_count / 100, 3.0)
    if state.research_notes:
        score += 1.5
    if state.analysis_notes:
        score += 1.5
    score += _citation_coverage(state) * 1.0
    if state.errors:
        score -= min(len(state.errors), 2)
    return max(0.0, min(score, 10.0))


def run_benchmark(
    run_name: str, query: str, runner: Runner
) -> tuple[ResearchState, BenchmarkMetrics]:
    """Measure latency, cost, citation coverage, and heuristic quality."""

    started = perf_counter()
    state = runner(query)
    latency = perf_counter() - started

    coverage = _citation_coverage(state)
    cost = _estimate_cost(state)
    quality = _quality_score(state)
    failure = "yes" if state.errors else "no"

    metrics = BenchmarkMetrics(
        run_name=run_name,
        latency_seconds=latency,
        estimated_cost_usd=cost if cost > 0 else None,
        quality_score=quality,
        notes=(
            f"citation_coverage={coverage:.2f}; failure={failure}; "
            f"routes={','.join(state.route_history)}"
        ),
    )
    return state, metrics
