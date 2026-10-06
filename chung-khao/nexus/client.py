"""Client HTTP/SDK và bộ theo dõi chi phí, token."""

from datetime import datetime, timezone
from functools import lru_cache
from time import perf_counter
from typing import Any, Callable

import httpx
from openai import OpenAI

from .config import get_settings, require_key


class UsageTracker:
    def __init__(self) -> None:
        self.records: list[dict[str, Any]] = []

    @property
    def total_cost(self) -> float:
        return sum(float(item.get("cost") or 0) for item in self.records)

    @property
    def total_tokens(self) -> int:
        return sum(int(item.get("tokens") or 0) for item in self.records)

    def add(self, endpoint: str, model: str, *, cost: float = 0, tokens: int = 0,
            latency: float = 0, ok: bool = True, error: str = "") -> None:
        self.records.append({
            "endpoint": endpoint, "model": model, "cost": cost, "tokens": tokens,
            "latency": latency, "ok": ok, "error": error,
            "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        })
        del self.records[:-100]

    def clear(self) -> None:
        self.records.clear()


tracker = UsageTracker()


@lru_cache(maxsize=1)
def openai_client() -> OpenAI:
    settings = get_settings()
    return OpenAI(
        api_key=require_key(), base_url=settings.base_url,
        timeout=settings.timeout, max_retries=settings.max_retries,
    )


@lru_cache(maxsize=1)
def http() -> httpx.Client:
    settings = get_settings()
    return httpx.Client(
        base_url=settings.base_url,
        headers={"Authorization": f"Bearer {require_key()}"},
        timeout=settings.timeout,
    )


def _tokens_from(parsed: Any) -> int:
    usage = getattr(parsed, "usage", None)
    total = getattr(usage, "total_tokens", None)
    if total is None:
        total = (getattr(usage, "input_tokens", 0) or 0) + (getattr(usage, "output_tokens", 0) or 0)
    return int(total or 0)


def tracked(endpoint: str, model_name: str, raw_fn: Callable[..., Any], **kwargs: Any) -> tuple[Any, float]:
    """Gọi SDK raw response, lấy chi phí từ header và ghi nhận cả lỗi."""
    started = perf_counter()
    try:
        raw = raw_fn(**kwargs)
        cost = float(raw.headers.get("x-litellm-response-cost", 0) or 0)
        parsed = raw.parse()
        tracker.add(endpoint, model_name, cost=cost, tokens=_tokens_from(parsed), latency=perf_counter() - started)
        return parsed, cost
    except Exception as exc:
        tracker.add(endpoint, model_name, latency=perf_counter() - started, ok=False, error=type(exc).__name__)
        raise


def explain_error(error: Exception) -> str:
    """Chuyển lỗi gateway thường gặp thành thông báo ngắn tiếng Việt."""
    message = str(error)
    lower = message.lower()
    status = getattr(error, "status_code", None)
    if status == 401 or "401" in lower:
        return "Gateway từ chối xác thực. Kiểm tra THUCCHIEN_API_KEY."
    if status == 429 or "429" in lower:
        if "budget" in lower or "exceeded" in lower:
            return "Ngân sách gateway đã hết. Kiểm tra hạn mức của đội."
        return "Gateway đang quá tải hoặc vượt giới hạn yêu cầu. Thử lại sau ít phút."
    if isinstance(error, (httpx.TimeoutException, TimeoutError)) or "timeout" in lower:
        return "Yêu cầu đến gateway quá thời gian chờ. Thử lại sau."
    if status:
        return f"Gateway trả lỗi HTTP {status}: {message[:300]}"
    return f"Không thể hoàn tất yêu cầu: {message[:300]}"
