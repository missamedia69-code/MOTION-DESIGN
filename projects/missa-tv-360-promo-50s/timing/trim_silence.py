#!/usr/bin/env python3
"""Rogne les silences ajoutés par le TTS en tête/queue des 6 segments VO.

Les fichiers bruts restent dans `assets/vo/raw/` ; les versions propres sont
écrites dans `assets/vo/seq-*.mp3`, consommées par `timing/generate.py`.
On conserve 0,10 s avant la première parole et 0,20 s après la dernière pour
ne pas couper d'attaque ni de respiration naturelle.

    python3 projects/missa-tv-360-promo-50s/timing/trim_silence.py
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import av
import imageio_ffmpeg
import numpy as np

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
RAW = PROJECT / "assets" / "vo" / "raw"
OUT = PROJECT / "assets" / "vo"
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
KEEP_IN = 0.10
KEEP_OUT = 0.20


def analyse(path: Path) -> tuple[float, float, float]:
    with av.open(str(path)) as container:
        chunks = []
        for frame in container.decode(audio=0):
            chunks.append(frame.to_ndarray().reshape(-1).astype(np.float32))
        sr = container.streams.audio[0].rate
        duration = float(container.duration) / av.time_base
    x = np.concatenate(chunks)
    window = int(sr * 0.02)
    n = len(x) // window
    rms = np.sqrt(np.mean(x[: n * window].reshape(n, window) ** 2, axis=1))
    active = np.where(rms > max(rms) * 0.006)[0]
    lead = active[0] * 0.02
    trail = (n - 1 - active[-1]) * 0.02
    return duration, max(0.0, lead - KEEP_IN), max(0.0, trail - KEEP_OUT)


def main() -> None:
    if not RAW.exists() or not list(RAW.glob("seq-*.mp3")):
        raise SystemExit(f"Segments bruts absents : {RAW}")
    for i in range(1, 7):
        name = f"seq-{i:02d}.mp3"
        duration, cut_in, cut_out = analyse(RAW / name)
        length = duration - cut_in - cut_out
        subprocess.run(
            [FFMPEG, "-y", "-loglevel", "error", "-i", str(RAW / name),
             "-ss", f"{cut_in:.3f}", "-t", f"{length:.3f}",
             "-codec:a", "libmp3lame", "-b:a", "128k", str(OUT / name)],
            check=True,
        )
        print(f"{name}: {duration:.2f} s → {length:.2f} s "
              f"(−{cut_in:.2f} s début, −{cut_out:.2f} s fin)")
    print("✅ Segments propres dans assets/vo/ — relancer timing/generate.py")


if __name__ == "__main__":
    main()
