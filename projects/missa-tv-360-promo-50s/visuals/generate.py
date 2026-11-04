#!/usr/bin/env python3
"""Visuels de travail de la promo MISSA TV 360 (50 s, 9:16).

Produit, sans dépendance externe autre que Pillow :
  - `storyboard/frames/*.png` : 6 plans 540x960
  - `storyboard/planche-storyboard.png` : planche 3x2 avec repères temporels

    python3 projects/missa-tv-360-promo-50s/visuals/generate.py

La mosaïque utilisait des pictogrammes (`pictos/`, tour 8) ; depuis le tour 9
elle consomme les **10 images générées** de `images/*.jpg` (outil image de
l'agent), recadrées en tuiles arrondies. Ces images ne sont pas régénérées par
ce script : elles sont des assets livrés. Palette et assets de marque :
`assets/images/` (logo, box, dégradé, pastille).
"""
from __future__ import annotations

import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
REPO = PROJECT.parents[1]
ASSETS = REPO / "assets"
IMAGES = ASSETS / "images"
FONTS = ASSETS / "fonts"
CONTENT_IMAGES = PROJECT / "images"
FRAME_DIR = PROJECT / "storyboard" / "frames"
SHEET = PROJECT / "storyboard" / "planche-storyboard.png"

W, H = 540, 960
JAUNE = (255, 212, 0)
BLEU_NUIT = (11, 16, 32)
BLEU = (22, 60, 160)
VERT = (0, 166, 81)
ORANGE = (255, 138, 52)
BLANC = (255, 255, 255)
ROUGE = (230, 60, 60)

KINDS = ["films", "manga", "series", "short-drama", "tv-radio",
         "lives", "sport", "docs", "enfants", "jeux-video"]
TILES = [JAUNE, BLEU_NUIT, VERT, BLEU, ORANGE,
         JAUNE, BLEU_NUIT, VERT, BLEU, ORANGE]


def font(size: int, black: bool = False) -> ImageFont.FreeTypeFont:
    name = "Montserrat-Black.ttf" if black else "Montserrat-Bold.ttf"
    return ImageFont.truetype(str(FONTS / name), size)


def glyph_color(tile: tuple[int, int, int]) -> tuple[int, int, int]:
    return BLEU_NUIT if tile in (JAUNE, ORANGE, VERT) else BLANC


