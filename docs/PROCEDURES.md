# Procédures opérationnelles — MOTION-DESIGN

Ce dépôt est un **moteur de montage motion design**. Voici les procédures standard,
dans l'ordre du flux de production.

---

## P0 · Vérifier le moteur (à chaque session)

```bash
./md doctor
```

Contrôle ffmpeg, PyAV, Pillow, polices, dossiers. Doit afficher **✅ Moteur opérationnel**.
Si des dépendances manquent : `make bootstrap`.

---

## P1 · Réception d'éléments (assets)

Tout élément reçu (police, logo, rush vidéo, musique, Lottie) passe par :

```bash
./md install <fichier|dossier|URL>...
# ex :
./md install ~/Downloads/logo.png ~/Downloads/track.mp3
./md install https://github.com/user/repo/raw/main/font.ttf
```

La procédure :
1. **Route** le fichier vers le bon dossier (`assets/fonts`, `images`, `videos`, `audio`, `lottie`)
2. **Valide** (police testée, média analysé, SVG converti en PNG)
3. **Met à jour** l'inventaire `assets/INVENTORY.md`

Contrôler l'inventaire à tout moment : `./md inventory`
URLs : seuls les hôtes autorisés fonctionnent (GitHub, PyPI, npm — voir `engine/install.py`).

---

## P2 · Création d'un projet

```bash
./md new <nom> --canvas <format> --template <modele>
# ex : ./md new teaser-ete --canvas 9x16 --template story
```

- Formats : `16x9` (YouTube) · `9x16` (Reels/TikTok) · `1x1` (feed) · `4x5` · `21x9` · `720p` (tests)
- Modèles : `base` (une scène titrée) · `story` (storyboard 3 scènes vertical)
- Résultat : `projects/<nom>/project.json` — **c'est le seul fichier à éditer**.

---

## P3 · Montage (édition du project.json)

Le montage est déclaratif : on décrit la timeline dans `project.json`
(format complet : [SPEC-PROJET.md](SPEC-PROJET.md)).

Règles d'or :
- Les chemins médias sont relatifs à la racine du dépôt (`assets/images/logo.png`)
  ou au dossier du projet.
- Un calque = `type` + `in`/`out` (secondes) + `anim` + `pos`.
- Vérifier la commande ffmpeg générée sans rendre : `./md render <nom> --dry-run`

---

## P4 · Rendu

```bash
./md render <nom>                        # MP4 haute qualité → livré en artefact
./md render <nom> --preset gif           # GIF animé
./md render <nom> --preset mp4-web       # prévisualisation rapide
./md render <nom> --out .cache/rendus/client-v1.mp4
```

Chaque rendu écrit `projects/<nom>/manifest.json` (durée, poids, date, réglages).
**Convention : plus de dossier `output/` — chaque livrable est remis en artefact.**

---

## P5 · Validation & prévisualisation

```bash
./md preview            # serveur HTTP → lien de prévisualisation navigateur
./md info .cache/rendus/mon-projet-mp4-hq.mp4   # vérif durée / résolution / poids
```

Checklist de validation : durée conforme, texte lisible, aucun clignotement
de première/dernière image, audio fondu en sortie.

---

## P6 · Livraison & suivi Git

- Versionner le **projet** (léger, reproductible) :
  ```bash
  git add projects/<nom>/ assets/ && git commit -m "projet: <nom>"
  ```
- Les livrables ne sont PAS versionnés : ils sont livrés en artefact.
- Le rendu est toujours reproductible : project.json + assets + `./md render`.

---

## P7 · Nettoyage

```bash
./md clean <nom>   # supprime .cache/<nom>/ (intermédiaires de scènes, PNG texte)
```

---

## P8 · Moteur HyperFrames (HTML → vidéo)

Pour un motion design riche (GSAP, CSS, web components) :

```bash
./scripts/hf check  projects/<nom>      # gate qualité (lint+runtime+motion+contraste)
./scripts/hf render projects/<nom> --quality draft --output .cache/rendus/<nom>.mp4
```

Procédure complète (init, vendoring CDN **obligatoire**, routage des skills) :
**[HYPERFRAMES.md](HYPERFRAMES.md)**.

---

## Dépannage

| Symptôme | Cause probable | Solution |
|---|---|---|
| `ffmpeg a échoué` | filtre/argument invalide | `MD_VERBOSE=1 ./md render …` pour voir la commande |
| Texte sans style | police introuvable | `./md fonts`, puis `./md install ma-police.ttf` |
| `dimensions paires` | canvas impair | utiliser un preset ou des dimensions paires |
| Rendu lent | preset `mp4-hq` (slow) | tester en `mp4-web`, livrer en `mp4-hq` |
| Média illisible | codec exotique | ré-encoder : voir P1, ou fournir un MP4 H.264 |
