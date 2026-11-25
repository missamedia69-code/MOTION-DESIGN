# MISSA TV 360 — production publicitaire

Ce projet est rendu avec le moteur générique `./md` du dépôt.

## Sources
- Audio master : `entrees/Pub Missa TV.wav`
- Logo : `entrees/Missa_TV_360_logo_1x1.png`
- Visuel publicitaire fourni : `entrees/Missa TV 360+ Entertainment Banner.png`
- Script de référence : `script.txt` (timings estimés sur l'énergie et les respirations du WAV)

## Production
`generate_visuals.py` produit des plans graphiques dédiés au catalogue, aux écrans et à la connexion limitée.
`generate_sfx.py` synthétise les effets sonores originaux.
`prepare.py` analyse le WAV, aligne les phrases, compose le projet et place les SFX sur les débuts de scène.

La GitHub Action rend les versions 9:16 et 16:9, lance le lint et produit une planche contact. Les vidéos finales et les aperçus sont publiés comme artefacts de workflow.
