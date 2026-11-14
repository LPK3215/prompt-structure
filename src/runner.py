"""跑一条任务一次会话，流式取回，记首字延迟与 token。"""

from __future__ import annotations

import time

from langchain_core.messages import HumanMessage

from config import make_model
from templates import build


def _text(content) -> str:
    if isinstance(content, str):
        return content
    parts = []
    for block in content or []:
        if isinstance(block, dict) and block.get("type") == "text":
            parts.append(block.get("text", ""))
        elif isinstance(block, str):
            parts.append(block)
    return "".join(parts)


def _retryable(e: Exception) -> bool:
    import openai

    return isinstance(e, (openai.RateLimitError, openai.APITimeoutError,
                          openai.APIConnectionError, openai.InternalServerError))


def run_task(task: dict, arm: str, model=None, max_attempts: int = 3) -> dict:
    model = model or make_model()
    prompt = build(task, arm)
    t0 = time.perf_counter()
    answer, error = "", ""
    ttft_ms, tokens_in, tokens_out = None, 0, 0

    for attempt in range(1, max_attempts + 1):
        answer, error, ttft_ms = "", "", None
        tokens_in, tokens_out = 0, 0
        try:
            parts = []
            for chunk in model.stream([HumanMessage(prompt)]):
                if ttft_ms is None:
                    piece = _text(chunk.content)
                    if piece:
                        ttft_ms = int((time.perf_counter() - t0) * 1000)
                parts.append(_text(chunk.content))
                if getattr(chunk, "usage_metadata", None):
                    tokens_in = chunk.usage_metadata.get("input_tokens", 0)
                    tokens_out = chunk.usage_metadata.get("output_tokens", 0)
            answer = "".join(parts).strip()
            break
        except Exception as e:
            error = f"{type(e).__name__}: {str(e)[:200]}"
            if not _retryable(e) or attempt == max_attempts:
                break
            time.sleep(4 * 2 ** (attempt - 1))

    latency = int((time.perf_counter() - t0) * 1000)
    return {
        "task_id": task["id"],
        "type": task["type"],
        "arm": arm,
        "prompt_chars": len(prompt),
        "answer": answer,
        "error": error,
        "ttft_ms": ttft_ms,
        "tokens_in": tokens_in,
        "tokens_out": tokens_out,
        "latency_ms": latency,
    }
