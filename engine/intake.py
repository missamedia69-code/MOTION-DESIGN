"""Réception des éléments d'une pub (dossier `entrees/`).

À chaque pub, l'utilisateur fournit :
  * l'**audio complet** de la pub (voix + musique déjà mixées) → il DICTE la durée
    et le rythme : la vidéo se cale dessus ;
  * les **logos** de la marque ;
  * les **détails en texte** (.txt / .md) : offre, arguments, ton, contacts… ;
  * des **vidéos et images complémentaires** (produit, ambiance, plans).

`scan()` trie tout ça, analyse l'audio (durée, respirations = points de coupe,
transcription si Whisper est disponible), extrait la palette du logo, et
prépare un **brief squelette** que l'agent complète à partir des détails texte.
"""
from __future__ import annotations

import colorsys
import json
import os
import re
import shutil

from . import probe

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INTAKE_DIR = os.path.join(REPO, "entrees")

AUDIO_EXT = {".mp3", ".wav", ".m4a", ".aac", ".ogg", ".flac", ".aiff", ".opus"}
IMAGE_EXT = {".png", ".jpg", ".jpeg", ".webp", ".svg", ".gif", ".bmp", ".tif", ".tiff"}
VIDEO_EXT = {".mp4", ".mov", ".webm", ".mkv", ".m4v", ".avi"}
TEXT_EXT = {".txt", ".md", ".json"}
FONT_EXT = {".ttf", ".otf"}
LOGO_RE = re.compile(r"(logo|marque|brand|embl[eè]me|sigle)", re.I)
IGNORED = {"README.md", ".gitkeep", ".DS_Store"}


# ── Tri ──────────────────────────────────────────────────────────────────────

def _sniff(path: str) -> str:
    """Devine le type d'un fichier sans extension (ex. 'Logo Ma Marque')."""
    with open(path, "rb") as f:
        head = f.read(16)
    if head.startswith(b"\x89PNG") or head[:3] == b"\xff\xd8\xff" or head[:4] == b"RIFF" and b"WEBP" in head:
        return ".png" if head.startswith(b"\x89PNG") else ".jpg" if head[:3] == b"\xff\xd8\xff" else ".webp"
    if head[:3] == b"ID3" or head[:2] in (b"\xff\xfb", b"\xff\xf3", b"\xff\xf2"):
        return ".mp3"
    if head[4:8] == b"ftyp":
        return ".mp4"
    if head.lstrip().startswith(b"<svg") or head.lstrip().startswith(b"<?xml"):
        return ".svg"
    return ""


def classify(path: str) -> str:
    """audio | logo | image | video | text | font | autre"""
    name = os.path.basename(path)
    ext = os.path.splitext(name)[1].lower() or _sniff(path)
    if ext in AUDIO_EXT:
        return "audio"
    if ext in VIDEO_EXT:
        info = probe.probe(path)
        return "video" if info.get("width") else "audio"
    if ext in IMAGE_EXT:
        return "logo" if LOGO_RE.search(name) else "image"
    if ext in TEXT_EXT:
        return "text"
    if ext in FONT_EXT:
        return "font"
    return "autre"


# ── Audio : durée, respirations, transcription ──────────────────────────────

def energy_envelope(path: str, hop: float = 0.05):
    """Enveloppe d'énergie (dB) de l'audio, fenêtres de `hop` secondes."""
    import av
    import numpy as np

    with av.open(path) as c:
        res = av.AudioResampler(format="flt", layout="mono", rate=8000)
        chunks = []
        for fr in c.decode(audio=0):
            for o in res.resample(fr):
                chunks.append(o.to_ndarray().ravel())
    if not chunks:
        return np.zeros(0), hop
    x = np.concatenate(chunks)
    w = max(1, int(hop * 8000))
    n = len(x) // w
    rms = np.sqrt((x[:n * w].reshape(n, w) ** 2).mean(1))
    db = 20 * np.log10(rms + 1e-6)
    return np.convolve(db, np.ones(4) / 4, "same"), hop


def breath_points(path: str, min_gap: float = 0.8, min_depth: float = 6.0) -> list[dict]:
    """Creux d'énergie (respirations, fins de phrase) = bons points de coupe.

    Fonctionne sur un audio déjà mixé (voix + musique), là où une détection de
    silence échoue. Retourne [{t, depth_db}] trié par temps.
    """
    import numpy as np

    s, hop = energy_envelope(path)
    if len(s) < 10:
        return []
    med = float(np.median(s))
    span = max(1, int(min_gap / hop / 2))
    pts = []
    for i in range(2, len(s) - 2):
        win = s[max(0, i - span):i + span + 1]
        if s[i] == win.min() and s[i] < med - min_depth:
            pts.append({"t": round(i * hop, 2), "depth_db": round(med - float(s[i]), 1)})
    return pts