def make_picto(kind: str, tile: tuple[int, int, int]) -> Image.Image:
    S = 512
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im, "RGBA")
    d.rounded_rectangle((16, 16, S - 16, S - 16), radius=96, fill=tile + (255,))
    g = glyph_color(tile) + (255,)
    t = tile + (255,)
    w = 16

    if kind == "films":
        d.rounded_rectangle((80, 140, 432, 372), radius=24, outline=g, width=w)
        d.rectangle((80, 140, 432, 190), fill=g)
        d.rectangle((80, 322, 432, 372), fill=g)
        for x in (120, 190, 260, 330, 400):
            d.rounded_rectangle((x - 14, 152, x + 14, 178), radius=6, fill=t)
            d.rounded_rectangle((x - 14, 334, x + 14, 360), radius=6, fill=t)
        d.polygon([(222, 222), (222, 292), (292, 257)], fill=g)
    elif kind == "manga":
        d.rounded_rectangle((90, 110, 422, 402), radius=24, outline=g, width=14)
        d.line((90, 256, 422, 256), fill=g, width=12)
        d.line((256, 110, 256, 402), fill=g, width=12)
        d.ellipse((286, 140, 410, 234), fill=g)
        d.polygon([(306, 224), (300, 272), (348, 230)], fill=g)
        for y in (170, 198):
            d.line((308, y, 388, y), fill=t, width=9)
    elif kind == "series":
        for i in range(3):
            y0 = 110 + i * 100
            d.rounded_rectangle((96, y0, 416, y0 + 76), radius=20, outline=g, width=14)
            d.rounded_rectangle((116, y0 + 18, 196, y0 + 58), radius=8, fill=g)
        d.polygon([(340, 128), (340, 168), (376, 148)], fill=g)
    elif kind == "short-drama":
        d.rounded_rectangle((160, 72, 352, 440), radius=40, outline=g, width=18)
        d.rounded_rectangle((180, 116, 332, 396), radius=14, fill=g)
        d.polygon([(228, 208), (228, 304), (312, 256)], fill=t)
        d.ellipse((238, 410, 274, 428), fill=g)
    elif kind == "tv-radio":
        d.rounded_rectangle((90, 190, 392, 352), radius=22, outline=g, width=18)
        d.line((150, 190, 214, 120), fill=g, width=14)
        d.line((332, 190, 268, 120), fill=g, width=14)
        d.polygon([(196, 238), (196, 304), (262, 271)], fill=g)
        for r in (44, 84):
            d.arc((396 - r, 180 - r, 396 + r, 180 + r), -55, 55, fill=g, width=13)
    elif kind == "lives":
        d.ellipse((150, 150, 362, 362), outline=g, width=18)
        d.ellipse((222, 222, 290, 290), fill=g)
        for r in (130, 180):
            d.arc((256 - r, 256 - r, 256 + r, 256 + r), -50, 50, fill=g, width=14)
            d.arc((256 - r, 256 - r, 256 + r, 256 + r), 130, 230, fill=g, width=14)
        d.ellipse((386, 104, 450, 168), fill=ROUGE + (255,))
    elif kind == "sport":
        d.ellipse((110, 110, 402, 402), outline=g, width=18)
        pts = []
        for i in range(5):
            a = -math.pi / 2 + i * 2 * math.pi / 5
            pts.append((256 + 52 * math.cos(a), 256 + 52 * math.sin(a)))
        d.polygon(pts, fill=g)
        for i in range(5):
            a = -math.pi / 2 + i * 2 * math.pi / 5
            d.line((256 + 52 * math.cos(a), 256 + 52 * math.sin(a),
                    256 + 145 * math.cos(a), 256 + 145 * math.sin(a)), fill=g, width=12)
        d.ellipse((110, 110, 402, 402), outline=g, width=18)
    elif kind == "docs":
        d.rounded_rectangle((80, 180, 432, 352), radius=26, outline=g, width=18)
        d.rectangle((140, 142, 226, 180), fill=g)
        d.ellipse((206, 212, 306, 312), outline=g, width=18)
        d.ellipse((238, 244, 274, 280), fill=g)
    elif kind == "enfants":
        pts = []
        for i in range(10):
            a = -math.pi / 2 + i * math.pi / 5
            r = 118 if i % 2 == 0 else 52
            pts.append((256 + r * math.cos(a), 236 + r * math.sin(a)))
        d.polygon(pts, fill=g)
        for cx, cy, r in ((120, 380, 26), (392, 380, 26), (256, 410, 20)):
            d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=g)
    elif kind == "jeux-video":
        d.rounded_rectangle((66, 186, 446, 354), radius=76, outline=g, width=18)
        d.rounded_rectangle((126, 252, 210, 272), radius=6, fill=g)
        d.rounded_rectangle((158, 220, 178, 304), radius=6, fill=g)
        for cx, cy in ((320, 232), (372, 272), (320, 312), (268, 272)):
            d.ellipse((cx - 19, cy - 19, cx + 19, cy + 19), fill=g)
    return im


def load_image(name: str, size: tuple[int, int]) -> Image.Image:
    return Image.open(IMAGES / name).convert("RGBA").resize(size, Image.Resampling.LANCZOS)


def new_frame() -> Image.Image:
    return Image.open(IMAGES / "fond-degrade.png").convert("RGBA").resize(
        (W, H), Image.Resampling.LANCZOS)


