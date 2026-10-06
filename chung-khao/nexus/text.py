"""Tác vụ ngôn ngữ trên gateway AI Thực Chiến."""

from dataclasses import dataclass, field
import json
import re
from typing import Any, Iterator

from .client import openai_client, tracked, tracker
from .config import get_settings, require_key
from .models import provider_of


@dataclass
class ChatResult:
    text: str
    model: str
    cost: float = 0
    reasoning: str = ""
    usage: dict[str, int] = field(default_factory=dict)
    sources: list[dict[str, str]] = field(default_factory=list)

    @property
    def tokens(self) -> dict[str, int]:
        return {
            "input": self.usage.get("prompt_tokens", 0),
            "output": self.usage.get("completion_tokens", 0),
            "reasoning": self.usage.get("reasoning_tokens", 0),
            "total": self.usage.get("total_tokens", 0),
        }


def _params(model: str, *, temperature: float | None, max_tokens: int | None,
            reasoning_effort: str | None, thinking: bool | None,
            json_mode: bool, web_search: bool, extra: dict[str, Any]) -> dict[str, Any]:
    params = dict(extra)
    token_limit = get_settings().default_max_tokens if max_tokens is None else max_tokens
    if token_limit:
        params["max_completion_tokens" if provider_of(model) == "openai" else "max_tokens"] = token_limit
    provider = provider_of(model)
    if provider != "openai" and temperature is not None:
        params["temperature"] = temperature
    if provider == "openai" and reasoning_effort:
        params["reasoning_effort"] = reasoning_effort
    if provider == "deepseek" and thinking is False:
        params["extra_body"] = {**params.get("extra_body", {}), "thinking": {"type": "disabled"}}
    if json_mode:
        params["response_format"] = {"type": "json_object"}
    if web_search and provider == "gemini":
        params["tools"] = [{"googleSearch": {}}]
    return params


def _image_data(image: bytes | str) -> str:
    import base64
    import mimetypes
    from pathlib import Path

    if isinstance(image, bytes):
        return "data:image/png;base64," + base64.b64encode(image).decode("ascii")
    if image.startswith(("http://", "https://", "data:")):
        return image
    path = Path(image)
    mime = mimetypes.guess_type(path.name)[0] or "image/png"
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode("ascii")


def _messages(prompt_or_messages: str | list[dict[str, Any]], system: str | None,
              images: list[bytes | str] | None) -> list[dict[str, Any]]:
    messages = [{"role": "system", "content": system}] if system else []
    if isinstance(prompt_or_messages, str):
        content: Any = prompt_or_messages
        if images:
            content = [{"type": "text", "text": prompt_or_messages}]
            content.extend({"type": "image_url", "image_url": {"url": _image_data(image)}} for image in images)
        messages.append({"role": "user", "content": content})
    else:
        messages.extend(prompt_or_messages)
        if images:
            for message in reversed(messages):
                if message.get("role") == "user":
                    prior = message.get("content", "")
                    content = [{"type": "text", "text": prior}] if isinstance(prior, str) else list(prior)
                    content.extend({"type": "image_url", "image_url": {"url": _image_data(image)}} for image in images)
                    message["content"] = content
                    break
    return messages


def _result(response: Any, model: str, cost: float) -> ChatResult:
    choice = response.choices[0]
    message = choice.message
    usage_obj = getattr(response, "usage", None)
    details = getattr(usage_obj, "completion_tokens_details", None)
    usage = {
        "prompt_tokens": int(getattr(usage_obj, "prompt_tokens", 0) or 0),
        "completion_tokens": int(getattr(usage_obj, "completion_tokens", 0) or 0),
        "total_tokens": int(getattr(usage_obj, "total_tokens", 0) or 0),
        "reasoning_tokens": int(getattr(details, "reasoning_tokens", 0) or 0),
    }
    extra = getattr(response, "model_extra", None) or getattr(message, "model_extra", None) or {}
    sources: list[dict[str, str]] = []
    for item in extra.get("vertex_ai_grounding_metadata", []) or []:
        for chunk in item.get("groundingChunks", []) or []:
            web = chunk.get("web", {})
            if web.get("uri"):
                sources.append({"title": web.get("title", "Nguồn tham khảo"), "url": web["uri"]})
    return ChatResult(
        text=getattr(message, "content", "") or "", model=model, cost=cost,
        reasoning=getattr(message, "reasoning_content", "") or "", usage=usage, sources=sources,
    )


