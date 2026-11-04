#!/usr/bin/env python3
"""Construit l'aperçu live : copies audio/images + formes d'onde + index.html.

    python3 projects/missa-tv-360-promo-50s/apercu/build.py

Puis servir le dossier avec :
    python3 -m http.server 8090 --bind 0.0.0.0
"""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
REPO = PROJECT.parents[1]
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
FONT = REPO / "assets" / "fonts" / "Montserrat-Bold.ttf"
JAUNE = (255, 212, 0)
FOND = (11, 16, 32)
BLANC = (255, 255, 255)

AUDIO = [
    ("template.mp3", REPO / "assets" / "audio" / "Voive Template.mp3",
     "1 · TEMPLATE VOCAL", "Référence uploadée sur GitHub · 24,02 s"),
    ("voix-origine.mp3", PROJECT / "assets" / "voix-off.mp3",
     "2 · VO D'ORIGINE", "voice-02 · 44,32 s"),
    ("voix-timbre.mp3", PROJECT / "assets" / "voix-off-timbre-seul.mp3",
     "3 · TIMBRE SEUL", "enveloppe spectrale du template"),
    ("voix-matchee.mp3", PROJECT / "assets" / "voix-off-matched.mp3",
     "4 · TIMBRE + HAUTEUR", "candidat « cloné » · correction x1,20"),
    ("comparaison.mp3", PROJECT / "assets" / "comparaison-voix.mp3",
     "A/B COMPLET", "4 extraits de 7 s enchaînés · 29,05 s"),
]


def decode(path: Path, rate: int = 22050) -> np.ndarray:
    raw = Path("/tmp") / "_apercu_wave.raw"
    subprocess.run(
        [FFMPEG, "-y", "-loglevel", "error", "-i", str(path), "-ac", "1",
         "-ar", str(rate), "-f", "f32le", "-acodec", "pcm_f32le", str(raw)],
        check=True,
    )
    x = np.fromfile(raw, dtype=np.float32)
    raw.unlink(missing_ok=True)
    return x


def waveforms() -> None:
    W, H = 1200, 760
    im = Image.new("RGB", (W, H), FOND)
    d = ImageDraw.Draw(im)
    f_title = ImageFont.truetype(str(FONT), 30)
    f_label = ImageFont.truetype(str(FONT), 20)
    f_sub = ImageFont.truetype(str(FONT), 15)
    d.text((40, 24), "COMPARAISON DES PISTES VO", font=f_title, fill=JAUNE)
    d.text((40, 64), "Formes d'onde · amplitude normalisée par piste",
           font=f_sub, fill=(159, 180, 216))
    top, height, gap = 110, 105, 32
    for i, (name, _, label, sub) in enumerate(AUDIO):
        y0 = top + i * (height + gap)
        d.rounded_rectangle((40, y0, W - 40, y0 + height), radius=14,
                            fill=(20, 32, 64))
        d.text((60, y0 + 12), label, font=f_label, fill=JAUNE)
        d.text((60, y0 + 40), sub, font=f_sub, fill=(170, 190, 225))
        x = decode(HERE / name)
        n = 900
        buckets = len(x) // n
        if buckets < 1:
            continue
        amp = np.abs(x[: n * buckets].reshape(n, buckets)).max(axis=1)
        peak = float(amp.max()) or 1.0
        amp = amp / peak
        base = y0 + height - 16
        for j, v in enumerate(amp):
            px = 60 + j * (W - 120) / n
            h = v * (height - 56)
            d.line((px, base - h, px, base + h), fill=(255, 212, 0), width=1)
    im.save(HERE / "formes-onde.png")


