# LIVRAISON — version d'évaluation (WIP) · 4 novembre 2026

> **Objectif demandé** : « générer cette vidéo afin d'évaluer l'état d'avancement ».
> ⚠️ **Ce fichier n'est PAS le film final et n'est pas diffusable.** Il sert à juger la structure,
> le rythme, la charte et la lisibilité. La voix, la musique, les vraies interfaces, le QR, le lien,
> les paiements et les conditions restent à fournir.

## Fichiers livrés

| Fichier | Contenu |
|---|---|
| **`missa-tv-360-pub-59s_9x16_wip.mp4`** | **le film WIP** — 1080×1920 · 30 i/s · **59,000 s** · H.264 + AAC 48 kHz · 12 Mo |
| `missa-tv-360-pub-59s_9x16_wip-contact.jpg` | planche chronologique de 14 vues (F01 → F13) |
| `missa-tv-360-pub-59s_9x16_wip-planche-05s.jpg` | **planche contact toutes les 0,5 s** (118 images, grille 12×10), demandée par la section M |
| `missa-tv-360-pub-59s_9x16_wip.md` | ce rapport |

Aperçu live (lecteur vidéo + lecteur audio + documents) : **port 8091** → `/apercu/index.html`.

## Ce que contient le WIP

- **13 séquences**, recalées sur les silences de la VO de travail (`TIMING-PROVISOIRE.md`) :
  F01 0→4,00 · F02 4,00→6,52 · F03 →11,07 · F04 →14,48 · F05 →16,53 · F06 →22,11 ·
  F07 →27,80 · F08 →34,55 · F09 →40,62 · F10 →43,07 · F11 →48,38 · F12 →55,16 · F13 →59,00.
- **Deux mondes** : papier/ardoise désaturé (0→16,8, aucun jaune, tampon rouge brique) puis
  noir MISSA `#0B0B0C` + jaune **`#F5BB00`** (valeur réelle du dépôt applicatif), vert `#009E49`,
  vert actif `#2FD37A`, rouge LIVE `#E53935`.
- **Typographie animée, interfaces vectorielles fictives, formes géométriques** : ticket qui s'imprime,
  télécommande, tuiles identiques, barres PUB, pièces, pivot « ON MÉRITE MIEUX. », logo, 12 pilules
  d'univers, rails d'affiches abstraites, mur de 40 chaînes génériques, onde audio + 120 points
  (aucune frontière dessinée), 3 cadres d'appareils, tickets de prix, calendrier 3×4
  (5 cases jaunes + 7 « OFFERT »), bouton « Télécharger » → ✓, micro-ticket « ACTIVÉ ».
- **Aucune photo, aucune image générée par IA, aucun personnage, aucune marque tierce, aucune affiche réelle.**
- **36 bandeaux de sous-titre mot à mot**, dans la bande sûre y 1280-1400, avec boîtes d'accent
  (rouge brique dans le monde 1, jaune dans le monde 2) et traits soulignés. Absents pendant le gag
  muet F02 et les 3 moments typographiques F05/F10/F13, conformément au CDC.
- **Montants conformes** : `XAF 2 000 / mois`, `XAF 10 000 / an`, `7 MOIS OFFERTS`,
  `moins de XAF 30 / jour`. À l'oral/sous-titre : « deux mille francs CFA », « dix mille francs CFA ».
- **Audio** : VO de travail (repère, 59,54 s recoupée à 59,00 s **par une coupe dans un silence**),
  **76 événements SFX** de la banque media-use (Pixabay Content License), VO au premier plan
  (RMS 0,133 vs SFX 0,050), crête 0,95. **Musique = silence** : `[MUSIQUE TENSION]` et
  `[MUSIQUE ELAN]` restent en placeholder. Pistes séparées 48 kHz 16 bits disponibles dans
  `studio-59s/missa-tv-360-pub-59s/assets/audio/` (`voix-montage.wav`, `sfx.wav`, `musique.wav`, `mix.wav`).

## PLACEHOLDERS visibles à l'écran (section C)

`[CAPTURES_APP]` · `[QR_CODE]` · `[LIEN_TELECHARGEMENT]` · `[MODES_DE_PAIEMENT]` ·
`[CONDITIONS_OFFRE]` · `[MUSIQUE ELAN]` · `[VOIX]` (voix de travail, pas la voix du film).

