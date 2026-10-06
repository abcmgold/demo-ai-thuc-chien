"""Thư viện tiện ích AI Thực Chiến Gateway."""

from .client import explain_error, http, openai_client, tracker, tracked
from .config import Settings, get_settings, require_key
from .embedding import cosine, embed
from .media import (
    download_video, edit_image, generate_image, generate_video, save_output,
    speech_to_text, start_video, text_to_speech, video_status,
)
from .models import (
    ASPECT_RATIOS, EMBED_MODELS, GEMINI_VOICES, IMAGE_MODELS, OPENAI_VOICES,
    REASONING_EFFORTS, STT_MODELS, TEXT_MODELS, TTS_MODELS, VIDEO_MODELS,
    provider_of,
)
from .spend import get_spend
from .text import ChatResult, chat, chat_json, chat_stream, web_search

__all__ = [
    "ASPECT_RATIOS", "ChatResult", "EMBED_MODELS", "GEMINI_VOICES", "IMAGE_MODELS",
    "OPENAI_VOICES", "REASONING_EFFORTS", "STT_MODELS", "Settings", "TEXT_MODELS",
    "TTS_MODELS", "VIDEO_MODELS", "chat", "chat_json", "chat_stream", "cosine",
    "download_video", "edit_image", "embed", "explain_error", "generate_image",
    "generate_video", "get_settings", "get_spend", "http", "openai_client",
    "provider_of", "require_key", "save_output", "speech_to_text", "start_video",
    "text_to_speech", "tracker", "tracked", "video_status", "web_search",
]
