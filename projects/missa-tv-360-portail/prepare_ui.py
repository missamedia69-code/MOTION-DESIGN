"""Build truthful animated-UI cutouts from the four client screenshots.

Run from any directory: python3 projects/missa-tv-360-portail/prepare_ui.py
The original PNGs remain untouched. No titles, artwork, playback status or app
controls are generated; the derivative files are only crops of real pixels.
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image

ASSETS = Path(__file__).resolve().parent / "assets"
CROPS = {
    "ui-films-row.png": ("app-films.png", (32, 164, 1268, 478)),
    "ui-mangas-row.png": ("app-mangas.png", (28, 160, 1258, 467)),
    "ui-music-player.png": ("app-music.png", (40, 175, 1260, 488)),
    # These navigation strips are genuine tabs; they do not show unprovided catalog pages.
    "ui-nav-docs.png": ("app-films.png", (591, 8, 959, 86)),
    "ui-nav-tv.png": ("app-music.png", (214, 7, 709, 88)),
    "ui-nav-audio.png": ("app-music.png", (697, 7, 976, 89)),
    # Excludes the unrelated game-title text, but retains the genuine player.
    "app-player-focus.png": ("app-player.png", (57, 185, 474, 453)),
}

for output_name, (source_name, bounds) in CROPS.items():
    with Image.open(ASSETS / source_name) as image:
        if not (0 <= bounds[0] < bounds[2] <= image.width and
                0 <= bounds[1] < bounds[3] <= image.height):
            raise ValueError(f"Invalid crop for {source_name}: {bounds}")
        cropped = image.crop(bounds)
        cropped.save(ASSETS / output_name, optimize=True)
        print(f"{source_name} {bounds} → {output_name} {cropped.size}")
