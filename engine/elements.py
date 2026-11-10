"""Bibliothèque d'éléments graphiques LIBRES DE DROITS pour les pubs.

Alternative ouverte à IconScout : icônes, emojis 3D et pictogrammes utilisables en
publicité commerciale, récupérés depuis des sources accessibles au moteur
(registry npm, GitHub), avec la licence de chaque fichier tracée.

    ./md elements sources                          # sources, styles, licences
    ./md elements chercher télé popcorn --style 3d  # recherche (mots en français ou anglais)
    ./md elements prendre fluent-3d:television tabler:download --couleur "#3dff6e"
    ./md elements kits                             # kits prêts à l'emploi
    ./md elements kit divertissement               # récupère tout un kit

Sources (licences acceptées : MIT, ISC, Apache-2.0 ; usage commercial sans attribution) :
  • fluent-3d / fluent-couleur / fluent-plat : Microsoft Fluent Emoji (~1 600 objets, 3D brillant,
    couleur, plat) — github.com/microsoft/fluentui-emoji, MIT
  • unicons / unicons-plein : Unicons d'IconScout (Apache-2.0), via Iconify
  • tabler, lucide, phosphor, remix, mingcute, material : icônes vectorielles, via Iconify (npm)

Les fichiers arrivent dans assets/elements/ (par défaut) avec assets/elements/LICENCES.md.
"""
from __future__ import annotations

import io
import json
import os
import re
import shutil
import subprocess
import tarfile
import unicodedata
import urllib.request

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(REPO, ".cache", "elements")
DEST = os.path.join(REPO, "assets", "elements")
UA = {"User-Agent": "MOTION-DESIGN-engine/2.0"}

FLUENT_REPO = "https://github.com/microsoft/fluentui-emoji"
FLUENT_STYLES = {"fluent-3d": ("3D", ".png", "3d"), "fluent-couleur": ("Color", ".svg", "couleur"),
                 "fluent-plat": ("Flat", ".svg", "plat")}

SOURCES = {
    "fluent-3d": {"style": "3d", "label": "Microsoft Fluent Emoji 3D (PNG 256 px, rendu 3D brillant)",
                  "licence": "MIT", "url": FLUENT_REPO},
    "fluent-couleur": {"style": "couleur", "label": "Microsoft Fluent Emoji couleur (SVG dégradés)",
                       "licence": "MIT", "url": FLUENT_REPO},
    "fluent-plat": {"style": "plat", "label": "Microsoft Fluent Emoji plat (SVG aplats)",
                    "licence": "MIT", "url": FLUENT_REPO},
    "unicons": {"style": "ligne", "iconify": "uil", "label": "Unicons d'IconScout (ligne)", "licence": "Apache-2.0"},
    "unicons-plein": {"style": "plein", "iconify": "uis", "label": "Unicons d'IconScout (plein)", "licence": "Apache-2.0"},
    "tabler": {"style": "ligne", "iconify": "tabler", "label": "Tabler Icons (ligne + filled)", "licence": "MIT"},
    "lucide": {"style": "ligne", "iconify": "lucide", "label": "Lucide (ligne)", "licence": "ISC"},
    "phosphor": {"style": "ligne", "iconify": "ph", "label": "Phosphor (ligne, plein, duotone)", "licence": "MIT"},
    "remix": {"style": "ligne", "iconify": "ri", "label": "Remix Icon (ligne + plein)", "licence": "Apache-2.0"},
    "mingcute": {"style": "ligne", "iconify": "mingcute", "label": "MingCute (ligne + plein, arrondi)", "licence": "Apache-2.0"},
    "material": {"style": "plein", "iconify": "material-symbols", "label": "Material Symbols (Google)", "licence": "Apache-2.0"},
    "iconvault": {"style": "ligne", "label": "IconVaultKit (serveur MCP) : 91 bibliothèques, licence vérifiée par bibliothèque",
                  "licence": "vérifiée", "url": "https://iconvaultkit.com/api/mcp"},
}
ICONVAULT = "https://iconvaultkit.com/api/mcp"
# bibliothèques de logos de marques (marques déposées) : jamais en pub
BRAND_SETS = {"simple-icons", "logos", "cib", "fa-brands", "fa6-brands", "skill-icons", "devicon", "devicon-plain",
              "vscode-icons", "brandico", "entypo-social", "bxl", "mdi-brand", "streamline-logos", "token-branded"}
