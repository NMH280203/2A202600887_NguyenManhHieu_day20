"""LLM client abstraction.

Production note: agents should depend on this interface instead of importing an SDK directly.
"""

from dataclasses import dataclass

from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from multi_agent_research_lab.core.config import Settings, get_settings

# Approximate gpt-4o-mini pricing (USD per token).
_INPUT_COST_PER_TOKEN = 0.15 / 1_000_000
_OUTPUT_COST_PER_TOKEN = 0.60 / 1_000_000


@dataclass(frozen=True)
class LLMResponse:
    content: str
    input_tokens: int | None = None
    output_tokens: int | None = None
    cost_usd: float | None = None


class LLMClient:
    """Provider-agnostic LLM client backed by OpenAI."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._client: OpenAI | None = None
        if self._settings.openai_api_key:
            self._client = OpenAI(
                api_key=self._settings.openai_api_key,
                timeout=float(self._settings.timeout_seconds),
            )

    def complete(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        """Return a model completion with retry, timeout, and token logging."""

        if self._client is None:
            return self._mock_complete(user_prompt)

        @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8))
        def _call() -> LLMResponse:
            response = self._client.chat.completions.create(  # type: ignore[union-attr]
                model=self._settings.openai_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.2,
            )
            choice = response.choices[0].message.content or ""
            usage = response.usage
            input_tokens = usage.prompt_tokens if usage else None
            output_tokens = usage.completion_tokens if usage else None
            cost = None
            if input_tokens is not None and output_tokens is not None:
                cost = (
                    input_tokens * _INPUT_COST_PER_TOKEN + output_tokens * _OUTPUT_COST_PER_TOKEN
                )
            return LLMResponse(
                content=choice,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost_usd=cost,
            )

        return _call()

    @staticmethod
    def _mock_complete(user_prompt: str) -> LLMResponse:
        preview = user_prompt[:120].replace("\n", " ")
        content = (
            f"[mock LLM response] Summarized findings for: {preview}... "
            "Key points include relevant background, recent developments, and "
            "practical implications."
        )
        return LLMResponse(content=content, input_tokens=80, output_tokens=160, cost_usd=0.0)
