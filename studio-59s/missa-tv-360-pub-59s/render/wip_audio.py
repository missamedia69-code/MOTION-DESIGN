#!/usr/bin/env python3
"""Bande-son WIP 59,00 s : VO de travail + SFX media-use, musique en SILENCE.

Produit des pistes séparées 48 kHz 16 bits (D.4) + le mix à muxer dans le MP4 :
  assets/audio/voix-montage.wav   (VO seule, 59,00 s)
  assets/audio/sfx.wav            (bruitages seuls)
  assets/audio/musique.wav        (silence : [MUSIQUE TENSION] / [MUSIQUE ELAN])
  assets/audio/mix.wav            (somme, crête ≤ 0,95)

La VO de travail dure 59,544 s : on retire 0,544 s DANS un silence repéré par
onsets.py (52,61 → 53,29), jamais en accélérant la voix.
"""
from __future__ import annotations
import subprocess
from pathlib import Path
import numpy as np
import imageio_ffmpeg

ROOT = Path(__file__).resolve().parents[1]
AUD = ROOT / "assets" / "audio"
SFX = ROOT.parent / ".claude" / "skills" / "media-use" / "audio" / "assets" / "sfx"
FF = imageio_ffmpeg.get_ffmpeg_exe()
SR, TOTAL = 48000, 59.0
N = int(SR * TOTAL)


def decode(path: Path) -> np.ndarray:
    out = subprocess.run(
        [FF, "-v", "error", "-i", str(path), "-f", "f32le", "-acodec", "pcm_f32le",
         "-ac", "1", "-ar", str(SR), "-"],
        capture_output=True, check=True).stdout
    return np.frombuffer(out, dtype=np.float32).copy()


def write_wav(path: Path, x: np.ndarray):
    pcm = np.clip(x, -1, 1)
    pcm = (pcm * 32767).astype("<i2")
    subprocess.run([FF, "-v", "error", "-y", "-f", "s16le", "-ar", str(SR), "-ac", "1",
                    "-i", "-", "-c:a", "pcm_s16le", str(path)],
                   input=pcm.tobytes(), check=True)


# --- 1. VO : coupe dans un silence uniquement ------------------------------
vo = decode(AUD / "voix-temporaire.mp3")
cut_a, cut_b = 52.70, 52.70 + (len(vo) / SR - TOTAL)
vo = np.concatenate([vo[:int(cut_a * SR)], vo[int(cut_b * SR):]])
vo = np.pad(vo[:N], (0, max(0, N - len(vo))))[:N].astype(np.float32)
vo *= 0.92

# --- 2. SFX : banque locale (Pixabay Content License) ----------------------
E = [
    ("typing", 0.00, .22), ("impact-bass-1", 0.50, .38),
    ("key-press", 1.00, .14), ("key-press", 1.30, .14), ("key-press", 1.60, .14),
    ("key-press", 1.90, .14), ("key-press", 2.20, .14), ("key-press", 2.50, .14),
    ("ping", 3.40, .20), ("ping", 3.60, .18), ("ping", 3.80, .16),
    ("click", 4.20, .16), ("click", 4.70, .16), ("click", 5.00, .16),
    ("click", 5.30, .16), ("click", 5.60, .16), ("click", 5.75, .16), ("click", 5.90, .16),
    ("pop", 5.60, .18), ("whoosh-short", 6.50, .22),
    ("impact-bass-2", 8.50, .20), ("impact-bass-2", 8.72, .20), ("impact-bass-2", 8.94, .20),
    ("whoosh-short", 11.10, .14), ("whoosh-short", 11.40, .14), ("whoosh-short", 11.70, .14),
    ("whoosh-cinematic", 13.00, .30),
    ("impact-bass-1", 16.00, .48), ("sparkle", 16.50, .26),
    ("impact-bass-2", 16.80, .34), ("chime", 16.90, .24),
] + [("click-soft", 18.50 + i * .12, .07) for i in range(12)] + [
    ("whoosh-short", 22.20 + i * .55, .11) for i in range(6)
] + [("notification", 28.50 + i * .18, .09) for i in range(6)] + [
    ("key-press", 33.00, .16), ("chime", 34.55, .22), ("whoosh-short", 38.55, .18),
    ("click", 40.62, .14), ("click", 41.17, .14), ("click", 41.72, .14),
    ("typing", 43.07, .20), ("chime", 45.30, .30), ("pop", 46.80, .28),
] + [("click-soft", 51.20 + i * .20, .11) for i in range(7)] + [
    ("key-press", 53.00, .16), ("click", 56.20, .30), ("chime", 56.30, .34),
    ("sparkle", 57.20, .26), ("typing", 58.00, .18),
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
    j = min(N, i + len(w))
    sfx[i:j] += w[:j - i]

# --- 3. pistes séparées + mix ----------------------------------------------
music = np.zeros(N, dtype=np.float32)   # [MUSIQUE TENSION] / [MUSIQUE ELAN] : silence
# Voix au premier plan, SFX sous la voix (section I.3)
vo *= 2.0
sfx *= 0.5
mix = vo + sfx + music
peak = float(np.max(np.abs(mix)))
if peak > 0.95:
    mix *= 0.95 / peak
    vo *= 0.95 / peak
    sfx *= 0.95 / peak

AUD.mkdir(parents=True, exist_ok=True)
for name, x in [("voix-montage.wav", vo), ("sfx.wav", sfx),
                ("musique.wav", music), ("mix.wav", mix)]:
    write_wav(AUD / name, x)

print(f"✅ 59,00 s · 48 kHz mono 16 bits · {len(E)} événements SFX · "
      f"crête {float(np.max(np.abs(mix))):.3f} · RMS VO {float(np.sqrt(np.mean(vo**2))):.4f}")
print("   voix-montage.wav / sfx.wav / musique.wav (silence) / mix.wav")
