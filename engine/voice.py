"""Génération des voix off (TTS) d'un projet MOTION-DESIGN.

Le montage reste déclaratif : les segments de VO vivent dans
``projects/<nom>/vo.json`` (id, texte, instant de placement). Deux backends :

* ``edge-tts``  — voix neuronales Microsoft Edge (service **en ligne**) ;
* ``voxcpm``    — VoxCPM2 local (modèle HuggingFace, non disponible dans le sandbox).

``--dry-run`` n'exécute rien, ne télécharge rien et ne crée aucun dossier : il
affiche les commandes exactes, ce qui permet de valider la chaîne hors ligne.

Voir docs/VOIX-TTS.md.
"""
from __future__ import annotations

import html
import importlib.util
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
from html.parser import HTMLParser

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECTS_DIR = os.path.join(REPO, "projects")

BACKENDS = ("edge-tts", "voxcpm")
DEFAULT_VOICE = "fr-FR-HenriNeural"
DEFAULT_BACKEND = "edge-tts"
DEFAULT_FORMAT = "mp3"
VALID_FORMATS = ("mp3", "wav")
ID_RE = re.compile(r"^[A-Za-z0-9_-]+$")
ADELAY_RE = re.compile(r"adelay=(\d+)\|\d+")


class _CaptionParser(HTMLParser):
    """Extrait les <div class="cap ..."> d'une composition HyperFrames."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.segments: list[dict] = []
        self._current: dict | None = None
        self._buf: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "div":
            return
        a = {k: (v or "") for k, v in attrs}
        if "cap" in a.get("class", "").split():
            self._current = {"start": float(a.get("data-start", 0) or 0)}
            self._buf = []

    def handle_data(self, data: str) -> None:
        if self._current is not None:
            self._buf.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "div" and self._current is not None:
            text = re.sub(r"\s+", " ", html.unescape("".join(self._buf))).strip()
            self._current["text"] = text
            self.segments.append(self._current)
            self._current = None


def parse_captions(path: str) -> list[dict]:
    """Lit les captions d'un index.html et retourne les segments s1..sN."""
    with open(path, encoding="utf-8") as f:
        parser = _CaptionParser()
        parser.feed(f.read())
    out = []
    for i, seg in enumerate(parser.segments, 1):
        if seg.get("text"):
            out.append({"id": f"s{i}", "start": round(float(seg["start"]), 3),
                        "text": seg["text"]})
    return out


def validate_script(data: dict) -> None:
    """Valide un manifeste vo.json (lève SystemExit avec un message clair)."""
    def fail(msg: str) -> None:
        raise SystemExit(f"ERREUR de validation vo.json : {msg}")

    segments = data.get("segments")
    if not isinstance(segments, list) or not segments:
        fail("'segments' doit être une liste non vide")

    seen: set[str] = set()
    for i, seg in enumerate(segments, 1):
        if not isinstance(seg, dict):
            fail(f"segment {i} : objet attendu")
        sid = str(seg.get("id", ""))
        if not ID_RE.match(sid):
            fail(f"segment {i} : id '{sid}' invalide (lettres, chiffres, -, _)")
        if sid in seen:
            fail(f"id en doublon : '{sid}'")
        seen.add(sid)
        if not str(seg.get("text", "")).strip():
            fail(f"segment '{sid}' : texte vide")
        try:
            start = float(seg.get("start", 0))
        except (TypeError, ValueError):
            fail(f"segment '{sid}' : 'start' doit être un nombre")
        if start < 0:
            fail(f"segment '{sid}' : 'start' négatif")

    backend = data.get("backend", DEFAULT_BACKEND)
    if backend not in BACKENDS:
        fail(f"backend '{backend}' inconnu ({', '.join(BACKENDS)})")
    fmt = data.get("format", DEFAULT_FORMAT)
    if fmt not in VALID_FORMATS:
        fail(f"format '{fmt}' inconnu ({', '.join(VALID_FORMATS)})")
    out_dir = data.get("out_dir", "")
    if not out_dir or os.path.isabs(out_dir) or ".." in out_dir.split(os.sep):
        fail("'out_dir' doit être un chemin relatif au dépôt, sans '..'")


