#!/usr/bin/env python3
"""Banque SFX procédurale pour la promo MISSA TV 360 (50 s, 9:16).

Aucun téléchargement, aucune dépendance audio externe : numpy + wave (stdlib).
Les fichiers sont déterministes (graine fixe) et mono 44,1 kHz / 16 bits.

    python3 projects/missa-tv-360-promo-50s/sfx/generate.py

Produit `sfx/wav/*.wav` et `sfx/MANIFEST.json`. Les WAV sont ignorés par Git
(`.gitignore` : *.wav) ; ce script permet de les régénérer après un clone.
"""
from __future__ import annotations

import json
import wave
from pathlib import Path

import numpy as np

SR = 44100
HERE = Path(__file__).resolve().parent
OUT = HERE / "wav"
RNG = np.random.default_rng(360)


def t(duration: float) -> np.ndarray:
    return np.arange(int(SR * duration), dtype=np.float64) / SR


def lowpass(noise: np.ndarray, alpha: float = 0.06) -> np.ndarray:
    out = np.empty_like(noise)
    acc = 0.0
    for i, v in enumerate(noise):
        acc += alpha * (v - acc)
        out[i] = acc
    return out


def save(name: str, x: np.ndarray, description: str) -> dict:
    x = np.asarray(x, dtype=np.float64)
    peak = float(np.max(np.abs(x))) or 1.0
    x = np.clip(x / peak * 0.82, -1.0, 1.0)
    pcm = (x * 32767).astype(np.int16)
    path = OUT / f"{name}.wav"
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    return {"file": f"wav/{name}.wav", "duration_s": round(len(x) / SR, 3),
            "description": description}


def whoosh(duration: float = 0.70) -> np.ndarray:
    n = int(SR * duration)
    noise = lowpass(RNG.normal(0, 1, n), alpha=0.045)
    shape = np.sin(np.linspace(0, np.pi, n)) ** 1.4
    sweep = np.sin(2 * np.pi * np.cumsum(np.linspace(90, 420, n)) / SR)
    return (noise * 0.85 + sweep * 0.25) * shape


def thump(duration: float = 0.55) -> np.ndarray:
    x = t(duration)
    freq = 95 * np.exp(-x * 7) + 42
    body = np.sin(2 * np.pi * np.cumsum(freq) / SR) * np.exp(-x * 7)
    crack = RNG.normal(0, 1, len(x)) * np.exp(-x * 45) * 0.35
    return body + crack


def pop(duration: float = 0.11) -> np.ndarray:
    x = t(duration)
    freq = 780 * np.exp(-x * 16) + 260
    return np.sin(2 * np.pi * np.cumsum(freq) / SR) * np.exp(-x * 34)


def click(duration: float = 0.045) -> np.ndarray:
    n = int(SR * duration)
    return RNG.normal(0, 1, n) * np.exp(-np.linspace(0, 12, n))


def tick(duration: float = 0.05) -> np.ndarray:
    x = t(duration)
    return np.sin(2 * np.pi * 1750 * x) * np.exp(-x * 85)


def key(duration: float = 0.030) -> np.ndarray:
    n = int(SR * duration)
    return RNG.normal(0, 1, n) * np.exp(-np.linspace(0, 16, n)) * 0.7


def beep(duration: float = 0.20) -> np.ndarray:
    x = t(duration)
    edge = np.minimum(1.0, np.minimum(x, duration - x) * 120)
    return (np.sin(2 * np.pi * 1180 * x) + 0.3 * np.sin(2 * np.pi * 2360 * x)) * edge * np.exp(-x * 3)


def chime(duration: float = 0.50) -> np.ndarray:
    x = t(duration)
    return (np.sin(2 * np.pi * 880 * x) + 0.6 * np.sin(2 * np.pi * 1320 * x)) * np.exp(-x * 6)


def riser(duration: float = 0.75) -> np.ndarray:
    x = t(duration)
    freq = np.linspace(180, 900, len(x))
    return np.sin(2 * np.pi * np.cumsum(freq) / SR) * (x / duration) ** 1.6 * np.exp(-x * 1.2)


def final_impact(duration: float = 0.90) -> np.ndarray:
    x = t(duration)
    base = thump(0.55)
    pad = np.zeros(len(x))
    pad[: len(base)] = base
    tone = (np.sin(2 * np.pi * 660 * x) + 0.5 * np.sin(2 * np.pi * 990 * x)) * np.exp(-x * 4) * 0.28
    return pad + tone


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    items = [
        ("whoosh", whoosh(), "Souffle de transition / ouverture"),
        ("impact", thump(), "Impact sourd d'ouverture"),
        ("pop", pop(), "Pop court : apparition d'un pictogramme"),
        ("click", click(), "Clic sec : recherche, révélation de prix"),
        ("tick", tick(), "Tick d'horloge pour le badge 24 h"),
        ("key", key(), "Frappe clavier : saisie du code"),
        ("beep", beep(), "Bip de scan du QR code"),
        ("chime", chime(), "Tintement discret de l'essai gratuit"),
        ("riser", riser(), "Montée courte avant la signature"),
        ("final_impact", final_impact(), "Impact final + tone de signature"),
    ]
    manifest = {"sample_rate": SR, "channels": 1, "bit_depth": 16,
                "generator": "sfx/generate.py", "seed": 360,
                "files": [save(name, signal, desc) for name, signal, desc in items]}
    (HERE / "MANIFEST.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"✅ {len(items)} SFX → {OUT.relative_to(HERE.parent.parent.parent.parent)}")
    for f in manifest["files"]:
        print(f"   {f['file']:<22} {f['duration_s']:.3f} s · {f['description']}")


if __name__ == "__main__":
    main()
