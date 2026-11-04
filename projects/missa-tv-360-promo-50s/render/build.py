#!/usr/bin/env python3
"""Construit et rend la vidéo MISSA TV 360 (50 s, 1080x1920, 30 fps).

Pipeline :
  1. assets PNG (tuiles, sous-titres, QR, champ de code, accents)
  2. bande-son 50 s = 6 segments VO + 10 familles de SFX
  3. project.json mono-scène à calques temporels absolus
  4. rendu via engine.render.render_project_data()

    python3 projects/missa-tv-360-promo-50s/render/build.py
"""
from __future__ import annotations

import sys
import subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
REPO = PROJECT.parents[1]
ASSETS = HERE / "assets"
IMAGES = PROJECT / "images"
VO = PROJECT / "assets" / "vo-matched"
SFX = PROJECT / "sfx" / "wav"
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
FONT_BOLD = REPO / "assets" / "fonts" / "Montserrat-Bold.ttf"
FONT_BLACK = REPO / "assets" / "fonts" / "Montserrat-Black.ttf"

W, H, FPS, DURATION = 1080, 1920, 30, 50.0
JAUNE = "#FFD400"
NAVY = "#0B1020"
BLANC = "#FFFFFF"
BLEU = "#163C9F"
GRIS = "#4A5E88"
VERT = "#00A651"

KINDS = ["films", "manga", "series", "short-drama", "tv-radio",
         "lives", "sport", "docs", "enfants", "jeux-video"]


def font(size: int, black: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_BLACK if black else FONT_BOLD), size)


def timing() -> list[dict]:
    rows = []
    for line in (PROJECT / "TIMING.md").read_text(encoding="utf-8").splitlines():
        if not line.startswith("| 0"):
            continue
        p = [c.strip() for c in line.split("|")]
        try:
            rows.append({"id": p[1], "title": p[2],
                         "start": float(p[3].replace(" s", "")),
                         "end": float(p[7].replace(" s", ""))})
        except (ValueError, IndexError):
            continue
    if len(rows) != 6:
        raise SystemExit(f"TIMING.md : 6 séquences attendues, {len(rows)} trouvées")
    return rows


def subtitles() -> list[tuple[float, float, str]]:
    out = []
    for block in (PROJECT / "subtitles.srt").read_text(encoding="utf-8").strip().split("\n\n"):
        lines = block.splitlines()
        if len(lines) < 3 or "-->" not in lines[1]:
            continue
        a, b = lines[1].split("-->")

        def sec(s: str) -> float:
            hh, mm, rest = s.strip().split(":")
            ss, ms = rest.split(",")
            return int(hh) * 3600 + int(mm) * 60 + int(ss) + int(ms) / 1000

        out.append((sec(a), min(sec(b), DURATION), " ".join(lines[2:])))
    return out


def hexrgb(c: str) -> tuple[int, int, int]:
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


# ── 1. Assets PNG ────────────────────────────────────────────────────────────

