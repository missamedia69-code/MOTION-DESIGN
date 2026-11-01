"""Rendu de texte en PNG transparent via Pillow (compense l'absence de drawtext).

Chaque calque texte devient une image RGBA exacte (police, taille, couleur,
contour, ombre, interlettrage, alignement, retour à la ligne), ensuite animée
comme un calque image par le moteur de rendu.
"""
from __future__ import annotations

import glob
import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_DIRS = [
    os.path.join(REPO, "assets", "fonts"),
    "/usr/share/fonts",
]


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


def _wrap(draw: ImageDraw.ImageDraw, text: str, font, max_width: int | None) -> list[str]:
    lines: list[str] = []
    for raw in text.split("\n"):
        if not max_width or draw.textlength(raw, font=font) <= max_width:
            lines.append(raw)
            continue
        cur = ""
        for word in raw.split(" "):
            trial = (cur + " " + word).strip()
            if draw.textlength(trial, font=font) <= max_width or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        lines.append(cur)
    return lines


def render_text_png(spec: dict, out_path: str, canvas_w: int, canvas_h: int,
                    project_dir: str | None = None) -> str:
    """Génère le PNG du texte. spec = calque texte du project.json."""
    text = spec.get("text", "")
    size = int(spec.get("size", 64))
    color = spec.get("color", "#ffffff")
    stroke_w = int(spec.get("stroke_width", 0))
    stroke_color = spec.get("stroke_color", "#000000")
    spacing = int(spec.get("letter_spacing", 0))
    align = spec.get("align", "center")  # center|left|right
    max_width = spec.get("max_width")
    shadow = spec.get("shadow")  # {color, blur, offset:[x,y]} ou true
    uppercase = spec.get("uppercase", False)
    if uppercase:
        text = text.upper()

    font_path = find_font(spec.get("font"), project_dir)
    font = ImageFont.truetype(font_path, size)

    tmp = Image.new("RGBA", (16, 16))
    dtmp = ImageDraw.Draw(tmp)
    lines = _wrap(dtmp, text, font, max_width)

    def line_width(s: str) -> float:
        if spacing:
            return sum(dtmp.textlength(ch, font=font) + spacing for ch in s) - (spacing if s else 0)
        return dtmp.textlength(s, font=font)

    ascent, descent = font.getmetrics()
    line_h = int((ascent + descent) * float(spec.get("line_height", 1.15)))
    block_w = int(max((line_width(l) for l in lines), default=1))
    block_h = line_h * len(lines)

    pad = size + (stroke_w * 2) + 40
    W, H = block_w + pad * 2, block_h + pad * 2
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    def draw_lines(target: ImageDraw.ImageDraw, fill, stroke_width=0, stroke_fill=None):
        y = pad
        for l in lines:
            if align == "center":
                x = pad + (block_w - line_width(l)) / 2
            elif align == "right":
                x = pad + (block_w - line_width(l))
            else:
                x = pad
            if spacing:
                for ch in l:
                    target.text((x, y), ch, font=font, fill=fill,
                                stroke_width=stroke_width, stroke_fill=stroke_fill)
                    x += dtmp.textlength(ch, font=font) + spacing
            else:
                target.text((x, y), l, font=font, fill=fill,
                            stroke_width=stroke_width, stroke_fill=stroke_fill)
            y += line_h

    # Ombre (calque flouté décalé)
    if shadow:
        sh = shadow if isinstance(shadow, dict) else {}
        s_color = sh.get("color", "#000000")
        s_blur = int(sh.get("blur", max(4, size // 8)))
        ox, oy = sh.get("offset", [0, max(3, size // 16)])
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ldraw = ImageDraw.Draw(layer)
        draw_lines(ldraw, s_color)
        layer = layer.filter(ImageFilter.GaussianBlur(s_blur))
        img.alpha_composite(layer, (int(ox), int(oy)))
        draw = ImageDraw.Draw(img)

    draw_lines(draw, color, stroke_w, stroke_color if stroke_w else None)

    # Recadre au contenu + petite marge, positionné au centre du bloc
    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    img.save(out_path)
    return out_path


def render_shape_png(spec: dict, out_path: str) -> str:
    """Génère un PNG pour un calque forme (rect / circle / line)."""
    kind = spec.get("kind", "rect")
    w = int(spec.get("w", 400))
    h = int(spec.get("h", 8))
    color = spec.get("color", "#ffffff")
    radius = int(spec.get("radius", 0))
    opacity = float(spec.get("opacity", 1.0))
    img = Image.new("RGBA", (max(w, 1), max(h, 1)), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    fill = color
    if opacity < 1.0:
        from PIL import ImageColor
        rgb = ImageColor.getrgb(color)
        fill = (rgb[0], rgb[1], rgb[2], int(255 * opacity))
    if kind == "circle":
        d.ellipse([0, 0, w - 1, h - 1], fill=fill)
    else:
        d.rounded_rectangle([0, 0, w - 1, h - 1], radius=min(radius, min(w, h) // 2), fill=fill)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    img.save(out_path)
    return out_path
