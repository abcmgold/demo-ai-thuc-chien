"""Tạo vector embedding và tính tương đồng cosine."""

from typing import Sequence

from .client import openai_client, tracked
from .config import get_settings


def embed(texts: str | list[str], model: str | None = None) -> list[list[float]]:
    model = model or get_settings().embed_model
    inputs = [texts] if isinstance(texts, str) else list(texts)
    vectors: list[list[float]] = []
    batches = [[item] for item in inputs] if model == "gemini-embedding-2" else [inputs]
    for batch in batches:
        response, _ = tracked("embeddings", model, openai_client().embeddings.with_raw_response.create,
                              model=model, input=batch)
        vectors.extend(item.embedding for item in response.data)
    return vectors


def cosine(a: Sequence[float], b: Sequence[float]) -> float:
    if len(a) != len(b) or not a:
        raise ValueError("Hai vector phải có cùng số chiều và không được rỗng.")
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(y * y for y in b) ** 0.5
    return dot / (norm_a * norm_b) if norm_a and norm_b else 0.0
