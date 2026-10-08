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


def run(args: list, capture: bool = False, echo: bool = True, quiet_ok: bool = False) -> subprocess.CompletedProcess:
    """Exécute ffmpeg avec les arguments donnés (liste, sans shell)."""
    cmd = [ffmpeg_exe(), "-hide_banner", "-y"] + [str(a) for a in args]
    if echo:
        printable = " ".join(shlex.quote(c) for c in cmd)
        print(f"» ffmpeg … ({len(printable)} caractères de commande)")
        if os.environ.get("MD_VERBOSE"):
            print(printable)
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        tail = (r.stderr or "")[-3500:]
        sys.stderr.write("\n── ffmpeg a échoué ──\n")
        if os.environ.get("MD_VERBOSE"):
            sys.stderr.write(" ".join(shlex.quote(c) for c in cmd) + "\n\n")
        sys.stderr.write(tail + "\n")
        raise SystemExit(1)
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
