# Workflow Trace Report

- **Run:** multi-agent
- **Exported:** 2026-06-24T05:01:05.880672+00:00
- **Query:** What is GraphRAG?

## Summary

- **Routes:** `researcher -> analyst -> writer -> critic -> writer -> critic -> done`
- **Total span duration:** 0.006s
- **Spans:** 15 | **Events:** 13
- **Citation coverage:** 0.0
- **Writer revisions:** 1
- **Errors:** none

## Spans (timing)

| Span | Duration (s) | Attributes |
|---|---:|---|
| `supervisor.route` | 0.000 | {"iteration": 0, "next_route": "researcher", "citation_coverage": null} |
| `researcher.search` | 0.000 | {"query": "What is GraphRAG?", "source_count": 3} |
| `researcher.summarize` | 0.000 | {"output_tokens": 160} |
| `supervisor.route` | 0.000 | {"iteration": 1, "next_route": "analyst", "citation_coverage": null} |
| `analyst.analyze` | 0.000 | {"output_tokens": 160} |
| `supervisor.route` | 0.000 | {"iteration": 2, "next_route": "writer", "citation_coverage": null} |
| `writer.compose` | 0.000 | {"revision": false, "writer_revisions": 0, "output_tokens": 160} |
| `supervisor.route` | 0.000 | {"iteration": 3, "next_route": "critic", "citation_coverage": null} |
| `critic.review` | 0.000 | {"citation_coverage": 0.0} |
| `supervisor.route` | 0.000 | {"iteration": 4, "next_route": "writer", "citation_coverage": 0.0} |
| `writer.compose` | 0.000 | {"revision": true, "writer_revisions": 0, "output_tokens": 160} |
| `supervisor.route` | 0.000 | {"iteration": 5, "next_route": "critic", "citation_coverage": 0.0} |
| `critic.review` | 0.000 | {"citation_coverage": 0.0} |
| `supervisor.route` | 0.000 | {"iteration": 6, "next_route": "done", "citation_coverage": 0.0} |
| `workflow.run` | 0.005 | {"query": "What is GraphRAG?", "routes": ["researcher", "analyst", "writer", … |

## State events

- **supervisor.route:** {"next": "researcher", "iteration": 1, "citation_coverage": null, "writer_revisions": 0}
- **researcher.done:** {"source_count": 3}
- **supervisor.route:** {"next": "analyst", "iteration": 2, "citation_coverage": null, "writer_revisions": 0}
- **analyst.done:** {}
- **supervisor.route:** {"next": "writer", "iteration": 3, "citation_coverage": null, "writer_revisions": 0}
- **writer.done:** {"revision": false, "writer_revisions": 0}
- **supervisor.route:** {"next": "critic", "iteration": 4, "citation_coverage": null, "writer_revisions": 0}
- **critic.done:** {"citation_coverage": 0.0, "passed": false}
- **supervisor.route:** {"next": "writer", "iteration": 5, "citation_coverage": 0.0, "writer_revisions": 0}
- **writer.done:** {"revision": true, "writer_revisions": 1}
- **supervisor.route:** {"next": "critic", "iteration": 6, "citation_coverage": 0.0, "writer_revisions": 1}
- **critic.done:** {"citation_coverage": 0.0, "passed": false}
- **supervisor.route:** {"next": "done", "iteration": 7, "citation_coverage": 0.0, "writer_revisions": 1}

## Agent results

- **supervisor:** Routing to researcher
- **researcher:** [mock LLM response] Summarized findings for: Query: What is GraphRAG?  Sources: [1] Overview of What is GraphRAG? URL: h
- **supervisor:** Routing to analyst
- **analyst:** [mock LLM response] Summarized findings for: Original query: What is GraphRAG?  Research notes: [mock LLM response] Summ
- **supervisor:** Routing to writer
- **writer:** [mock LLM response] Summarized findings for: Query: What is GraphRAG?  Research notes: [mock LLM response] Summarized fi
- **supervisor:** Routing to critic
- **critic:** [mock LLM response] Summarized findings for: Query: What is GraphRAG?  Answer: [mock LLM response] Summarized findings f
- **supervisor:** Routing to writer
- **writer:** [mock LLM response] Summarized findings for: Query: What is GraphRAG?  Research notes: [mock LLM response] Summarized fi
- **supervisor:** Routing to critic
- **critic:** [mock LLM response] Summarized findings for: Query: What is GraphRAG?  Answer: [mock LLM response] Summarized findings f
- **supervisor:** Routing to done