LICENCES_OK = {"MIT", "ISC", "Apache-2.0", "CC0-1.0"}
STYLES = {"3d": "objets 3D brillants (emojis Fluent)", "couleur": "illustrations couleur à dégradés",
          "plat": "illustrations en aplats", "ligne": "pictogrammes au trait (recolorables)",
          "plein": "pictogrammes pleins (recolorables)"}

# Recherche en français : mot → termes anglais des bibliothèques (clés sans accents).
FR = {
    "tele": ["television", "tv"], "television": ["television", "tv"], "tv": ["tv", "television"],
    "film": ["film", "movie", "clapper", "cinema"], "films": ["film", "movie", "clapper"], "cinema": ["cinema", "movie", "clapper", "film"],
    "serie": ["tv", "television", "series", "play"], "series": ["tv", "television", "play"],
    "sport": ["sport", "soccer", "ball", "trophy"], "foot": ["soccer", "football", "ball"], "football": ["soccer", "football"],
    "ballon": ["ball", "soccer"], "basket": ["basketball"], "trophee": ["trophy"], "medaille": ["medal"],
    "musique": ["music", "musical", "note", "headphone"], "casque": ["headphone", "headphones"], "radio": ["radio"],
    "micro": ["microphone", "mic"], "podcast": ["microphone", "podcast", "mic"], "chanson": ["music", "musical"],
    "manga": ["manga", "anime", "eyes"], "anime": ["anime"], "dessin": ["cartoon", "drawing"], "enfant": ["child", "kid", "baby"],
    "enfants": ["child", "kid", "children"], "famille": ["family"], "jeu": ["game", "gamepad", "video game"], "manette": ["gamepad", "video game", "joystick"],
    "camera": ["camera", "video", "movie camera"], "video": ["video", "movie", "play"], "direct": ["live", "broadcast", "antenna", "satellite"],
    "live": ["live", "broadcast"], "chaine": ["channel", "tv", "broadcast"], "chaines": ["channel", "tv", "broadcast"],
    "lecture": ["play"], "play": ["play"], "pause": ["pause"],
    "telephone": ["phone", "mobile", "smartphone"], "smartphone": ["smartphone", "mobile", "phone"], "mobile": ["mobile", "phone"],
    "tablette": ["tablet", "device-tablet"], "ordinateur": ["laptop", "computer", "desktop"], "pc": ["laptop", "computer"],
    "wifi": ["wifi", "wireless"], "internet": ["internet", "globe", "world", "web"], "monde": ["world", "globe", "earth"],
    "reseau": ["signal", "network", "antenna", "wifi"], "signal": ["signal", "antenna"], "box": ["router", "wifi"],
    "telecharger": ["download"], "telechargement": ["download"], "installer": ["download", "install"],
    "prix": ["price", "tag", "money", "dollar", "coin"], "argent": ["money", "coin", "dollar", "banknote"], "piece": ["coin"],
    "billet": ["banknote", "money"], "promo": ["sale", "discount", "percent", "tag"], "reduction": ["discount", "percent", "sale"],
    "offre": ["gift", "tag", "sale"], "cadeau": ["gift", "present", "wrapped gift"], "gratuit": ["gift", "free"],
    "offert": ["gift", "present"], "horloge": ["clock", "alarm clock", "time"], "chrono": ["stopwatch", "timer"], "temps": ["clock", "time", "hourglass"],
    "heure": ["clock", "time"], "calendrier": ["calendar"], "date": ["calendar"], "mois": ["calendar"],
    "etoile": ["star", "glowing star"], "coeur": ["heart"], "feu": ["fire"], "fusee": ["rocket"], "eclair": ["lightning", "zap", "high voltage", "bolt"],
    "fete": ["party", "confetti", "party popper"], "confetti": ["confetti", "party popper"], "bravo": ["clapping", "party"],
    "nouveau": ["new", "sparkles"], "magie": ["sparkles", "magic"], "brillant": ["sparkles", "glowing"],
    "ok": ["check", "ok"], "valide": ["check", "check mark"], "coche": ["check", "check mark"], "securite": ["shield", "lock"],
    "bouclier": ["shield"], "cadenas": ["lock", "locked"], "stable": ["shield", "check"],
    "panier": ["cart", "shopping cart", "basket"], "boutique": ["shop", "store"], "livraison": ["delivery", "truck"],
    "camion": ["truck"], "carte": ["credit card", "card"], "paiement": ["credit card", "money", "wallet"], "portefeuille": ["wallet"],
    "maison": ["house", "home"], "salon": ["couch", "sofa", "house"], "canape": ["couch", "sofa"], "pop-corn": ["popcorn"], "popcorn": ["popcorn"],
    "fleche": ["arrow"], "bas": ["down"], "haut": ["up"], "recherche": ["search", "magnifying glass"], "loupe": ["magnifying glass", "search"],
    "notification": ["bell", "notification"], "cloche": ["bell"], "message": ["message", "chat", "speech balloon"], "whatsapp": ["chat", "message", "phone"],
    "partage": ["share"], "aime": ["like", "thumbs up", "heart"], "pouce": ["thumbs up"], "sourire": ["smile", "smiling face"],
    "qualite": ["hd", "high definition", "star"], "hd": ["hd"], "satellite": ["satellite", "satellite antenna"], "antenne": ["antenna", "satellite antenna"],
}

