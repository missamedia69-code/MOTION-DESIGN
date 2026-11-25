# MOTION-DESIGN — consignes pour tout agent IA

Ce dépôt est un **moteur de pubs motion design**. Ton travail : à partir des éléments
que l'utilisateur dépose, livrer une pub de qualité, **vérifiée**, dans les formats demandés.

## Ce que l'utilisateur fournit

Dans `entrees/` (ou en pièces jointes que tu y copies) :

| Élément | Obligatoire | Rôle |
|---|---|---|
| **L'audio de la pub** (voix + musique mixées, ou voix seule) | oui | fixe la durée ; chaque phrase dite devient une scène, calée au mot près |
| **Le logo** (PNG transparent, « logo » dans le nom) | oui | couleurs de la pub déduites du logo ; révélation du logo ; fin de pub |
| `script.txt` (le texte dit, une phrase par ligne) | conseillé | texte exact à l'écran (sinon : transcription locale faster-whisper) |
| `details.txt` (`Marque : …`, `Site : …`, `Bouton : …`, `Style : energique/premium/doux`, `Couleur : #hex`, `Sous-titres : oui`) | non | réglages |
| Images / vidéos (`produit.png`…) | non | produit en 3D, médias plein cadre sous les phrases |

Le reste, tu le trouves ou le fabriques : icônes et emojis 3D **libres de droits** via la
bibliothèque (`md_elements_search` / `./md elements chercher …`), formes, halos, motifs,
particules et transitions générés par le moteur. Si l'utilisateur te donne une clé d'API
de génération d'images, les skills `bfl-api`, `atlas-cloud`, `flux-best-practices` décrivent
comment générer un visuel ; dépose-le ensuite dans `entrees/`.

## Le geste principal

```bash
./md pub                         # entrees/ → aperçu + vidéo 9:16 vérifiée
./md pub --formats 9x16,1x1,16x9 # déclinaisons
./md pub --apercu                # aperçu seul (rapide), pour valider avant de rendre
./md pub --brief brief.json      # storyboard sur mesure (voir ci-dessous)
```

Avec MCP (serveur `motion-design`, déclaré dans `.mcp.json`) : outil **`md_pub`**
(`render: false` pour l'aperçu, `true` pour la vidéo + le verdict).

Ce que fait le moteur (`engine/studio.py`) : écoute l'audio (phrases et mots horodatés),
déduit la marque du logo, construit un **storyboard** (accroche, logo, chiffre, liste, prix,
bouton… selon ce qui est dit), compose une scène HyperFrames par phrase (texte qui arrive au
rythme de la voix, caméra, transitions, fond vivant), contrôle, rend, normalise le son
à -14 LUFS, puis **juge la vidéo** (`engine/verify.py`).

## Ta boucle de travail (obligatoire)

1. `md_pub` / `./md pub --apercu` → **regarde la planche d'aperçu** (image renvoyée).
2. Corrige le storyboard s'il le faut : reprends `storyboard` (dans la réponse ou
   `projects/<nom>-<format>/storyboard.json`), modifie-le, renvoie-le en `brief.scenes`.
   Types : `hook`, `phrase`, `logo`, `product`, `media`, `benefits`, `stat`, `price`, `cta`.
   Champs utiles : `text`, `items` (liste), `stats` [{value, prefix, label}],
   `price`, `old_price`, `currency`, `label`, `badge`, `button`, `url`, `file`, `image`.
3. Rends (`render: true`) et lis le **verdict** : `OK`, `À AMÉLIORER` ou `À CORRIGER`.
   Une erreur (vidéo qui ne bouge pas, image vide, fin trop longue) se corrige toujours
   avant de livrer. Cite les chiffres du verdict à l'utilisateur, ne les estime jamais.
4. Livre les chemins des MP4 (`.cache/rendus/`) et la planche.

## Règles de métier (à respecter quand tu écris un storyboard)

- L'accroche se lit en moins de 1,5 s ; une idée par scène ; le texte suit la voix.
- On coupe en plein mouvement ; rien n'est figé plus de ~1 s ; la fin est courte.
- Ne jamais inventer de chiffres, d'avis ou de prix : seulement ce que dit l'audio ou
  ce que donne l'utilisateur.
- Pas de marques, logos ou personnages de tiers (droits).
- Méthode détaillée : skills `motionmaxxing`, `business-motion-film`, `ad-creative-video`,
  `beat-sync-editing` ; patterns de storyboard : `docs/craft/storyboard/`.

## Autres outils

- `./md ad` / `md_ad_render` : **mode rapide** (ffmpeg, sans navigateur) depuis un brief
  (`hook`, `benefits`, `offer`, `cta`…), pour des déclinaisons en volume.
- `./md verifier <vidéo>` / `md_verify` : juger n'importe quelle vidéo.
- `./md rythme <musique>` / `md_rythme` : tempo, temps, montées.
- `./md doctor` : diagnostic ; `make test` : tests.
- Manuel complet : `docs/PILOTE.md` ; sources et licences des skills : `docs/SKILLS-SOURCES.md`.

## Installation (une fois)

```bash
make bootstrap   # Python (pillow, numpy, av, faster-whisper), Node (HyperFrames, GSAP), ffmpeg, Chromium
```
