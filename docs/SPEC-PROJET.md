# Spécification `project.json`

Un projet = un dossier `projects/<nom>/` contenant `project.json`.
Le montage est **déclaratif** : le moteur compile ce fichier en graphe ffmpeg.

## Structure générale

```jsonc
{
  "name": "mon-projet",
  "title": "Titre lisible",
  "canvas": "9x16",              // preset (16x9|9x16|1x1|4x5|21x9|720p)
                                 // OU objet {"width":1080,"height":1920,"fps":30}
  "export": {
    "preset": "mp4-hq",          // mp4-hq|mp4-web|mp4-h265|gif|webm-vp9|mov-alpha
    "filename": "livrable.mp4"   // optionnel (déposé dans .cache/rendus/, livré en artefact)
  },
  "transitions": { "type": "fade", "duration": 0.5 },  // entre scènes (xfade)
  "audio": {                     // piste musicale (optionnelle)
    "file": "assets/audio/track.mp3",
    "volume": 0.8, "fade_in": 0.5, "fade_out": 1.5, "in": 0
  },
  "duration": 6,                 // durée si une seule scène
  "background": "#0b1020",       // couleur #hex OU chemin d'image OU "transparent"
  "layers": [ ... ],             // mode une scène
  "scenes": [ ... ]              // mode multi-scènes (remplace layers/duration/background)
}
```

**Mode multi-scènes** : `scenes: [ {"duration":4, "background":"#...", "layers":[...],
"transition":{"type":"slideleft","duration":0.6}}, ... ]` — la `transition` d'une scène
régle l'enchaînement **vers la suivante**. Transitions : `fade, fadeblack, fadewhite,
wipeleft, wiperight, wipeup, wipedown, slideleft, slideright, slideup, slidedown,
circleopen, circleclose, dissolve, pixelize, zoomin…` (`./md presets`).

## Calques (`layers`)

Ordre dans la liste = ordre d'empilement (premier = plus en dessous).
Fenêtre temporelle : `in` / `out` en **secondes** (timeline de la scène).

### Communs à tous les calques

| Clé | Type | Défaut | Description |
|---|---|---|---|
| `in` / `out` | float | 0 / fin | fenêtre d'apparition (s) |
| `pos` | string \| [x,y] | `"center"` | `center, top, bottom, top_third, bottom_third` ou `[x,y]` = **centre** du calque en px |
| `anim` | string | `none` | voir table des animations |
| `anim_duration` | float | 0.6 | durée des anims slide/pop/grow |
| `amplitude` | float | 80 | distance des slides (px) |

### `type: "image"`

| Clé | Défaut | Description |
|---|---|---|
| `file` | — | chemin (relatif racine, projet, ou nom dans assets/) |
| `fit` | `contain` | `cover` (remplit/rogne), `contain` (entier), `stretch`, `original` |
| `full_bleed` | false | true → `cover` pleine canvas |
| `scale` | — | `{"w":400}` ou `{"w":400,"h":300}` taille explicite |
| `fade_in` / `fade_out` | 0.5 | pour les anims `fade*` |

### `type: "text"` (rendu Pillow → PNG, animé comme image)

| Clé | Défaut | Description |
|---|---|---|
| `text` | — | contenu, `\n` = saut de ligne |
| `font` | DejaVuSans-Bold | nom de fichier dans `assets/fonts/` ou `/usr/share/fonts` |
| `size` | 64 | corps en px |
| `color` | `#ffffff` | couleur |
| `align` | `center` | `center` \| `left` \| `right` |
| `max_width` | — | retour à la ligne automatique (px) |
| `letter_spacing` | 0 | interlettrage (px) |
| `line_height` | 1.15 | interlignage (×) |
| `uppercase` | false | force les capitales |
| `stroke_width` / `stroke_color` | 0 / `#000` | contour |
| `shadow` | — | `true` ou `{"color":"#000","blur":8,"offset":[0,6]}` |
| `fit` | `original` | généralement laisser tel quel |

### `type: "shape"` (généré à la volée)

| Clé | Défaut | Description |
|---|---|---|
| `kind` | `rect` | `rect` \| `circle` |
| `w` / `h` | 400 / 8 | dimensions px |
| `radius` | 0 | coins arrondis (rect) |
| `color` | `#ffffff` | couleur |
| `opacity` | 1.0 | 0→1 |

### `type: "video"`

| Clé | Défaut | Description |
|---|---|---|
| `file` | — | chemin du rush |
| `src_in` | 0 | point d'entrée **dans le rush** (s) |
| `fit` | `cover` | idem image |
| `fade_in` / `fade_out` | 0.5 | fondus alpha |

L'audio des rushes est ignoré (mixage géré par `audio` projet — v1).

## Animations (`anim`)

| Animation | Effet | Calques |
|---|---|---|
| `none` | statique | tous |
| `fade` | fondu alpha in/out | tous |
| `fade_up` `fade_down` `fade_left` `fade_right` | fondu + glissement | tous |
| `slide_up` `slide_down` `slide_left` `slide_right` | glissement sans fondu | tous |
| `pop` | zoom 86→100 % + fondu | image/texte/forme |
| `grow_x` `grow_y` | barre qui se déploie | forme (barres de progression…) |
| `kenburns_in` `kenburns_out` | zoom progressif (pleine canvas) | image |
| `kenburns_pan_left` `kenburns_pan_right` | travelling latéral | image |