KITS = {
    "divertissement": ["fluent-3d:television", "fluent-3d:popcorn", "fluent-3d:clapper board", "fluent-3d:film frames",
                       "fluent-3d:movie camera", "fluent-3d:soccer ball", "fluent-3d:trophy", "fluent-3d:headphone",
                       "fluent-3d:studio microphone", "fluent-3d:radio", "fluent-3d:video game", "fluent-3d:musical notes",
                       "fluent-3d:satellite antenna", "fluent-3d:globe showing europe-africa"],
    "offre": ["fluent-3d:wrapped gift", "fluent-3d:money bag", "fluent-3d:coin", "fluent-3d:stopwatch",
              "fluent-3d:alarm clock", "fluent-3d:calendar", "fluent-3d:check mark button", "fluent-3d:party popper",
              "fluent-3d:confetti ball", "fluent-3d:sparkles", "fluent-3d:fire", "fluent-3d:high voltage", "fluent-3d:star"],
    "appareils": ["fluent-3d:mobile phone", "fluent-3d:laptop", "fluent-3d:desktop computer", "fluent-3d:television",
                  "fluent-3d:satellite antenna", "fluent-3d:globe with meridians"],
    "interface": ["tabler:download", "tabler:player-play-filled", "tabler:wifi", "tabler:world", "tabler:device-tv",
                  "tabler:device-mobile", "tabler:device-tablet", "tabler:device-laptop", "tabler:check", "tabler:shield-check",
                  "tabler:clock", "tabler:calendar", "tabler:gift", "tabler:star-filled", "tabler:music", "tabler:movie",
                  "tabler:ball-football", "tabler:microphone", "tabler:radio", "tabler:search", "tabler:bell", "tabler:arrow-down"],
}


# ── utilitaires ───────────────────────────────────────────────
def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s.lower())
    return "".join(c for c in s if not unicodedata.combining(c))


def _slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", _norm(s)).strip("-")


def _groups(query: list[str] | str) -> list[list[str]]:
    """Un groupe de termes par mot demandé (mot français connu → ses traductions anglaises)."""
    words = query.split() if isinstance(query, str) else [w for q in query for w in q.split()]
    groups = []
    for w in words:
        n = _norm(w)
        trad = FR.get(n) or FR.get(n.rstrip("s"))
        groups.append(list(dict.fromkeys(trad if trad else [n])))
    return groups


def _terms(query) -> list[str]:
    return list(dict.fromkeys(t for g in _groups(query) for t in g))


