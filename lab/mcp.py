"""Serveur MCP stdio : une IA se connecte au labo comme un laborantin.

Protocole JSON-RPC 2.0 sur stdin/stdout, sans dépendance externe. Un client
MCP (Claude Code, Cursor, …) peut alors appeler les instruments :

    {"command":"python3","args":["-m","lab.mcp"]}

Deux familles d'outils :

* **md_*** — le cockpit du moteur (v2) : capacités, kits de marque, brief
  pub → montage, contrôle qualité, aperçus en images, rendu multi-formats,
  lecture/écriture de projets. C'est la voie principale d'un agent pilote.
* **lab_*** — le laboratoire « données → vidéo » (graphiques animés).
"""
from __future__ import annotations

import base64
import contextlib
import io
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from lab import bench, instruments, spec as spec_mod  # noqa: E402
from engine import probe  # noqa: E402

PROTOCOL_VERSION = "2024-11-05"
SUPPORTED_PROTOCOLS = ("2024-11-05", "2025-03-26", "2025-06-18")
SERVER_VERSION = "2.0.0"
INSTRUCTIONS = (
    "Moteur MOTION-DESIGN (vidéos publicitaires motion design). Boucle du pilote : "
    "md_intake (éléments déposés : audio complet, logos, détails, médias) → md_cockpit → "
    "md_elements_search / md_elements_get (emojis 3D, icônes libres de droits) → "
    "md_ad_compose (brief pub) ou project.json → md_lint → md_preview "
    "(regarder les images) → md_render. md_guide donne le manuel complet."
)

_PROJECT_ARGS = {
    "name": {"type": "string", "description": "projet existant dans projects/"},
    "project": {"type": "object", "description": "project.json en ligne (alternative à name)"},
}