def transcribe(path: str, language: str = "fr") -> list[dict] | None:
    """Transcription horodatée si faster-whisper ET son modèle sont disponibles.

    Retourne [{start, end, text}] ou None (pas de modèle : ce n'est pas une erreur).
    Modèle : MD_WHISPER_MODEL (défaut 'small'). Nécessite l'accès à huggingface.co
    au premier usage, ou un modèle déjà présent en cache.
    """
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        return None
    try:
        model = WhisperModel(os.environ.get("MD_WHISPER_MODEL", "small"), device="cpu",
                             compute_type="int8")
        segs, _ = model.transcribe(path, language=language, vad_filter=False)
        return [{"start": round(s.start, 2), "end": round(s.end, 2), "text": s.text.strip()}
                for s in segs]
    except Exception:  # noqa: BLE001 — modèle indisponible (réseau) : on continue sans
        return None


def analyse_audio(path: str, with_transcript: bool = True) -> dict:
    info = probe.probe(path)
    out = {"file": os.path.relpath(path, REPO), "duration_s": info.get("duration"),
           "breaths": breath_points(path)}
    if with_transcript:
        tr = transcribe(path)
        out["transcript"] = tr
        if tr is None:
            out["transcript_note"] = ("transcription indisponible (modèle Whisper non téléchargé) : "
                                      "caler le texte d'après les détails et les respirations")
    return out


# ── Logo : palette de marque ─────────────────────────────────────────────────

def _hex(rgb) -> str:
    return "#%02X%02X%02X" % tuple(int(max(0, min(255, c))) for c in rgb[:3])


def _mix(a, b, t: float):
    return tuple(a[i] * (1 - t) + b[i] * t for i in range(3))


def logo_palette(path: str, k: int = 6) -> dict:
    """Couleurs dominantes d'un logo (pixels opaques) + couleur d'accent suggérée."""
    from PIL import Image

    with Image.open(path) as im:
        img = im.convert("RGBA")
    img.thumbnail((160, 160))
    px = [p[:3] for p in img.getdata() if p[3] > 160]
    if not px:
        return {"colors": [], "accent": None}
    sample = Image.new("RGB", (len(px), 1))
    sample.putdata(px)
    q = sample.quantize(colors=k, method=Image.Quantize.MEDIANCUT)
    pal = q.getpalette()[:k * 3]
    counts = sorted(q.getcolors(), reverse=True)
    colors = []
    for count, idx in counts:
        rgb = tuple(pal[idx * 3: idx * 3 + 3])
        h, s, v = colorsys.rgb_to_hsv(*(c / 255 for c in rgb))
        colors.append({"hex": _hex(rgb), "share": round(count / len(px), 3),
                       "saturation": round(s, 2), "value": round(v, 2)})
    vivid = [c for c in colors if c["saturation"] > 0.35 and c["value"] > 0.35]
    accent = max(vivid, key=lambda c: c["share"] * (0.5 + c["saturation"]))["hex"] if vivid else None
    return {"colors": colors, "accent": accent}


def brand_from_logo(name: str, logo: str, title: str | None = None,
                    fonts: dict | None = None) -> dict:
    """Kit de marque déduit du logo : accent = couleur vive dominante, fond sombre teinté."""
    from . import lint

    pal = logo_palette(logo)
    accent = pal["accent"] or "#4F8CFF"
    a = tuple(int(accent[i:i + 2], 16) for i in (1, 3, 5))
    night = (11, 15, 26)
    background = _hex(_mix(night, a, 0.05))
    surface = _hex(_mix(night, a, 0.13))
    on_accent = "#0B1020" if lint.contrast(accent, "#0B1020") >= lint.contrast(accent, "#FFFFFF") else "#FFFFFF"
    def far(h: str) -> bool:
        b = tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))
        return sum((x - y) ** 2 for x, y in zip(a, b)) ** 0.5 > 80
    second = next((c["hex"] for c in pal["colors"] if far(c["hex"]) and c["saturation"] > 0.35), None)
    return {
        "title": title or name,
        "colors": {"background": background, "surface": surface, "primary": "#FFFFFF",
                   "accent": accent, "secondary": second or accent, "muted": "#A9B4C8",
                   "text": "#FFFFFF", "on_accent": on_accent},
        "fonts": fonts or {"title": "Montserrat-Black.ttf", "heading": "Montserrat-ExtraBold.ttf",
                           "body": "Montserrat-Bold.ttf"},
        "logo": os.path.relpath(logo, REPO) if os.path.isabs(logo) else logo,
        "_source": "déduit automatiquement du logo (à ajuster si besoin)",
        "_palette_logo": pal["colors"],
    }


# ── Réception complète ───────────────────────────────────────────────────────

