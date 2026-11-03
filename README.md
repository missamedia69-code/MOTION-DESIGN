# MOTION-DESIGN — moteur de montage

Ce dépôt est un **moteur de montage motion design** : un espace de travail complet où
l'on dépose des éléments (polices, logos, rushes, musiques), on décrit un montage de
façon déclarative (`project.json`), et le moteur produit les livrables (MP4, GIF, WebM,
ProRes alpha) livrés **en artefact** (rendus temporaires dans `.cache/rendus/`).

## Démarrage rapide

```bash
make bootstrap                      # dépendances + diagnostic
./md new demo --canvas 16x9         # crée projects/demo/project.json
#   … éditer project.json (le montage se décrit, il ne se code pas)
./md render demo                    # → livrable livré en artefact
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
├── .cache/rendus/        ← rendus temporaires, LIVRÉS EN ARTEFACT (pas de dossier output/)
└── .cache/             ← intermédiaires de rendu (ignorés par git)
```

## Commandes principales

| Commande | Rôle |
|---|---|
| `./md doctor` | diagnostic du moteur |
| `./md install <fichiers\|URLs>` | installe des éléments dans `assets/` (+ validation + inventaire) |
| `./md new <nom> --canvas 9x16` | crée un projet depuis un modèle |
| `./md render <nom> [--preset gif]` | rend le projet (livrable livré en artefact) |
| `./md vo <nom> [--dry-run]` | génère les voix off depuis `vo.json` (TTS edge-tts / VoxCPM) — voir [docs/VOIX-TTS.md](docs/VOIX-TTS.md) |
| `./md lab demo` / `./md lab run spec.json` | **Laboratoire** : données en entrée → vidéo motion design |
| `./md lab serve` / `./md lab mcp` | paillasse HTTP + API JSON, ou serveur MCP pour agent IA |
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
- **Voix off** : segments déclaratifs dans `vo.json`, génération `./md vo`
  (edge-tts / VoxCPM), `--dry-run` hors ligne et contrôle d'alignement avec le mix
- **Formats** : 16:9, 9:16 (Reels/TikTok), 1:1, 4:5, 21:9, 720p — fps configurable

## Moteur n°2 : HyperFrames (HTML → vidéo)

Le dépôt embarque aussi **HyperFrames** (HeyGen) et **107 skills d'agent**
(noyau HeyGen 21 + LottieFiles 1 + design-motion-principles 1 + frankxai 5 +
OpenMontage 79), dans `.agents/skills/` avec miroirs `.claude/skills/` et
`agent/skills/`, verrouillés par `skills-lock.json`. CLI via `./scripts/hf`,
rendu Chromium headless embarqué adapté au sandbox
(voir [docs/HYPERFRAMES.md](docs/HYPERFRAMES.md)).

Ajout d'un skill : `npx skills add <owner>/<repo> -a claude-code -a eve -y` ;
contrôle : `make skills-check`. Procédure et catalogue :
[docs/plan-skills.md](docs/plan-skills.md) · annuaire des dépôts, prompts et
ressources : [docs/RESSOURCES-MOTION.md](docs/RESSOURCES-MOTION.md).

```bash
./scripts/hf check  projects/hf-demo                 # gate qualité
./scripts/hf render projects/hf-demo --quality draft --output .cache/rendus/hf-demo.mp4
```

## Le Laboratoire : données → vidéo, pilotable par une IA

Le moteur est aussi une **machine adressable par programme** : une IA s'y
connecte comme un laborantin, dépose un échantillon de données, consulte les
instruments, lance une expérience et récupère un MP4.

```bash
./md lab demo                          # données d'exemple → livrables/lab/*.mp4
./md lab run spec.json --dry-run       # valider/compiler sans rendre
./md lab serve --port 8080             # paillasse web + API /api/runs
./md lab mcp                           # serveur MCP stdio (tools/list, tools/call)
```

Entrée minimale : `{"title":"…","data":[{"label":"Jan","value":12}, …]}`.
Le compositeur fabrique 4 scènes (hook → KPI → barres animées → CTA) dans le
format `project.json` existant, puis `render_project_data()` l'envoie à ffmpeg.
Documentation complète : **[docs/LAB-MOTION.md](docs/LAB-MOTION.md)** ·
manuel de l'agent : **[lab/AGENT.md](lab/AGENT.md)**.

## Dépendances

`python3` · `imageio-ffmpeg` (binaire ffmpeg statique) · `av` (PyAV) · `pillow` ·
ImageMagick (optionnel, conversion SVG→PNG) · `node ≥22` (`hyperframes`,
`@sparticuz/chromium`, `gsap` épinglés dans `package.json`).
Installation complète : `make bootstrap`.

---
Licence Apache-2.0 — voir [LICENSE](LICENSE).
