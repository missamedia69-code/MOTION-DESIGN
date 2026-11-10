"""CLI du moteur MOTION-DESIGN.

Usage : ./md <commande> [options]
Commandes : doctor, new, render, lint, apercu, ad, brands, cockpit, vo, lab, list, info, inventory, install, fonts, presets, preview, clean
"""
from __future__ import annotations

import argparse
import json
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
    try:
        import numpy
        print(f"numpy       : {numpy.__version__} (dégradés)")
    except ImportError:
        print("numpy       : ABSENT → pip3 install numpy (dégradés)"); ok = False
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
    from engine import brand, render
    print(f"Moteur      : v{render.ENGINE_VERSION} · {len(render.ANIMS)} entrées · "
          f"{len(render.EXITS)} sorties · {len(render.IDLES)} idle · kits : "
          f"{', '.join(b['name'] for b in brand.list_brands()) or 'aucun'}")
    if ok and getattr(_args, "full", False):
        import contextlib
        import io
        import time
        t0 = time.time()
        proj = {"canvas": {"width": 320, "height": 180, "fps": 15}, "scenes": [
            {"duration": 1, "background": {"gradient": ["#0B1020", "#3b1d7a"]}, "layers": [
                {"type": "text", "text": "Auto test", "split": "word", "size": 28, "anim": "fade_up"},
                {"type": "shape", "kind": "rect", "w": 200, "h": 6, "pos": ["50%", "75%"],
                 "anim": "grow_x", "color": "#FFD400"}]},
            {"duration": 1, "background": "#0B1020", "layers": [
                {"type": "counter", "to": 100, "size": 40, "anim": "punch", "count_duration": 0.6}]}]}
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                out = render.render_project_data(proj, REPO, "doctor-selftest",
                                                 out_path=os.path.join(REPO, ".cache", "doctor.mp4"))
            print(f"Rendu test  : OK ({time.time() - t0:.1f}s) → {os.path.relpath(out, REPO)}")
        except SystemExit as exc:
            ok = False
            print(f"Rendu test  : ÉCHEC\n{exc}")
        finally:
            shutil.rmtree(os.path.join(REPO, ".cache", "doctor-selftest"), ignore_errors=True)
    print("\n" + ("✅ Moteur opérationnel." if ok else "⚠️  Des dépendances manquent."))
    sys.exit(0 if ok else 1)


def cmd_new(args) -> None:
    from engine import project
    project.new(args.name, canvas_preset=args.canvas, template=args.template)


def cmd_render(args) -> None:
    from engine import render
    formats = [f.strip() for f in args.formats.split(",") if f.strip()] if args.formats else None
    render.render_project(args.name, export_name=args.preset, out_path=args.out,
                          dry_run=args.dry_run, fps_override=args.fps,
                          formats=formats, draft=args.draft)


def cmd_lint(args) -> None:
    from engine import lint, project
    proj, pdir = project.load(args.name)
    rep = lint.lint(proj, pdir, args.canvas)
    if args.json:
        print(json.dumps(rep, ensure_ascii=False, indent=2))
    else:
        print(lint.format_report(rep))
    sys.exit(0 if rep["ok"] else 1)


def cmd_apercu(args) -> None:
    from engine import frames, project
    proj, pdir = project.load(args.name)
    at = [float(t) for t in args.at.split(",")] if args.at else None
    res = frames.preview(proj, pdir, args.name, at=at, count=args.count,
                         canvas_override=args.canvas, draft=not args.final)
    print(json.dumps(res, ensure_ascii=False, indent=2))


def cmd_ad(args) -> None:
    from engine import ads, frames, lint, project, render
    if args.example:
        print(json.dumps(ads.example(), ensure_ascii=False, indent=2))
        return
    if args.templates:
        print(json.dumps(ads.templates(), ensure_ascii=False, indent=2))
        return
    if not args.brief:
        raise SystemExit("ERREUR : fournir un brief JSON (./md ad brief.json) ou --example")
    with open(args.brief, encoding="utf-8") as f:
        brief = json.load(f)
    proj = ads.compose(brief)
    name = project.slugify(args.name or proj["name"])
    pdir = REPO
    if args.save:
        pj = project.save(name, proj)
        pdir = os.path.dirname(pj)
        print(f"💾 Projet enregistré : {os.path.relpath(pj, REPO)}")
    rep = lint.lint(proj, pdir)
    print(lint.format_report(rep))
    if not rep["ok"]:
        sys.exit(1)
    if args.preview:
        print(json.dumps(frames.preview(proj, pdir, name), ensure_ascii=False, indent=2))
    if args.render:
        formats = [f.strip() for f in args.formats.split(",")] if args.formats else [None]
        for fmt in formats:
            p_fmt = ads.compose(brief, canvas=fmt) if fmt else proj
            render.render_project_data(p_fmt, pdir, name, export_name=args.preset,
                                       canvas_override=fmt, draft=args.draft)
    elif not args.save and not args.preview:
        print(json.dumps(proj, ensure_ascii=False, indent=2))