def build_assets() -> None:
    for d in ("tiles", "sub"):
        (ASSETS / d).mkdir(parents=True, exist_ok=True)

    # Accroche : bande jaune diagonale
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(im).polygon([(0, 0), (W, 0), (W, 240), (0, 560)], fill=hexrgb(JAUNE) + (255,))
    im.save(ASSETS / "slash.png")

    # Barre de recherche
    bw, bh = 920, 150
    im = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    d = ImageDraw.Draw(im, "RGBA")
    d.rounded_rectangle((0, 0, bw - 1, bh - 1), radius=75,
                        fill=(18, 30, 64, 255), outline=hexrgb(JAUNE) + (255,), width=5)
    d.ellipse((42, 44, 102, 104), outline=hexrgb(JAUNE) + (255,), width=7)
    d.line((98, 100, 132, 134), fill=hexrgb(JAUNE) + (255,), width=7)
    d.rounded_rectangle((180, 68, 800, 80), radius=6, fill=(140, 165, 215, 255))
    im.save(ASSETS / "search.png")

    # 10 tuiles arrondies
    tw, th = 430, 212
    for kind in KINDS:
        src = Image.open(IMAGES / f"{kind}.jpg").convert("RGB")
        tile = ImageOps.fit(src, (tw, th), method=Image.Resampling.LANCZOS)
        mask = Image.new("L", (tw, th), 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, tw, th), radius=36, fill=255)
        out = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
        out.paste(tile, (0, 0), mask)
        d = ImageDraw.Draw(out, "RGBA")
        d.rounded_rectangle((0, 0, tw - 1, th - 1), radius=36,
                            outline=hexrgb(JAUNE) + (255,), width=4)
        out.save(ASSETS / "tiles" / f"{kind}.png")

    # Anneau « DATA »
    r = 400
    im = Image.new("RGBA", (r, r), (0, 0, 0, 0))
    ImageDraw.Draw(im, "RGBA").arc((20, 20, r - 20, r - 20), 0, 300,
                                  fill=hexrgb(VERT) + (255,), width=32)
    im.save(ASSETS / "ring.png")

    # QR code déterministe
    n, cell, q = 21, 360 / 21, 360
    im = Image.new("RGBA", (q, q), hexrgb(NAVY) + (255,))
    d = ImageDraw.Draw(im, "RGBA")
    x = np.random.default_rng(360).random((n, n))
    for i in range(n):
        for j in range(n):
            if x[i, j] < 0.48:
                d.rectangle((j * cell, i * cell, (j + 1) * cell, (i + 1) * cell),
                            fill=(255, 255, 255, 255))
    for fi, fj in ((0, 0), (0, 14), (14, 0)):
        d.rectangle((fj * cell, fi * cell, (fj + 7) * cell, (fi + 7) * cell),
                    fill=hexrgb(NAVY) + (255,))
        d.rectangle(((fj + 1) * cell, (fi + 1) * cell, (fj + 6) * cell, (fi + 6) * cell),
                    fill=(255, 255, 255, 255))
        d.rectangle(((fj + 2) * cell, (fi + 2) * cell, (fj + 5) * cell, (fi + 5) * cell),
                    fill=hexrgb(NAVY) + (255,))
    im.save(ASSETS / "qr.png")

    # Champ du code d'activation
    cw, ch = 840, 140
    im = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    d = ImageDraw.Draw(im, "RGBA")
    d.rounded_rectangle((0, 0, cw - 1, ch - 1), radius=28,
                        fill=(18, 30, 64, 255), outline=hexrgb(JAUNE) + (255,), width=5)
    f, f2 = font(30), font(38)
    d.text((40, ch / 2), "CODE D'ACTIVATION", font=f, fill=(190, 205, 235, 255), anchor="lm")
    d.text((cw - 40, ch / 2), "•••• ••••", font=f2, fill=(255, 255, 255, 255), anchor="rm")
    im.save(ASSETS / "code-field.png")

    # Bouton ACTIVER
    bw, bh = 400, 120
    im = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    d = ImageDraw.Draw(im, "RGBA")
    d.rounded_rectangle((0, 0, bw - 1, bh - 1), radius=60, fill=hexrgb(JAUNE) + (255,))
    d.text((bw / 2, bh / 2), "ACTIVER", font=font(46, True), fill=hexrgb(NAVY) + (255,), anchor="mm")
    im.save(ASSETS / "button.png")

    # 20 bandeaux de sous-titres
    sw, sh = 1000, 150
    f = font(40)
    for idx, (_, _, text) in enumerate(subtitles(), 1):
        im = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
        d = ImageDraw.Draw(im, "RGBA")
        d.rounded_rectangle((0, 0, sw - 1, sh - 1), radius=30, fill=(6, 10, 22, 255))
        words, lines, cur = text.split(), [], ""
        for w_ in words:
            trial = (cur + " " + w_).strip()
            if d.textlength(trial, font=f) <= 900:
                cur = trial
            else:
                lines.append(cur)
                cur = w_
        if cur:
            lines.append(cur)
        step = 48
        y0 = sh / 2 - (len(lines) - 1) * step / 2
        for k, line in enumerate(lines):
            d.text((sw / 2, y0 + k * step), line, font=f,
                   fill=(255, 255, 255, 255), anchor="mm")
        im.save(ASSETS / "sub" / f"{idx:02d}.png")


