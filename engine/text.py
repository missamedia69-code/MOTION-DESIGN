"""Rendu Pillow des calques générés : texte, formes, dégradés, compteurs.

Chaque calque texte devient une image RGBA exacte (police, taille, couleur,
contour, ombre, pastille de fond, interlettrage, alignement, retour à la
ligne), ensuite animée comme un calque image par le moteur de rendu.

Texte cinétique : `render_text_tokens` découpe le texte (mot, ligne, lettre)
en N images **de même taille et même cadrage** que le bloc complet — chaque
image ne contient qu'un morceau. Superposées au même endroit, elles
reconstituent exactement le texte, et peuvent apparaître en cascade.
"""
from __future__ import annotations

import glob
import math
import os

from PIL import Image, ImageColor, ImageDraw, ImageFilter, ImageFont

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_DIRS = [
    os.path.join(REPO, "assets", "fonts"),
    "/usr/share/fonts",
]
MAX_TOKENS = 40


# ── Polices ──────────────────────────────────────────────────────────────────

def list_fonts() -> list[dict]:
    fonts = []
    for d in FONT_DIRS:
        for p in sorted(glob.glob(os.path.join(d, "**", "*.ttf"), recursive=True) +
                        glob.glob(os.path.join(d, "**", "*.otf"), recursive=True)):
            fonts.append({"file": os.path.basename(p), "path": p,
                          "source": "assets" if d.startswith(REPO) else "système"})
    return fonts


def find_font(name: str | None, project_dir: str | None = None) -> str:
    """Résout une police : nom de fichier, chemin, ou défaut."""
    candidates: list[str] = []
    if name:
        if os.path.isabs(name) and os.path.exists(name):
            return name
        search_dirs = list(FONT_DIRS)
        if project_dir:
            search_dirs.insert(0, project_dir)
        for d in search_dirs:
            hits = glob.glob(os.path.join(d, "**", name), recursive=True)
            candidates += hits
            if not os.path.splitext(name)[1]:
                for ext in (".ttf", ".otf"):
                    candidates += glob.glob(os.path.join(d, "**", name + ext), recursive=True)
        for c in candidates:
            if os.path.exists(c):
                return c
    # Défaut : DejaVu Sans Bold si dispo, sinon première police trouvée
    for d in FONT_DIRS:
        for pat in ("**/DejaVuSans-Bold.ttf", "**/*.ttf", "**/*.otf"):
            hits = sorted(glob.glob(os.path.join(d, pat), recursive=True))
            if hits:
                return hits[0]
    raise FileNotFoundError("Aucune police TTF/OTF trouvée (assets/fonts ou /usr/share/fonts).")


def font_exists(name: str | None, project_dir: str | None = None) -> bool:
    """True si la police demandée existe vraiment (pas de repli silencieux)."""
    if not name:
        return True
    try:
        path = find_font(name, project_dir)
    except FileNotFoundError:
        return False
    return os.path.basename(path).lower() == os.path.basename(name).lower() or \
        os.path.splitext(os.path.basename(path))[0].lower() == name.lower()


def _rgba(color, opacity: float = 1.0) -> tuple[int, int, int, int]:
    rgb = ImageColor.getrgb(color)
    a = rgb[3] if len(rgb) == 4 else 255
    return rgb[0], rgb[1], rgb[2], int(a * max(0.0, min(1.0, opacity)))


# ── Mise en page du texte ────────────────────────────────────────────────────

def _wrap(draw: ImageDraw.ImageDraw, text: str, font, max_width: int | None) -> list[str]:
    lines: list[str] = []
    for raw in text.split("\n"):
        if not max_width or draw.textlength(raw, font=font) <= max_width:
            lines.append(raw)
            continue
        cur = ""
        # Typographie : « % ? ! : ; € » ne commencent jamais une ligne.
        words: list[str] = []
        for w in raw.split(" "):
            if words and w and all(ch in "%?!:;€$»)" for ch in w):
                words[-1] += " " + w
            else:
                words.append(w)
        for word in words:
            trial = (cur + " " + word).strip()
            if draw.textlength(trial, font=font) <= max_width or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        lines.append(cur)
    return lines