def draw_subtitle(im: Image.Image, lines: list[str]) -> None:
    d = ImageDraw.Draw(im, "RGBA")
    f = font(24)
    wrapped: list[str] = []
    for line in lines:
        cur = ""
        for word in line.split():
            cand = (cur + " " + word).strip()
            if d.textbbox((0, 0), cand, font=f)[2] <= 450:
                cur = cand
            else:
                wrapped.append(cur)
                cur = word
        if cur:
            wrapped.append(cur)
    h = len(wrapped) * 32 + 30
    top = H - 56 - h
    d.rounded_rectangle((24, top, W - 24, H - 40), radius=22, fill=(6, 10, 22, 255))
    for i, line in enumerate(wrapped):
        d.text((W // 2, top + 15 + i * 32 + 16), line, font=f,
               fill=(255, 255, 255, 255), anchor="mm")


def draw_qr(d: ImageDraw.ImageDraw, x: int, y: int, size: int) -> None:
    n, cell = 21, size / 21
    rng = random.Random(360)
    for i in range(n):
        for j in range(n):
            if rng.random() < 0.48:
                d.rectangle((x + j * cell, y + i * cell, x + (j + 1) * cell,
                             y + (i + 1) * cell), fill=(255, 255, 255, 255))
    for fi, fj in ((0, 0), (0, 14), (14, 0)):
        d.rectangle((x + fj * cell, y + fi * cell, x + (fj + 7) * cell,
                     y + (fi + 7) * cell), fill=BLEU_NUIT + (255,))
        d.rectangle((x + (fj + 1) * cell, y + (fi + 1) * cell,
                     x + (fj + 6) * cell, y + (fi + 6) * cell), fill=(255, 255, 255, 255))
        d.rectangle((x + (fj + 2) * cell, y + (fi + 2) * cell,
                     x + (fj + 5) * cell, y + (fi + 5) * cell), fill=BLEU_NUIT + (255,))


def frame_01() -> Image.Image:
    im = new_frame()
    d = ImageDraw.Draw(im, "RGBA")
    d.polygon([(0, 0), (W, 0), (W, 120), (0, 280)], fill=JAUNE + (255,))
    im.alpha_composite(load_image("logo-missa.png", (300, 300)), (120, 260))
    d.text((W // 2, 640), "EN AFRIQUE, ON PAIE…", font=font(30, True),
           fill=BLANC + (255,), anchor="mm")
    d.rounded_rectangle((190, 672, 350, 680), radius=4, fill=JAUNE + (255,))
    draw_subtitle(im, ["En Afrique, on paie… et on n'a rien à regarder."])
    return im


def frame_02() -> Image.Image:
    im = new_frame()
    d = ImageDraw.Draw(im, "RGBA")
    d.rounded_rectangle((40, 92, 500, 168), radius=38, fill=(18, 30, 64, 255),
                        outline=JAUNE + (255,), width=3)
    d.ellipse((68, 112, 108, 152), outline=JAUNE + (255,), width=5)
    d.line((106, 150, 130, 166), fill=JAUNE + (255,), width=5)
    d.rounded_rectangle((150, 122, 420, 132), radius=5, fill=(140, 165, 215, 255))
    im.alpha_composite(load_image("box-mtn-cutout.png", (140, 140)), (375, 8))
    tw, th = 215, 106
    for i, kind in enumerate(KINDS):
        col, row = i % 2, i // 2
        x, y = 40 + col * 235, 190 + row * 118
        src = Image.open(CONTENT_IMAGES / f"{kind}.jpg").convert("RGB")
        tile_img = ImageOps.fit(src, (tw, th), method=Image.Resampling.LANCZOS,
                                centering=(0.5, 0.5))
        mask = Image.new("L", (tw, th), 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, tw, th), radius=22, fill=255)
        im.paste(tile_img, (x, y), mask)
        d.rounded_rectangle((x, y, x + tw, y + th), radius=22,
                            outline=JAUNE + (255,), width=2)
    draw_subtitle(im, ["Avec votre box WiFi ou votre connexion, tapez un film, une série, un manga."])
    return im


def frame_03() -> Image.Image:
    im = new_frame()
    d = ImageDraw.Draw(im, "RGBA")
    im.alpha_composite(load_image("pastille.png", (110, 110)), (40, 120))
    for i in range(4):
        hh = 26 + i * 24
        color = JAUNE + (255,) if i < 2 else (74, 94, 136, 255)
        d.rounded_rectangle((150 + i * 46, 400 - hh, 150 + i * 46 + 32, 400),
                            radius=6, fill=color)
    d.text((W // 2, 470), "FAIBLE DÉBIT", font=font(30, True),
           fill=BLANC + (255,), anchor="mm")
    d.text((W // 2, 516), "STABLE · ÉCONOME", font=font(22),
           fill=JAUNE + (255,), anchor="mm")
    d.arc((170, 570, 370, 770), 0, 300, fill=VERT + (255,), width=18)
    d.text((W // 2, 670), "DATA", font=font(34, True), fill=BLANC + (255,), anchor="mm")
    draw_subtitle(im, ["Et même avec un faible débit, ça reste stable. Pas de coupures, et l'appli économise vos données."])
    return im


def frame_04() -> Image.Image:
    im = new_frame()
    d = ImageDraw.Draw(im, "RGBA")
    im.alpha_composite(load_image("pastille.png", (360, 360)), (90, 220))
    d.text((W // 2, 400), "24 H", font=font(92, True), fill=BLEU_NUIT + (255,), anchor="mm")
    d.text((W // 2, 630), "ESSAI GRATUIT", font=font(30, True),
           fill=JAUNE + (255,), anchor="mm")
    draw_subtitle(im, ["Vingt-quatre heures pour tout essayer. Gratuitement. Ouvrez, cherchez, regardez."])
    return im


def frame_05() -> Image.Image:
    im = new_frame()
    d = ImageDraw.Draw(im, "RGBA")
    d.text((W // 2, 110), "1 000 XAF / MOIS", font=font(36, True),
           fill=BLANC + (255,), anchor="mm")
    d.text((W // 2, 178), "10 000 XAF / AN", font=font(44, True),
           fill=JAUNE + (255,), anchor="mm")
    draw_qr(d, 180, 250, 180)
    d.rounded_rectangle((60, 480, 480, 550), radius=18, fill=(18, 30, 64, 255),
                        outline=JAUNE + (255,), width=3)
    d.text((84, 515), "CODE D'ACTIVATION", font=font(19),
           fill=(190, 205, 235, 255), anchor="lm")
    d.text((456, 515), "•••• ••••", font=font(22), fill=BLANC + (255,), anchor="rm")
    d.rounded_rectangle((170, 580, 370, 640), radius=30, fill=JAUNE + (255,))
    d.text((W // 2, 610), "ACTIVER", font=font(28, True),
           fill=BLEU_NUIT + (255,), anchor="mm")
    draw_subtitle(im, ["Après, prenez votre code. Un mois, deux, trois, comme vous voulez."])
    return im


def frame_06() -> Image.Image:
    im = Image.new("RGBA", (W, H), JAUNE + (255,))
    d = ImageDraw.Draw(im, "RGBA")
    im.alpha_composite(load_image("logo-missa.png", (320, 320)), (110, 220))
    d.text((W // 2, 630), "ACTIVEZ VOTRE CODE", font=font(36, True),
           fill=BLEU_NUIT + (255,), anchor="mm")
    d.text((W // 2, 690), "10 000 XAF / AN", font=font(26, True),
           fill=BLEU + (255,), anchor="mm")
    draw_subtitle(im, ["MISSA TV 360. Activez votre code. Et ne ratez plus rien."])
    return im


LABELS = [
    "01 · 00–05 s · Accroche « En Afrique »",
    "02 · 05–20 s · Mosaïque des 10 univers",
    "03 · 20–28 s · Faible débit / données",
    "04 · 28–34 s · Essai 24 h",
    "05 · 34–44 s · Prix + activation",
    "06 · 44–50 s · Signature",
]


def main() -> None:
    missing = [k for k in KINDS if not (CONTENT_IMAGES / f"{k}.jpg").exists()]
    if missing:
        raise SystemExit(f"Images de contenu manquantes : {', '.join(missing)}")
    FRAME_DIR.mkdir(parents=True, exist_ok=True)
    frames = [frame_01(), frame_02(), frame_03(), frame_04(), frame_05(), frame_06()]
    for i, frame in enumerate(frames, 1):
        frame.convert("RGB").save(FRAME_DIR / f"plan-{i:02d}.png")
    bar = 52
    sheet = Image.new("RGB", (3 * W, 2 * (H + bar)), BLEU_NUIT)
    sd = ImageDraw.Draw(sheet)
    f = font(22)
    for i, (frame, label) in enumerate(zip(frames, LABELS)):
        col, row = i % 3, i // 3
        x, y = col * W, row * (H + bar)
        sheet.paste(frame.convert("RGB"), (x, y + bar))
        sd.text((x + 18, y + bar // 2), label, font=f, fill=JAUNE, anchor="lm")
    sheet.save(SHEET)
    print(f"✅ {len(KINDS)} images de contenu intégrées → {CONTENT_IMAGES.relative_to(REPO)}")
    print(f"✅ {len(frames)} plans → {FRAME_DIR.relative_to(REPO)}")
    print(f"✅ planche → {SHEET.relative_to(REPO)} ({sheet.width}x{sheet.height})")


if __name__ == "__main__":
    main()