MD_TOOLS = [
    {"name": "md_cockpit", "description": "Toutes les capacités du moteur : formats, exports, animations, easing, idle, sorties, calques et leurs champs, kits de marque, templates pub, polices, assets, projets. À appeler en premier.",
     "inputSchema": {"type": "object", "properties": {}}},
    {"name": "md_guide", "description": "Manuel du pilote (docs/PILOTE.md) : règles de mise en scène pub, exemples, diagnostic.",
     "inputSchema": {"type": "object", "properties": {}}},
    {"name": "md_intake", "description": "À APPELER EN PREMIER pour une nouvelle pub : analyse entrees/ (audio complet de la pub → durée, respirations ; script.txt = texte dit → calé phrase par phrase sur l'audio ; logos → palette ; détails .txt → contenu ; vidéos/images complémentaires). Renvoie un brief squelette. install=true copie dans assets/ ; brand=\"nom\" crée le kit de marque d'après le logo.",
     "inputSchema": {"type": "object", "properties": {"install": {"type": "boolean"}, "brand": {"type": "string"}}}},
    {"name": "md_brands", "description": "Kits de marque (couleurs, polices, logo) utilisables via \"brand\" et les jetons $accent, $font.title, $logo.",
     "inputSchema": {"type": "object", "properties": {}}},
    {"name": "md_projects", "description": "Liste des projets enregistrés.",
     "inputSchema": {"type": "object", "properties": {}}},
    {"name": "md_project_get", "description": "Lit projects/<name>/project.json.",
     "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]}},
    {"name": "md_project_save", "description": "Enregistre (crée ou remplace) projects/<name>/project.json après validation.",
     "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}, "project": {"type": "object"},
                                                      "overwrite": {"type": "boolean"}}, "required": ["name", "project"]}},
    {"name": "md_lint", "description": "Contrôle qualité avant rendu : errors (bloquant), warnings (lisibilité, zones sûres TikTok/Reels, contraste, accroche tardive), infos. Chaque remarque indique le champ exact (where).",
     "inputSchema": {"type": "object", "properties": {**_PROJECT_ARGS, "canvas": {"type": "string", "description": "contrôler pour un autre format"}}}},
    {"name": "md_preview", "description": "Rend un brouillon rapide (scènes en cache) et RENVOIE UNE PLANCHE CONTACT EN IMAGE pour vérifier la mise en scène sans regarder la vidéo.",
     "inputSchema": {"type": "object", "properties": {**_PROJECT_ARGS,
        "at": {"type": "array", "items": {"type": "number"}, "description": "instants (s) à capturer"},
        "count": {"type": "integer", "description": "nombre d'images réparties (défaut 6)"},
        "canvas": {"type": "string"}, "frames": {"type": "boolean", "description": "renvoyer aussi chaque image séparément"}}}},
    {"name": "md_render", "description": "Rendu final. formats = déclinaisons (ex. [\"9x16\",\"1x1\",\"16x9\"]) grâce aux unités relatives. Bloquant.",
     "inputSchema": {"type": "object", "properties": {**_PROJECT_ARGS,
        "preset": {"type": "string", "description": "mp4-social (pub), mp4-hq, mp4-web, gif, webm-vp9, mov-alpha…"},
        "formats": {"type": "array", "items": {"type": "string"}},
        "draft": {"type": "boolean"}}}},
    {"name": "md_elements_search", "description": "Cherche des éléments graphiques LIBRES DE DROITS pour la pub (alternative à IconScout) : emojis 3D Microsoft Fluent (~1 600 objets : TV, popcorn, ballon, cadeau, horloge…), icônes ligne/plein (Unicons d'IconScout, Tabler, Lucide, Phosphor, Remix, MingCute, Material). Mots en français ou anglais. Renvoie des ids source:nom + licence.",
     "inputSchema": {"type": "object", "properties": {"query": {"type": "string"},
        "style": {"type": "string", "enum": ["3d", "couleur", "plat", "ligne", "plein"]},
        "source": {"type": "string"}, "limit": {"type": "integer"}}, "required": ["query"]}},
    {"name": "md_elements_get", "description": "Télécharge des éléments (ids de md_elements_search, ou un kit : divertissement, offre, appareils, interface) dans assets/elements/ et met à jour LICENCES.md. color recolore les icônes ligne/plein ; png=true ajoute des PNG transparents. Renvoie aussi une planche contact en image.",
     "inputSchema": {"type": "object", "properties": {"ids": {"type": "array", "items": {"type": "string"}},
        "kit": {"type": "string"}, "dest": {"type": "string"}, "color": {"type": "string"},
        "size": {"type": "integer"}, "png": {"type": "boolean"}}}},
    {"name": "md_ad_example", "description": "Brief publicitaire d'exemple + schéma des champs + templates (promo, offre, annonce, preuve).",
     "inputSchema": {"type": "object", "properties": {}}},
    {"name": "md_ad_compose", "description": "Brief pub (accroche, produit, bénéfices, preuve, offre, CTA, musique, voix) → project.json complet et rythmé. save=true l'enregistre dans projects/.",
     "inputSchema": {"type": "object", "properties": {"brief": {"type": "object"}, "save": {"type": "boolean"},
                                                      "name": {"type": "string"}}, "required": ["brief"]}},
    {"name": "md_ad_render", "description": "Brief pub → contrôle → rendu (multi-formats possible). Raccourci de md_ad_compose + md_render.",
     "inputSchema": {"type": "object", "properties": {"brief": {"type": "object"}, "preset": {"type": "string"},
                                                      "formats": {"type": "array", "items": {"type": "string"}},
                                                      "draft": {"type": "boolean"}}, "required": ["brief"]}},
]

