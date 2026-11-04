#!/usr/bin/env python3
"""Transfert d'enveloppe spectrale — approximation locale d'un clonage vocal.

⚠️ Ce n'est PAS un clonage d'identité : aucun modèle de conversion de voix
n'est disponible hors ligne ici. L'outil analyse l'empreinte acoustique d'un
audio de référence (hauteur, brillance, enveloppe spectrale) et applique son
**enveloppe spectrale moyenne** à une VO déjà générée. Cela rapproche la
couleur du timbre, pas l'identité du locuteur ni la prosodie.

    # dès que le template est dans assets/audio/
    python3 tools/voice-match.py

    # ou explicitement
    python3 tools/voice-match.py --reference "assets/audio/Voive Template.mp3"

    # autotest sans template (utilise un segment VO existant comme référence)
    python3 tools/voice-match.py --self-test

Dépendances : numpy, PyAV, imageio-ffmpeg, ffmpeg (libmp3lame).
"""
from __future__ import annotations

import argparse
import os
import subprocess
from pathlib import Path

import imageio_ffmpeg
import numpy as np

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
REPO = PROJECT.parents[1]
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
SR = 44100
N_FFT = 2048
HOP = 512
EXTS = {".mp3", ".wav", ".m4a", ".aac", ".ogg", ".opus", ".flac", ".aiff"}


def decode(path: Path) -> np.ndarray:
    raw = Path("/tmp") / f"_vm_in_{os.getpid()}.raw"
    subprocess.run(
        [FFMPEG, "-y", "-loglevel", "error", "-i", str(path),
         "-ac", "1", "-ar", str(SR), "-f", "f32le", "-acodec", "pcm_f32le", str(raw)],
        check=True,
    )
    x = np.fromfile(raw, dtype=np.float32)
    raw.unlink(missing_ok=True)
    return x


def rel(path: Path) -> str:
    return os.path.relpath(path.resolve(), PROJECT)


def encode(y: np.ndarray, out: Path, pitch: float = 1.0) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    raw = Path("/tmp") / f"_vm_out_{os.getpid()}.raw"
    y.astype(np.float32).tofile(raw)
    af = []
    if abs(pitch - 1.0) > 0.001:
        af = ["-af", f"asetrate={SR * pitch:.2f},aresample={SR},atempo={1 / pitch:.6f}"]
    subprocess.run(
        [FFMPEG, "-y", "-loglevel", "error", "-f", "f32le", "-ar", str(SR),
         "-ac", "1", "-i", str(raw)] + af +
        ["-codec:a", "libmp3lame", "-b:a", "160k", str(out)],
        check=True,
    )
    raw.unlink(missing_ok=True)


def smooth(v: np.ndarray, k: int = 33) -> np.ndarray:
    kernel = np.ones(k, dtype=np.float64) / k
    pad = k // 2
    return np.convolve(np.pad(v, (pad, pad), mode="edge"), kernel, mode="valid")