HTML = """<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MISSA TV 360 — aperçu voix & storyboard</title>
<style>
  :root { --jaune:#FFD400; --fond:#0B1020; --carte:#142040; --texte:#EAF0FF; }
  * { box-sizing:border-box; }
  body { margin:0; background:var(--fond); color:var(--texte);
         font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;
         padding:28px; max-width:1100px; margin:auto; }
  h1 { color:var(--jaune); font-size:26px; margin:0 0 6px; }
  p.lead { color:#9FB4D8; margin:0 0 26px; font-size:15px; }
  h2 { color:var(--jaune); font-size:19px; margin:32px 0 14px;
       border-bottom:1px solid #24365f; padding-bottom:8px; }
  .carte { background:var(--carte); border:1px solid #24365f; border-radius:14px;
           padding:16px 18px; margin-bottom:12px; }
  .carte b { color:var(--jaune); display:block; margin-bottom:4px; font-size:15px; }
  .carte small { color:#9FB4D8; display:block; margin-bottom:10px; }
  audio { width:100%; height:38px; }
  video { width:100%; max-height:560px; background:#000; border-radius:10px;
          display:block; margin-bottom:8px; }
  .grille { display:grid; grid-template-columns:1fr 1fr; gap:16px; }
  .grille img { width:100%; border-radius:12px; border:1px solid #24365f; display:block; }
  .grille figcaption { color:#9FB4D8; font-size:13px; margin-top:6px; }
  table { border-collapse:collapse; width:100%; font-size:14px; }
  th,td { text-align:left; padding:8px 10px; border-bottom:1px solid #24365f; }
  th { color:var(--jaune); }
  .note { background:#1b2b52; border-left:4px solid var(--jaune); padding:14px 16px;
          border-radius:8px; font-size:14px; line-height:1.5; margin-top:24px; }
  code { background:#0a1228; padding:2px 6px; border-radius:4px; color:var(--jaune); }
  @media (max-width:760px) { .grille { grid-template-columns:1fr; } }
</style>
</head>
<body>
<h1>MISSA TV 360 · promo 50 s · 9:16</h1>
<p class="lead">Aperçu de travail — voix, storyboard et images de la grille. Tout est lu en relatif depuis cette page.</p>

<h2>Voir la vidéo rendue</h2>
<div class="carte">
  <video controls playsinline preload="metadata" src="video.mp4"></video>
  <small>MISSA TV 360 · 50 s · 1080x1920 · VO + 10 SFX · 20 sous-titres</small>
</div>

<h2>Écouter les 5 pistes</h2>
__CARTES__

<h2>Comparaison visuelle des formes d'onde</h2>
<div class="carte"><img src="formes-onde.png" alt="Formes d'onde" style="width:100%;border-radius:8px"></div>

<h2>Mesures acoustiques</h2>
<div class="carte"><table>
<tr><th>Mesure</th><th>Template</th><th>VO voice-02</th></tr>
<tr><td>F0 médian</td><td>294 Hz</td><td>203 Hz</td></tr>
<tr><td>Centre spectral</td><td>4 015 Hz</td><td>2 324 Hz</td></tr>
<tr><td>Durée</td><td>24,02 s</td><td>44,32 s</td></tr>
</table></div>

<h2>Visuels validés</h2>
<div class="grille">
  <figure><img src="storyboard.png" alt="Storyboard"><figcaption>Storyboard 6 plans · 50 s</figcaption></figure>
  <figure><img src="images10.jpg" alt="10 images"><figcaption>Les 10 images générées de la grille</figcaption></figure>
</div>

<div class="note"><b>⚠️ Limite</b> : le transfert spectral rapproche la couleur du
timbre mais ne clone pas l'identité, la prosodie ni l'accent. Un vrai clonage
nécessite VoxCPM2 sur un poste connecté : <code>./md vo --backend voxcpm --voice "assets/audio/Voive Template.mp3"</code>.
Voir <code>CLONAGE-VOIX.md</code>.</div>
</body>
</html>
"""


def main() -> None:
    for name, src, _, _ in AUDIO:
        if not src.exists():
            raise SystemExit(f"Source absente : {src}")
        shutil.copy2(src, HERE / name)
    shutil.copy2(PROJECT / "storyboard" / "planche-storyboard.png", HERE / "storyboard.png")
    shutil.copy2(PROJECT / "images" / "planche-images.jpg", HERE / "images10.jpg")
    video = REPO / "livrables" / "missa-tv-360-promo-50s.mp4"
    if not video.exists():
        raise SystemExit(f"Vidéo absente : {video}")
    shutil.copy2(video, HERE / "video.mp4")
    waveforms()
    cards = "\n".join(
        f'<div class="carte"><b>{label}</b><small>{sub}</small>'
        f'<audio controls preload="metadata" src="{name}"></audio></div>'
        for name, _, label, sub in AUDIO
    )
    (HERE / "index.html").write_text(HTML.replace("__CARTES__", cards), encoding="utf-8")
    print("✅ Aperçu construit :", HERE)
    for p in sorted(HERE.iterdir()):
        if p.is_file():
            print("  ", p.name, p.stat().st_size // 1024, "Ko")


if __name__ == "__main__":
    main()
