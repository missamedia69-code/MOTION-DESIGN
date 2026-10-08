# HyperFrames dans le moteur

**HyperFrames** (HeyGen) est le second moteur de rendu du dépôt : on écrit du **HTML/CSS/GSAP**
« seekable » et il produit un MP4 déterministe. Il cohabite avec le moteur déclaratif
(`./md render`) ; les deux livrent dans `output/`.

- **21 skills** installés : `.agents/skills/` (+ `skills-lock.json`). Le routeur est
  `.agents/skills/hyperframes/SKILL.md` — à lire avant toute création.
- **CLI** : toujours via le wrapper `./scripts/hf …` (il prépare ffmpeg/ffprobe + Chromium).

## Environnement sandbox (spécifique à ce dépôt)

Le sandbox n'a PAS accès aux CDN Chrome/jsdelivr. Tout est résolu via les hôtes
autorisés (npm, PyPI, GitHub) :

| Besoin | Solution | Où |
|---|---|---|
| ffmpeg / ffprobe | binaire statique (imageio-ffmpeg + build v5 via codeload) | `/usr/local/bin` |
| Chrome headless | `@sparticuz/chromium` (tarball npm) + libs AL2023 | `scripts/ensure-browser.mjs` → `/tmp/chromium` |
| CLI hyperframes | `npm i -D hyperframes` (épinglé dans `package.json`) | `node_modules` |
| GSAP / libs web | **vendoring obligatoire** (jamais de CDN) | `projects/<x>/vendor/` |

Réinstallation complète : `bash scripts/bootstrap.sh` (idempotent).

## Procédure H1 · Créer un projet HyperFrames

```bash
cd projects && HYPERFRAMES_SKIP_SKILLS=1 ../scripts/hf init <nom> \
  --example blank --non-interactive --resolution portrait   # ou landscape/square
cd ..
```

## Procédure H2 · Vendorer les libs (OBLIGATOIRE ici)

Tout `<script src="https://cdn…">` doit devenir un fichier local :

```bash
npm i -D gsap                      # hôte autorisé : registry.npmjs.org
mkdir -p projects/<nom>/vendor && cp node_modules/gsap/dist/gsap.min.js projects/<nom>/vendor/
# puis dans index.html : <script src="vendor/gsap.min.js"></script>
```

Même règle pour polices web, CSS distants, etc. (téléverser dans `vendor/` ou `assets/`).

## Procédure H3 · Écrire la composition

Contrat d'auteur complet : `.agents/skills/hyperframes-core/SKILL.md`.
Résumé : `data-duration`, `data-start`, `data-width/height` sur `#root` ; chaque élément
animé = `.clip` avec `data-start/data-duration/data-track-index` ; animations **seekables**
enregistrées dans `window.__timelines["main"]` (GSAP `paused: true`).

## Procédure H4 · Contrôler puis rendre

```bash
./scripts/hf check  projects/<nom>                    # gate : lint+runtime+layout+motion+contraste
./scripts/hf render projects/<nom> --quality draft  \
  --output output/<nom>.mp4                           # itération rapide
./scripts/hf render projects/<nom> --quality delivery --output output/<nom>-final.mp4
```

Formats dispo : `--format mp4|webm|mov|gif|png-sequence|hls` (mov/webm = transparent).
Vérifier ensuite : `./md info output/<nom>.mp4`.

## Procédure H5 · Prévisualisation & studio

```bash
./scripts/hf preview --background projects/<nom>      # URL timeline pour revue
```

## Routage des demandes (skills)

Le routeur `.agents/skills/hyperframes/SKILL.md` choisit le workflow selon le livrable :
slideshow, embedded-captions, talking-head-recut, music-to-video, motion-graphics,
pr-to-video, product-launch-video, faceless-explainer, general-video,
remotion-to-hyperframes… Chaque workflow s'installe à la demande
(`npx hyperframes skills update <workflow>`).

## Quel moteur choisir ?

| Critère | `./md render` (déclaratif) | `./scripts/hf render` (HTML) |
|---|---|---|
| Montage simple (titres, calques, xfade, audio) | ✅ idéal | possible |
| Motion design riche (GSAP, CSS, web components) | limité | ✅ idéal |
| Reproductibilité | project.json | index.html + vendor/ |
| Rendu alpha | mov-alpha | `--format mov/webm` |

Les deux partagent `assets/` (médias installés via `./md install`) et `output/`.
