"""CLI du moteur MOTION-DESIGN.

Usage : ./md <commande> [options]
Commandes : doctor, new, render, vo, lab, list, info, inventory, install, fonts, presets, preview, clean
"""
from __future__ import annotations

import argparse
import os
import shutil
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)


def cmd_doctor(_args) -> None:
    from engine import ffmpeg, presets
    print("── MOTION-DESIGN · diagnostic moteur ──\n")
    ok = True
    print(f"ffmpeg      : {ffmpeg.version()}")
    try:
        import imageio_ffmpeg  # noqa: F401
        print("imageio-ffmpeg : OK")
    except ImportError:
        print("imageio-ffmpeg : absent (facultatif si ffmpeg système)")
    try:
        import av
        print(f"PyAV        : {av.__version__}")
    except ImportError:
        print("PyAV        : ABSENT → pip3 install av"); ok = False
    try:
        import PIL
        print(f"Pillow      : {PIL.__version__}")
    except ImportError:
        print("Pillow      : ABSENT → pip3 install pillow"); ok = False
    from engine import text as text_mod
    fonts = text_mod.list_fonts()
    print(f"Polices     : {len(fonts)} disponibles")
    from shutil import which
    print(f"ImageMagick : {'OK (SVG→PNG)' if which('convert') else 'absent (SVG non convertis)'}")
    presets_list = ", ".join(presets.EXPORT_PRESETS)
    print(f"Exports     : {presets_list}")
    print(f"Formats     : {', '.join(presets.CANVAS_PRESETS)}")
    # test d'écriture (plus de dossier output/ : livrables dans .cache/rendus/)
    for d in (".cache/rendus", "projects", "assets"):
        p = os.path.join(REPO, d)
        probe_dir = p
        while not os.path.isdir(probe_dir) and probe_dir != REPO:
            probe_dir = os.path.dirname(probe_dir)
        writable = os.access(probe_dir, os.W_OK)
        if not writable:
            ok = False
        print(f"Dossier {d:<14}: {'OK' if writable else 'NON ACCESSIBLE'}")
    print("\n" + ("✅ Moteur opérationnel." if ok else "⚠️  Des dépendances manquent."))
    sys.exit(0 if ok else 1)


def cmd_new(args) -> None:
    from engine import project
    project.new(args.name, canvas_preset=args.canvas, template=args.template)


def cmd_render(args) -> None:
    from engine import render
    render.render_project(args.name, export_name=args.preset, out_path=args.out,
                          dry_run=args.dry_run, fps_override=args.fps)


def cmd_vo(args) -> None:
    from engine import voice
    voice.generate(args)


def cmd_lab(args) -> None:
    from lab import cli as lab_cli
    lab_cli.main(args)


def cmd_list(_args) -> None:
    from engine import project
    projs = project.list_projects()
    if not projs:
        print("Aucun projet. Créez-en un : ./md new <nom> --canvas 9x16")
        return
    print(f"{'PROJET':<28} {'CANVAS':<8} TITRE")
    for p in projs:
        print(f"{p['name']:<28} {str(p['canvas']):<8} {p['title']}")


def cmd_info(args) -> None:
    from engine import probe
    info = probe.probe(args.file)
    for k, v in info.items():
        print(f"{k:<12}: {v}")


def cmd_inventory(_args) -> None:
    from engine import inventory
    inventory.print_inventory()
    inventory.write_inventory()


def cmd_install(args) -> None:
    from engine import install
    install.install(args.sources)


def cmd_fonts(_args) -> None:
    from engine import text as text_mod
    fonts = text_mod.list_fonts()
    if not fonts:
        print("Aucune police. Installez-en : ./md install MaPolice.ttf")
        return
    for f in fonts:
        print(f"{f['file']:<42} ({f['source']})")


def cmd_presets(_args) -> None:
    from engine import presets
    print("── Formats (canvas) ──")
    for k, v in presets.CANVAS_PRESETS.items():
        print(f"{k:<8} {v['width']}×{v['height']}@{v['fps']}  — {v['label']}")
    print("\n── Exports ──")
    for k, v in presets.EXPORT_PRESETS.items():
        print(f"{k:<10} {v['label']}")
    print("\n── Transitions (xfade) ──")
    print(", ".join(presets.XFADE_TRANSITIONS))


def cmd_preview(args) -> None:
    from engine import serve
    serve.serve(args.port)