# ── 2. Bande-son ─────────────────────────────────────────────────────────────

def decode(path: Path, rate: int = 48000) -> np.ndarray:
    raw = Path("/tmp") / f"_mix_{abs(hash(str(path)))}.raw"
    subprocess.run(
        [FFMPEG, "-y", "-loglevel", "error", "-i", str(path), "-ac", "1",
         "-ar", str(rate), "-f", "f32le", "-acodec", "pcm_f32le", str(raw)],
        check=True,
    )
    x = np.fromfile(raw, dtype=np.float32)
    raw.unlink(missing_ok=True)
    return x


def build_mix(rows: list[dict]) -> Path:
    rate = 48000
    bed = np.zeros(int(DURATION * rate), dtype=np.float32)

    def place(path: Path, at: float, volume: float) -> None:
        x = decode(path, rate)
        i = int(at * rate)
        j = min(len(bed), i + len(x))
        if i < len(bed):
            bed[i:j] += x[: j - i] * volume

    for k, r in enumerate(rows, 1):
        place(VO / f"seq-{k:02d}.mp3", r["start"], 1.0)

    s2, s3, s4, s5, s6 = (r["start"] for r in rows[1:])
    events = [(0.0, "impact.wav", 0.45), (0.0, "whoosh.wav", 0.35)]
    for i in range(10):
        events.append((s2 + 0.5 + i * 1.15, "pop.wav", 0.30))
    events += [
        (s2 + 4.0, "click.wav", 0.25),
        (s3, "whoosh.wav", 0.30), (s3 + 0.10, "click.wav", 0.25),
        (s4, "tick.wav", 0.25), (s4 + 0.22, "tick.wav", 0.25),
        (s4 + 0.35, "chime.wav", 0.30),
        (s5 + 0.30, "click.wav", 0.25), (s5 + 2.20, "click.wav", 0.25),
        (s5 + 4.20, "click.wav", 0.25),
        (s5 + 7.00, "beep.wav", 0.30), (s5 + 7.30, "key.wav", 0.22),
        (s5 + 7.50, "key.wav", 0.22), (s5 + 7.70, "key.wav", 0.22),
        (s6, "final_impact.wav", 0.50), (s6 + 0.05, "riser.wav", 0.30),
    ]
    for at, name, vol in events:
        place(SFX / name, at, vol)

    peak = float(np.max(np.abs(bed))) or 1.0
    bed = np.clip(bed / peak * 0.89, -1.0, 1.0)
    raw = Path("/tmp") / "_bande_son.raw"
    bed.astype(np.float32).tofile(raw)
    out = PROJECT / "assets" / "bande-son.mp3"
    subprocess.run(
        [FFMPEG, "-y", "-loglevel", "error", "-f", "f32le", "-ar", str(rate),
         "-ac", "1", "-i", str(raw), "-codec:a", "libmp3lame", "-b:a", "192k", str(out)],
        check=True,
    )
    raw.unlink(missing_ok=True)
    return out


# ── 3. project.json ──────────────────────────────────────────────────────────

def layer(**kw) -> dict:
    return kw