def cmd_entrees(args) -> None:
    from engine import intake
    rep = intake.scan(args.dossier)
    if args.install or args.brand:
        rep["installation"] = intake.install(rep, args.brand)
    if args.json:
        print(json.dumps(rep, ensure_ascii=False, indent=2))
        return
    print(f"── Réception : {rep['dossier']} ──")
    a = rep.get("audio")
    if a:
        print(f"🎧 Audio complet : {a['file']} · {a['duration_s']}s · "
              f"{len(a['breaths'])} respirations (points de coupe)")
        for seg in a.get("script") or []:
            print(f"    {seg['start']:>6.2f}–{seg['end']:<6.2f} {seg['text']}")
    for lg in rep.get("logos", []):
        print(f"🏷  Logo : {lg['file']} · accent suggéré {lg['palette'].get('accent')}")
    for d in rep.get("details", []):
        print(f"📝 Détails : {d['file']} ({len(d['content'])} caractères)")
    for m in rep.get("medias", []):
        extra = f" · {m['duration_s']}s" if m.get("duration_s") else ""
        print(f"🖼  {m['kind']} : {m['file']} · {m.get('width')}x{m.get('height')} {m.get('orientation', '')}{extra}")
    if rep.get("manquants"):
        print("⚠  Manquant : " + ", ".join(rep["manquants"]))
    if rep.get("installation"):
        inst = rep["installation"]
        print(f"📦 Copiés dans assets/ : {len(inst['copies'])}" +
              (f" · kit de marque : {inst['brand']}" if inst.get("brand") else ""))
    print("\nBrief squelette (à compléter avec les détails texte) :")
    print(json.dumps(rep["brief_squelette"], ensure_ascii=False, indent=2))


def cmd_brands(_args) -> None:
    from engine import brand
    for b in brand.list_brands():
        if "error" in b:
            print(f"{b['name']:<14} ⚠ {b['error']}")
            continue
        cols = " ".join(f"{k}={v}" for k, v in b["colors"].items())
        print(f"{b['name']:<14} {b['title']}\n{'':<14} {cols}\n{'':<14} logo={b.get('logo')}")


def cmd_cockpit(args) -> None:
    from engine import cockpit
    if args.guide:
        print(cockpit.guide())
    else:
        print(json.dumps(cockpit.capabilities(), ensure_ascii=False, indent=2))


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


def cmd_elements(args) -> None:
    import json as _json
    from engine import elements
    act = args.action
    if act == "sources":
        print(_json.dumps(elements.sources(), ensure_ascii=False, indent=2))
    elif act == "kits":
        for k, v in elements.KITS.items():
            print(f"{k:16s} {len(v):3d} éléments : " + ", ".join(i.split(':', 1)[1] for i in v))
    elif act == "chercher":
        r = elements.search(args.mots, style=args.style, source=args.source, limit=args.max)
        print(f"Termes : {', '.join(r['termes'])} — {r['total']} résultat(s)")
        for x in r["resultats"]:
            print(f"  {x.get('apercu', ' '):2s} {x['id']:48s} {x['style']:8s} {x['licence']}")
        for k, v in r.get("erreurs", {}).items():
            print(f"⚠️  {k} : {v}")
    elif act in ("prendre", "kit"):
        if act == "kit":
            r = elements.kit(args.mots[0], dest=args.vers, color=args.couleur, png=args.png)
        else:
            r = elements.get(args.mots, dest=args.vers, color=args.couleur, size=args.taille, png=args.png)
        for f in r["recuperes"]:
            print(f"✅ {f}")
        for k, v in r["erreurs"].items():
            print(f"❌ {k} : {v}")
        print(f"Licences : {r['licences']}")
    elif act == "planche":
        print(elements.sheet(args.vers))
    elif act == "vider-cache":
        elements.clear_cache(); print("cache des éléments vidé")