def chat(prompt_or_messages: str | list[dict[str, Any]], *, model: str | None = None,
         system: str | None = None, images: list[bytes | str] | None = None,
         temperature: float | None = None, max_tokens: int | None = None,
         reasoning_effort: str | None = None, thinking: bool | None = None,
         json_mode: bool = False, web_search: bool = False, **extra: Any) -> ChatResult:
    model = model or get_settings().text_model
    if web_search and provider_of(model) == "openai":
        return web_search_answer(prompt_or_messages if isinstance(prompt_or_messages, str) else str(prompt_or_messages), model=model)
    params = _params(model, temperature=temperature, max_tokens=max_tokens,
                     reasoning_effort=reasoning_effort, thinking=thinking,
                     json_mode=json_mode, web_search=web_search, extra=extra)
    params.update(model=model, messages=_messages(prompt_or_messages, system, images))
    response, cost = tracked("chat/completions", model, openai_client().chat.completions.with_raw_response.create, **params)
    return _result(response, model, cost)


def chat_stream(prompt_or_messages: str | list[dict[str, Any]], *, model: str | None = None,
                system: str | None = None, temperature: float | None = None,
                max_tokens: int | None = None, reasoning_effort: str | None = None,
                thinking: bool | None = None, **extra: Any) -> Iterator[str]:
    model = model or get_settings().text_model
    params = _params(model, temperature=temperature, max_tokens=max_tokens,
                     reasoning_effort=reasoning_effort, thinking=thinking,
                     json_mode=False, web_search=False, extra=extra)
    params.update(model=model, messages=_messages(prompt_or_messages, system, None), stream=True,
                  stream_options={"include_usage": True})
    started = __import__("time").perf_counter()
    token_count = 0
    try:
        for chunk in openai_client().chat.completions.create(**params):
            if chunk.usage:
                token_count = int(chunk.usage.total_tokens or 0)
            if chunk.choices:
                delta = chunk.choices[0].delta
                content = getattr(delta, "content", None)
                if content:
                    yield content
        tracker.add("chat/completions(stream)", model, tokens=token_count,
                    latency=__import__("time").perf_counter() - started)
    except Exception as exc:
        tracker.add("chat/completions(stream)", model,
                    latency=__import__("time").perf_counter() - started,
                    ok=False, error=type(exc).__name__)
        raise


def chat_json(prompt: str, *, schema_hint: str | None = None, **kwargs: Any) -> Any:
    instruction = "Trả lời bằng một đối tượng JSON hợp lệ, không thêm markdown."
    if schema_hint:
        instruction += f" Cấu trúc mong muốn: {schema_hint}"
    result = chat(prompt, system=instruction, json_mode=True, **kwargs)
    text = result.text.strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.IGNORECASE)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if not match:
            raise ValueError("Gateway không trả về JSON hợp lệ.")
        return json.loads(match.group(0))


def web_search_answer(question: str, *, model: str | None = None) -> ChatResult:
    model = model or get_settings().text_model
    if provider_of(model) != "openai":
        return chat(question, model=model, web_search=True)
    require_key()
    response, cost = tracked(
        "responses", model, openai_client().responses.with_raw_response.create,
        model=model, input=question, tools=[{"type": "web_search"}],
    )
    sources: list[dict[str, str]] = []
    for item in getattr(response, "output", []) or []:
        for content in getattr(item, "content", []) or []:
            for annotation in getattr(content, "annotations", []) or []:
                url = getattr(annotation, "url", None)
                if url:
                    sources.append({"title": getattr(annotation, "title", "Nguồn tham khảo"), "url": url})
    usage = getattr(response, "usage", None)
    return ChatResult(
        text=getattr(response, "output_text", "") or "", model=model, cost=cost,
        usage={"prompt_tokens": int(getattr(usage, "input_tokens", 0) or 0),
               "completion_tokens": int(getattr(usage, "output_tokens", 0) or 0),
               "total_tokens": int(getattr(usage, "total_tokens", 0) or 0)},
        sources=sources,
    )


def web_search(question: str, *, model: str | None = None) -> ChatResult:
    return web_search_answer(question, model=model)
