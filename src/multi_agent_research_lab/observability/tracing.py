"""Tracing hooks with optional LangSmith integration."""

import logging
import os
from collections.abc import Iterator
from contextlib import contextmanager
from time import perf_counter
from typing import Any

from multi_agent_research_lab.core.config import get_settings

logger = logging.getLogger(__name__)
_trace_buffer: list[dict[str, Any]] = []


def configure_tracing() -> None:
    """Enable LangSmith tracing when credentials are present."""

    settings = get_settings()
    if settings.langsmith_api_key:
        os.environ.setdefault("LANGCHAIN_TRACING_V2", "true")
        os.environ.setdefault("LANGCHAIN_API_KEY", settings.langsmith_api_key)
        os.environ.setdefault("LANGCHAIN_PROJECT", settings.langsmith_project)


def clear_trace_buffer() -> None:
    """Reset the in-memory span buffer before a new workflow run."""

    _trace_buffer.clear()


def get_trace_buffer() -> list[dict[str, Any]]:
    """Return collected trace spans for local inspection."""

    return list(_trace_buffer)


@contextmanager
def trace_span(name: str, attributes: dict[str, Any] | None = None) -> Iterator[dict[str, Any]]:
    """Record a span locally and optionally forward to LangSmith via LangChain env vars."""

    configure_tracing()
    started = perf_counter()
    span: dict[str, Any] = {"name": name, "attributes": attributes or {}, "duration_seconds": None}
    try:
        yield span
    finally:
        span["duration_seconds"] = perf_counter() - started
        _trace_buffer.append(span)
        logger.debug("trace_span %s %.3fs attrs=%s", name, span["duration_seconds"], attributes)
