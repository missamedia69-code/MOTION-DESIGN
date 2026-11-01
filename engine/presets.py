"""Presets de format (canvas) et d'export du moteur."""
from __future__ import annotations

# Formats de diffusion → dimensions du canvas
CANVAS_PRESETS: dict[str, dict] = {
    "16x9":   {"width": 1920, "height": 1080, "fps": 30, "label": "YouTube / TV / écran"},
    "9x16":   {"width": 1080, "height": 1920, "fps": 30, "label": "Reels / TikTok / Shorts / Story"},
    "1x1":    {"width": 1080, "height": 1080, "fps": 30, "label": "Feed Instagram / LinkedIn"},
    "4x5":    {"width": 1080, "height": 1350, "fps": 30, "label": "Feed Instagram portrait"},
    "21x9":   {"width": 2560, "height": 1080, "fps": 30, "label": "Cinématique ultralarge"},
    "720p":   {"width": 1280, "height": 720,  "fps": 30, "label": "HD léger (tests rapides)"},
}

# Presets d'export → arguments ffmpeg (vidéo + audio)
EXPORT_PRESETS: dict[str, dict] = {
    "mp4-hq": {
        "ext": ".mp4",
        "args": ["-c:v", "libx264", "-crf", "18", "-preset", "slow",
                 "-pix_fmt", "yuv420p", "-profile:v", "high",
                 "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart"],
        "label": "MP4 haute qualité (livrable standard)",
    },
    "mp4-web": {
        "ext": ".mp4",
        "args": ["-c:v", "libx264", "-crf", "23", "-preset", "veryfast",
                 "-pix_fmt", "yuv420p",
                 "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart"],
        "label": "MP4 léger (prévisualisation / web)",
    },
    "mp4-h265": {
        "ext": ".mp4",
        "args": ["-c:v", "libx265", "-crf", "24", "-preset", "medium",
                 "-pix_fmt", "yuv420p", "-tag:v", "hvc1",
                 "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart"],
        "label": "MP4 H.265 (poids réduit, qualité égale)",
    },
    "gif": {
        "ext": ".gif",
        "args": [],  # pipeline palettegen/paletteuse dédié dans render.py
        "label": "GIF animé (palette optimisée)",
        "gif_fps": 15,
        "gif_width": 640,
    },
    "webm-vp9": {
        "ext": ".webm",
        "args": ["-c:v", "libvpx-vp9", "-crf", "32", "-b:v", "0", "-row-mt", "1",
                 "-c:a", "libopus", "-b:a", "128k"],
        "label": "WebM VP9 (web, fond transparent possible)",
    },
    "mov-alpha": {
        "ext": ".mov",
        "args": ["-c:v", "prores_ks", "-profile:v", "4444", "-pix_fmt", "yuva444p10le",
                 "-c:a", "pcm_s16le"],
        "label": "ProRes 4444 avec canal alpha (compositing)",
    },
}

# Transitions xfade disponibles (sous-ensemble fiable)
XFADE_TRANSITIONS = [
    "fade", "fadeblack", "fadewhite", "wipeleft", "wiperight", "wipeup", "wipedown",
    "slideleft", "slideright", "slideup", "slidedown", "circleopen", "circleclose",
    "dissolve", "pixelize", "diagtl", "diagbr", "hlslice", "hrslice", "smoothleft",
    "smoothright", "zoomin",
]

DEFAULT_CANVAS = "16x9"
DEFAULT_EXPORT = "mp4-hq"


def canvas(preset_or_custom: str | dict) -> dict:
    if isinstance(preset_or_custom, dict):
        c = dict(CANVAS_PRESETS[DEFAULT_CANVAS])
        c.update(preset_or_custom)
        return c
    if preset_or_custom in CANVAS_PRESETS:
        return dict(CANVAS_PRESETS[preset_or_custom])
    raise KeyError(f"Preset canvas inconnu : {preset_or_custom}. Dispo : {', '.join(CANVAS_PRESETS)}")


def export(name: str) -> dict:
    if name not in EXPORT_PRESETS:
        raise KeyError(f"Preset d'export inconnu : {name}. Dispo : {', '.join(EXPORT_PRESETS)}")
    return EXPORT_PRESETS[name]