def _get(url: str, timeout: int = 120) -> bytes:
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
        return r.read()


def _match(h: str, t: str) -> int:
    words = re.split(r"[\s\-_]+", h)
    if h == t:
        return 100
    if t in words or (" " in t and t in h):
        return 80
    if len(t) >= 3 and any(w.startswith(t) for w in words):
        return 45
    if len(t) >= 4 and t in h:
        return 25
    return 0


def _score(name: str, keywords: list[str], groups: list[list[str]]) -> int:
    """Somme, par mot demandé, de la meilleure correspondance. Le nom compte plus que les mots-clés ;
    bonus quand plusieurs traductions d'un même mot correspondent (« ballon foot » → soccer ball)."""
    total = 0
    for g in groups:
        hits = []
        for t in g:
            m = max([_match(name, t)] + [int(_match(k, t) * 0.6) for k in keywords])
            if m:
                hits.append(m)
        if hits:
            total += max(hits) + 10 * (len(hits) - 1)
    return total


# ── Iconify (npm @iconify-json/<prefix>) ─────────────────────
def _iconify_set(prefix: str) -> dict:
    path = os.path.join(CACHE, "iconify", f"{prefix}.json")
    if not os.path.exists(path):
        meta = json.loads(_get(f"https://registry.npmjs.org/@iconify-json/{prefix}/latest"))
        lic = meta.get("license", "")
        if lic not in LICENCES_OK:
            raise ValueError(f"@iconify-json/{prefix} : licence {lic} non retenue (attribution ou partage requis)")
        with tarfile.open(fileobj=io.BytesIO(_get(meta["dist"]["tarball"])), mode="r:gz") as tf:
            data = json.load(tf.extractfile("package/icons.json"))
        data["_version"], data["_licence"] = meta["version"], lic
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f)
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _iconify_svg(data: dict, name: str, color: str | None, size: int) -> str:
    icons, aliases = data["icons"], data.get("aliases", {})
    seen = 0
    while name not in icons and name in aliases and seen < 5:
        name = aliases[name]["parent"]; seen += 1
    if name not in icons:
        raise KeyError(name)
    ic = icons[name]
    w, h = ic.get("width", data.get("width", 24)), ic.get("height", data.get("height", 24))
    body = ic["body"]
    if color:
        body = body.replace("currentColor", color)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{round(size * h / w)}" '
            f'viewBox="0 0 {w} {h}">{body}</svg>\n')


# ── IconVaultKit (serveur MCP HTTP, 91 bibliothèques Iconify) ──
def _vault_call(tool: str, arguments: dict) -> str:
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/call",
                       "params": {"name": tool, "arguments": arguments}}).encode()
    req = urllib.request.Request(ICONVAULT, data=body, headers={**UA, "Content-Type": "application/json",
                                                                "Accept": "application/json, text/event-stream"})
    with urllib.request.urlopen(req, timeout=60) as r:
        res = json.loads(r.read())
    if "error" in res:
        raise RuntimeError(res["error"].get("message", "erreur IconVaultKit"))
    return res["result"]["content"][0]["text"]


