#!/usr/bin/env python3
"""Bande-son WIP v2, 59,00 s : VO de travail corrigée + SFX media-use.

Produit les 4 pistes séparées 48 kHz 16 bits (D.4) + le mix à muxer :
  voix-montage.wav · sfx.wav · musique.wav (SILENCE) · mix.wav

Révision 1.1 : la VO de travail contient désormais « Mille francs CFA par
mois. » et « Deux mois offerts ! ». Elle dure exactement 59,00 s : plus aucune
coupe n'est nécessaire, donc sous-titres / images / son partagent le MÊME
calage (render/wip_cuts.py). Le nombre de bruitages passe de 76 à ~34 pour
accompagner la cure d'épurement visuelle.
"""
from __future__ import annotations
import subprocess
import sys
from pathlib import Path
import numpy as np
import imageio_ffmpeg

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from wip_cuts import S  # noqa: E402

AUD = ROOT / "assets" / "audio"
SFX = ROOT.parent / ".claude" / "skills" / "media-use" / "audio" / "assets" / "sfx"
FF = imageio_ffmpeg.get_ffmpeg_exe()
SR, TOTAL = 48000, 59.0
N = int(SR * TOTAL)
T = {fid: a for fid, a, _ in S}


def A(fid, off=0.0):
    return T[fid] + off


def decode(path: Path) -> np.ndarray:
    out = subprocess.run(
        [FF, "-v", "error", "-i", str(path), "-f", "f32le", "-acodec", "pcm_f32le",
         "-ac", "1", "-ar", str(SR), "-"],
        capture_output=True, check=True).stdout
    return np.frombuffer(out, dtype=np.float32).copy()


def write_wav(path: Path, x: np.ndarray):
    pcm = (np.clip(x, -1, 1) * 32767).astype("<i2")
    subprocess.run([FF, "-v", "error", "-y", "-f", "s16le", "-ar", str(SR), "-ac", "1",
                    "-i", "-", "-c:a", "pcm_s16le", str(path)],
                   input=pcm.tobytes(), check=True)


# --- 1. VO : déjà exactement 59,00 s, aucune coupe, aucune accélération ----
vo = decode(AUD / "voix-temporaire.mp3")
vo = np.pad(vo[:N], (0, max(0, N - len(vo))))[:N].astype(np.float32)

# --- 2. SFX : banque locale (Pixabay Content License), calés sur les gestes -
E = [
    ("typing", A("F01", 0.05), .22), ("impact-bass-1", A("F01", 0.50), .38),
    ("key-press", A("F01", 1.00), .14), ("key-press", A("F01", 1.30), .14),
    ("key-press", A("F01", 1.60), .14), ("ping", A("F01", 3.40), .20),
    ("click", A("F02", 0.35), .16), ("click", A("F02", 1.10), .16),
    ("click", A("F02", 1.85), .16), ("pop", A("F02", 2.10), .18),
    ("impact-bass-2", A("F03", 0.20), .20), ("impact-bass-2", A("F03", 2.25), .22),
    ("whoosh-short", A("F04", 0.10), .18), ("whoosh-cinematic", A("F04", 1.70), .28),
    ("impact-bass-1", A("F05", 1.52), .50), ("sparkle", A("F05", 1.75), .26),
    ("impact-bass-2", A("F06", 0.30), .34), ("chime", A("F06", 0.45), .24),
] + [(("click-soft", A("F06", 1.10 + i * 0.18), .07)) for i in range(6)] + [
    ("whoosh-short", A("F07", 0.35), .12), ("whoosh-short", A("F07", 1.00), .12),
    ("whoosh-short", A("F07", 2.20), .12),
    ("notification", A("F08", 0.60), .11), ("notification", A("F08", 2.60), .11),
    ("notification", A("F08", 4.50), .11), ("whoosh-short", A("F08", 6.30), .14),
    ("chime", A("F09", 0.25), .22), ("click-soft", A("F09", 1.60), .08),
    ("click-soft", A("F09", 3.20), .08), ("whoosh-short", A("F09", 5.10), .14),
    ("click", A("F10", 0.05), .14), ("click", A("F10", 0.30), .14),
    ("click", A("F10", 0.55), .14), ("chime", A("F10", 1.35), .22),
    ("typing", A("F11", 0.10), .20), ("chime", A("F11", 1.00), .30),
    ("pop", A("F12", 0.10), .24), ("click-soft", A("F12", 3.30), .10),
    ("click-soft", A("F12", 3.45), .10), ("chime", A("F12", 3.75), .26),
    ("click", A("F13", 0.75), .24), ("sparkle", A("F13", 1.60), .24),
    ("typing", A("F13", 2.60), .16),
]
sfx = np.zeros(N, dtype=np.float32)
cache: dict[str, np.ndarray] = {}
for name, at, gain in E:
    f = SFX / f"{name}.mp3"
    if not f.exists():
        continue
    if name not in cache:
        cache[name] = decode(f)
    w = (cache[name] * gain).astype(np.float32)
    i = int(at * SR)
    if i >= N:
        continue
    k = min(N, i + len(w))
    sfx[i:k] += w[:k - i]

# --- 3. pistes séparées + mix ----------------------------------------------
music = np.zeros(N, dtype=np.float32)   # [MUSIQUE TENSION] / [MUSIQUE ELAN]
sfx *= 0.5                             # voix au premier plan (section I.3)
mix = vo + sfx + music
peak = float(np.max(np.abs(mix)))
if peak > 0.95:
    for x in (mix, vo, sfx):
        x *= 0.95 / peak

AUD.mkdir(parents=True, exist_ok=True)
for name, x in [("voix-montage.wav", vo), ("sfx.wav", sfx),
                ("musique.wav", music), ("mix.wav", mix)]:
    write_wav(AUD / name, x)

print(f"✅ 59,00 s · 48 kHz mono 16 bits · {len(E)} événements SFX · "
      f"crête {float(np.max(np.abs(mix))):.3f} · "
      f"RMS VO {float(np.sqrt(np.mean(vo ** 2))):.4f} / "
      f"SFX {float(np.sqrt(np.mean(sfx ** 2))):.4f}")
