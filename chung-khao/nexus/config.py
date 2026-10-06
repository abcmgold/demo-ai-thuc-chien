"""Cấu hình dùng chung cho AI Thực Chiến Gateway."""

from dataclasses import dataclass
from functools import lru_cache
import os
from pathlib import Path

from dotenv import load_dotenv

CHUNG_KHAO_DIR = Path(__file__).resolve().parents[1]
REPO_DIR = CHUNG_KHAO_DIR.parent

# Giá trị đã có trong môi trường luôn được ưu tiên; không in hoặc lưu API key.
load_dotenv(CHUNG_KHAO_DIR / ".env", override=False)
load_dotenv(REPO_DIR / ".env", override=False)


@dataclass(frozen=True)
class Settings:
    api_key: str
    base_url: str
    timeout: float
    max_retries: int
    text_model: str
    image_model: str
    video_model: str
    tts_model: str
    stt_model: str
    embed_model: str
    default_max_tokens: int | None
    output_dir: Path


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    output_dir = Path(os.getenv("NEXUS_OUTPUT_DIR", str(CHUNG_KHAO_DIR / "outputs")))
    if not output_dir.is_absolute():
        output_dir = CHUNG_KHAO_DIR / output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    raw_max_tokens = os.getenv("DEFAULT_MAX_TOKENS", "0").strip()
    max_tokens = int(raw_max_tokens) if raw_max_tokens else 0
    return Settings(
        api_key=os.getenv("THUCCHIEN_API_KEY", "").strip(),
        base_url=os.getenv("THUCCHIEN_BASE_URL", "https://api.thucchien.ai").rstrip("/"),
        timeout=float(os.getenv("NEXUS_TIMEOUT", "120")),
        max_retries=int(os.getenv("NEXUS_MAX_RETRIES", "3")),
        text_model=os.getenv("DEFAULT_TEXT_MODEL", "gemini-3.1-flash-lite"),
        image_model=os.getenv("DEFAULT_IMAGE_MODEL", "nano-banana-2-lite"),
        video_model=os.getenv("DEFAULT_VIDEO_MODEL", "veo-3.1-lite-generate-001"),
        tts_model=os.getenv("DEFAULT_TTS_MODEL", "gemini-2.5-flash-preview-tts"),
        stt_model=os.getenv("DEFAULT_STT_MODEL", "gemini-3.5-transcribe-preview"),
        embed_model=os.getenv("DEFAULT_EMBED_MODEL", "gemini-embedding-001"),
        default_max_tokens=max_tokens or None,
        output_dir=output_dir,
    )


def require_key() -> str:
    """Trả API key hoặc báo lỗi hướng dẫn bằng tiếng Việt."""
    key = get_settings().api_key
    if not key:
        raise RuntimeError("Chưa cấu hình THUCCHIEN_API_KEY. Hãy thêm key vào biến môi trường hoặc chung-khao/.env.")
    return key