Résolus sans rien inventer : `[HEX_JAUNE] = #F5BB00` et `[LOGO_OFFICIEL]` =
`assets/images/logo-missa.png` désigné par le propriétaire (**« MISSA TV 360 »**, 1254×1254,
fond jaune opaque, identité bleu/vert — voir `assets/img/README.md`).

## Contrôles effectués sur le VRAI rendu

| Contrôle | Résultat |
|---|---|
| `npx hyperframes --version` | **0.8.82** (figé) |
| `npx hyperframes validate . --json` | **ok: true · 0 erreur JS · 0 warning** · 1 contraste transitoire pendant un fade-in de 0,14 s |
| `npx hyperframes doctor` | FFmpeg ✓ · FFprobe ✓ · Chrome ✓ |
| Rendu | **1770 images**, 2 min 06, screenshot capture / GPU logiciel |
| Sonde MP4 | **1080×1920 · 30/1 fps · H.264 · AAC 48 kHz mono · 59,000 s** |
| Énergie audio (6 tranches de 10 s) | RMS 0,122 → 0,169, aucune tranche silencieuse |
| Images noires (118 échantillons à 0,5 s) | **0** (le noir du pivot est habillé par le grain 5 %) |
| Images quasi figées | 5 échantillons isolés (5,5 / 6,0 / 15,5 / 45,5 / 49,0 s), aucun > 0,5 s |
| Planche 0,5 s | 118 images, 12×10 |

## Limites connues de cette version d'évaluation

1. **Voix** : VO de travail générée, masculine non garantie, **pas** la voix du film. `voix.mp3` attendu.
2. **Minutage** : `onsets.json` est **provisoire** — mots répartis par séquence sur les phrases
   détectées par l'énergie, **pas transcrits mot à mot**. `mots.py`/Whisper exige un modèle non
   téléchargeable ici ; le vrai minutage sera refait sur la voix définitive.
3. **Animation** : version simplifiée (apparitions scale/opacity, dérive caméra, 563 tweens GSAP),
   sans les 3 niveaux de profondeur systématiques, ni tous les objets-ponts, ni les 12 relais
   `handoff_in`/`handoff_out` du storyboard détaillé.
4. **Musique** : absente (2 morceaux CC0 attendus) ; pas de ducking à évaluer.
5. **Interfaces** : reconstruites en vecteurs **fictifs** faute de `[CAPTURES_APP]`, pas fidèles à l'app.
6. **Logo** : PNG à fond jaune opaque (pas de transparence), identité bleu/vert à confirmer.
7. **Mix** : crête normalisée à 0,95, **-14 LUFS / -1 dBTP non calibrés** (à faire à l'étape 5).
8. **Aucune clé API, aucun push, aucune publication.** Aucun commit effectué.

## Reproduire le WIP

```bash
bash studio-59s/setup.sh                       # CLI 0.8.82, polices OFL, Chromium, FFmpeg/FFprobe
. studio-59s/env.sh
cd studio-59s/missa-tv-360-pub-59s
python3 tools/timing-provisoire.py             # onsets.json / SRT / TIMING
python3 render/wip_build.py                    # index.html (13 scènes, GSAP local)
python3 render/wip_audio.py                    # 4 pistes WAV 48 kHz
cd ../ && npx hyperframes render missa-tv-360-pub-59s -o /tmp/wip-video.mp4 --quality draft --workers 2
ffmpeg -i /tmp/wip-video.mp4 -i missa-tv-360-pub-59s/assets/audio/mix.wav \
  -c:v copy -c:a aac -b:a 192k -ar 48000 -t 59.0 -movflags +faststart \
  ../../livrables/missa-tv-360-pub-59s_9x16_wip.mp4
python3 missa-tv-360-pub-59s/render/wip_check.py ../../livrables/missa-tv-360-pub-59s_9x16_wip.mp4
```

## Prochaines étapes (points d'arrêt)

2. `voix.mp3` → `mots.py` + `onsets.py --transcript` → vrai `onsets.json` → recalage définitif.
3. 3 directions × 3 styleframes 1080×1920 → **choix sur image** → `frame.md` + `STORYBOARD.md` + grille 15 points.
4. Séquence **F01 seule** validée, puis les 12 autres → `assemble.sh` (coupe uniquement, sortie au noir).
5. 2 musiques CC0, 3-4 options, ducking, SFX calés sur les gestes, **-14 LUFS / -1 dBTP**, contrôle final.
6. Livraison `missa-tv-360-pub-59s_9x16.mp4`, puis déclinaison 16:9 (K) après validation.