class _TextLayout:
    """Calcule la géométrie d'un bloc texte une seule fois (partagée par les tokens)."""

    def __init__(self, spec: dict, project_dir: str | None = None):
        text = str(spec.get("text", ""))
        if spec.get("uppercase"):
            text = text.upper()
        self.size = max(4, int(round(float(spec.get("size", 64)))))
        self.color = spec.get("color", "#ffffff")
        self.stroke_w = int(round(float(spec.get("stroke_width", 0))))
        self.stroke_color = spec.get("stroke_color", "#000000")
        self.spacing = float(spec.get("letter_spacing", 0))
        self.align = spec.get("align", "center")
        max_width = spec.get("max_width")
        self.max_width = int(max_width) if max_width else None
        self.shadow = spec.get("shadow")
        self.box = spec.get("box")
        self.font = ImageFont.truetype(find_font(spec.get("font"), project_dir), self.size)

        tmp = Image.new("RGBA", (16, 16))
        self.dtmp = ImageDraw.Draw(tmp)
        self.lines = _wrap(self.dtmp, text, self.font, self.max_width)
        ascent, descent = self.font.getmetrics()
        self.line_h = int((ascent + descent) * float(spec.get("line_height", 1.15)))
        self.block_w = int(max((self.line_width(l) for l in self.lines), default=1)) or 1
        self.block_h = self.line_h * len(self.lines)

        bpad = self._box_padding()
        self.pad = self.size + self.stroke_w * 2 + 40 + max(bpad)
        self.W = self.block_w + self.pad * 2
        self.H = self.block_h + self.pad * 2

    def _box_padding(self) -> tuple[int, int]:
        if not self.box:
            return 0, 0
        box = self.box if isinstance(self.box, dict) else {}
        pad = box.get("padding", [int(self.size * 0.45), int(self.size * 0.22)])
        if isinstance(pad, (int, float)):
            pad = [pad, pad]
        return int(pad[0]), int(pad[1])

    def line_width(self, s: str) -> float:
        if self.spacing:
            return sum(self.dtmp.textlength(ch, font=self.font) + self.spacing for ch in s) \
                - (self.spacing if s else 0)
        return self.dtmp.textlength(s, font=self.font)

    def glyphs(self):
        """Itère (index_ligne, index_mot, index_lettre, x, y, caractère)."""
        y = self.pad
        word_i = char_i = 0
        for li, line in enumerate(self.lines):
            lw = self.line_width(line)
            if self.align == "center":
                x = self.pad + (self.block_w - lw) / 2
            elif self.align == "right":
                x = self.pad + (self.block_w - lw)
            else:
                x = self.pad
            prev_space = True  # chaque ligne commence un nouveau mot
            for ch in line:
                if ch == " ":
                    prev_space = True
                else:
                    if prev_space and char_i:
                        word_i += 1
                    prev_space = False
                yield li, word_i, char_i, x, y, ch
                x += self.dtmp.textlength(ch, font=self.font) + self.spacing
                if ch != " ":
                    char_i += 1
            y += self.line_h

    def draw(self, img: Image.Image, keep=None, fill=None, stroke=True,
             offset=(0, 0)) -> None:
        """Dessine les glyphes retenus par `keep(li, wi, ci)` (None = tous)."""
        draw = ImageDraw.Draw(img)
        fill = fill or self.color
        ox, oy = offset
        if keep is None and not self.spacing:
            # Chemin rapide : ligne entière (meilleur crénage)
            y = self.pad
            for line in self.lines:
                lw = self.line_width(line)
                x = self.pad + ((self.block_w - lw) / 2 if self.align == "center"
                                else (self.block_w - lw) if self.align == "right" else 0)
                draw.text((x + ox, y + oy), line, font=self.font, fill=fill,
                          stroke_width=self.stroke_w if stroke else 0,
                          stroke_fill=self.stroke_color if stroke and self.stroke_w else None)
                y += self.line_h
            return
        for li, wi, ci, x, y, ch in self.glyphs():
            if ch == " " or (keep is not None and not keep(li, wi, ci)):
                continue
            draw.text((x + ox, y + oy), ch, font=self.font, fill=fill,
                      stroke_width=self.stroke_w if stroke else 0,
                      stroke_fill=self.stroke_color if stroke and self.stroke_w else None)

    def render(self, keep=None, with_box: bool = True) -> Image.Image:
        img = Image.new("RGBA", (self.W, self.H), (0, 0, 0, 0))
        if with_box and self.box:
            box = self.box if isinstance(self.box, dict) else {}
            px, py = self._box_padding()
            radius = int(box.get("radius", self.size * 0.3))
            fill = _rgba(box.get("color", "#000000"), float(box.get("opacity", 1.0)))
            ImageDraw.Draw(img).rounded_rectangle(
                [self.pad - px, self.pad - py,
                 self.pad + self.block_w + px, self.pad + self.block_h + py],
                radius=radius, fill=fill)
        if self.shadow:
            sh = self.shadow if isinstance(self.shadow, dict) else {}
            s_blur = int(sh.get("blur", max(4, self.size // 8)))
            ox, oy = sh.get("offset", [0, max(3, self.size // 16)])
            layer = Image.new("RGBA", (self.W, self.H), (0, 0, 0, 0))
            self.draw(layer, keep, fill=_rgba(sh.get("color", "#000000"),
                                              float(sh.get("opacity", 0.85))), stroke=False)
            layer = layer.filter(ImageFilter.GaussianBlur(s_blur))
            img.alpha_composite(layer, (int(ox), int(oy)))
        self.draw(img, keep)
        return img

    def token_count(self, split: str) -> int:
        if split == "line":
            return len(self.lines)
        last = None
        for li, wi, ci, *_rest in self.glyphs():
            last = (li, wi, ci)
        if last is None:
            return 0
        return (last[1] + 1) if split == "word" else (last[2] + 1)


def render_text_png(spec: dict, out_path: str, canvas_w: int = 0, canvas_h: int = 0,
                    project_dir: str | None = None) -> str:
    """Génère le PNG du texte. spec = calque texte du project.json."""
    lay = _TextLayout(spec, project_dir)
    img = lay.render()
    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    img.save(out_path)
    return out_path


def render_text_tokens(spec: dict, out_dir: str, tag: str,
                       project_dir: str | None = None) -> list[str]:
    """Texte cinétique : une image par mot/ligne/lettre, toutes au même cadrage.

    La pastille (`box`) éventuelle est rendue comme token 0 (elle apparaît
    en premier, le texte se pose dessus).
    """
    split = spec.get("split", "word")
    if split not in ("word", "line", "char"):
        raise SystemExit(f"ERREUR : split '{split}' inconnu (word|line|char)")
    lay = _TextLayout(spec, project_dir)
    full = lay.render(keep=lambda *_: True)
    bbox = full.getbbox() or (0, 0, lay.W, lay.H)
    n = lay.token_count(split)
    if n > MAX_TOKENS:
        raise SystemExit(f"ERREUR : texte cinétique trop long ({n} {split}s > {MAX_TOKENS}). "
                         "Utiliser split='word' ou 'line', ou raccourcir le texte.")
    os.makedirs(out_dir, exist_ok=True)
    paths = []
    if lay.box:
        box_img = Image.new("RGBA", (lay.W, lay.H), (0, 0, 0, 0))
        saved_shadow, lay.shadow = lay.shadow, None
        tmp = lay.render(keep=lambda *_: False)
        lay.shadow = saved_shadow
        box_img.alpha_composite(tmp)
        p = os.path.join(out_dir, f"{tag}_box.png")
        box_img.crop(bbox).save(p)
        paths.append(p)
    for k in range(n):
        if split == "line":
            keep = (lambda kk: lambda li, wi, ci: li == kk)(k)
        elif split == "word":
            keep = (lambda kk: lambda li, wi, ci: wi == kk)(k)
        else:
            keep = (lambda kk: lambda li, wi, ci: ci == kk)(k)
        img = lay.render(keep=keep, with_box=False)
        p = os.path.join(out_dir, f"{tag}_tok{k:02d}.png")
        img.crop(bbox).save(p)
        paths.append(p)
    return paths


# ── Compteur animé ───────────────────────────────────────────────────────────

def format_number(value: float, decimals: int = 0, sep: str = " ",
                  decimal_sep: str = ",") -> str:
    s = f"{abs(value):,.{decimals}f}"
    s = s.replace(",", "\x00").replace(".", decimal_sep).replace("\x00", sep)
    return ("-" if value < 0 else "") + s


def render_counter_frames(spec: dict, out_dir: str, tag: str, fps: float,
                          project_dir: str | None = None) -> tuple[str, int]:
    """Images d'un compteur (from → to) avec easing. Retourne (motif %03d, nb)."""
    from . import easing

    v0 = float(spec.get("from", 0))
    v1 = float(spec.get("to", spec.get("value", 100)))
    dur = max(0.2, float(spec.get("count_duration", 1.5)))
    decimals = int(spec.get("decimals", 0))
    sep = spec.get("thousands", " ")
    dsep = spec.get("decimal_sep", ",")
    prefix, suffix = str(spec.get("prefix", "")), str(spec.get("suffix", ""))
    curve = spec.get("ease", "expo_out")
    n = max(2, int(round(dur * fps)) + 1)

    def label(v: float) -> str:
        return f"{prefix}{format_number(v, decimals, sep, dsep)}{suffix}"

    # Cadre commun = la valeur la plus large (pas de tremblement de mise en page)
    widest = max((label(v0), label(v1)), key=len)
    base = dict(spec, text=widest)
    lay = _TextLayout(base, project_dir)
    probe = lay.render()
    bbox = probe.getbbox() or (0, 0, lay.W, lay.H)
    bw, bh = bbox[2] - bbox[0], bbox[3] - bbox[1]
    bw += bw % 2
    bh += bh % 2
    os.makedirs(out_dir, exist_ok=True)
    pattern = os.path.join(out_dir, f"{tag}_cnt%03d.png")
    for i in range(n):
        p = i / (n - 1)
        v = v0 + (v1 - v0) * easing.evaluate(curve, p)
        v = round(v, decimals)
        layf = _TextLayout(dict(spec, text=label(v)), project_dir)
        img = layf.render()
        ib = img.getbbox() or (0, 0, layf.W, layf.H)
        glyph = img.crop(ib)
        frame = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
        align = spec.get("align", "center")
        if align == "left":
            x = 0
        elif align == "right":
            x = bw - glyph.width
        else:
            x = (bw - glyph.width) // 2
        frame.alpha_composite(glyph, (max(0, x), max(0, (bh - glyph.height) // 2)))
        frame.save(pattern % i)
    return pattern, n


# ── Formes et dégradés ───────────────────────────────────────────────────────

def _gradient_image(w: int, h: int, stops: list[str], angle: float = 90,
                    kind: str = "linear") -> Image.Image:
    """Dégradé multi-arrêts (linéaire orienté ou radial) en RGBA."""
    import numpy as np

    cols = np.array([_rgba(c) for c in stops], dtype=np.float32)
    if len(cols) == 1:
        cols = np.vstack([cols, cols])
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    if kind == "radial":
        cx, cy = (w - 1) / 2, (h - 1) / 2
        t = np.sqrt(((xx - cx) / max(cx, 1)) ** 2 + ((yy - cy) / max(cy, 1)) ** 2) / math.sqrt(2)
        t = np.clip(t * 1.25, 0, 1)
    else:
        a = math.radians(angle)
        dx, dy = math.sin(a), -math.cos(a)   # 0° = bas→haut, 90° = gauche→droite
        proj = (xx - w / 2) * dx + (yy - h / 2) * dy
        span = abs(w / 2 * dx) + abs(h / 2 * dy) or 1
        t = np.clip((proj / span + 1) / 2, 0, 1)
    seg = t * (len(cols) - 1)
    i0 = np.clip(np.floor(seg).astype(int), 0, len(cols) - 2)
    f = (seg - i0)[..., None]
    out = cols[i0] * (1 - f) + cols[i0 + 1] * f
    return Image.fromarray(out.round().astype(np.uint8), "RGBA")


def render_gradient_png(spec: dict, w: int, h: int, out_path: str) -> str:
    """Fond dégradé : {"gradient": ["#a", "#b", ...], "angle": 135, "type": "linear|radial"}."""
    img = _gradient_image(w, h, list(spec.get("gradient") or ["#000000", "#333333"]),
                          float(spec.get("angle", 180)), spec.get("type", "linear"))
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    img.save(out_path)
    return out_path


SHAPE_KINDS = ["rect", "circle", "ring", "line", "triangle"]


def render_shape_png(spec: dict, out_path: str) -> str:
    """Génère un PNG pour un calque forme.

    kind : rect | circle | ring (anneau) | line | triangle
    Options : color, gradient [..] + angle, radius, opacity,
              stroke / stroke_color (contour), ring_width.
    """
    kind = spec.get("kind", "rect")
    if kind not in SHAPE_KINDS:
        raise SystemExit(f"ERREUR : forme '{kind}' inconnue ({', '.join(SHAPE_KINDS)})")
    w = max(1, int(round(float(spec.get("w", 400)))))
    h = max(1, int(round(float(spec.get("h", 8)))))
    color = spec.get("color", "#ffffff")
    radius = int(round(float(spec.get("radius", 0))))
    opacity = float(spec.get("opacity", 1.0))
    stroke = int(round(float(spec.get("stroke", 0))))
    stroke_color = spec.get("stroke_color", "#ffffff")

    # Masque de la forme (en L), rempli ensuite par couleur ou dégradé.
    ss = 4 if kind in ("circle", "ring", "triangle") or radius else 1  # anticrénelage
    mw, mh = w * ss, h * ss
    mask = Image.new("L", (mw, mh), 0)
    md = ImageDraw.Draw(mask)
    outline = None
    if kind == "circle":
        md.ellipse([0, 0, mw - 1, mh - 1], fill=255)
    elif kind == "ring":
        rw = int(round(float(spec.get("ring_width", max(2, min(w, h) * 0.08))))) * ss
        md.ellipse([0, 0, mw - 1, mh - 1], fill=255)
        md.ellipse([rw, rw, mw - 1 - rw, mh - 1 - rw], fill=0)
    elif kind == "triangle":
        md.polygon([(mw / 2, 0), (mw - 1, mh - 1), (0, mh - 1)], fill=255)
    else:  # rect, line
        r = min(radius * ss, min(mw, mh) // 2)
        md.rounded_rectangle([0, 0, mw - 1, mh - 1], radius=r, fill=255)
    if ss > 1:
        mask = mask.resize((w, h), Image.LANCZOS)
    if stroke and kind in ("rect", "circle"):
        outline = Image.new("L", (w * ss, h * ss), 0)
        od = ImageDraw.Draw(outline)
        sw = stroke * ss
        if kind == "circle":
            od.ellipse([0, 0, w * ss - 1, h * ss - 1], outline=255, width=sw)
        else:
            r = min(radius * ss, min(w, h) * ss // 2)
            od.rounded_rectangle([0, 0, w * ss - 1, h * ss - 1], radius=r, outline=255, width=sw)
        if ss > 1:
            outline = outline.resize((w, h), Image.LANCZOS)

    if spec.get("gradient"):
        fill = _gradient_image(w, h, list(spec["gradient"]), float(spec.get("angle", 90)),
                               spec.get("gradient_type", "linear"))
    elif spec.get("fill") is False or color in (None, "none", "transparent"):
        fill = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        mask = Image.new("L", (w, h), 0)
    else:
        fill = Image.new("RGBA", (w, h), _rgba(color))
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    img.paste(fill, (0, 0), mask)
    if outline is not None:
        img.paste(Image.new("RGBA", (w, h), _rgba(stroke_color)), (0, 0), outline)
    if opacity < 1.0:
        a = img.getchannel("A").point(lambda v: int(v * max(0.0, opacity)))
        img.putalpha(a)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    img.save(out_path)
    return out_path
