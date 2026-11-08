"""Aperçus : images fixes et planche contact d'un montage.

C'est le rétroviseur du pilote : un agent IA rend un brouillon rapide
(15 i/s, ultrafast, scènes en cache) puis regarde quelques images clés au
lieu de visionner la vidéo. Les images sont petites (largeur ~480 px) pour
rester légères dans le contexte d'un agent.
"""
from __future__ import annotations

import os

from PIL import Image, ImageDraw, ImageFont

from . import ffmpeg, probe

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def default_times(duration: float, count: int = 6) -> list[float]:
    """Instants répartis sur la vidéo (évite la toute première/dernière image)."""
    count = max(1, min(24, int(count)))
    if duration <= 0:
        return [0.0]
    step = duration / (count + 1)
    return [round(step * (k + 1), 2) for k in range(count)]


def extract(video: str, times: list[float], out_dir: str, width: int = 480) -> list[str]:
    """Extrait une image PNG par instant (seek précis)."""
    os.makedirs(out_dir, exist_ok=True)
    info = probe.probe(video)
    dur = float(info.get("duration") or 0)
    paths = []
    for k, t in enumerate(times):
        t = max(0.0, min(float(t), max(0.0, dur - 0.05))) if dur else max(0.0, float(t))
        out = os.path.join(out_dir, f"frame{k:02d}-{t:06.2f}s.png")
        ffmpeg.run(["-ss", f"{t:.3f}", "-i", video, "-frames:v", "1",
                    "-vf", f"scale={int(width)}:-2:flags=lanczos", out], echo=False)
        paths.append(out)
    return paths


def contact_sheet(paths: list[str], times: list[float], out_path: str,
                  cols: int | None = None, title: str | None = None) -> str:
    """Assemble les images en planche contact avec l'horodatage de chacune."""
    imgs = [Image.open(p).convert("RGB") for p in paths]
    if not imgs:
        raise SystemExit("ERREUR : aucune image pour la planche contact")
    tw, th = imgs[0].size
    cols = cols or (3 if tw >= th else 6)
    cols = max(1, min(cols, len(imgs)))
    rows = (len(imgs) + cols - 1) // cols
    gap, label_h = 12, 28
    top = 40 if title else 0
    W = cols * tw + (cols + 1) * gap
    H = top + rows * (th + label_h) + (rows + 1) * gap
    sheet = Image.new("RGB", (W, H), (17, 19, 24))
    d = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 16)
        tfont = ImageFont.truetype("DejaVuSans-Bold.ttf", 20)
    except OSError:
        font = tfont = ImageFont.load_default()
    if title:
        d.text((gap, 10), title, fill=(232, 234, 240), font=tfont)
    for k, (img, t) in enumerate(zip(imgs, times)):
        r, c = divmod(k, cols)
        x = gap + c * (tw + gap)
        y = top + gap + r * (th + label_h + gap)
        sheet.paste(img, (x, y))
        d.text((x, y + th + 5), f"{t:.2f} s", fill=(163, 169, 184), font=font)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    sheet.save(out_path)
    return out_path


def preview(proj: dict, project_dir: str, name: str, at: list[float] | None = None,
            count: int = 6, canvas_override=None, width: int = 480,
            sheet: bool = True, draft: bool = True) -> dict:
    """Brouillon rapide → images clés (+ planche). Retourne les chemins."""
    import contextlib
    import io

    from . import render

    buf = io.StringIO()
    tag = f"{name}-apercu" + (f"-{canvas_override}" if isinstance(canvas_override, str) else "")
    out_dir = os.path.join(REPO, ".cache", "apercus", tag)
    video = os.path.join(out_dir, "brouillon.mp4")
    with contextlib.redirect_stdout(buf):
        render.render_project_data(proj, project_dir, name, out_path=video,
                                   canvas_override=canvas_override, draft=draft)
    dur = float(probe.probe(video).get("duration") or 0)
    times = [float(t) for t in at] if at else default_times(dur, count)
    for f in os.listdir(out_dir):
        if f.startswith("frame") and f.endswith(".png"):
            os.remove(os.path.join(out_dir, f))
    paths = extract(video, times, out_dir, width)
    result = {"video": os.path.relpath(video, REPO), "duration_s": dur,
              "times": times, "frames": [os.path.relpath(p, REPO) for p in paths]}
    if sheet:
        sp = contact_sheet(paths, times, os.path.join(out_dir, "planche.png"),
                           title=f"{proj.get('title') or name} · {dur:.1f} s")
        result["sheet"] = os.path.relpath(sp, REPO)
    return result
