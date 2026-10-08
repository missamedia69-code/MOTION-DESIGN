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
    "filename": "livrable.mp4"   // optionnel (déposé dans output/)
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
