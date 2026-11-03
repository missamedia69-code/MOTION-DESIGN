# Le Laboratoire MOTION-DESIGN

> **Principe** : une IA se connecte au moteur comme un **laborantin** entre dans
> un labo. Elle dépose un **échantillon** (des données), consulte les
> **instruments**, applique un **protocole**, lance une **expérience** et repart
> avec un **artefact** : une vidéo motion design.

```
        ┌────────────────── IA / laborantin ──────────────────┐
        │  MCP stdio  ·  API HTTP  ·  CLI ./md lab  ·  paillasse web
        └───────────────────────┬─────────────────────────────┘
                                │  échantillon JSON (data[])
                                ▼
   ÉCHANTILLON  ──▶  PROTOCOLE  ──▶  INSTRUMENTS  ──▶  EXPÉRIENCE  ──▶  ARTEFACT
   spec.json        lab/spec.py      engine/*          lab/bench.py     livrables/lab/*.mp4
                    validation       canvas/exports    render_project_data
                    + métriques      polices/animations + manifeste JSON
                                │
                                ▼
                    COMPOSITEUR lab/composer.py
                    données → scenes[] / layers[] (project.json en mémoire)
                                │
                                ▼
                    MOTEUR EXISTANT engine/render.py → ffmpeg
```

## 1. Pourquoi cette révision

Avant, produire une vidéo demandait d'**éditer un `project.json` à la main** ou
d'écrire une composition HTML HyperFrames : le moteur était un outil pour humain,
pas une machine à laquelle un agent peut se brancher. Désormais :

| Avant | Après |
|---|---|
| Entrée = `project.json` écrit à la main | Entrée = **données brutes** (`label`/`value`) + quelques options |
| 1 projet = 1 dossier versionné | 1 expérience = 1 id, montage en mémoire, registre JSON |
| Sortie = `.cache/rendus/` temporaire | Sortie = `livrables/lab/*.mp4` **remis en artefact** |
| Accès = CLI seule | Accès = **CLI + API HTTP + MCP stdio + interface web** |
| `render_project()` chargeait forcément un dossier | **`render_project_data()`** accepte un montage déjà chargé |

Le moteur ffmpeg/Pillow n'a pas été réécrit : il a été **rendu adressable par
programme**. C'est le changement d'architecture, pas un moteur bis.

## 2. Les cinq objets du labo

| Objet | Fichier | Rôle |
|---|---|---|
| **Échantillon** | `spec.json` (ou JSON posté) | données d'entrée : 1 à 12 lignes `{label, value}`, titre, style, narration |
| **Protocole** | `lab/spec.py` | valide, normalise, calcule total / max / moyenne / meilleur label |
| **Instruments** | `lab/instruments.py` | inventaire : canvas, exports, transitions, animations, polices, assets, ffmpeg |
| **Compositeur** | `lab/composer.py` | traduit les données en 4 scènes déclaratives : `hook → kpi → bars → cta` |
| **Paillasse / expérience** | `lab/bench.py` | orchestre validation → composition → rendu → manifeste |
| **Artefact** | `livrables/lab/<nom>-<id>.mp4` | vidéo + registre `.cache/lab/registry.json` + `project.json` reproductible |

Les barres de la scène 3 sont **la donnée elle-même** : hauteur proportionnelle
à `value / max`, apparition en cascade (`grow_y` décalé). Le KPI de la scène 2
affiche la somme calculée par le protocole.

## 3. Trois façons pour une IA de se connecter

### a) MCP stdio — la connexion « laborantin » native

```json
{
  "mcpServers": {
    "motion-lab": {
      "command": "python3",
      "args": ["-m", "lab.mcp"],
      "cwd": "/home/user/MOTION-DESIGN"
    }
  }
}
```

Outils : `lab_instruments`, `lab_schema`, `lab_example`, `lab_validate`,
`lab_run`, `lab_submit`, `lab_status`, `lab_runs`, `lab_artifact`.
Séquence type d'un agent : `lab_example` → modifier `data` → `lab_validate` →
`lab_run` (ou `lab_submit` + `lab_status`) → `lab_artifact`.

```bash
printf '%s\n' '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"lab_run","arguments":{"spec":{"title":"Test","data":[{"label":"A","value":3},{"label":"B","value":7}]},"dry_run":true}}}' | ./md lab mcp
```

### b) API HTTP — paillasse web + intégrations

```bash
./md lab serve --port 8080          # ou make lab-serve
curl -s localhost:8080/api/instruments
curl -s -X POST localhost:8080/api/runs -H 'Content-Type: application/json' -d @spec.json
curl -s localhost:8080/api/runs/<id>
curl -s localhost:8080/api/runs/<id>/artifact -o video.mp4
```

