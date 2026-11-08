# MOTION-DESIGN — moteur générique de vidéos publicitaires motion design

On **décrit** une vidéo en JSON (un brief pub ou un montage détaillé) et le moteur
la **fabrique** : animations, typographie, transitions, son, puis export prêt pour les
réseaux sociaux en 9:16, 1:1, 4:5 et 16:9.

Le moteur est **générique** : il sert n'importe quelle marque, n'importe quel produit,
n'importe quelle devise ou langue. L'identité visuelle vient d'un kit de marque
(`brands/<nom>.json`) ou est **déduite automatiquement du logo fourni**.

Il sert aux humains comme aux **agents IA**. Un agent qui ouvre ce dossier s'y
connecte automatiquement (MCP), comme un pilote dans un cockpit : il voit les
instruments, compose, vérifie, regarde des aperçus et livre.

```
brief / project.json ──► contrôle qualité ──► aperçu (planche contact) ──► rendu MP4 multi-formats
```

---

## Sommaire

1. [Installation](#1-installation)
2. [Créer une pub : les éléments à fournir, puis le brief](#2-créer-une-pub-en-2-minutes-avec-un-brief)
3. [Créer un montage sur mesure (project.json)](#3-créer-un-montage-sur-mesure-projectjson)
4. [Piloter le moteur avec un agent IA](#4-piloter-le-moteur-avec-un-agent-ia)
5. [Comment le moteur fonctionne](#5-comment-le-moteur-fonctionne)
6. [Référence rapide](#6-référence-rapide)
7. [Autres outils du dépôt](#7-autres-outils-du-dépôt)

---

## 1. Installation

```bash
make bootstrap          # Python (pillow, numpy, av, imageio-ffmpeg) + Node + ffmpeg
./md doctor --full      # diagnostic + rendu d'essai : doit finir par « ✅ Moteur opérationnel »
```

Prérequis : `python3`, `ffmpeg` (système, ou binaire statique installé par le
bootstrap). Node n'est utile que pour HyperFrames (section 7).

---

## 2. Créer une pub en 2 minutes avec un brief

### Ce qu'on fournit à chaque pub

On dépose dans **`entrees/`** (upload GitHub sur `main`, ou pièces jointes à l'agent) :

| Élément | Rôle dans le moteur |
|---|---|
| **L'audio complet de la pub** (voix + musique déjà mixées) | fixe la **durée** ; les coupes entre scènes se calent sur ses **respirations** |
| **Les logos de la marque** | logo de fin de pub ; **couleurs de la vidéo déduites du logo** |
| **Le texte dit dans l'audio** (`script.txt`) | calé phrase par phrase sur l'audio : l'agent sait ce qui est dit à chaque instant ; sous-titres synchronisés en option (`"subtitles": true`) |
| **Les détails en `.txt`** | accroche, arguments, offre, prix, contacts : l'agent en tire le brief |
| **Vidéos et images complémentaires** | une scène chacune : photo plein cadre en mouvement, vidéo, ou produit détouré, avec légende |

```bash
./md entrees                       # analyse tout : durée et respirations de l'audio, script calé
                                   # phrase par phrase, palette du logo, détails, médias ; brief pré-rempli
./md entrees --brand ma-marque     # + copie dans assets/ et crée brands/ma-marque.json d'après le logo
```

### Le brief

Le **brief** décrit le *message*, pas l'animation. Le moteur choisit la mise en scène.
Avec un `audio_master`, la durée de la vidéo est celle de l'audio et les coupes
tombent sur les respirations (`"sync": true`, par défaut). On peut aussi imposer des
instants de coupe exacts avec `"cuts": [2.4, 6.1, …]`.

```json
{
  "template": "promo",
  "brand": "ma-marque",
  "canvas": "9x16",
  "audio_master": "entrees/pub-complete.mp3",
  "logo": "entrees/logo.png",
  "hook": "Et si tout devenait plus simple ?",
  "product": {"image": "entrees/produit.png", "name": "Le Produit", "tagline": "Pensé pour vous"},
  "media": [
    {"file": "entrees/ambiance.jpg", "caption": "Partout avec vous"},
    {"file": "entrees/demo.mp4", "caption": "Prise en main en 2 minutes", "start": 3}
  ],
  "benefits": ["Livraison en 24 h", "Satisfait ou remboursé", "Sans abonnement"],
  "proof": {"value": 5000, "prefix": "+", "label": "clients satisfaits"},
  "offer": {"price": 29, "old_price": 49, "currency": "€", "label": "aujourd'hui", "badge": "-40 %"},
  "cta": "J'en profite",
  "url": "votre-site.com"
}
```

Modèle prêt à copier : `templates/ad/brief-promo.json` (marque démo).

**Vérifier et prévisualiser :**

```bash
./md ad mon-brief.json --save --preview
```

Le projet est enregistré dans `projects/<nom>/`. Le contrôle qualité s'affiche, et une
**planche contact** (images clés) est créée dans
`.cache/apercus/<nom>-apercu/planche.png`.

**Rendre les vidéos finales :**

```bash
./md ad mon-brief.json --render --formats 9x16,1x1,16x9
```

Les MP4 arrivent dans `.cache/rendus/` (un fichier par format).

### Les 4 templates

| Template | Déroulé | Pour |
|---|---|---|
| `promo` | accroche → produit → médias → bénéfices → preuve → offre → bouton | présenter un produit |
| `offre` | accroche → prix barré qui chute → bénéfices → bouton (plus rapide) | soldes, promo limitée |
| `annonce` | accroche → produit → bénéfices → bouton | lancement, nouveauté |
| `preuve` | accroche → chiffre clé animé → bénéfices → bouton | preuve sociale |

Tous les champs sauf `hook` sont optionnels. Une scène sans contenu est sautée. Les
médias complémentaires (`media`) s'insèrent après le produit, ou après l'accroche. L'ordre
peut être imposé avec `"scenes": ["hook", "media", "offer", "cta"]`.
`duration` (6, 15, 30…) ajuste le rythme. Voir `./md ad --example` et
`./md ad --templates`.

---

## 3. Créer un montage sur mesure (project.json)

Pour un contrôle total, on écrit le montage scène par scène.

```bash
./md new ma-video --canvas 9x16 --template story   # crée projects/ma-video/project.json
# … éditer le fichier
./md lint ma-video                                 # contrôle qualité
./md apercu ma-video                               # brouillon rapide + planche contact
./md render ma-video --preset mp4-social --formats 9x16,1x1
```

Exemple minimal (une scène, unités relatives, kit de marque) :

```json
{
  "brand": "demo",
  "canvas": "9x16",
  "export": {"preset": "mp4-social"},
  "scenes": [{
    "duration": 4,
    "background": {"gradient": ["$background", "$surface"], "angle": 160},
    "layers": [
      {"type": "text", "text": "Offre de lancement", "split": "word", "font": "$font.title",
       "size": "9vmin", "color": "$text", "pos": ["50%", "40%"], "anim": "fade_up",
       "ease": "back_out"},
      {"type": "counter", "to": 29, "suffix": " €", "size": "14vmin", "color": "$accent",
       "pos": ["50%", "55%"], "in": 0.6, "anim": "punch"},
      {"type": "image", "file": "$logo", "scale": {"w": "30vmin"}, "pos": ["50%", "75%"],
       "in": 1, "anim": "pop", "idle": "float"}
    ]
  }]
}
```

Chaque calque a une **fenêtre** (`in`/`out` en secondes), une **position** (`pos`),
une **entrée** (`anim` + `ease`), une **sortie** (`exit`) et un **mouvement continu**
(`idle`). Spécification complète : **[docs/SPEC-PROJET.md](docs/SPEC-PROJET.md)**.

---

## 4. Piloter le moteur avec un agent IA

### Connexion

Le fichier `.mcp.json` à la racine déclare le serveur **`motion-design`**. Un agent
compatible MCP (Claude Code, Cursor…) ouvert dans ce dossier s'y connecte tout seul.
Lancement manuel : `python3 -m lab.mcp` (JSON-RPC sur stdio, sans dépendance).

### La boucle du pilote

| Étape | Outil MCP | Ce que l'agent obtient |
|---|---|---|
| 0. Réception | `md_intake` | analyse de `entrees/` : audio (durée, respirations), logos (palette), détails, médias + brief pré-rempli |
| 1. Instruments | `md_cockpit` | formats, exports, animations, marques, templates, polices, assets |
| 2. Composer | `md_ad_compose` ou `md_project_save` | un montage complet (brief) ou enregistré (sur mesure) |
| 3. Contrôler | `md_lint` | erreurs bloquantes + alertes avec le champ exact à corriger |
| 4. Regarder | `md_preview` | une **image** de planche contact du brouillon |
| 5. Livrer | `md_render` / `md_ad_render` | les MP4, un par format |

Autres outils : `md_guide` (manuel), `md_brands`, `md_projects`, `md_project_get`,
`md_ad_example`. Le laboratoire « données → graphique animé » reste disponible
via les outils `lab_*`.

Manuel du pilote, avec les règles de mise en scène publicitaire :
**[docs/PILOTE.md](docs/PILOTE.md)**.

Sans MCP, la même chose en ligne de commande : `./md cockpit` (JSON des capacités),
`./md cockpit --guide` (manuel).

---

## 5. Comment le moteur fonctionne

### Vue d'ensemble

```
            ┌──────────── brief pub ────────────┐
            │  engine/ads.py (compositeur)      │
            └───────────────┬───────────────────┘
                            ▼
                     project.json  ◄──── écrit à la main ou par un agent
                            │
     ┌──────────────────────┼─────────────────────────────────────┐
     │ 1. Normalisation     │ engine/brand.py + engine/layout.py  │
     │    jetons $accent → couleurs, "50%"/"8vmin" → pixels       │
     │ 2. Contrôle qualité  │ engine/lint.py                      │
     │ 3. Calques générés   │ engine/text.py (Pillow)             │
     │    textes, formes, dégradés, compteurs → images PNG        │
     │ 4. Graphe par scène  │ engine/render.py                    │
     │    fond + calques empilés, animations = expressions ffmpeg │
     │    rendues EN PARALLÈLE, MISES EN CACHE                    │
     │ 5. Assemblage        │ transitions xfade entre scènes      │
     │ 6. Audio             │ musique + voix (ducking) + effets,  │
     │                      │ normalisation -14 LUFS              │
     │ 7. Export            │ preset (mp4-social, gif, prores…)   │
     └──────────────────────┴─────────────────────────────────────┘
                            ▼
              .cache/rendus/<nom>-<format>-<preset>.mp4
```

### Les étapes en détail

1. **Normalisation.** Les jetons de marque (`$accent`, `$font.title`, `$logo`) sont
   remplacés par les valeurs du kit `brands/<nom>.json`. Les unités relatives (`"50%"`,
   `"8vw"`, `"6vmin"`) sont converties en pixels **pour le format demandé**. C'est
   pourquoi un même projet se rend en 9:16, 1:1 et 16:9.

2. **Contrôle qualité** (`lint`). Avant de dépenser du temps de rendu, le moteur
   vérifie les fichiers, les polices, les animations, les durées et les transitions. Il
   applique aussi des règles pub : texte trop petit pour un mobile, texte caché par
   l'interface TikTok/Reels (zones sûres), contraste insuffisant, accroche trop tardive
   (après 1,5 s).

3. **Calques générés.** ffmpeg ne dessine pas bien le texte, alors chaque texte, forme,
   dégradé ou compteur est dessiné en image PNG transparente avec Pillow. Le texte
   « mot par mot » (`split`) devient plusieurs images superposées qui apparaissent en
   cascade. Un compteur devient une courte séquence d'images.

4. **Graphe par scène.** Chaque scène devient un graphe de filtres ffmpeg : un fond,
   puis chaque calque superposé (`overlay`) dans l'ordre de la liste. Les animations
   sont des **expressions mathématiques évaluées à chaque image** : position, échelle,
   rotation, transparence, masque de révélation, avec des courbes d'accélération
   (`ease_out`, `back_out`…).

5. **Parallélisme et cache.** Les scènes sont rendues en même temps (jusqu'à 4,
   variable `MD_JOBS`). Chaque scène reçoit une empreinte calculée sur son contenu, ses
   fichiers et la version du moteur. Une scène inchangée sort du cache, donc retoucher
   une seule scène ne recalcule qu'elle.

6. **Calage sur l'audio.** Quand l'audio complet de la pub est fourni (`audio_master`),
   il fixe la durée totale. Le moteur repère dans son enveloppe d'énergie les creux
   (respirations, fins de phrase), même sous une musique, et place les coupes entre
   scènes sur ces creux. Un agent peut aussi imposer les coupes exactes (`cuts`), par
   exemple au début d'une phrase du script.

7. **Assemblage et audio.** Les scènes sont enchaînées avec des transitions `xfade`
   (fondu, glissé, volet…). L'audio est placé sur la timeline globale : musique
   (bouclée si besoin), voix off qui fait **baisser automatiquement la musique**
   (ducking), effets sonores calés sur les scènes. Le tout passe ensuite par une
   normalisation de volume (-14 LUFS, le standard des réseaux sociaux).

8. **Export.** Le preset choisit l'encodage (`mp4-social` = H.264 compatible régies
   pub). Le fichier est d'abord écrit en `.part`, puis renommé, ce qui évite de livrer
   un fichier à moitié écrit. En cas d'échec, ffmpeg renvoie un message lisible qui
   indique la cause.

### Organisation du code

| Fichier | Rôle |
|---|---|
| `md` | point d'entrée de la ligne de commande (`./md -h`) |
| `engine/cli.py` | commandes `./md …` |
| `engine/render.py` | cœur : graphes ffmpeg, animations, audio, parallélisme, cache |
| `engine/text.py` | rendu Pillow : texte, texte cinétique, formes, dégradés, compteurs |
| `engine/easing.py` | courbes d'accélération (expressions ffmpeg) |
| `engine/layout.py` | unités relatives et normalisation |
| `engine/brand.py` | kits de marque et jetons |
| `engine/lint.py` | contrôle qualité |
| `engine/ads.py` | compositeur publicitaire (brief → montage, calage sur l'audio) |
| `engine/intake.py` | réception : tri des fichiers, analyse audio, palette du logo |
| `engine/frames.py` | aperçus : images clés et planche contact |
| `engine/cockpit.py` | inventaire des capacités (partagé CLI / MCP) |
| `engine/presets.py` | formats, exports, zones sûres, durées pub |
| `lab/mcp.py` | serveur MCP (outils `md_*` et `lab_*`) |
| `lab/` | laboratoire données → vidéo (compositeur, API HTTP) |
| `tests/` | tests hors ligne (`make test`) |

### Arborescence des données

```
MOTION-DESIGN/
├── assets/        ← bibliothèque partagée : fonts, images, videos, audio (./md install)
├── brands/        ← kits de marque (un par client) : demo.json, neutre.json, missa.json…
├── entrees/       ← éléments déposés pour la pub en cours (audio, logos, détails, médias)
├── projects/      ← 1 dossier = 1 projet (project.json)
├── templates/     ← modèles de projet (base, story) et briefs pub (ad/)
├── docs/          ← PILOTE.md, SPEC-PROJET.md, PROCEDURES.md, VOIX-TTS.md…
├── livrables/     ← vidéos livrées et versionnées
└── .cache/        ← rendus (rendus/), aperçus (apercus/), intermédiaires (non versionné)
```

---

## 6. Référence rapide

### Commandes

| Commande | Rôle |
|---|---|
| `./md doctor [--full]` | diagnostic du moteur (+ rendu d'essai) |
| `./md entrees [--brand nom] [--json]` | réception des éléments déposés + brief pré-rempli |
| `./md ad <brief.json> [--save] [--preview] [--render] [--formats …]` | pub depuis un brief |
| `./md ad --example` / `--templates` | brief d'exemple / liste des templates |
| `./md new <nom> --canvas 9x16 [--template story]` | nouveau projet |
| `./md lint <nom> [--canvas 1x1]` | contrôle qualité |
| `./md apercu <nom> [--at 0.5,2,4] [--canvas 1x1]` | brouillon + planche contact |
| `./md render <nom> [--preset …] [--formats …] [--draft]` | rendu final |
| `./md brands` / `./md fonts` / `./md presets` | marques, polices, formats et exports |
| `./md cockpit [--guide]` | capacités en JSON / manuel du pilote |
| `./md install <fichiers\|URLs>` | ajouter des éléments à `assets/` |
| `./md vo <nom>` | voix off TTS depuis `vo.json` ([docs/VOIX-TTS.md](docs/VOIX-TTS.md)) |
| `./md info <média>` | durée, résolution, codecs d'un fichier |
| `./md clean <nom>` | vider le cache d'un projet |
| `make help` | les mêmes actions en cibles `make` |

### Formats (`canvas`)

`9x16` (Reels/TikTok/Shorts) · `9x16-60` · `1x1` · `4x5` · `16x9` · `1.91x1`
(pub lien) · `2x3` (Pinterest) · `21x9` · `4k` · `720p` · ou `{"width", "height", "fps"}`.

### Exports (`preset`)

`mp4-social` (pub, -14 LUFS) · `mp4-hq` · `mp4-web` · `mp4-h265` · `mp4-draft`
(brouillon) · `gif` · `webm-vp9` · `mov-alpha` (ProRes avec transparence).

### Animations

| Type | Valeurs |
|---|---|
| Entrées `anim` | `fade`, `fade_up/down/left/right`, `slide_up/down/left/right`, `pop`, `scale_in`, `zoom_in`, `punch`, `rotate_in`, `grow_x`, `grow_y`, `kenburns_in/out/pan_left/pan_right` |
| Courbes `ease` | `ease_out`, `ease_in`, `ease_in_out`, `expo_out`, `back_out`, `back_in`, `elastic_out`, `snap`, `linear` |
| Sorties `exit` | `fade`, `fade_up`, `fade_down`, `slide_*`, `scale_out` |
| Continu `idle` | `float`, `drift`, `pulse`, `sway`, `breathe` |

### Calques

`text` (avec `split`, `box`, `shadow`…), `counter`, `image`, `video`, `shape`
(`rect`, `circle`, `ring`, `line`, `triangle`, dégradés), `audio`.

### Variables d'environnement

| Variable | Effet |
|---|---|
| `MD_JOBS` | scènes rendues en parallèle (défaut : min(4, nombre de CPU)) |
| `MD_FFMPEG_TIMEOUT` | délai maximal d'une commande ffmpeg en secondes (défaut 1800) |
| `MD_FFMPEG` | chemin d'un binaire ffmpeg précis |
| `MD_VERBOSE` | affiche les commandes ffmpeg complètes |

### Ajouter une marque (un kit par client)

Le plus rapide : déposer le logo dans `entrees/` puis lancer `./md entrees --brand ma-marque`.
Le kit est créé à partir des couleurs du logo. À la main : copier `brands/neutre.json` vers
`brands/ma-marque.json` et remplir `colors`,
`fonts` et `logo`. Ensuite, `"brand": "ma-marque"` dans un brief ou un projet suffit.
Les jetons `$accent`, `$background`, `$text`, `$muted`, `$on_accent`, `$font.title`,
`$font.body` et `$logo` deviennent utilisables.

---

## 7. Autres outils du dépôt

- **Laboratoire données → vidéo** : des chiffres (`{"label", "value"}`) deviennent
  une vidéo de graphique animé en 4 scènes. Voir `./md lab demo`, `./md lab serve`
  (interface web et API HTTP), [docs/LAB-MOTION.md](docs/LAB-MOTION.md) et
  [lab/AGENT.md](lab/AGENT.md).
- **HyperFrames (HTML → vidéo)** : second moteur, pour des compositions HTML/CSS/GSAP.
  Il s'accompagne de 107 skills d'agent dans `.agents/skills/`. Voir `./scripts/hf`
  et [docs/HYPERFRAMES.md](docs/HYPERFRAMES.md).
- **Voix off** : génération TTS (edge-tts, VoxCPM) depuis un `vo.json`, voir
  [docs/VOIX-TTS.md](docs/VOIX-TTS.md).
- **Procédures de production** : [docs/PROCEDURES.md](docs/PROCEDURES.md).

## Tests

```bash
make test        # 54 tests hors ligne, dont de vrais rendus ffmpeg (~10 s)
```

---
Licence Apache-2.0 — voir [LICENSE](LICENSE).
