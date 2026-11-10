# Éléments graphiques libres de droits (`./md elements`)

Le moteur sait chercher et récupérer lui-même des **emojis 3D, illustrations et icônes**
utilisables en publicité commerciale, sans compte ni abonnement : c'est l'équivalent ouvert
d'IconScout. Chaque fichier récupéré est tracé avec sa licence dans
`assets/elements/LICENCES.md` (et `licences.json`).

Module : `engine/elements.py` · Outils MCP : `md_elements_search`, `md_elements_get`.

## Sources

| Id de source | Contenu | Style | Licence |
|---|---|---|---|
| `fluent-3d` | Microsoft Fluent Emoji : ~1 600 objets (TV, popcorn, ballon, cadeau, horloge, téléphone…) | **3D brillant** (PNG 256 px, fond transparent) | MIT |
| `fluent-couleur` | les mêmes objets en illustration vectorielle à dégradés | couleur (SVG) | MIT |
| `fluent-plat` | les mêmes objets en aplats | plat (SVG) | MIT |
| `unicons`, `unicons-plein` | **Unicons d'IconScout** | ligne / plein (SVG) | Apache-2.0 |
| `tabler` | Tabler Icons (~5 000) | ligne + filled | MIT |
| `lucide` | Lucide | ligne | ISC |
| `phosphor` | Phosphor (ligne, plein, duotone…) | ligne | MIT |
| `remix` | Remix Icon | ligne + fill | Apache-2.0 |
| `mingcute` | MingCute (arrondi) | ligne + fill | Apache-2.0 |
| `material` | Material Symbols (Google) | plein | Apache-2.0 |

Licences acceptées : MIT, ISC, Apache-2.0, CC0 (usage commercial, pas d'attribution obligatoire).
Les collections sous CC-BY / CC-BY-SA (attribution ou partage imposés) sont refusées automatiquement.

Accès réseau utilisé : registry npm (`@iconify-json/<collection>`) et GitHub
(`microsoft/fluentui-emoji`, clone partiel : seuls les fichiers demandés sont téléchargés).
Cache : `.cache/elements/` (`./md elements vider-cache`).

## Commandes

```bash
./md elements sources                                   # sources, styles, licences, kits
./md elements chercher télé popcorn --style 3d           # mots en français ou en anglais
./md elements chercher télécharger wifi --style ligne --max 10
./md elements prendre fluent-3d:television "fluent-3d:soccer ball" tabler:download
./md elements prendre tabler:download --couleur "#3dff6e" --png   # icône recolorée + PNG transparent
./md elements kits                                      # kits prêts à l'emploi
./md elements kit offre --vers projects/ma-pub/assets    # tout un kit, ailleurs que assets/elements/
./md elements planche                                   # planche contact des PNG (vérification visuelle)
```

Les ids ont la forme `source:nom` (copier ceux affichés par `chercher`). Options :
`--style 3d|couleur|plat|ligne|plein`, `--source <id>`, `--vers <dossier>`, `--couleur #hex`
(icônes ligne/plein), `--taille <px>`, `--png`.

## Kits

| Kit | Contenu |
|---|---|
| `divertissement` | TV, popcorn, clap, pellicule, caméra, ballon, trophée, casque, micro, radio, manette, notes, antenne, globe (3D) |
| `offre` | cadeau, sac d'argent, pièce, chrono, réveil, calendrier, coche, cotillons, confettis, étincelles, feu, éclair, étoile (3D) |
| `appareils` | téléphone, portable, ordinateur, TV, antenne, globe (3D) |
| `interface` | télécharger, lecture, wifi, monde, TV/mobile/tablette/portable, coche, bouclier, horloge, calendrier, cadeau, étoile, musique, film, foot, micro, radio, loupe, cloche, flèche (icônes ligne) |

Les quatre kits sont déjà installés dans `assets/elements/` (icônes `interface` en blanc, SVG + PNG).

## Dans une composition

- **HyperFrames (HTML/GSAP)** : copier les fichiers dans `projects/<pub>/assets/` (`--vers`), puis
  `<img src="assets/television-3d.png">`. Les SVG d'icônes se recolorent avec `--couleur`, ou
  s'intègrent en ligne dans le HTML.
- **project.json / brief** : calque image `{"type": "image", "src": "assets/elements/popcorn-3d.png", …}`.
- Animer : entrée `pop`/`back_out`, `idle: float` ou rotation légère ; les emojis 3D font de très
  bons « objets héros » (cadeau pour une offre, chrono pour une durée, ballon pour le sport).

## Limites

- Pas de photos ni de vidéos réalistes ici : les déposer dans `entrees/`, ou ouvrir l'accès à une
  banque d'images (clé d'API) dans l'environnement.
- Les emojis 3D Fluent font 256 px : parfaits jusqu'à ~300 px à l'écran, au-delà préférer
  `fluent-couleur` (vectoriel, net à toute taille).
- IconScout lui-même demande un compte et une clé d'API (contenus Premium payants) ; ses
  **Unicons** libres sont en revanche disponibles ici (`unicons`, `unicons-plein`).
