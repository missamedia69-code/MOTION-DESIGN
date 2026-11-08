"""Résolution et exécution du binaire ffmpeg."""
from __future__ import annotations

import functools
import os
import shlex
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@functools.lru_cache
def ffmpeg_exe() -> str:
    """Retourne le chemin du binaire ffmpeg (système ou statique imageio)."""
    exe = os.environ.get("MD_FFMPEG")
    if exe and os.path.exists(exe):
        return exe
    from shutil import which

    exe = which("ffmpeg")
    if exe:
        return exe
    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        sys.exit(
            "ERREUR : ffmpeg introuvable.\n"
            "  → pip3 install imageio-ffmpeg   (binaire statique)\n"
            "  → ou définir MD_FFMPEG=/chemin/vers/ffmpeg"
        )


def _diagnose(stderr: str) -> str:
    """Extrait les lignes utiles d'un échec ffmpeg (pour un humain ou un agent IA)."""
    lines = [l.strip() for l in (stderr or "").splitlines() if l.strip()]
    keys = ("error", "invalid", "no such", "not found", "unable", "failed", "cannot",
            "unknown", "does not", "too many", "out of", "permission")
    useful = [l for l in lines if any(k in l.lower() for k in keys)]
    pick = (useful[-6:] if useful else []) + [l for l in lines[-4:] if l not in useful[-6:]]
    return "\n".join(pick)[-1500:] or "(aucun message ffmpeg)"


def run(args: list, capture: bool = False, echo: bool = True, quiet_ok: bool = False) -> subprocess.CompletedProcess:
    """Exécute ffmpeg avec les arguments donnés (liste, sans shell).

    En cas d'échec, lève SystemExit avec un diagnostic lisible (pas un simple
    code retour) : c'est ce message qu'un agent pilote reçoit pour corriger.
    Délai maximal : MD_FFMPEG_TIMEOUT secondes (défaut 1800).
    """
    cmd = [ffmpeg_exe(), "-hide_banner", "-y", "-nostdin"] + [str(a) for a in args]
    if echo:
        printable = " ".join(shlex.quote(c) for c in cmd)
        print(f"» ffmpeg … ({len(printable)} caractères de commande)")
        if os.environ.get("MD_VERBOSE"):
            print(printable)
    timeout = float(os.environ.get("MD_FFMPEG_TIMEOUT", "1800"))
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        raise SystemExit(f"ERREUR ffmpeg : délai dépassé ({timeout:.0f}s, MD_FFMPEG_TIMEOUT)") from exc
    if r.returncode != 0:
        tail = (r.stderr or "")[-3500:]
        if os.environ.get("MD_VERBOSE"):
            sys.stderr.write("\n── ffmpeg a échoué ──\n")
            sys.stderr.write(" ".join(shlex.quote(c) for c in cmd) + "\n\n")
            sys.stderr.write(tail + "\n")
        raise SystemExit(f"ERREUR ffmpeg (code {r.returncode}) :\n{_diagnose(r.stderr)}")
    return r


def dry_run(args: list) -> None:
    cmd = [ffmpeg_exe(), "-hide_banner", "-y"] + [str(a) for a in args]
    print(" ".join(shlex.quote(c) for c in cmd))


def version() -> str:
    try:
        out = subprocess.run([ffmpeg_exe(), "-version"], capture_output=True, text=True)
        return out.stdout.splitlines()[0] if out.stdout else "?"
    except SystemExit:
        return "absent"