| Route | Rôle |
|---|---|
| `GET /` | paillasse web (éditeur JSON, état des expériences, lien artefact) |
| `GET /api/health`, `/api/instruments`, `/api/schema`, `/api/example` | découverte par l'agent |
| `POST /api/runs` | soumet un échantillon → `202 {"id":...}` (tâche de fond) |
| `POST /api/runs?dry=1` | validation + compilation sans rendu |
| `GET /api/runs`, `/api/runs/<id>` | registre et état détaillé (logs, erreurs, métriques) |
| `GET /api/runs/<id>/artifact` | téléchargement du MP4 |
| `GET /api/runs/<id>/project` | `project.json` exact produit par le compositeur |

Le serveur écoute sur `0.0.0.0`, n'a aucune allowlist d'host et l'interface
n'utilise que des URLs relatives : compatible avec un preview navigateur.

### c) CLI — une expérience, une commande

```bash
./md lab demo                       # données d'exemple → MP4 (720p, ~6,5 s)
./md lab run spec.json              # votre échantillon
./md lab run spec.json --dry-run    # compile sans produire de vidéo
./md lab schema | ./md lab instruments | ./md lab runs | ./md lab status <id>
make lab A=run INPUT=spec.json  ·  make lab-demo  ·  make lab-mcp
```

## 4. Protocole d'entrée (minimal)

```json
{
  "title": "Ventes T3 2026",
  "canvas": "720p",
  "data": [
    {"label": "Jan", "value": 12},
    {"label": "Fév", "value": 19},
    {"label": "Mar", "value": 15}
  ],
  "narrative": {"hook": "Vos chiffres prennent vie", "cta": "On est ensemble !"}
}
```

Tout le reste est optionnel et normalisé : `style` (4 couleurs `#RRGGBB`,
police, transition xfade), `brand.logo`, `duration` (1–10 s par scène),
`preset` (mp4-web par défaut), `name`. Les valeurs doivent être des nombres
finis ≥ 0 ; 12 lignes maximum. Le détail complet : `./md lab schema`.

**Reproductibilité** : mêmes données + même spec = même montage. Chaque
expérience conserve son `project.json` dans `.cache/lab/<id>/` et ses
métadonnées dans le registre ; l'artefact seul est livré.

## 5. Ce qui a été révisé dans le moteur lui-même

- `engine/render.py` : extraction de **`render_project_data(proj, project_dir, …)`** ;
  `render_project()` n'est plus qu'un chargeur. Un agent peut rendre un montage
  fabriqué en mémoire sans créer de dossier dans `projects/`.
- `engine/cli.py` : nouvelle commande `lab` ; `doctor` ne teste plus le dossier
  `output/` (supprimé par convention) mais `.cache/rendus/`, et remonte au
  parent existant pour le test d'écriture → diagnostic enfin exact.
- `Makefile` : cibles `lab`, `lab-serve`, `lab-demo`, `lab-mcp`, `test`.
- `.gitignore` : exception `!livrables/lab/*.mp4` pour que les artefacts du labo
  soient livrés, tout en continuant d'ignorer les médias lourds ailleurs.
- `tests/test_lab.py` : tests hors-ligne du protocole, du compositeur, du
  registre, des outils MCP et des routes HTTP.

## 6. Limites et suite

- Le labo produit pour l'instant des **vidéos muettes** ; la VO se superpose
  ensuite via `./md vo` (voir [VOIX-TTS.md](VOIX-TTS.md)) et le mixage ffmpeg.
- Les scènes sont au nombre de 4 et typées ; pour une composition libre,
  l'agent peut récupérer `/api/runs/<id>/project`, l'éditer et le rendre avec
  `render_project_data` ou `./md render` — le format reste celui de
  [SPEC-PROJET.md](SPEC-PROJET.md).
- HyperFrames (HTML/GSAP) reste disponible pour les motion designs riches ;
  le labo s'appuie sur le moteur déclaratif ffmpeg, plus rapide et déterministe
  pour des données.
- Le registre `.cache/lab/` est un intermédiaire non versionné ; après un clone,
  `./md lab demo` suffit à repeupler le labo.

Manuel destiné à l'agent : **[lab/AGENT.md](../lab/AGENT.md)** ·
annuaire des skills : [plan-skills.md](plan-skills.md) ·
ressources : [RESSOURCES-MOTION.md](RESSOURCES-MOTION.md).
