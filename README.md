# MOTION-DESIGN — moteur de montage

Ce dépôt est un **moteur de montage motion design** : un espace de travail complet où
l'on dépose des éléments (polices, logos, rushes, musiques), on décrit un montage de
façon déclarative (`project.json`), et le moteur produit les livrables (MP4, GIF, WebM,
ProRes alpha) dans `output/`.

## Démarrage rapide

```bash
make bootstrap                      # dépendances + diagnostic
./md new demo --canvas 16x9         # crée projects/demo/project.json
#   … éditer project.json (le montage se décrit, il ne se code pas)
./md render demo                    # → output/demo-mp4-hq.mp4
./md preview                        # prévisualisation navigateur
```

## Arborescence

```
MOTION-DESIGN/
├── md                  ← CLI du moteur (./md -h)
├── Makefile            ← automatisations (make help)
├── engine/             ← code du moteur (Python : rendu ffmpeg, texte Pillow…)
├── projects/           ← 1 dossier = 1 projet (project.json = le montage)
├── assets/             ← bibliothèque partagée (fonts, images, videos, audio, lottie)
│   └── INVENTORY.md    ← inventaire généré automatiquement
├── templates/          ← modèles de projet (base, story)
├── docs/               ← procédures (PROCEDURES.md) et spec (SPEC-PROJET.md)
├── output/             ← LIVRABLES FINAUX
└── .cache/             ← intermédiaires de rendu (ignorés par git)
```

## Commandes principales

| Commande | Rôle |
|---|---|
| `./md doctor` | diagnostic du moteur |
| `./md install <fichiers\|URLs>` | installe des éléments dans `assets/` (+ validation + inventaire) |
| `./md new <nom> --canvas 9x16` | crée un projet depuis un modèle |
| `./md render <nom> [--preset gif]` | rend le projet vers `output/` |
| `./md preview` | serveur de prévisualisation des sorties |
| `./md inventory` / `./md fonts` / `./md presets` | bibliothèque, polices, presets |
| `./md info <media>` | analyse d'un média (durée, résolution, codecs) |
| `./md clean <nom>` | purge les intermédiaires |

## Le montage : déclaratif

Le montage vit dans `projects/<nom>/project.json` : scènes, calques (texte, image,
vidéo, formes), fenêtres temporelles, animations (fondu, glissement, Ken Burns, pop,
barres qui se déploient…), transitions xfade entre scènes, mixage audio.
Format complet : **[docs/SPEC-PROJET.md](docs/SPEC-PROJET.md)** ·
Procédures de production : **[docs/PROCEDURES.md](docs/PROCEDURES.md)**

## Capacités du moteur

- **Rendu** : ffmpeg 7 (libx264, libx265, VP9, ProRes 4444 **avec alpha**, GIF palette)
- **Texte** : rendu typographique Pillow (polices TTF/OTF, contour, ombre, interlettrage,
  césure) — compense l'absence de `drawtext` du binaire statique
- **Animation** : fondus, slides, pop, Ken Burns (zoompan), barres progressives, rotation
- **Montage** : multi-scènes chaînées en xfade (21 transitions), mixage audio multi-pistes
  avec fondus
- **Formats** : 16:9, 9:16 (Reels/TikTok), 1:1, 4:5, 21:9, 720p — fps configurable

## Dépendances

`python3` · `imageio-ffmpeg` (binaire ffmpeg statique) · `av` (PyAV) · `pillow` ·
ImageMagick (optionnel, conversion SVG→PNG). Installation : `make bootstrap`.

---
Licence Apache-2.0 — voir [LICENSE](LICENSE).