def envelope(x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    win = np.hanning(N_FFT).astype(np.float32)
    n = 1 + (len(x) - N_FFT) // HOP
    mags = np.empty((n, N_FFT // 2 + 1), dtype=np.float32)
    rms = np.empty(n, dtype=np.float32)
    for i in range(n):
        seg = x[i * HOP: i * HOP + N_FFT] * win
        mags[i] = np.abs(np.fft.rfft(seg))
        rms[i] = np.sqrt(np.mean(seg ** 2))
    active = rms > max(rms.max() * 0.06, 1e-7)
    env = mags[active].mean(axis=0) if active.any() else mags.mean(axis=0)
    return smooth(env.astype(np.float64)) + 1e-6, np.fft.rfftfreq(N_FFT, 1 / SR)


def f0_median(x: np.ndarray) -> float | None:
    win, hop = int(SR * 0.04), int(SR * 0.01)
    n = 1 << (2 * win - 1).bit_length()
    global_rms = float(np.sqrt(np.mean(x ** 2))) or 1e-6
    lo, hi = int(SR / 500), int(SR / 70)
    values = []
    for i in range(0, len(x) - win, hop):
        seg = x[i: i + win].astype(np.float64)
        if np.sqrt(np.mean(seg ** 2)) < global_rms * 0.3:
            continue
        seg -= seg.mean()
        f = np.fft.rfft(seg, n)
        corr = np.fft.irfft(f * np.conj(f))[:win]
        lag = lo + int(np.argmax(corr[lo:hi]))
        values.append(SR / lag)
    return round(float(np.median(values)), 1) if values else None


def band_energy(env: np.ndarray, freqs: np.ndarray) -> dict[str, float]:
    bands = {"graves 0-300": (0, 300), "bas-medium 300-1000": (300, 1000),
             "medium 1000-3000": (1000, 3000), "aigus 3000-8000": (3000, 8000)}
    out = {}
    total = float(env.sum())
    for name, (a, b) in bands.items():
        sel = (freqs >= a) & (freqs < b)
        out[name] = round(float(env[sel].sum() / total * 100), 1)
    return out


def fingerprint(path: Path, x: np.ndarray) -> dict:
    env, freqs = envelope(x)
    return {
        "fichier": rel(path),
        "duree_s": round(len(x) / SR, 2),
        "f0_median_hz": f0_median(x),
        "centre_spectral_hz": round(float((env * freqs).sum() / env.sum()), 0),
        "rms": round(float(np.sqrt(np.mean(x ** 2))), 4),
        "bandes_pct": band_energy(env, freqs),
    }


def transfer(x: np.ndarray, ratio: np.ndarray) -> np.ndarray:
    win = np.hanning(N_FFT).astype(np.float32)
    n = 1 + (len(x) - N_FFT) // HOP
    out = np.zeros(len(x) + N_FFT, dtype=np.float32)
    norm = np.zeros_like(out)
    for i in range(n):
        seg = x[i * HOP: i * HOP + N_FFT] * win
        spec = np.fft.rfft(seg)
        shaped = np.abs(spec) * ratio * np.exp(1j * np.angle(spec))
        y = np.fft.irfft(shaped, n=N_FFT).astype(np.float32) * win
        out[i * HOP: i * HOP + N_FFT] += y
        norm[i * HOP: i * HOP + N_FFT] += win ** 2
    y = out[: len(x)] / np.maximum(norm[: len(x)], 1e-6)
    peak = float(np.max(np.abs(y))) or 1.0
    return np.clip(y / peak * 0.89, -1.0, 1.0)


def report(path: Path, title: str, ref: dict, src: dict, out: Path | None,
           note: str) -> None:
    lines = [
        f"# {title}", "",
        "> ⚠️ Transfert d'**enveloppe spectrale**, pas clonage d'identité.",
        "> La prosodie, l'accent et l'identité du locuteur ne sont pas reproduits.",
        "", "## Empreinte de la référence", "",
        f"- Fichier : `{ref['fichier']}`",
        f"- Durée : {ref['duree_s']} s · F0 médian : {ref['f0_median_hz']} Hz",
        f"- Centre spectral : {ref['centre_spectral_hz']} Hz · RMS : {ref['rms']}",
    ]
    for k, v in ref["bandes_pct"].items():
        lines.append(f"- {k} : {v} %")
    lines += ["", "## Empreinte de la VO source", "",
              f"- Fichier : `{src['fichier']}`",
              f"- Durée : {src['duree_s']} s · F0 médian : {src['f0_median_hz']} Hz",
              f"- Centre spectral : {src['centre_spectral_hz']} Hz · RMS : {src['rms']}", ""]
    if out:
        lines += [f"## Sortie", "", f"`{out.relative_to(PROJECT)}` — VO dont l'enveloppe",
                  "spectrale a été ramenée vers celle de la référence.", ""]
    lines += ["## État", "", note, ""]
    path.write_text("\n".join(lines), encoding="utf-8")


def find_reference() -> Path | None:
    """Cherche le template déposé à la racine du dépôt, puis dans le projet."""
    for audio in (REPO / "assets" / "audio", PROJECT / "assets" / "audio"):
        hit = next((p for p in sorted(audio.glob("*")) if p.suffix.lower() in EXTS), None)
        if hit:
            return hit
    return None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--reference")
    ap.add_argument("--source", default="assets/voix-off.mp3")
    ap.add_argument("--out", default="assets/voix-off-matched.mp3")
    ap.add_argument("--report", default="VOICE-MATCH.md")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--batch", action="store_true",
                    help="applique aussi le transfert aux 6 segments VO")
    ap.add_argument("--pitch", default="none",
                    help="none (défaut), auto (F0 réf/source, plafonné à 1.20) ou facteur")
    args = ap.parse_args()

    report_path = PROJECT / args.report
    source = PROJECT / args.source
    if not source.exists():
        raise SystemExit(f"VO source absente : {source}")

    selftest = args.self_test
    ref = (PROJECT / args.reference).resolve() if args.reference else None
    if selftest and ref is None:
        ref = PROJECT / "assets" / "vo" / "raw" / "seq-01.mp3"
    if ref is None:
        ref = find_reference()
    if ref is None or not ref.exists():
        src_x = decode(source)
        placeholder = {"fichier": "— référence absente —", "duree_s": 0,
                       "f0_median_hz": None, "centre_spectral_hz": 0,
                       "rms": 0, "bandes_pct": {}}
        report(report_path, "Transfert de timbre — référence manquante",
               placeholder, fingerprint(source, src_x), None,
               "Aucun audio de référence dans `assets/audio/`. Déposer le template "
               "(ex. `Voive Template.mp3`) puis relancer `python3 tools/voice-match.py`.")
        print("❌ Référence absente — rapport écrit :", report_path.relative_to(PROJECT))
        raise SystemExit(2)

    ref_x, src_x = decode(ref), decode(source)
    ref_fp, src_fp = fingerprint(ref, ref_x), fingerprint(source, src_x)
    env_r, _ = envelope(ref_x)
    env_s, _ = envelope(src_x)
    ratio = smooth(np.clip(env_r / env_s, 0.3, 3.0))
    if args.pitch == "none":
        pitch = 1.0
    elif args.pitch == "auto":
        f0r, f0s = ref_fp["f0_median_hz"], src_fp["f0_median_hz"]
        pitch = round(min(max(f0r / f0s, 0.85), 1.20), 3) if f0r and f0s else 1.0
    else:
        pitch = float(args.pitch)
    out = Path("/tmp/voice-match-selftest.mp3") if selftest else PROJECT / args.out
    encode(transfer(src_x, ratio), out, pitch)
    note = ("Autotest réussi : un segment VO existant a servi de référence factice, "
            "la chaîne analyse → transfert → encodage fonctionne. "
            "Relancer sans `--self-test` avec le vrai template.") if selftest else (
            "Transfert appliqué. Écouter la sortie et comparer à la VO d'origine ; "
            "si le résultat est métallique, réduire l'amplitude du ratio dans le script.")
    if args.batch and not selftest:
        target = PROJECT / "assets" / "vo-matched"
        target.mkdir(parents=True, exist_ok=True)
        segments = sorted((PROJECT / "assets" / "vo").glob("seq-*.mp3"))
        for seg in segments:
            encode(transfer(decode(seg), ratio), target / seg.name, pitch)
        note += (f"\n\nTransfert appliqué aux **{len(segments)} segments** → "
                 "`assets/vo-matched/` ; les durées sont inchangées, "
                 "`TIMING.md` et `subtitles.srt` restent valables.")
    note += f"\n\nCorrection de hauteur : **×{pitch}**" + (
        " (désactivée)" if pitch == 1.0 else
        " — plafonnée à 1.20 pour éviter un effet « voix de dessin animé ».")
    report(report_path, "Transfert de timbre" + (" — AUTOTEST" if selftest else ""),
           ref_fp, src_fp, None if selftest else out, note)
    print(f"✅ {'AUTOTEST' if selftest else 'Transfert'} → {out}")
    print(f"   F0 réf {ref_fp['f0_median_hz']} Hz / source {src_fp['f0_median_hz']} Hz")
    print(f"   Centre spectral réf {ref_fp['centre_spectral_hz']} Hz / source {src_fp['centre_spectral_hz']} Hz")
    print("   Rapport :", report_path.relative_to(PROJECT))


if __name__ == "__main__":
    main()