def scan(folder: str | None = None, with_transcript: bool = True) -> dict:
    """Inventaire + analyse des éléments déposés. Aucun fichier modifié."""
    folder = folder or INTAKE_DIR
    if not os.path.isdir(folder):
        raise SystemExit(f"ERREUR : dossier d'entrée introuvable : {folder}")
    found: dict[str, list] = {k: [] for k in ("audio", "logo", "image", "video", "text", "font", "autre")}
    for root, _, files in os.walk(folder):
        for f in sorted(files):
            if f in IGNORED or f.startswith("."):
                continue
            p = os.path.join(root, f)
            found[classify(p)].append(p)

    rel = lambda p: os.path.relpath(p, REPO)  # noqa: E731
    report: dict = {"dossier": rel(folder), "fichiers": {k: [rel(p) for p in v] for k, v in found.items() if v}}

    # Audio principal = le plus long (l'audio complet de la pub)
    audios = sorted(found["audio"], key=lambda p: probe.probe(p).get("duration") or 0, reverse=True)
    if audios:
        report["audio"] = analyse_audio(audios[0], with_transcript)
        if len(audios) > 1:
            report["audio_secondaires"] = [rel(p) for p in audios[1:]]

    # Logos (si aucun nommé « logo », une image PNG transparente fera l'affaire)
    logos = found["logo"]
    if not logos:
        logos = [p for p in found["image"] if _has_alpha(p)][:1]
        if logos:
            found["image"].remove(logos[0])
    report["logos"] = [{"file": rel(p), "palette": logo_palette(p)} for p in logos]

    # Détails texte
    details = []
    for p in found["text"]:
        try:
            with open(p, encoding="utf-8", errors="replace") as f:
                details.append({"file": rel(p), "content": f.read()[:20000]})
        except OSError:
            pass
    report["details"] = details

    # Médias complémentaires
    media = []
    for p in found["image"] + found["video"]:
        info = probe.probe(p)
        item = {"file": rel(p), "kind": "video" if p in found["video"] else "image",
                "width": info.get("width"), "height": info.get("height")}
        if item["kind"] == "video":
            item["duration_s"] = info.get("duration")
            item["has_audio"] = bool(info.get("audio"))
        if item["width"] and item["height"]:
            item["orientation"] = ("portrait" if item["height"] > item["width"] * 1.1 else
                                   "paysage" if item["width"] > item["height"] * 1.1 else "carré")
        media.append(item)
    report["medias"] = media
    report["polices"] = [rel(p) for p in found["font"]]

    report["manquants"] = [m for m, ok in (
        ("audio complet de la pub", bool(audios)), ("logo", bool(logos)),
        ("détails texte (.txt)", bool(details))) if not ok]
    report["brief_squelette"] = skeleton(report)
    return report


def _has_alpha(path: str) -> bool:
    try:
        from PIL import Image
        with Image.open(path) as im:
            if im.mode not in ("RGBA", "LA", "P"):
                return False
            alpha = im.convert("RGBA").getchannel("A")
            return alpha.getextrema()[0] < 250
    except Exception:  # noqa: BLE001
        return False


def skeleton(report: dict) -> dict:
    """Brief pré-rempli avec tout ce qui se déduit des fichiers ; le reste à compléter."""
    b: dict = {
        "template": "promo",
        "canvas": "9x16",
        "preset": "mp4-social",
        "hook": "À COMPLÉTER depuis les détails texte",
        "benefits": [],
        "cta": "À COMPLÉTER",
    }
    if report.get("audio"):
        b["audio_master"] = report["audio"]["file"]
        b["sync"] = True
        b["duration"] = report["audio"]["duration_s"]
    if report.get("logos"):
        logo = report["logos"][0]["file"]
        b["logo"] = logo
        # Identité déduite du logo : utilisable telle quelle, sans kit de marque.
        kit = brand_from_logo("auto", os.path.join(REPO, logo))
        b["style"] = {k: kit["colors"][k] for k in ("background", "surface", "accent", "muted",
                                                    "text", "on_accent")}
        b["_marque"] = ("couleurs déduites du logo ; pour un kit réutilisable : "
                        "./md entrees --brand <nom> puis \"brand\": \"<nom>\"")
    if report.get("medias"):
        b["media"] = [{"file": m["file"], "caption": ""} for m in report["medias"]]
    return b


def install(report: dict, brand_name: str | None = None) -> dict:
    """Copie les éléments dans assets/ (bibliothèque) et crée le kit de marque si demandé."""
    done: dict = {"copies": [], "brand": None}
    dest = {"audio": "audio", "logo": "images", "image": "images", "video": "videos", "font": "fonts"}
    for kind, files in report.get("fichiers", {}).items():
        if kind not in dest:
            continue
        for f in files:
            src = os.path.join(REPO, f)
            name = os.path.basename(src)
            if not os.path.splitext(name)[1]:
                name += _sniff(src) or ""
            target = os.path.join(REPO, "assets", dest[kind], name)
            os.makedirs(os.path.dirname(target), exist_ok=True)
            shutil.copy2(src, target)
            done["copies"].append(os.path.relpath(target, REPO))
    if brand_name and report.get("logos"):
        logo_src = os.path.join(REPO, report["logos"][0]["file"])
        name = os.path.basename(logo_src)
        if not os.path.splitext(name)[1]:
            name += _sniff(logo_src) or ".png"
        kit = brand_from_logo(brand_name, os.path.join("assets", "images", name))
        slug = re.sub(r"[^a-z0-9]+", "-", brand_name.lower()).strip("-")
        path = os.path.join(REPO, "brands", f"{slug}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(kit, f, indent=2, ensure_ascii=False)
        done["brand"] = os.path.relpath(path, REPO)
    return done
