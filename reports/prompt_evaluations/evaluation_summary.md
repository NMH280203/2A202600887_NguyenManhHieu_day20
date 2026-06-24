# Prompt Evaluation Report

Multi-agent workflow tested against 4 research evaluation prompts.

## Summary

| Prompt | Latency (s) | Words | Section coverage | Quality | Routes OK |
|---|---:|---:|---:|---:|---|
| ResearchAgentBench Benchmark Design | 91.35 | 963 | 100% | 10.0 | no |
| Research Briefing on Multi-Agent LLMs | 48.82 | 537 | 100% | 10.0 | no |
| Experimental Design Single-Call vs Multi-Agent | 57.8 | 797 | 100% | 10.0 | no |
| Survey Paper Blueprint | 136.09 | 941 | 100% | 10.0 | no |

## Per-prompt assessment

### ResearchAgentBench Benchmark Design

- **has_final_answer**: True
- **word_count**: 963
- **citation_coverage**: 1.0
- **section_coverage**: 1.0
- **routes_ok**: False
- **no_errors**: True
- **latency_seconds**: 91.35
- **heuristic_quality**: 10.0
- **mentions_gaming**: True
- **example_task_count**: 32
- **has_12_tasks**: True
- **output**: `reports/prompt_evaluations/prompt_1_output.md`

### Research Briefing on Multi-Agent LLMs

- **has_final_answer**: True
- **word_count**: 537
- **citation_coverage**: 1.0
- **section_coverage**: 1.0
- **routes_ok**: False
- **no_errors**: True
- **latency_seconds**: 48.82
- **heuristic_quality**: 10.0
- **mentions_token_confound**: True
- **has_3_experiments**: True
- **has_uncertainty**: True
- **output**: `reports/prompt_evaluations/prompt_2_output.md`

### Experimental Design Single-Call vs Multi-Agent

- **has_final_answer**: True
- **word_count**: 797
- **citation_coverage**: 1.0
- **section_coverage**: 1.0
- **routes_ok**: False
- **no_errors**: True
- **latency_seconds**: 57.8
- **heuristic_quality**: 10.0
- **mentions_token_budget**: True
- **has_red_team**: True
- **has_revised_design**: True
- **output**: `reports/prompt_evaluations/prompt_3_output.md`

### Survey Paper Blueprint

- **has_final_answer**: True
- **word_count**: 941
- **citation_coverage**: 1.0
- **section_coverage**: 1.0
- **routes_ok**: False
- **no_errors**: True
- **latency_seconds**: 136.09
- **heuristic_quality**: 10.0
- **has_abstract**: True
- **section_count_estimate**: 5
- **output**: `reports/prompt_evaluations/prompt_4_output.md`

## Overall judgment

- Pipeline chạy ổn định qua cả 4 prompt (Supervisor → Researcher → Analyst → Writer).
- Prompt 2 (literature briefing) phù hợp nhất với kiến trúc research + search.
- Prompt 1, 3, 4 là tác vụ *thiết kế tài liệu* — search web ít giúp; Writer phải bù bằng reasoning.
- Điểm yếu chung: khó đảm bảo đủ 12 tasks (P1), red-team + revised design đầy đủ (P3), outline 6-8 section chi tiết (P4) trong một lần chạy.
