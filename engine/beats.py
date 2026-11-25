"""Rythme d'une musique : tempo (BPM), temps, premiers temps de mesure, montées.

Sert à caler le montage sur la musique (les coupes tombent sur les temps, le
plus gros moment sur la montée) — technique du skill beat-sync-editing :
frames_per_beat = (60 / BPM) × fps ; on coupe sur des phrases de 2/4/8 temps.

Dépendances : numpy + ffmpeg (décodage). Aucun réseau.
"""
from __future__ import annotations

import subprocess

import numpy as np

from . import ffmpeg as ff

SR = 22050
HOP = 512
NFFT = 2048


def _decode(path: str, sr: int = SR) -> np.ndarray:
    cmd = [ff.ffmpeg_exe(), "-v", "error", "-i", path, "-ac", "1", "-ar", str(sr),
           "-f", "f32le", "-"]
    raw = subprocess.run(cmd, capture_output=True, check=False).stdout
    if not raw:
        raise SystemExit(f"ERREUR : audio illisible : {path}")
    return np.frombuffer(raw, dtype=np.float32).copy()


def onset_envelope(y: np.ndarray) -> np.ndarray:
    """Flux spectral (log-magnitude, demi-onde) : pics = attaques."""
    if len(y) < NFFT:
        y = np.pad(y, (0, NFFT - len(y)))
    n = 1 + (len(y) - NFFT) // HOP
    idx = np.arange(NFFT)[None, :] + HOP * np.arange(n)[:, None]
    frames = y[idx] * np.hanning(NFFT)[None, :]
    mag = np.log1p(10 * np.abs(np.fft.rfft(frames, axis=1)))
    flux = np.maximum(0, np.diff(mag, axis=0)).sum(axis=1)
    flux = np.concatenate([[0.0], flux])
    flux -= np.convolve(flux, np.ones(16) / 16, mode="same")   # retire la tendance
    flux = np.maximum(flux, 0)
    return flux / (flux.max() or 1.0)


def _tempo(env: np.ndarray, fr: float, lo: float = 70, hi: float = 180) -> float:
    ac = np.correlate(env, env, mode="full")[len(env) - 1:]
    lags = np.arange(len(ac))
    bpm = 60 * fr / np.maximum(lags, 1)
    ok = (bpm >= lo) & (bpm <= hi)
    if not ok.any():
        return 120.0
    # léger biais vers 120 BPM (zone la plus probable en pub)
    w = np.exp(-0.5 * (np.log2(bpm[ok] / 120) / 0.9) ** 2)
    best = lags[ok][np.argmax(ac[ok] * w)]
    # affinage parabolique
    if 1 <= best < len(ac) - 1:
        a, b, c = ac[best - 1], ac[best], ac[best + 1]
        d = (a - c) / (2 * (a - 2 * b + c) or 1)
        best = best + float(np.clip(d, -0.5, 0.5))
    return float(60 * fr / best)


def analyse(path: str) -> dict:
    """Retourne bpm, beats (s), downbeats (s), drops (s) et la durée."""
    y = _decode(path)
    dur = len(y) / SR
    env = onset_envelope(y)
    fr = SR / HOP
    bpm = _tempo(env, fr)
    period = 60 / bpm * fr                       # en trames d'enveloppe
    # phase : la grille qui récolte le plus d'énergie d'attaque
    phases = np.linspace(0, period, 32, endpoint=False)
    scores = []
    for ph in phases:
        pos = np.arange(ph, len(env), period).astype(int)
        scores.append(env[pos[pos < len(env)]].sum())
    ph = phases[int(np.argmax(scores))]
    grid = np.arange(ph, len(env), period)
    # recale chaque temps sur l'attaque la plus proche (± 1/8 de temps)
    win = max(1, int(period / 8))
    beats = []
    for g in grid:
        a, b = max(0, int(g) - win), min(len(env), int(g) + win + 1)
        beats.append((a + int(np.argmax(env[a:b]))) / fr if b > a else g / fr)
    beats = [round(t, 3) for t in beats if t <= dur]
    # premier temps de mesure (4/4) : la position modulo 4 la plus accentuée
    if len(beats) >= 8:
        acc = [sum(env[min(len(env) - 1, int(t * fr))] for t in beats[k::4]) for k in range(4)]
        k0 = int(np.argmax(acc))
    else:
        k0 = 0
    downbeats = beats[k0::4]
    # montées (drops) : plus forte hausse d'énergie RMS sur ~2 s
    rms = np.sqrt(np.convolve(y ** 2, np.ones(HOP) / HOP, mode="same")[::HOP] + 1e-12)
    rms_db = 20 * np.log10(rms + 1e-9)
    span = int(2 * fr)
    drops = []
    if len(rms_db) > 2 * span:
        rise = rms_db[span:] - rms_db[:-span]
        for _ in range(3):
            i = int(np.argmax(rise))
            if rise[i] < 6:
                break
            t = (i + span) / fr
            drops.append(round(min(downbeats or beats or [t], key=lambda d: abs(d - t)), 3))
            rise[max(0, i - span): i + span] = -1e9
    return {"file": path, "duration": round(dur, 3), "bpm": round(bpm, 1),
            "beat_period": round(60 / bpm, 4), "beats": beats, "downbeats": downbeats,
            "drops": sorted(set(drops))}


def snap(times: list[float], grid: list[float], tolerance: float = 0.25) -> list[float]:
    """Aimante chaque instant sur le temps le plus proche (si à moins de `tolerance` s)."""
    out = []
    for t in times:
        if not grid:
            out.append(t)
            continue
        g = min(grid, key=lambda b: abs(b - t))
        out.append(round(g, 3) if abs(g - t) <= tolerance else t)
    return out
