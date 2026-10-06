"""Model, giọng đọc và tham số được gateway hỗ trợ."""

TEXT_MODELS = (
    "gemini-3.1-flash-lite", "gemini-3.5-flash-lite", "gemini-3.5-flash",
    "gemini-3.1-pro-preview", "gpt-6-luna", "gpt-6-sol", "gpt-6.1-sol",
    "gpt-6-astra", "gpt-5.6-luna", "deepseek-flash", "deepseek-v4-pro",
)
IMAGE_MODELS = ("nano-banana-2-lite", "nano-banana-2", "nano-banana-pro", "gpt-image-2.5-flare", "gpt-image-2.5-sunburst")
VIDEO_MODELS = ("veo-3.1-lite-generate-001", "veo-3.1-fast-generate-001", "veo-3.1-generate-001")
TTS_MODELS = ("gemini-2.5-flash-preview-tts", "gemini-3.1-flash-tts-preview", "gpt-4o-mini-tts")
STT_MODELS = ("gemini-3.5-transcribe-preview", "gpt-4o-mini-transcribe", "gpt-4o-transcribe", "gpt-transcribe", "whisper-1")
EMBED_MODELS = ("gemini-embedding-001", "gemini-embedding-2", "text-multilingual-embedding-002", "text-embedding-005", "text-embedding-3-small", "text-embedding-3-large")
GEMINI_VOICES = ("Zephyr", "Puck", "Charon", "Kore", "Fenrir", "Leda", "Orus", "Aoede", "Callirrhoe", "Autonoe", "Enceladus", "Iapetus", "Umbriel", "Algieba", "Despina", "Erinome", "Algenib", "Rasalgethi", "Laomedeia", "Achernar", "Alnilam", "Schedar", "Gacrux", "Pulcherrima", "Achird", "Zubenelgenubi", "Vindemiatrix", "Sadachbia", "Sadaltager", "Sulafat")
OPENAI_VOICES = ("alloy", "echo", "fable", "onyx", "nova", "shimmer")
ASPECT_RATIOS = ("1:1", "3:4", "4:3", "16:9", "9:16")
REASONING_EFFORTS = {
    **{model: ("none", "low", "medium", "high", "xhigh") for model in ("gpt-6-sol", "gpt-6-luna", "gpt-5.6-luna", "gpt-5.6-terra", "gpt-5.6-sol")},
    **{model: ("low", "medium", "high", "xhigh") for model in ("gpt-6.1-sol", "gpt-6-astra")},
    "o3": ("low", "medium", "high"),
    "o4-mini": ("low", "medium", "high"),
}


def provider_of(model: str) -> str:
    name = model.lower()
    if name.startswith(("gpt-", "o3", "o4", "whisper")):
        return "openai"
    if name.startswith("deepseek"):
        return "deepseek"
    return "gemini"