def build_layers(rows: list[dict]) -> list[dict]:
    s1, s2, s3, s4, s5, s6 = rows
    L: list[dict] = []

    def add(**kw):
        L.append(kw)

    # S1 — accroche
    add(type="image", file="render/assets/slash.png", pos="center",
        **{"in": 0.0, "out": s1["end"]}, anim="fade", fade_in=0.25, fade_out=0.4)
    add(type="image", file="assets/images/logo-missa.png",
        scale={"w": 620}, fit="contain", pos=[540, 760],
        **{"in": 0.3, "out": s1["end"]}, anim="pop", fade_in=0.35, anim_duration=0.6)
    add(type="text", text="EN AFRIQUE, ON PAIE…", size=60, color=BLANC,
        font="Montserrat-Black.ttf", pos=[540, 1280], max_width=940,
        **{"in": 0.8, "out": s1["end"]}, anim="fade_up", anim_duration=0.6)
    add(type="shape", kind="rect", w=320, h=10, radius=5, color=JAUNE,
        pos=[540, 1360], **{"in": 1.2, "out": s1["end"]},
        anim="grow_x", anim_duration=0.7)

    # S2 — mosaïque des 10 univers
    add(type="image", file="render/assets/search.png", pos=[540, 260],
        **{"in": s2["start"], "out": s2["end"]}, anim="fade", fade_in=0.3, fade_out=0.3)
    add(type="image", file="assets/images/box-mtn-cutout.png",
        scale={"w": 280}, fit="contain", pos=[850, 210],
        **{"in": s2["start"], "out": s2["end"]}, anim="fade", fade_in=0.4, fade_out=0.4)
    for i, kind in enumerate(KINDS):
        col, row = i % 2, i // 2
        x = 295 + col * 490
        y = 420 + row * 245
        add(type="image", file=f"render/assets/tiles/{kind}.png", pos=[x, y],
            **{"in": round(s2["start"] + 0.35 + i * 1.15, 2), "out": s2["end"]},
            anim="pop", fade_in=0.30, anim_duration=0.45)

    # S3 — faible débit
    for i, (hh, col) in enumerate(zip((52, 104, 156, 208), (JAUNE, JAUNE, GRIS, GRIS))):
        add(type="shape", kind="rect", w=64, h=hh, radius=10, color=col,
            pos=[340 + i * 92, 800 - hh / 2],
            **{"in": s3["start"], "out": s3["end"]},
            anim="grow_y", anim_duration=0.6)
    add(type="text", text="FAIBLE DÉBIT", size=62, color=BLANC,
        font="Montserrat-Black.ttf", pos=[540, 960],
        **{"in": s3["start"] + 0.3, "out": s3["end"]}, anim="fade_up")
    add(type="text", text="STABLE · ÉCONOME", size=38, color=JAUNE,
        pos=[540, 1040], **{"in": s3["start"] + 0.5, "out": s3["end"]}, anim="fade")
    add(type="image", file="render/assets/ring.png", pos=[540, 1340],
        **{"in": s3["start"] + 0.4, "out": s3["end"]}, anim="pop", fade_in=0.4)
    add(type="text", text="DATA", size=68, color=BLANC,
        font="Montserrat-Black.ttf", pos=[540, 1340],
        **{"in": s3["start"] + 0.6, "out": s3["end"]}, anim="fade")
    add(type="image", file="assets/images/pastille.png",
        scale={"w": 220}, fit="contain", pos=[150, 300],
        **{"in": s3["start"], "out": s3["end"]}, anim="fade", fade_in=0.3, fade_out=0.3)

    # S4 — essai 24 h
    add(type="image", file="assets/images/pastille.png",
        scale={"w": 720}, fit="contain", pos=[540, 800],
        **{"in": s4["start"], "out": s4["end"]}, anim="pop", fade_in=0.4)
    add(type="text", text="24 H", size=180, color=NAVY,
        font="Montserrat-Black.ttf", pos=[540, 800],
        **{"in": s4["start"] + 0.2, "out": s4["end"]}, anim="pop")
    add(type="text", text="ESSAI GRATUIT", size=60, color=JAUNE,
        font="Montserrat-Black.ttf", pos=[540, 1260],
        **{"in": s4["start"] + 0.4, "out": s4["end"]}, anim="fade_up")

    # S5 — prix & activation
    add(type="text", text="1 000 XAF / MOIS", size=72, color=BLANC,
        font="Montserrat-Black.ttf", pos=[540, 220],
        **{"in": s5["start"], "out": s5["end"]}, anim="fade_up")
    add(type="text", text="10 000 XAF / AN", size=88, color=JAUNE,
        font="Montserrat-Black.ttf", pos=[540, 360],
        **{"in": s5["start"] + 0.3, "out": s5["end"]}, anim="pop", fade_in=0.3)
    add(type="image", file="render/assets/qr.png", pos=[540, 700],
        **{"in": s5["start"] + 0.6, "out": s5["end"]}, anim="fade", fade_in=0.4)
    add(type="image", file="render/assets/code-field.png", pos=[540, 1000],
        **{"in": s5["start"] + 2.5, "out": s5["end"]}, anim="fade", fade_in=0.4)
    add(type="image", file="render/assets/button.png", pos=[540, 1220],
        **{"in": s5["start"] + 3.5, "out": s5["end"]}, anim="pop", fade_in=0.3)

    # S6 — signature
    add(type="shape", kind="rect", w=W, h=H, radius=0, color=JAUNE,
        pos=[540, 960], **{"in": s6["start"], "out": DURATION},
        anim="fade", fade_in=0.35, fade_out=0.01)
    add(type="image", file="assets/images/logo-missa.png",
        scale={"w": 640}, fit="contain", pos=[540, 620],
        **{"in": s6["start"] + 0.2, "out": DURATION}, anim="pop", fade_in=0.4)
    add(type="text", text="ACTIVEZ VOTRE CODE", size=72, color=NAVY,
        font="Montserrat-Black.ttf", pos=[540, 1260], max_width=980,
        **{"in": s6["start"] + 0.4, "out": DURATION}, anim="fade_up")
    add(type="text", text="10 000 XAF / AN", size=52, color=BLEU,
        font="Montserrat-Black.ttf", pos=[540, 1380],
        **{"in": s6["start"] + 0.6, "out": DURATION}, anim="fade")

    # Sous-titres (au-dessus de tout)
    for idx, (a, b, _) in enumerate(subtitles(), 1):
        add(type="image", file=f"render/assets/sub/{idx:02d}.png", pos=[540, 1730],
            **{"in": round(a, 2), "out": round(b, 2)},
            anim="fade", fade_in=0.10, fade_out=0.10)
    return L