def cmd_clean(args) -> None:
    cache = os.path.join(REPO, ".cache", args.name)
    if os.path.isdir(cache):
        shutil.rmtree(cache)
        print(f"🧹 Intermédiaires supprimés : .cache/{args.name}/")
    else:
        print(f"Rien à nettoyer pour '{args.name}'.")


def main() -> None:
    ap = argparse.ArgumentParser(prog="md", description="Moteur de montage MOTION-DESIGN")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("doctor", help="diagnostic du moteur").set_defaults(fn=cmd_doctor)

    p = sub.add_parser("new", help="créer un projet")
    p.add_argument("name")
    p.add_argument("--canvas", default="16x9", help="format : 16x9|9x16|1x1|4x5|21x9|720p")
    p.add_argument("--template", default="base")
    p.set_defaults(fn=cmd_new)

    p = sub.add_parser("render", help="rendre un projet (livrable livré en artefact)")
    p.add_argument("name")
    p.add_argument("--preset", help="mp4-hq|mp4-web|mp4-h265|gif|webm-vp9|mov-alpha")
    p.add_argument("--out", help="chemin de sortie personnalisé")
    p.add_argument("--fps", type=float)
    p.add_argument("--dry-run", action="store_true", help="afficher la commande sans exécuter")
    p.set_defaults(fn=cmd_render)

    p = sub.add_parser("vo", help="générer les voix off d'un projet (TTS)")
    p.add_argument("name", help="nom du projet")
    p.add_argument("--script", help="manifeste vo.json (défaut : projects/<nom>/vo.json)")
    p.add_argument("--backend", choices=("edge-tts", "voxcpm"), help="moteur TTS")
    p.add_argument("--voice", help="voix (ex. fr-FR-HenriNeural, ou fichier de référence VoxCPM)")
    p.add_argument("--rate", help="edge-tts : ex. -5%% ou +10%%")
    p.add_argument("--model", help="VoxCPM : identifiant HuggingFace ou chemin local")
    p.add_argument("--out-dir", help="dossier de sortie (relatif au dépôt)")
    p.add_argument("--dry-run", action="store_true", help="afficher les commandes sans rien exécuter")
    p.add_argument("--force", action="store_true", help="régénérer les clips déjà présents")
    p.add_argument("--from-captions", action="store_true", help="lire les captions de index.html")
    p.add_argument("--write-script", action="store_true", help="écrire vo.json depuis les captions")
    p.add_argument("--mix", action="store_true", help="afficher les adelay ffmpeg dérivés du manifeste")
    p.add_argument("--check-mix", metavar="FICHIER", help="comparer les starts au script de mixage")
    p.set_defaults(fn=cmd_vo)

    p = sub.add_parser("lab", help="laboratoire : données en entrée → vidéo en sortie")
    p.add_argument("action", nargs="?", default="serve",
                   choices=("serve", "mcp", "run", "demo", "schema", "example",
                            "instruments", "runs", "status"),
                   help="serve=paillasse HTTP, mcp=connexion IA, run=une expérience")
    p.add_argument("--input", help="fichier spec.json (run)")
    p.add_argument("--id", help="id d'expérience (status)")
    p.add_argument("--host", default="0.0.0.0")
    p.add_argument("--port", type=int, default=8080)
    p.add_argument("--limit", type=int, default=30)
    p.add_argument("--dry-run", action="store_true", help="valider le montage sans rendre")
    p.set_defaults(fn=cmd_lab)

    sub.add_parser("list", help="liste des projets").set_defaults(fn=cmd_list)

    p = sub.add_parser("info", help="analyser un média")
    p.add_argument("file")
    p.set_defaults(fn=cmd_info)

    sub.add_parser("inventory", help="inventaire de assets/").set_defaults(fn=cmd_inventory)

    p = sub.add_parser("install", help="installer des éléments dans assets/")
    p.add_argument("sources", nargs="+", help="fichiers, dossiers ou URLs")
    p.set_defaults(fn=cmd_install)

    sub.add_parser("fonts", help="liste des polices").set_defaults(fn=cmd_fonts)
    sub.add_parser("presets", help="liste des presets").set_defaults(fn=cmd_presets)

    p = sub.add_parser("preview", help="serveur de prévisualisation des sorties")
    p.add_argument("--port", type=int, default=8080)
    p.set_defaults(fn=cmd_preview)

    p = sub.add_parser("clean", help="supprimer les intermédiaires d'un projet")
    p.add_argument("name")
    p.set_defaults(fn=cmd_clean)

    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
