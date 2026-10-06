"""Tạo/chỉnh ảnh, video và xử lý âm thanh qua gateway."""

import base64
from datetime import datetime
from pathlib import Path
import time
from typing import Callable

from .client import http, openai_client, tracked, tracker
from .config import get_settings, require_key
from .text import _messages


def generate_image(prompt: str, *, model: str | None = None, aspect_ratio: str = "1:1",
                   size: str = "1024x1024", quality: str = "low") -> tuple[bytes, float]:
    model = model or get_settings().image_model
    extra: dict = {"extra_body": {"aspect_ratio": aspect_ratio}} if model.startswith("nano-banana") else {}
    params = {"model": model, "prompt": prompt, "n": 1, **extra}
    if model.startswith("gpt-image"):
        params.update(size=size, quality=quality)
    response, cost = tracked("images/generations", model,
                             openai_client().images.with_raw_response.generate, **params)
    return base64.b64decode(response.data[0].b64_json), cost


def edit_image(prompt: str, images: list[bytes | str], *, model: str | None = None) -> list[bytes]:
    model = model or get_settings().image_model
    response, _ = tracked(
        "chat/completions", model, openai_client().chat.completions.with_raw_response.create,
        model=model, messages=_messages(prompt, None, images), modalities=["image", "text"],
    )
    message = response.choices[0].message
    raw_images = (getattr(message, "model_extra", None) or {}).get("images", [])
    outputs = []
    for item in raw_images:
        url = item.get("image_url", {}).get("url", "")
        if url.startswith("data:"):
            outputs.append(base64.b64decode(url.split(",", 1)[1]))
    return outputs


def start_video(prompt: str, *, model: str | None = None, seconds: str = "4",
                size: str = "1280x720", image: bytes | str | None = None) -> str:
    model = model or get_settings().video_model
    require_key()
    payload = {"model": model, "prompt": prompt, "seconds": str(seconds), "size": size}
    started = time.perf_counter()
    if image is None:
        response = http().post("/v1/videos", json=payload)
    else:
        import mimetypes
        if isinstance(image, bytes):
            file_content, filename, mime = image, "reference.png", "image/png"
        elif image.startswith(("http://", "https://")):
            import httpx
            remote = httpx.get(image, timeout=get_settings().timeout)
            remote.raise_for_status()
            file_content = remote.content
            filename = Path(image.split("?", 1)[0]).name or "reference.png"
            mime = remote.headers.get("content-type", "image/png").split(";", 1)[0]
        else:
            path = Path(image)
            file_content, filename = path.read_bytes(), path.name
            mime = mimetypes.guess_type(filename)[0] or "image/png"
        response = http().post("/v1/videos", data=payload,
                               files={"input_reference": (filename, file_content, mime)})
    response.raise_for_status()
    tracker.add("videos", model,
                cost=float(response.headers.get("x-litellm-response-cost", 0) or 0),
                latency=time.perf_counter() - started)
    return response.json()["id"]


def video_status(video_id: str) -> dict:
    return http().get(f"/v1/videos/{video_id}").raise_for_status().json()


def download_video(video_id: str) -> bytes:
    return http().get(f"/v1/videos/{video_id}/content").raise_for_status().content


def generate_video(prompt: str, on_update: Callable[[dict], None] | None = None, **kwargs) -> bytes:
    video_id = start_video(prompt, **kwargs)
    deadline = time.monotonic() + 600
    while time.monotonic() < deadline:
        status = video_status(video_id)
        if on_update:
            on_update(status)
        if status.get("status") == "completed":
            return download_video(video_id)
        if status.get("status") == "failed":
            raise RuntimeError(status.get("error", "Tạo video thất bại."))
        time.sleep(10)
    raise TimeoutError("Tạo video quá thời gian chờ 10 phút.")


def text_to_speech(text: str, *, model: str | None = None, voice: str | None = None) -> bytes:
    model = model or get_settings().tts_model
    voice = voice or ("alloy" if model.startswith("gpt-") else "Zephyr")
    response = http().post("/audio/speech", json={"model": model, "input": text, "voice": voice})
    response.raise_for_status()
    tracker.add("audio/speech", model, cost=float(response.headers.get("x-litellm-response-cost", 0) or 0))
    return response.content


def speech_to_text(audio_bytes: bytes, *, model: str | None = None, filename: str = "audio.mp3") -> str:
    model = model or get_settings().stt_model
    data = {"model": model}
    if model == "gpt-transcribe":
        data["response_format"] = "json"
    response = http().post("/audio/transcriptions", data=data,
                           files={"file": (filename, audio_bytes, "application/octet-stream")})
    response.raise_for_status()
    tracker.add("audio/transcriptions", model,
                cost=float(response.headers.get("x-litellm-response-cost", 0) or 0))
    return response.json().get("text", "")


def save_output(data: bytes, ext: str) -> Path:
    suffix = ext.lstrip(".")
    path = get_settings().output_dir / f"{datetime.now().strftime('%Y%m%d-%H%M%S-%f')}.{suffix}"
    path.write_bytes(data)
    return path
