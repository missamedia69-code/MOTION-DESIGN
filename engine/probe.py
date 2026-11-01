"""Analyse de fichiers média (durée, résolution, fps, audio) via PyAV."""
from __future__ import annotations

import os

IMG_EXT = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff", ".gif", ".svg"}
VID_EXT = {".mp4", ".mov", ".mkv", ".avi", ".webm", ".m4v", ".ogv"}
AUD_EXT = {".mp3", ".wav", ".ogg", ".m4a", ".aac", ".flac", ".aiff"}


def probe(path: str) -> dict:
    """Retourne un dict d'infos sur le média, ou {'error': ...}."""
    path = str(path)
    info = {"path": path, "file": os.path.basename(path), "size": os.path.getsize(path)}
    ext = os.path.splitext(path)[1].lower()
    info["kind"] = "image" if ext in IMG_EXT else "video" if ext in VID_EXT else "audio" if ext in AUD_EXT else "fichier"
    try:
        import av

        with av.open(path) as c:
            if c.streams.video:
                s = c.streams.video[0]
                info["width"] = s.width
                info["height"] = s.height
                info["codec"] = s.codec_context.name
                if s.average_rate:
                    info["fps"] = round(float(s.average_rate), 3)
                dur = None
                if c.duration:
                    dur = c.duration / av.time_base
                elif s.duration is not None and s.time_base:
                    dur = float(s.duration * s.time_base)
                if dur:
                    info["duration"] = round(dur, 3)
            if c.streams.audio:
                a = c.streams.audio[0]
                info["audio"] = True
                info["audio_codec"] = a.codec_context.name
                info["sample_rate"] = a.rate
                if "duration" not in info and c.duration:
                    info["duration"] = round(c.duration / av.time_base, 3)
            else:
                info["audio"] = info["kind"] == "audio"
    except Exception as e:  # noqa: BLE001
        info["error"] = str(e)
    return info


def fmt_size(n: int) -> str:
    for unit in ("o", "Ko", "Mo", "Go"):
        if n < 1024 or unit == "Go":
            return f"{n:.0f} {unit}" if unit == "o" else f"{n / 1:.1f} {unit}"
        n /= 1024
    return f"{n} o"