def main() -> None:
    rows = timing()
    print("⏱  Séquences :", ", ".join(f"{r['id']}={r['start']}–{r['end']}s" for r in rows))
    build_assets()
    print(f"🎨 Assets PNG générés ({len(subtitles())} sous-titres, {len(KINDS)} tuiles)")
    mix = build_mix(rows)
    print("🔊 Bande-son :", mix.relative_to(REPO))

    proj = {
        "name": "missa-tv-360-promo-50s",
        "title": "MISSA TV 360 — promo verticale 50 s",
        "canvas": {"width": W, "height": H, "fps": FPS},
        "export": {"preset": "mp4-web"},
        "duration": DURATION,
        "background": "assets/images/fond-degrade.png",
        "audio": {"file": "assets/bande-son.mp3", "in": 0.0,
                  "volume": 1.0, "fade_in": 0, "fade_out": 0},
        "layers": build_layers(rows),
    }
    pj = PROJECT / "project.json"
    pj.write_text(__import__("json").dumps(proj, ensure_ascii=False, indent=2) + "\n",
                  encoding="utf-8")
    print(f"📄 project.json : {len(proj['layers'])} calques")

    from engine.render import render_project_data
    out = REPO / "livrables" / "missa-tv-360-promo-50s.mp4"
    out.parent.mkdir(parents=True, exist_ok=True)
    render_project_data(proj, str(PROJECT), "missa-tv-360-promo-50s",
                        out_path=str(out))
    print("🎬 Artefact :", out.relative_to(REPO))


if __name__ == "__main__":
    main()
