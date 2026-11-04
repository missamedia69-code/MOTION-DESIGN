#!/usr/bin/env python3
"""Contrôle du VRAI rendu (section M) : images noires, images figées, durée.

Usage : python3 render/wip_check.py <fichier.mp4>
Échantillonne 2 images/s (0,5 s), en niveaux de gris 64×114.
"""
import subprocess, sys
from pathlib import Path
import numpy as np
import imageio_ffmpeg

FF = imageio_ffmpeg.get_ffmpeg_exe()
SRC = sys.argv[1] if len(sys.argv) > 1 else "../../livrables/missa-tv-360-pub-59s_9x16_wip.mp4"
W, H, FPS = 64, 114, 2

raw = subprocess.run(
    [FF, "-v", "error", "-i", str(SRC), "-vf", f"fps={FPS},scale={W}:{H},format=gray",
     "-f", "rawvideo", "-pix_fmt", "gray", "-"],
    capture_output=True, check=True).stdout
n = len(raw) // (W * H)
a = np.frombuffer(raw, dtype=np.uint8)[:n * W * H].reshape(n, H, W).astype(np.float32)
t = np.arange(n) / FPS

dark = [(round(float(t[i]), 2), round(float(a[i].mean()), 1)) for i in range(n) if a[i].mean() < 8]
diff = np.array([np.abs(a[i] - a[i - 1]).mean() if i else 999 for i in range(n)])
frozen = [(round(float(t[i]), 2), round(float(diff[i]), 2)) for i in range(n) if diff[i] < 0.35]

print(f"échantillons : {n} ({t[-1]:.1f} s à {FPS} img/s)")
print(f"luminance moyenne : {a.mean():.1f} · min {a.min():.1f} · max {a.max():.1f}")
print(f"images noires (<8) : {len(dark)} → {dark[:14]}")
print(f"images quasi figées (Δ<0,35) : {len(frozen)} → {frozen[:14]}")
print("noirs intentionnels attendus : ~16,0-16,8 (pivot) et 58,7-59,0 (fondu final)")
print("OK" if len(dark) <= 6 else "⚠️ trop d'images noires à vérifier")
