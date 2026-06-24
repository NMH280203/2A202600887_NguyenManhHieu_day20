#!/usr/bin/env python3
"""Run evaluation prompts through the multi-agent workflow and score outputs."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from time import perf_counter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from multi_agent_research_lab.core.schemas import ResearchQuery  # noqa: E402
from multi_agent_research_lab.core.state import ResearchState  # noqa: E402
from multi_agent_research_lab.evaluation.benchmark import _citation_coverage, _quality_score  # noqa: E402
from multi_agent_research_lab.graph.workflow import MultiAgentWorkflow  # noqa: E402
from multi_agent_research_lab.observability.logging import configure_logging  # noqa: E402
from multi_agent_research_lab.observability.trace_export import export_trace
from multi_agent_research_lab.observability.tracing import clear_trace_buffer, configure_tracing  # noqa: E402

PROMPTS_PATH = ROOT / "prompts" / "evaluation_prompts.json"
OUTPUT_DIR = ROOT / "reports" / "prompt_evaluations"


def _section_hit(answer: str, keyword: str) -> bool:
    return bool(re.search(rf"\b{re.escape(keyword)}\b", answer, re.IGNORECASE))


def _count_example_tasks(answer: str) -> int:
    numbered = len(re.findall(r"(?m)^\s*\d+[\.\)]\s+", answer))
    bullets = len(re.findall(r"(?m)^\s*[-*]\s+", answer))
    return max(numbered, bullets)


def evaluate_output(prompt: dict, state: ResearchState, latency: float) -> dict:
    answer = state.final_answer or ""
    lower = answer.lower()

    section_hits = sum(1 for s in prompt["required_sections"] if _section_hit(answer, s))
    section_coverage = section_hits / max(len(prompt["required_sections"]), 1)

    checks: dict[str, bool | int | float] = {
        "has_final_answer": bool(answer.strip()),
        "word_count": len(answer.split()),
        "citation_coverage": round(_citation_coverage(state), 2),
        "section_coverage": round(section_coverage, 2),
        "routes_ok": "critic" in state.route_history or state.route_history == [
            "researcher",
            "analyst",
            "writer",
            "done",
        ],
        "no_errors": len(state.errors) == 0,
        "latency_seconds": round(latency, 2),
        "heuristic_quality": round(_quality_score(state), 2),
    }

    prompt_id = prompt["id"]
    if prompt_id == "prompt_1":
        checks["mentions_gaming"] = any(
            w in lower for w in ["gaming", "game the", "adversarial", "stress-test", "stress test"]
        )
        checks["example_task_count"] = _count_example_tasks(answer)
        checks["has_12_tasks"] = checks["example_task_count"] >= 12
    elif prompt_id == "prompt_2":
        checks["mentions_token_confound"] = any(
            w in lower for w in ["token", "prompt engineering", "self-reflection", "confound"]
        )
        checks["has_3_experiments"] = len(re.findall(r"experiment", lower)) >= 3
        checks["has_uncertainty"] = any(
            w in lower for w in ["uncertain", "unclear", "unresolved", "open question"]
        )
    elif prompt_id == "prompt_3":
        checks["mentions_token_budget"] = "token" in lower and "budget" in lower
        checks["has_red_team"] = "red-team" in lower or "red team" in lower
        checks["has_revised_design"] = "revised" in lower
    elif prompt_id == "prompt_4":
        checks["has_abstract"] = "abstract" in lower
        checks["section_count_estimate"] = len(re.findall(r"(?m)^#{1,3}\s+", answer)) + len(
            re.findall(r"(?m)^\s*\d+[\.\)]\s+[A-Z]", answer)
        )

    return {
        "prompt_id": prompt_id,
        "prompt_name": prompt["name"],
        "checks": checks,
        "routes": state.route_history,
        "errors": state.errors,
        "source_count": len(state.sources),
    }


def render_evaluation_report(results: list[dict]) -> str:
    lines = [
        "# Prompt Evaluation Report",
        "",
        "Multi-agent workflow tested against 4 research evaluation prompts.",
        "",
        "## Summary",
        "",
        "| Prompt | Latency (s) | Words | Section coverage | Quality | Routes OK |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for r in results:
        c = r["checks"]
        lines.append(
            f"| {r['prompt_name']} | {c['latency_seconds']} | {c['word_count']} | "
            f"{c['section_coverage']:.0%} | {c['heuristic_quality']} | "
            f"{'yes' if c['routes_ok'] else 'no'} |"
        )

    lines.extend(["", "## Per-prompt assessment", ""])
    for r in results:
        lines.append(f"### {r['prompt_name']}")
        lines.append("")
        for key, val in r["checks"].items():
            lines.append(f"- **{key}**: {val}")
        lines.append(f"- **output**: `reports/prompt_evaluations/{r['prompt_id']}_output.md`")
        lines.append("")

    lines.extend(
        [
            "## Overall judgment",
            "",
            "- Pipeline chạy ổn định qua cả 4 prompt (Supervisor → Researcher → Analyst → Writer).",
            "- Prompt 2 (literature briefing) phù hợp nhất với kiến trúc research + search.",
            "- Prompt 1, 3, 4 là tác vụ *thiết kế tài liệu* — search web ít giúp; Writer phải bù bằng reasoning.",
            "- Điểm yếu chung: khó đảm bảo đủ 12 tasks (P1), red-team + revised design đầy đủ (P3), outline 6-8 section chi tiết (P4) trong một lần chạy.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    configure_logging("INFO")
    configure_tracing()
    prompts = json.loads(PROMPTS_PATH.read_text(encoding="utf-8"))
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    workflow = MultiAgentWorkflow()
    results: list[dict] = []

    for prompt in prompts:
        print(f"Running {prompt['id']}: {prompt['name']}...")
        clear_trace_buffer()
        state = ResearchState(request=ResearchQuery(query=prompt["query"], max_sources=5))
        started = perf_counter()
        result = workflow.run(state)
        latency = perf_counter() - started

        trace_dir = OUTPUT_DIR / "traces"
        json_path, md_path = export_trace(
            result,
            output_dir=trace_dir,
            run_name=prompt["id"],
            slug=prompt["id"],
        )

        out_path = OUTPUT_DIR / f"{prompt['id']}_output.md"
        out_path.write_text(
            f"# {prompt['name']}\n\n## Routes\n{result.route_history}\n\n"
            f"## Trace\n- JSON: `{json_path}`\n- Report: `{md_path}`\n\n"
            f"## Sources ({len(result.sources)})\n"
            + "\n".join(f"- {s.title}: {s.url}" for s in result.sources)
            + f"\n\n## Final Answer\n\n{result.final_answer or '(empty)'}\n",
            encoding="utf-8",
        )

        evaluation = evaluate_output(prompt, result, latency)
        results.append(evaluation)
        print(f"  Done in {latency:.1f}s, {evaluation['checks']['word_count']} words")

    report = render_evaluation_report(results)
    (OUTPUT_DIR / "evaluation_summary.md").write_text(report, encoding="utf-8")
    json_path = OUTPUT_DIR / "evaluation_metrics.json"
    json_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nReport: {OUTPUT_DIR / 'evaluation_summary.md'}")


if __name__ == "__main__":
    main()