LAB_TOOLS = [
    {"name": "lab_instruments", "description": "Liste les instruments disponibles (canvas, exports, polices, animations, assets).",
     "inputSchema": {"type": "object", "properties": {}}},
    {"name": "lab_schema", "description": "Retourne le protocole d'entrée attendu et un exemple complet.",
     "inputSchema": {"type": "object", "properties": {}}},
    {"name": "lab_example", "description": "Retourne un échantillon de données prêt à soumettre.",
     "inputSchema": {"type": "object", "properties": {}}},
    {"name": "lab_validate", "description": "Valide et normalise un protocole sans rien rendre.",
     "inputSchema": {"type": "object", "properties": {"spec": {"type": "object"}}, "required": ["spec"]}},
    {"name": "lab_run", "description": "Exécute une expérience : données en entrée → vidéo en sortie. Bloquant (rendu complet).",
     "inputSchema": {"type": "object", "properties": {
         "spec": {"type": "object"},
         "dry_run": {"type": "boolean", "description": "true = valider le montage sans produire de fichier"}}, "required": ["spec"]}},
    {"name": "lab_submit", "description": "Soumet une expérience en tâche de fond et retourne son id (non bloquant).",
     "inputSchema": {"type": "object", "properties": {"spec": {"type": "object"}}, "required": ["spec"]}},
    {"name": "lab_status", "description": "État détaillé d'une expérience (status, artefact, logs, erreur).",
     "inputSchema": {"type": "object", "properties": {"id": {"type": "string"}}, "required": ["id"]}},
    {"name": "lab_runs", "description": "Liste des dernières expériences.",
     "inputSchema": {"type": "object", "properties": {"limit": {"type": "integer"}}}},
    {"name": "lab_artifact", "description": "Chemin et métadonnées de l'artefact vidéo d'une expérience.",
     "inputSchema": {"type": "object", "properties": {"id": {"type": "string"}}, "required": ["id"]}},
]

TOOLS = MD_TOOLS + LAB_TOOLS


def _resolve(args: dict) -> tuple[dict, str, str]:
    """(projet, dossier du projet, nom) depuis `name` ou `project` en ligne."""
    from engine import project as project_mod
    if args.get("project") is not None:
        proj = args["project"]
        if not isinstance(proj, dict):
            raise SystemExit("ERREUR : 'project' doit être un objet JSON")
        name = project_mod.slugify(str(args.get("name") or proj.get("name") or "agent"))
        return proj, REPO, name
    if args.get("name"):
        proj, pdir = project_mod.load(args["name"])
        return proj, pdir, project_mod.slugify(args["name"])
    raise SystemExit("ERREUR : fournir 'name' (projet existant) ou 'project' (JSON en ligne)")