def _set_licence(prefix: str) -> str:
    """Licence d'une bibliothèque Iconify (registry npm @iconify-json/<prefix>), mise en cache."""
    path = os.path.join(CACHE, "licences-iconify.json")
    cache = json.load(open(path, encoding="utf-8")) if os.path.exists(path) else {}
    if prefix not in cache:
        try:
            cache[prefix] = json.loads(_get(f"https://registry.npmjs.org/@iconify-json/{prefix}/latest", 30)).get("license", "?")
        except Exception:
            cache[prefix] = "?"
        os.makedirs(CACHE, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(cache, f)
    return cache[prefix]


def _vault_ok(prefix: str) -> tuple[bool, str]:
    if prefix in BRAND_SETS or "logo" in prefix or "brand" in prefix:
        return False, "logos de marques"
    lic = _set_licence(prefix)
    return lic in LICENCES_OK, lic


# ── Microsoft Fluent Emoji (git partiel : seuls les fichiers demandés sont téléchargés) ──
def _fluent_repo() -> str:
    d = os.path.join(CACHE, "fluentui-emoji")
    if not os.path.isdir(os.path.join(d, ".git")):
        os.makedirs(CACHE, exist_ok=True)
        subprocess.run(["git", "clone", "-q", "--filter=blob:none", "--no-checkout", "--depth", "1", FLUENT_REPO, d],
                       check=True)
    return d


def _fluent_index() -> list[dict]:
    path = os.path.join(CACHE, "fluent-index.json")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    d = _fluent_repo()
    files = subprocess.run(["git", "-C", d, "ls-tree", "-r", "--name-only", "HEAD", "assets/"],
                           capture_output=True, text=True, check=True).stdout.splitlines()
    metas = [f for f in files if f.endswith("/metadata.json") and f.count("/") == 2]
    # récupération groupée des métadonnées (mots-clés) en un seul échange
    subprocess.run(["git", "-C", d, "sparse-checkout", "set", "--no-cone", "/assets/*/metadata.json"], check=True,
                   capture_output=True)
    subprocess.run(["git", "-C", d, "checkout", "-q", "HEAD"], check=True, capture_output=True)
    by_dir: dict[str, list[str]] = {}
    for f in files:
        by_dir.setdefault(f.split("/")[1], []).append(f)
    index = []
    for m in metas:
        folder = m.split("/")[1]
        try:
            with open(os.path.join(d, m), encoding="utf-8") as fh:
                md = json.load(fh)
        except (OSError, ValueError):
            md = {}
        entry = {"name": folder, "keywords": md.get("keywords", []), "glyph": md.get("glyph", ""), "group": md.get("group", "")}
        for src, (sub, ext, _) in FLUENT_STYLES.items():
            cand = [f for f in by_dir[folder] if f"/{sub}/" in f and f.endswith(ext)]
            cand.sort(key=lambda f: (0 if "/Default/" in f else 1, len(f)))
            if cand:
                entry[src] = cand[0]
        index.append(entry)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False)
    return index


def _fluent_file(path_in_repo: str) -> bytes:
    d = _fluent_repo()
    return subprocess.run(["git", "-C", d, "show", f"HEAD:{path_in_repo}"], capture_output=True, check=True).stdout


# ── API publique ──────────────────────────────────────────────
def sources() -> dict:
    return {"styles": STYLES, "sources": {k: {kk: vv for kk, vv in v.items() if kk != "iconify"} for k, v in SOURCES.items()},
            "licences_acceptees": sorted(LICENCES_OK), "kits": {k: len(v) for k, v in KITS.items()},
            "destination": os.path.relpath(DEST, REPO)}


def search(query, style: str | None = None, source: str | None = None, limit: int = 24) -> dict:
    groups, terms = _groups(query), _terms(query)
    if not terms:
        raise ValueError("indiquer au moins un mot à chercher")
    srcs = [source] if source else [k for k, v in SOURCES.items() if not style or v["style"] == style]
    if source and source not in SOURCES:
        raise ValueError(f"source inconnue : {source} ({', '.join(SOURCES)})")
    results, errors = [], {}
    fluent = [s for s in srcs if s in FLUENT_STYLES]
    if fluent:
        try:
            for e in _fluent_index():
                sc = _score(_norm(e["name"]), [_norm(k) for k in e["keywords"]], groups)
                if sc:
                    for s in fluent:
                        if s in e:
                            results.append({"id": f"{s}:{_norm(e['name'])}", "score": sc + 5, "source": s,
                                            "style": SOURCES[s]["style"], "licence": "MIT", "apercu": e["glyph"]})
        except Exception as ex:  # réseau, git…
            errors["fluent"] = str(ex)
    for s in srcs:
        pref = SOURCES[s].get("iconify")
        if not pref:
            continue
        try:
            data = _iconify_set(pref)
        except Exception as ex:
            errors[s] = str(ex)
            continue
        for name in list(data["icons"]) + list(data.get("aliases", {})):
            sc = _score(name.replace("-", " "), [], groups)
            if sc:
                results.append({"id": f"{s}:{name}", "score": sc, "source": s, "style": SOURCES[s]["style"],
                                "licence": data["_licence"]})
    if "iconvault" in srcs:
        try:
            seen = set()
            for g in _groups(query):
                txt = _vault_call("search_icons", {"query": g[0], "limit": 100})
                for line in txt.splitlines():
                    m = re.match(r"\s*([a-z0-9-]+):([a-z0-9-]+)\s", line + " ")
                    if not m or line.startswith("Found") or m.group(0) in seen:
                        continue
                    seen.add(m.group(0))
                    prefix, nm = m.group(1), m.group(2)
                    if source != "iconvault" and prefix in {v.get("iconify") for v in SOURCES.values()}:
                        continue  # déjà couvert par une source dédiée
                    ok, lic = _vault_ok(prefix)
                    if ok:
                        results.append({"id": f"iconvault:{prefix}:{nm}", "score": _score(nm.replace("-", " "), [], groups) - 5,
                                        "source": "iconvault", "style": "ligne", "licence": lic})
        except Exception as ex:
            errors["iconvault"] = str(ex)
    results.sort(key=lambda r: (-r["score"], len(r["id"])))
    out = {"requete": query if isinstance(query, str) else " ".join(query), "termes": terms,
           "resultats": results[:limit], "total": len(results)}
    if errors:
        out["erreurs"] = errors
    return out