def cmd_fonts(_args) -> None:
    try:
        import numpy
        print(f"numpy       : {numpy.__version__} (dégradés)")
    except ImportError:
        print("numpy       : ABSENT → pip3 install numpy (dégradés)"); ok = False
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

    p = sub.add_parser("doctor", help="diagnostic du moteur")
    p.add_argument("--full", action="store_true", help="inclut un rendu d'essai complet")
    p.set_defaults(fn=cmd_doctor)

    p = sub.add_parser("new", help="créer un projet")
    p.add_argument("name")
    p.add_argument("--canvas", default="16x9", help="format : 16x9|9x16|1x1|4x5|21x9|720p|1.91x1|2x3|4k")
    p.add_argument("--template", default="base")
    p.set_defaults(fn=cmd_new)

    p = sub.add_parser("render", help="rendre un projet (livrable livré en artefact)")
    p.add_argument("name")
    p.add_argument("--preset", help="mp4-hq|mp4-social|mp4-web|mp4-h265|mp4-draft|gif|webm-vp9|mov-alpha")
    p.add_argument("--out", help="chemin de sortie personnalisé")
    p.add_argument("--fps", type=float)
    p.add_argument("--dry-run", action="store_true", help="afficher la commande sans exécuter")
    p.add_argument("--formats", help="décliner en plusieurs formats : 9x16,1x1,16x9")
    p.add_argument("--draft", action="store_true", help="brouillon rapide (15 i/s, ultrafast)")
    p.set_defaults(fn=cmd_render)

    p = sub.add_parser("lint", help="contrôle qualité avant rendu (erreurs, lisibilité, zones sûres)")
    p.add_argument("name")
    p.add_argument("--canvas", help="contrôler pour un autre format (ex. 9x16)")
    p.add_argument("--json", action="store_true")
    p.set_defaults(fn=cmd_lint)

    p = sub.add_parser("apercu", help="brouillon + images clés + planche contact")
    p.add_argument("name")
    p.add_argument("--at", help="instants en secondes : 0.5,2,4.2")
    p.add_argument("--count", type=int, default=6, help="nombre d'images (si pas de --at)")
    p.add_argument("--canvas", help="format à prévisualiser")
    p.add_argument("--final", action="store_true", help="qualité finale au lieu du brouillon")
    p.set_defaults(fn=cmd_apercu)

    p = sub.add_parser("ad", help="pub depuis un brief (accroche, produit, offre, CTA…)")
    p.add_argument("brief", nargs="?", help="brief JSON")
    p.add_argument("--example", action="store_true", help="afficher un brief d'exemple")
    p.add_argument("--templates", action="store_true", help="lister les templates pub")
    p.add_argument("--name", help="nom du projet")
    p.add_argument("--save", action="store_true", help="enregistrer dans projects/<nom>/")
    p.add_argument("--preview", action="store_true", help="planche contact du brouillon")
    p.add_argument("--render", action="store_true", help="rendre la vidéo")
    p.add_argument("--formats", help="9x16,1x1,16x9")
    p.add_argument("--preset", help="export (défaut : celui du brief, mp4-social)")
    p.add_argument("--draft", action="store_true")
    p.set_defaults(fn=cmd_ad)

    p = sub.add_parser("entrees", help="réception des éléments d'une pub (audio, logos, détails, médias)")
    p.add_argument("dossier", nargs="?", help="dossier (défaut entrees/)")
    p.add_argument("--install", action="store_true", help="copier les éléments dans assets/")
    p.add_argument("--brand", help="créer brands/<nom>.json d'après le logo (implique --install)")
    p.add_argument("--json", action="store_true")
    p.set_defaults(fn=cmd_entrees)

    sub.add_parser("brands", help="kits de marque disponibles").set_defaults(fn=cmd_brands)

    p = sub.add_parser("cockpit", help="capacités complètes du moteur (JSON pour agent IA)")
    p.add_argument("--guide", action="store_true", help="afficher le manuel du pilote")
    p.set_defaults(fn=cmd_cockpit)

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

    p = sub.add_parser("elements", help="éléments graphiques libres de droits (emojis 3D, icônes) + licences")
    p.add_argument("action", choices=["sources", "kits", "chercher", "prendre", "kit", "planche", "vider-cache"])
    p.add_argument("mots", nargs="*", help="mots à chercher (fr/en), ids source:nom, ou nom du kit")
    p.add_argument("--style", choices=["3d", "couleur", "plat", "ligne", "plein"])
    p.add_argument("--source", help="limiter à une source (voir : elements sources)")
    p.add_argument("--max", type=int, default=24, help="nombre de résultats")
    p.add_argument("--vers", help="dossier de destination (défaut assets/elements/)")
    p.add_argument("--couleur", help="couleur des icônes ligne/plein, ex. #3dff6e")
    p.add_argument("--taille", type=int, default=512, help="taille en px des SVG/PNG d'icônes")
    p.add_argument("--png", action="store_true", help="convertir aussi les SVG en PNG transparents")
    p.set_defaults(fn=cmd_elements)

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
