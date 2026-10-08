# Sorties (`output/`)

Ce dossier contient les **livrables finaux** du moteur.

- Chaque rendu y est déposé : `output/<projet>-<export>.mp4`
- Les fichiers lourds ne sont **pas versionnés** par défaut (`.gitignore`).
  Pour forcer le suivi d'un livrable : `git add -f output/mon-livrable.mp4`
- Le manifeste de chaque rendu (durée, poids, date, réglages) est écrit dans
  `projects/<projet>/manifest.json`.
- Prévisualisation navigateur : `./md preview` puis ouvrir le lien affiché.