## Moteur v2 — options avancées

### Projet

| Clé | Description |
|---|---|
| `brand` | kit `brands/<nom>.json` → jetons `$accent`, `$font.title`, `$logo`… dans tout le projet |
| `background` | aussi `{"gradient": ["#a", "#b"], "angle": 135}`, `{"gradient": [...], "type": "radial"}` ou `{"image": "…"}` |
| `audio` | musique : fichier, objet `{file, volume, loop, fade_in, fade_out, at, src_in}` ou **liste** |
| `voiceover` | voix off (même format) : la musique est baissée automatiquement dessous (ducking) |
| `sfx` | effets `[{"file": "…", "at": 1.2, "volume": 0.8}]` (timeline globale) |
| `mix` | `{"duck": true, "duck_ratio": 8, "duck_threshold": 0.03, "loudnorm": -14}` |
| `export.loudnorm` | normalisation (LUFS), automatique avec `mp4-social` |

Un calque `{"type": "audio", "file": "…", "in": 0.4}` **dans une scène** se cale sur le
début de la scène (effet synchronisé). Une vidéo avec `"keep_audio": true` garde son son.

### Unités relatives

Toute dimension accepte `120`, `"120px"`, `"50%"` (axe du champ : x et largeur → W,
y et hauteur → H), `"8vw"`, `"8vh"`, `"6vmin"`, `"6vmax"`. Un projet en unités relatives se
décline en plusieurs formats : `./md render <nom> --formats 9x16,1x1,16x9`.

### Calques : mouvement

| Clé | Valeurs |
|---|---|
| `anim` | + `scale_in`, `zoom_in`, `punch`, `rotate_in` ; `slide_*` entrent depuis le hors-champ (sauf si `amplitude` est donné) ; `grow_x/grow_y` = vraie révélation masquée |
| `ease` | `linear, ease_in, ease_out (défaut), ease_in_out, expo_out, back_out, back_in, elastic_out, snap` |
| `exit` | `fade, fade_up, fade_down, slide_up, slide_down, slide_left, slide_right, scale_out` (+ `exit_duration`, `exit_ease`) |
| `idle` | `float, drift, pulse, sway, breathe` (+ `idle_amplitude`, `idle_period`) |
| `anchor` | point du calque placé sur `pos` : `center, top_left, top, top_right, left, right, bottom_left, bottom, bottom_right` |
| `opacity` / `rotate` | 0→1 / degrés |
| `enabled` | `false` = calque ignoré |

### Nouveaux types et options

- **Texte cinétique** : `"split": "word" | "line" | "char"`, `"stagger": 0.08` (les morceaux apparaissent en cascade avec l'`anim` du calque).
- **Pastille** : `"box": {"color": "#000", "opacity": 0.6, "padding": [24, 12], "radius": 16}` (révélée par `box_anim`, défaut `grow_x`).
- **Compteur** : `{"type": "counter", "from": 0, "to": 10000, "prefix": "+", "suffix": " €", "decimals": 0, "count_duration": 1.5, "ease": "expo_out"}` + champs texte.
- **Formes** : `kind` `rect | circle | ring | line | triangle`, `gradient` + `angle`, `stroke` + `stroke_color`, `ring_width`.
- **Vidéo** : `speed`, `loop`, `keep_audio`, `audio_role`.

### Formats et exports ajoutés

Canvas : `1.91x1` (1200×628 pub lien), `2x3` (Pinterest), `4k`, `9x16-60`.
Exports : `mp4-social` (H.264 High, débit plafonné, -14 LUFS), `mp4-draft` (brouillon 15 i/s).

### Pipeline

Les scènes sont rendues **en parallèle** (`MD_JOBS`, défaut min(4, CPU)) et **mises en cache**
par empreinte (contenu, fichiers, code du moteur) : seules les scènes modifiées sont
recalculées. Le livrable est écrit de façon atomique (`.part` puis renommage).

## Exemples

### Logo + titre sur fond vidéo

```json
{
  "canvas": "16x9", "duration": 8,
  "audio": { "file": "assets/audio/musique.mp3", "volume": 0.7 },
  "layers": [
    { "type": "video", "file": "assets/videos/rush.mp4", "in": 0, "out": 8,
      "src_in": 12, "fit": "cover" },
    { "type": "image", "file": "assets/images/logo.png", "in": 0.5, "out": 7.5,
      "pos": "top", "scale": { "w": 260 }, "anim": "fade" },
    { "type": "text", "text": "LANCEMENT\n2026", "size": 110, "in": 1.5, "out": 7,
      "pos": "center", "anim": "fade_up", "shadow": true }
  ]
}
```

### Barre de progression + Ken Burns

```json
{
  "layers": [
    { "type": "image", "file": "assets/images/photo.jpg", "full_bleed": true,
      "in": 0, "out": 6, "anim": "kenburns_in" },
    { "type": "shape", "kind": "rect", "w": 900, "h": 10, "radius": 5,
      "color": "#3b82f6", "pos": [960, 980], "in": 0.5, "out": 6, "anim": "grow_x" }
  ]
}
```