def _quiet(fn, *a, **kw):
    """Exécute fn en capturant stdout (le canal MCP ne doit contenir que du JSON-RPC)."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        res = fn(*a, **kw)
    return res, [l for l in buf.getvalue().splitlines() if l.strip()][-12:]


def _image_block(path: str, max_w: int = 1600) -> dict:
    from PIL import Image
    img = Image.open(path).convert("RGB")
    if img.width > max_w:
        img = img.resize((max_w, int(img.height * max_w / img.width)), Image.LANCZOS)
    out = io.BytesIO()
    img.save(out, "JPEG", quality=82)
    return {"type": "image", "data": base64.b64encode(out.getvalue()).decode("ascii"),
            "mimeType": "image/jpeg"}


def _rel(p: str) -> str:
    return os.path.relpath(p, REPO)


def _render_outputs(proj, pdir, name, preset, formats, draft):
    from engine import render as render_mod
    outs = []
    for fmt in (formats or [None]):
        path, _ = _quiet(render_mod.render_project_data, proj, pdir, name,
                         export_name=preset, canvas_override=fmt, draft=bool(draft))
        info = probe.probe(path)
        outs.append({"format": fmt or proj.get("canvas"), "path": _rel(path), "abs_path": path,
                     "duration_s": info.get("duration"), "bytes": info.get("size"),
                     "resolution": f"{info.get('width')}x{info.get('height')}"})
    return outs


def call_md_tool(name: str, args: dict) -> dict:
    from engine import ads, brand, cockpit, frames, lint, project as project_mod

    def text(payload) -> dict:
        return {"content": [{"type": "text",
                             "text": payload if isinstance(payload, str) else
                             json.dumps(payload, ensure_ascii=False, indent=2)}]}

    if name == "md_cockpit":
        return text(cockpit.capabilities())
    if name == "md_guide":
        return text(cockpit.guide())
    if name == "md_brands":
        return text(brand.list_brands())
    if name == "md_intake":
        from engine import intake
        rep = intake.scan()
        if args.get("install") or args.get("brand"):
            rep["installation"] = intake.install(rep, args.get("brand"))
        return text(rep)
    if name == "md_projects":
        return text(project_mod.list_projects())
    if name == "md_project_get":
        proj, _ = project_mod.load(args["name"])
        return text(proj)
    if name == "md_project_save":
        pj = project_mod.save(args["name"], args["project"], overwrite=args.get("overwrite", True))
        rep = lint.lint(args["project"], os.path.dirname(pj))
        return text({"saved": _rel(pj), "lint": rep})
    if name == "md_lint":
        proj, pdir, _ = _resolve(args)
        return text(lint.lint(proj, pdir, args.get("canvas")))
    if name == "md_preview":
        proj, pdir, pname = _resolve(args)
        rep = lint.lint(proj, pdir, args.get("canvas"))
        if not rep["ok"]:
            return {"content": [{"type": "text", "text": json.dumps(
                {"error": "le contrôle qualité bloque l'aperçu", "lint": rep},
                ensure_ascii=False, indent=2)}], "isError": True}
        res = frames.preview(proj, pdir, pname, at=args.get("at"), count=int(args.get("count", 6)),
                             canvas_override=args.get("canvas"), width=360)
        blocks = [{"type": "text", "text": json.dumps(
            {**res, "warnings": rep["warnings"]}, ensure_ascii=False, indent=2)},
            _image_block(os.path.join(REPO, res["sheet"]))]
        if args.get("frames"):
            blocks += [_image_block(os.path.join(REPO, f), 720) for f in res["frames"]]
        return {"content": blocks}
    if name == "md_render":
        proj, pdir, pname = _resolve(args)
        rep = lint.lint(proj, pdir)
        if not rep["ok"]:
            return {"content": [{"type": "text", "text": json.dumps(
                {"error": "rendu refusé : erreurs de contrôle", "lint": rep},
                ensure_ascii=False, indent=2)}], "isError": True}
        outs = _render_outputs(proj, pdir, pname, args.get("preset"), args.get("formats"),
                               args.get("draft"))
        return text({"outputs": outs, "warnings": rep["warnings"]})
    if name == "md_elements_search":
        from engine import elements
        return text(elements.search(args["query"], style=args.get("style"), source=args.get("source"),
                                    limit=int(args.get("limit", 24))))
    if name == "md_elements_get":
        from engine import elements
        dest = os.path.join(REPO, args["dest"]) if args.get("dest") else None
        if args.get("kit"):
            res = elements.kit(args["kit"], dest=dest, color=args.get("color"), png=bool(args.get("png")))
        else:
            res = elements.get(args.get("ids") or [], dest=dest, color=args.get("color"),
                               size=int(args.get("size", 512)), png=bool(args.get("png")))
        blocks = [{"type": "text", "text": json.dumps(res, ensure_ascii=False, indent=2)}]
        try:
            blocks.append(_image_block(os.path.join(REPO, elements.sheet(dest))))
        except Exception:
            pass
        return {"content": blocks}
    if name == "md_ad_example":
        return text(ads.schema())
    if name in ("md_ad_compose", "md_ad_render"):
        proj = ads.compose(args["brief"])
        pname = project_mod.slugify(args.get("name") or proj["name"])
        pdir = REPO
        result: dict = {"name": pname}
        if name == "md_ad_compose" and args.get("save"):
            pj = project_mod.save(pname, proj)
            pdir = os.path.dirname(pj)
            result["saved"] = _rel(pj)
        rep = lint.lint(proj, pdir)
        result["lint"] = rep
        if name == "md_ad_compose":
            result["project"] = proj
            return text(result)
        if not rep["ok"]:
            return {"content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}],
                    "isError": True}
        outs = []
        for fmt in (args.get("formats") or [None]):
            p_fmt = ads.compose(args["brief"], canvas=fmt) if fmt else proj
            outs += _render_outputs(p_fmt, pdir, pname, args.get("preset"), [fmt] if fmt else None,
                                    args.get("draft"))
        result["outputs"] = outs
        return text(result)
    return {"content": [{"type": "text", "text": f"Outil inconnu : {name}"}], "isError": True}


def call_tool(name: str, args: dict) -> dict:
    """Exécute un outil. Retourne le payload `result` MCP."""
    def text(payload) -> dict:
        return {"content": [{"type": "text",
                             "text": json.dumps(payload, ensure_ascii=False, indent=2)}]}

    try:
        if name.startswith("md_"):
            return call_md_tool(name, args)
        if name == "lab_instruments":
            return text(instruments.inventory())
        if name == "lab_schema":
            return text(spec_mod.schema())
        if name == "lab_example":
            return text(spec_mod.example())
        if name == "lab_validate":
            return text({"valid": True, "spec": spec_mod.validate(args["spec"])})
        if name == "lab_run":
            return text(bench.run_experiment(args["spec"], dry_run=bool(args.get("dry_run", False))))
        if name == "lab_submit":
            return text(bench.submit(args["spec"]))
        if name == "lab_status":
            rec = bench.get(args["id"])
            return text(rec or {"error": "expérience inconnue"})
        if name == "lab_runs":
            return text(bench.list_runs(limit=int(args.get("limit", 30))))
        if name == "lab_artifact":
            rec = bench.get(args["id"])
            if not rec or not rec.get("artifact"):
                return text({"error": "artefact indisponible"})
            path = os.path.join(REPO, rec["artifact"])
            return text({"path": rec["artifact"],
                         "url": f"/api/runs/{rec['id']}/artifact",
                         "probe": probe.probe(path) if os.path.isfile(path) else {"error": "fichier absent"}})
        return {"content": [{"type": "text", "text": f"Outil inconnu : {name}"}], "isError": True}
    except SystemExit as exc:
        return {"content": [{"type": "text", "text": str(exc)}], "isError": True}
    except Exception as exc:  # noqa: BLE001
        return {"content": [{"type": "text", "text": f"{type(exc).__name__}: {exc}"}], "isError": True}


def handle(msg: dict) -> dict | None:
    """Traite un message JSON-RPC. None = notification (pas de réponse)."""
    method = msg.get("method", "")
    mid = msg.get("id")
    params = msg.get("params") or {}

    if method == "initialize":
        asked = params.get("protocolVersion")
        result = {
            "protocolVersion": asked if asked in SUPPORTED_PROTOCOLS else PROTOCOL_VERSION,
            "capabilities": {"tools": {"listChanged": False}},
            "serverInfo": {"name": "motion-design", "version": SERVER_VERSION},
            "instructions": INSTRUCTIONS,
        }
    elif method == "ping":
        result = {}
    elif method == "tools/list":
        result = {"tools": TOOLS}
    elif method == "tools/call":
        # stdout est le canal JSON-RPC : toute sortie parasite des outils est capturée.
        result, _ = _quiet(call_tool, params.get("name", ""), params.get("arguments") or {})
    elif method.startswith("notifications/"):
        return None
    else:
        if mid is None:
            return None
        return {"jsonrpc": "2.0", "id": mid,
                "error": {"code": -32601, "message": f"Méthode inconnue : {method}"}}

    if mid is None:
        return None
    return {"jsonrpc": "2.0", "id": mid, "result": result}


def main() -> None:
    """Boucle stdio : une requête JSON par ligne, une réponse par ligne.

    stdout est réservé au protocole : tout autre affichage (rendus, threads
    de fond) est redirigé vers stderr pour ne jamais corrompre le canal.
    """
    channel = sys.stdout
    sys.stdout = sys.stderr
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except ValueError:
            channel.write(json.dumps({"jsonrpc": "2.0", "id": None, "error": {
                "code": -32700, "message": "JSON invalide"}}) + "\n")
            channel.flush()
            continue
        if not isinstance(msg, dict):
            continue
        try:
            response = handle(msg)
        except Exception as exc:  # noqa: BLE001 — le serveur ne doit jamais tomber
            response = None if msg.get("id") is None else {
                "jsonrpc": "2.0", "id": msg.get("id"),
                "error": {"code": -32603, "message": f"{type(exc).__name__}: {exc}"}}
        if response is not None:
            channel.write(json.dumps(response, ensure_ascii=False) + "\n")
            channel.flush()


if __name__ == "__main__":
    main()