def _licences_append(rows: list[dict], dest: str) -> None:
    jpath = os.path.join(dest, "licences.json")
    data = []
    if os.path.exists(jpath):
        with open(jpath, encoding="utf-8") as f:
            data = json.load(f)
    known = {r["fichier"] for r in rows}
    data = [r for r in data if r["fichier"] not in known] + rows
    with open(jpath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    lines = ["# Licences des éléments graphiques", "",
             "Récupérés par `./md elements` (engine/elements.py). Toutes ces licences autorisent l'usage "
             "commercial (publicité) sans attribution obligatoire.", "",
             "| Fichier | Source | Élément d'origine | Licence |", "|---|---|---|---|"]
    lines += [f"| `{r['fichier']}` | {r['source']} | {r['origine']} | {r['licence']} |" for r in data]
    with open(os.path.join(dest, "LICENCES.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def _rasterize(svg_path: str, size: int) -> str | None:
    """SVG → PNG transparent via le Chromium de Playwright (si présent)."""
    png = os.path.splitext(svg_path)[0] + ".png"
    js = ("const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();"
          f"const p=await b.newPage({{viewport:{{width:{size},height:{size}}}}});"
          "const fs=require('fs');const svg=fs.readFileSync(process.argv[1],'utf8');"
          "await p.setContent(`<html><body style=\"margin:0;background:transparent\">${svg.replace('<svg ','<svg style=\"width:100%;height:100%\" ')}</body></html>`);"
          "await p.screenshot({path:process.argv[2],omitBackground:true});await b.close();})();")
    r = subprocess.run(["node", "-e", js, svg_path, png], capture_output=True, text=True, cwd=REPO)
    return png if r.returncode == 0 and os.path.exists(png) else None


def get(ids: list[str], dest: str | None = None, color: str | None = None, size: int = 512,
        png: bool = False) -> dict:
    """Récupère des éléments (ids « source:nom ») dans dest (défaut assets/elements/)."""
    dest = os.path.abspath(dest or DEST)
    os.makedirs(dest, exist_ok=True)
    ok, ko, rows = [], {}, []
    for ident in ids:
        if ":" not in ident:
            ko[ident] = "format attendu : source:nom (voir ./md elements chercher)"
            continue
        src, name = ident.split(":", 1)
        if src not in SOURCES:
            ko[ident] = f"source inconnue ({', '.join(SOURCES)})"
            continue
        try:
            if src in FLUENT_STYLES:
                entry = next((e for e in _fluent_index() if _norm(e["name"]) == _norm(name)), None)
                if not entry or src not in entry:
                    raise KeyError(f"« {name} » introuvable en {src}")
                ext = FLUENT_STYLES[src][1]
                fname = f"{_slug(entry['name'])}-{FLUENT_STYLES[src][2]}{ext}"
                with open(os.path.join(dest, fname), "wb") as f:
                    f.write(_fluent_file(entry[src]))
                origin, lic = f"Fluent Emoji « {entry['name']} » ({entry[src]})", "MIT"
            elif src == "iconvault":
                if ":" not in name:
                    raise KeyError("format attendu : iconvault:bibliotheque:icone")
                prefix, nm = name.split(":", 1)
                ok_lic, lic = _vault_ok(prefix)
                if not ok_lic:
                    raise ValueError(f"bibliothèque {prefix} refusée ({lic}) : licence non compatible pub sans attribution")
                svg = _vault_call("get_icon_svg", {"collection": prefix, "name": nm, "size": size,
                                                   **({"color": color} if color else {})})
                if not svg.lstrip().startswith("<svg"):
                    raise KeyError(svg[:120])
                fname = f"{prefix}-{_slug(nm)}" + (f"-{_slug(color)}" if color else "") + ".svg"
                with open(os.path.join(dest, fname), "w", encoding="utf-8") as f:
                    f.write(svg.strip() + "\n")
                origin = f"IconVaultKit « {prefix}:{nm} » (bibliothèque Iconify {prefix})"
            else:
                data = _iconify_set(SOURCES[src]["iconify"])
                svg = _iconify_svg(data, name, color, size)
                fname = f"{src}-{_slug(name)}" + (f"-{_slug(color)}" if color else "") + ".svg"
                with open(os.path.join(dest, fname), "w", encoding="utf-8") as f:
                    f.write(svg)
                origin = f"{SOURCES[src]['label']} « {name} » (@iconify-json/{SOURCES[src]['iconify']}@{data['_version']})"
                lic = data["_licence"]
            files = [fname]
            if png and fname.endswith(".svg"):
                p = _rasterize(os.path.join(dest, fname), size)
                if p:
                    files.append(os.path.basename(p))
            for fn in files:
                rows.append({"fichier": fn, "source": src, "origine": origin, "licence": lic})
            ok += [os.path.relpath(os.path.join(dest, fn), REPO) for fn in files]
        except Exception as ex:
            ko[ident] = str(ex)
    if rows:
        _licences_append(rows, dest)
    return {"recuperes": ok, "erreurs": ko, "licences": os.path.relpath(os.path.join(dest, "LICENCES.md"), REPO)}


def kit(name: str, dest: str | None = None, color: str | None = None, png: bool = False) -> dict:
    if name not in KITS:
        raise ValueError(f"kit inconnu : {name} ({', '.join(KITS)})")
    return get(KITS[name], dest=dest, color=color, png=png)


def clear_cache() -> None:
    shutil.rmtree(CACHE, ignore_errors=True)


def sheet(folder: str | None = None, out: str | None = None, cell: int = 180) -> str:
    """Planche contact des éléments PNG d'un dossier (pour vérifier d'un coup d'œil)."""
    from PIL import Image, ImageDraw
    folder = os.path.abspath(folder or DEST)
    files = sorted(f for f in os.listdir(folder) if f.lower().endswith(".png"))
    if not files:
        raise ValueError(f"aucun PNG dans {folder}")
    cols = min(8, len(files)); rows = (len(files) + cols - 1) // cols
    img = Image.new("RGB", (cols * cell, rows * (cell + 24)), (22, 30, 70))
    dr = ImageDraw.Draw(img)
    for i, f in enumerate(files):
        im = Image.open(os.path.join(folder, f)).convert("RGBA")
        im.thumbnail((cell - 30, cell - 30))
        x, y = (i % cols) * cell, (i // cols) * (cell + 24)
        img.paste(im, (x + (cell - im.width) // 2, y + (cell - im.height) // 2), im)
        dr.text((x + 6, y + cell + 4), f[: cell // 7], fill=(230, 230, 240))
    out = out or os.path.join(REPO, ".cache", "elements", "planche.jpg")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    img.save(out, quality=88)
    return os.path.relpath(out, REPO)