def load_script(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    validate_script(data)
    return data


def script_from_captions(project: str, index_html: str, backend: str = DEFAULT_BACKEND,
                         voice: str = DEFAULT_VOICE, out_dir: str = ".cache/vo9") -> dict:
    return {
        "project": project,
        "backend": backend,
        "voice": voice,
        "out_dir": out_dir,
        "format": DEFAULT_FORMAT,
        "segments": parse_captions(index_html),
        "note": "Textes extraits des captions de index.html ; ajuster 'start' selon le mix ffmpeg.",
    }


def resolve_out_dir(out_dir: str) -> str:
    return out_dir if os.path.isabs(out_dir) else os.path.join(REPO, out_dir)


def build_command(segment: dict, out_path: str, backend: str, voice: str,
                  rate: str = "", model: str = "") -> list[str]:
    """Construit une commande (argv, sans shell) pour un segment."""
    text = str(segment["text"]).strip()
    if backend == "edge-tts":
        # edge-tts écrit du MP3 par défaut ; --format n'existe pas dans son CLI.
        cmd = ["edge-tts", "--voice", voice, "--text", text,
               "--write-media", out_path]
        if rate:
            # Forme --opt=valeur obligatoire : une valeur négative (-4%) serait
            # sinon interprétée comme une option par argparse.
            cmd += [f"--rate={rate}"]
        return cmd
    if backend == "voxcpm":
        cmd = [sys.executable, os.path.join(REPO, "engine", "voxcpm_cli.py"),
               "--text", text, "--out", out_path]
        if model:
            cmd += ["--model", model]
        if voice and not voice.startswith("fr-"):
            cmd += ["--reference", voice]
        return cmd
    raise SystemExit(f"ERREUR : backend '{backend}' inconnu ({', '.join(BACKENDS)})")


NETWORK_MARKERS = (
    "clientconnector", "cannot connect", "dns", "aiohttp", "socket.gaierror",
    "wsclient", "wsserverhandshake", "connectionrefused", "timed out",
    "timeouterror", "proxyerror", "ssl", "network is unreachable",
)


def diagnose(backend: str, tail: str) -> str:
    """Transforme une erreur de backend en consigne actionnable."""
    low = tail.lower()
    if any(marker in low for marker in NETWORK_MARKERS):
        if backend == "edge-tts":
            return ("→ Le service Microsoft Edge TTS est injoignable depuis cet environnement.\n"
                    "  Lancez `./md vo` sur un poste avec Internet, ou utilisez l'outil\n"
                    "  vocal intégré à l'agent (docs/VOIX-TTS.md §2 et §4).")
        return ("→ Téléchargement/accès réseau impossible (modèle HuggingFace).\n"
                "  Pré-installez le modèle sur un poste connecté, puis relancez ici.")
    if "no such file" in low or "not found" in low:
        return "→ Binaire, paquet ou modèle introuvable : vérifiez l'installation du backend."
    return "→ Vérifiez le backend, la voix et le modèle (docs/VOIX-TTS.md)."


def check_backend(backend: str) -> None:
    """Pré-vérification (ignorée en --dry-run)."""
    if backend == "edge-tts":
        if shutil.which("edge-tts") is None:
            raise SystemExit(
                "ERREUR : edge-tts absent.\n"
                "  → pip3 install edge-tts\n"
                "  → attention : le service Microsoft Edge est en ligne et n'est PAS\n"
                "    joignable depuis le sandbox de ce dépôt (voir docs/VOIX-TTS.md)."
            )
    elif backend == "voxcpm":
        if importlib.util.find_spec("voxcpm") is None:
            raise SystemExit(
                "ERREUR : le paquet 'voxcpm' est absent.\n"
                "  → pip3 install voxcpm  (sur un poste avec accès HuggingFace)\n"
                "  → le modèle VoxCPM2 (huggingface.co/openbmb/VoxCPM2) n'est pas\n"
                "    téléchargeable depuis le sandbox (voir docs/VOIX-TTS.md)."
            )


def mix_delays_from_text(source: str) -> list[float]:
    """Extrait les adelay=ms|ms d'une chaîne (commandes ffmpeg)."""
    return [int(m) / 1000 for m in ADELAY_RE.findall(source)]


def mix_delays(path: str) -> list[float]:
    """Extrait les adelay=ms|ms d'un script de mixage ffmpeg."""
    with open(path, encoding="utf-8") as f:
        return mix_delays_from_text(f.read())


def check_mix(segments: list[dict], mix_path: str) -> None:
    """Compare les 'start' du manifeste aux adelay du mix (alerte simple)."""
    delays = mix_delays(mix_path)
    if not delays:
        print(f"  ⚠ Aucun adelay trouvé dans {mix_path}")
        return
    n = min(len(delays), len(segments))
    drift = 0
    for i in range(n):
        start = float(segments[i].get("start", 0))
        if abs(start - delays[i]) > 0.05:
            drift += 1
            print(f"  ⚠ {segments[i]['id']} : manifeste {start:.2f}s / mix {delays[i]:.2f}s")
    if drift == 0:
        print(f"  ✅ {n} décalages cohérents avec {mix_path}")
    else:
        print(f"  → {drift} écart(s) : ajuster 'start' dans vo.json ou le mix.")


def print_mix_hints(segments: list[dict], out_dir: str, fmt: str) -> None:
    print("── Adelay ffmpeg dérivés de vo.json ──")
    for seg in segments:
        ms = int(round(float(seg.get("start", 0)) * 1000))
        path = os.path.join(out_dir, f"{seg['id']}.{fmt}")
        print(f"[{seg['id']}] adelay={ms}|{ms}  ← {path}")


def generate(args) -> None:
    """Point d'entrée de `./md vo`."""
    from engine import project

    pdir = project.project_dir(args.name)
    if not os.path.isdir(pdir):
        raise SystemExit(f"ERREUR : projet '{args.name}' introuvable ({pdir}).")

    script_path = args.script or os.path.join(pdir, "vo.json")
    index_html = os.path.join(pdir, "index.html")

    if args.from_captions:
        if not os.path.isfile(index_html):
            raise SystemExit(f"ERREUR : {index_html} introuvable (--from-captions).")
        data = script_from_captions(args.name, index_html)
        print(f"→ {len(data['segments'])} captions extraites de {os.path.relpath(index_html, REPO)}")
        if args.write_script:
            with open(script_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                f.write("\n")
            print(f"✅ Manifeste écrit : {os.path.relpath(script_path, REPO)}")
    else:
        if not os.path.isfile(script_path):
            raise SystemExit(
                f"ERREUR : {os.path.relpath(script_path, REPO)} absent.\n"
                f"  → ./md vo {args.name} --from-captions --write-script"
            )
        data = load_script(script_path)

    backend = args.backend or data.get("backend", DEFAULT_BACKEND)
    voice = args.voice or data.get("voice", DEFAULT_VOICE)
    rate = args.rate or data.get("rate", "")
    model = args.model or data.get("model_path", "")
    fmt = data.get("format", DEFAULT_FORMAT)
    out_dir = args.out_dir or data.get("out_dir", ".cache/vo9")
    abs_out = resolve_out_dir(out_dir)
    segments = data["segments"]

    commands = [
        (seg, build_command(seg, os.path.join(out_dir, f"{seg['id']}.{fmt}"),
                            backend, voice, rate, model))
        for seg in segments
    ]

    if args.mix:
        print_mix_hints(segments, out_dir, fmt)
        return

    if args.check_mix:
        mix_path = args.check_mix if os.path.isabs(args.check_mix) else os.path.join(pdir, args.check_mix)
        print(f"── Contrôle du mix : {os.path.relpath(mix_path, REPO)} ──")
        check_mix(segments, mix_path)
        return

    print(f"── VO : {len(segments)} segments · backend {backend} · voix {voice} ──")
    print(f"   sortie : {out_dir}/<id>.{fmt}\n")

    if args.dry_run:
        print("(dry-run : aucune commande exécutée, aucun fichier créé)\n")
        for seg, cmd in commands:
            print(f"[{seg['id']}] t={float(seg.get('start', 0)):.2f}s  {shlex.join(cmd)}")
        print("\nPré-requis hors dry-run :")
        print("  edge-tts → pip3 install edge-tts + accès au service Microsoft (hors sandbox)")
        print("  voxcpm   → pip3 install voxcpm + modèle HuggingFace (hors sandbox)")
        return

    check_backend(backend)
    os.makedirs(abs_out, exist_ok=True)
    done, skipped, total_bytes = 0, 0, 0
    for seg, cmd in commands:
        out_path = os.path.join(abs_out, f"{seg['id']}.{fmt}")
        if os.path.isfile(out_path) and os.path.getsize(out_path) > 0 and not args.force:
            print(f"  ⏭  {seg['id']} : déjà présent (--force pour régénérer)")
            skipped += 1
            total_bytes += os.path.getsize(out_path)
            continue
        # Chemins absolus à l'exécution (le dry-run affiche des chemins relatifs lisibles)
        real_cmd = [c if c != os.path.join(out_dir, f"{seg['id']}.{fmt}") else out_path for c in cmd]
        try:
            r = subprocess.run(real_cmd, capture_output=True, text=True, timeout=90)
        except subprocess.TimeoutExpired:
            raise SystemExit(
                f"ERREUR : le backend a expiré sur '{seg['id']}' (90 s).\n"
                "  → service en ligne injoignable ou modèle trop lent ; voir docs/VOIX-TTS.md"
            )
        if r.returncode != 0:
            tail = (r.stderr or r.stdout or "").strip()[-1200:]
            raise SystemExit(
                f"ERREUR : échec sur le segment '{seg['id']}' (backend {backend}).\n"
                f"{diagnose(backend, tail)}\n\n"
                f"── Détail technique ──\n{tail}"
            )
        size = os.path.getsize(out_path) if os.path.isfile(out_path) else 0
        total_bytes += size
        done += 1
        print(f"  ✅ {seg['id']}.{fmt}  ({size / 1024:.0f} Ko)  t={float(seg.get('start', 0)):.2f}s")

    print(f"\n✅ {done} clip(s) généré(s), {skipped} ignoré(s), {total_bytes / 1024:.0f} Ko au total.")
    print(f"   → {out_dir}/  ·  mixer ensuite avec le script ffmpeg du projet.")
