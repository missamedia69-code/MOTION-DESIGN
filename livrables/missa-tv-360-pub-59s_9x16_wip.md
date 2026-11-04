# LIVRAISON — version d'évaluation **WIP v2** · 4 novembre 2026

> ⚠️ **Ce fichier n'est PAS le film final et n'est pas diffusable.** Il sert à juger la structure,
> le rythme, la charte et la lisibilité. La voix, la musique, les vraies interfaces, le QR, le lien,
> les paiements et les conditions restent à fournir.
>
> **RÉVISION 1.1** — cette version corrige le retour du propriétaire : **tarifs**, et **cure
> d'épurement visuelle**. Les transitions, jugées cohérentes, n'ont **pas** été modifiées.

## Fichiers livrés

| Fichier | Contenu |
|---|---|
| **`missa-tv-360-pub-59s_9x16_wip.mp4`** | **le film WIP v2** — 1080×1920 · 30 i/s · **59,000 s** · H.264 + AAC 48 kHz · **10 939 754 o** |
| `..._wip-contact.jpg` | planche chronologique de 14 vues (F01 → F13 → fin) |
| `..._wip-planche-05s.jpg` | **planche contact toutes les 0,5 s** (118 images, grille 12×10), demandée par la section M |
| `missa-tv-360-pub-59s_9x16_wip.md` | ce rapport |

Aperçu live (lecteur vidéo + lecteur audio + documents) : **port 8091** → `/apercu/index.html`.

## 1. Correction des tarifs — cohérence des paroles, des sous-titres et de l'image

Le WIP v1 annonçait à tort « deux mille francs CFA par mois » et « 7 mois offerts ».
**Faits réels fournis par le propriétaire :**

| Donnée | Valeur retenue |
|---|---|
| Abonnement mensuel | **`XAF 1 000 / mois`** — à l'oral/sous-titre **« mille francs CFA »** |
| Abonnement annuel | **`XAF 10 000 / an`** — à l'oral/sous-titre **« dix mille francs CFA »** |
| 12 mois au tarif mensuel | **12 × 1 000 = 12 000 XAF** |
| Écart | **12 000 − 10 000 = 2 000 XAF = 2 MOIS OFFERTS** (l'année coûte le prix de 10 mois) |
| 10 000 / 365 | **27,4 XAF/jour → « moins de trente francs par jour »** (formulation conservée, elle reste exacte) |

- **VO de travail corrigée** sur les deux phrases fautives, sans accélérer la voix et sans recouper
  le montage : elle dure exactement **59,00 s**. Les sous-titres, les images et les SFX partagent
  désormais la **même source de coupes** (`render/wip_cuts.py`).
- `onsets.json` / `sous-titres.srt` régénérés : **149 mots, 43 phrases, 40 cues SRT**.
- Tous les documents (`SPEC-V2.md`, `SCRIPT.md` G.2/G.3, `DECISIONS.md`, `RAPPORT-ETAPE-0.md`,
  `apercu/index.html`, `index.html`) ne contiennent plus aucune ancienne valeur.
- **`2 MOIS OFFERTS`** est le libellé retenu (formulation du script validé, et la section L.2
  déconseille « gratuit » sauf si exact). Le propriétaire a dit « 2 mois gratuits » : **à confirmer**
  au moment de la VO définitive, une seule substitution suffirait.
- Le calcul `10 000 / 12 ≈ 833 XAF/mois` est désormais arithmétiquement exact mais reste **non dit**
  dans le spot, conformément à l'interdiction initiale.

## 2. Cure d'épurement — « trop touffu », « éléments qui se répètent », « pas assez élaboré »

Système unique : marge **90 px**, colonne **900 px**, contenu **y 240 → 1200**, sous-titre
**y 1280 → 1400**, dégradé radial de profondeur, filets d'angle, **un seul point focal par plan**,
**un seul accent coloré par séquence**, et un **rail de progression continu** sur les 59 s
(rouge brique → jaune au pivot). Dérive caméra lente et continue sur les 13 séquences.

| Séquence | WIP v1 | WIP v2 |
|---|---|---|
| F01 ticket | 6 lignes + 3 « MÊME FILM » + lune + tampon | 3 lignes, 1 filet, 1 tampon |
| F02 gag | 6 tuiles + 7 compteurs + spinner + visage | 1 écran, 1 tuile identique, 1 touche, compteur x1→x3 |
| F03 douleurs | 12 tuiles + 3 « REDIFFUSION » + « VU x10 » | **3 cartes** identiques + 1 étiquette |
| F04 pubs | 7 barres PUB + 8 pièces | **1 barre** + **1 pièce** qui s'en va |
| F06 univers | 12 pilules dispersées | **1 grille** de 6 univers réels, libellés lisibles |
| F07 contenus | 6 affiches + 12 épisodes + 4 cases + bouton | 3 cartes travaillées (filets internes, triangle de lecture) |
| F08 direct | **40 chaînes** + 6 badges LIVE + sport + PIN | **1 écran**, 1 badge LIVE, 3 lignes |
| F09 radios | 24 barres + **120 points** + micro + lecteur + casque | 1 cadran + 1 arc + **12 barres** |
| F10 appareils | 3 cadres remplis + ✓ | 3 silhouettes → **1 seul** écran + moment typographique |
| F12 annuel | calendrier 3×4, 7 cases « OFFERT », 7 pulsations | **1 barre de 12 segments** (10 jaunes + 2 verts) + `2 MOIS OFFERTS` |
| F13 CTA | logo + bouton + ✓ + 4 zones + micro-ticket + chœur | logo + **1 bouton** + 1 cadre de placeholders |

- **13 séquences**, **329 tweens GSAP**, **34 bandeaux de sous-titre** (au lieu de 563 / 36),
  **~120 éléments décoratifs** au lieu de ~250. Le MP4 livré passe de 12,3 Mo (v1) à **10,9 Mo**.
- **Transitions conservées telles quelles** : coupes franches, objet-pont point jaune → logo,
  pivot sur noir à 16,0 s, rime ticket/prix, sortie au noir à 59,0 s. Aucune coupe n'a été ajoutée.
- **Aucune photo, aucune image IA, aucun personnage, aucune marque tierce, aucune affiche réelle.**
- Sous-titre mot à mot en permanence (sauf gag muet F02 et les 3 moments typographiques F05/F10/F13),
  une seule ligne, taille adaptée à la longueur, boîtes d'accent et traits soulignés.

## 3. PLACEHOLDERS visibles (section C) — **rien n'est inventé**

`[VOIX]` · `[MUSIQUE TENSION]` · `[MUSIQUE ELAN]` · `[CAPTURES_APP]` · `[QR_CODE]` ·
`[LIEN_TELECHARGEMENT]` · `[MODES_DE_PAIEMENT]` · `[CONDITIONS_OFFRE]`.

Ils apparaissent à l'écran en F06, F07, F09, F10 et dans le cadre dédié de F13. Conformément à
« tu vas me les demander plus tard et je vais te les fournir » : **aucune question n'est posée
maintenant**, aucun élément n'est fabriqué, la liste est simplement laissée en attente.

Résolus sans rien inventer : `[HEX_JAUNE] = #F5BB00` (dépôt applicatif) et `[LOGO_OFFICIEL]` =
`assets/images/logo-missa.png` désigné par le propriétaire (**« MISSA TV 360 »**, 1254×1254, fond
jaune opaque, identité bleu/vert — voir `assets/img/README.md`).

## 4. Contrôles effectués sur le VRAI rendu

| Contrôle | Résultat |
|---|---|
| `npx hyperframes --version` | **0.8.82** (figé, jamais `@latest`) |
| `npx hyperframes lint --json` | **0 erreur · 17 warnings consultatifs** (mono-composition, sous-compositions à faire à l'étape 4 ; fichier > 350 lignes ; 2 `<img>` du même logo). Aucun chevauchement GSAP restant. |
| `npx hyperframes validate --json` | **ok: true · 0 erreur JS · 0 warning · 0 échec de contraste** (v1 en avait 1) |
| Rendu | **1770 images**, 59,0 s, capture screenshot / GPU logiciel, 2 min 38 |
| Sonde MP4 | **1080×1920 · 30/1 fps · H.264 · AAC 48 kHz mono · 59,000 s** |
| Images noires (118 échantillons à 0,5 s) | **0** |
| Images quasi figées (Δ < 0,35) | **0** (v1 : 5, première passe v2 : 11 → dérive caméra renforcée) |
| Planche 0,5 s | 118 images, 12×10 |
| Énergie audio (6 tranches de 10 s) | RMS 0,115 → 0,175, aucune tranche silencieuse |
| Audio | VO de travail corrigée, **48 événements SFX** (banque media-use, Pixabay Content License), RMS VO 0,120 / SFX 0,061, crête 0,950. **Musique = silence**. |

## 5. Limites connues de cette version d'évaluation

1. **Voix** : VO de travail générée, **pas** la voix du film. `voix.mp3` attendu (point d'arrêt 2).
2. **Minutage** : `onsets.json` reste **provisoire** — mots répartis par séquence sur les phrases
   détectées par l'énergie, **pas transcrits mot à mot**. `mots.py`/Whisper demande un modèle non
   téléchargeable ici ; le vrai minutage sera refait sur la voix définitive.
3. **Animation** : mono-composition WIP (pas de `compositions/` par séquence), 3 niveaux de
   profondeur non systématiques, `handoff_in`/`handoff_out` du storyboard détaillé pas encore écrits.
4. **Musique** : absente (2 morceaux CC0 attendus) ; pas de ducking à évaluer.
5. **Interfaces** : reconstruites en vecteurs **fictifs** faute de `[CAPTURES_APP]`, pas fidèles à l'app.
6. **Logo** : PNG à fond jaune opaque (pas de transparence), identité bleu/vert à confirmer.
7. **Mix** : crête normalisée à 0,950, **−14 LUFS / −1 dBTP non calibrés** (étape 5).
8. **Libellé « 2 MOIS OFFERTS »** : formulation à valider (voir §1).
9. Aucun styleframe définitif, aucun `frame.md`/`STORYBOARD.md` validé, aucune F01 isolée validée,
   **aucune publication**, **aucune clé API**, aucun merge vers `main`.

## 6. Reproduire le WIP v2

```bash
bash studio-59s/setup.sh                       # CLI 0.8.82, polices OFL, Chromium, FFmpeg/FFprobe
. studio-59s/env.sh
cd studio-59s/missa-tv-360-pub-59s
python3 tools/timing-provisoire.py             # onsets.json / SRT / TIMING / render/wip_cuts.py
python3 render/wip_build.py                    # index.html (13 scènes, GSAP local)
python3 render/wip_audio.py                    # 4 pistes WAV 48 kHz
cd ../ && npx hyperframes render missa-tv-360-pub-59s -o /tmp/wip.mp4 --quality draft --workers 2
ffmpeg -i /tmp/wip.mp4 -i missa-tv-360-pub-59s/assets/audio/mix.wav \
  -c:v copy -c:a aac -b:a 192k -ar 48000 -t 59.0 -movflags +faststart \
  ../../livrables/missa-tv-360-pub-59s_9x16_wip.mp4
python3 missa-tv-360-pub-59s/render/wip_check.py ../../livrables/missa-tv-360-pub-59s_9x16_wip.mp4
```

## 7. Prochaines étapes (points d'arrêt)

2. `voix.mp3` → `mots.py` + `onsets.py --transcript` → vrai `onsets.json` → recalage définitif,
   et confirmation du libellé « offerts / gratuits ».
3. 3 directions × 3 styleframes 1080×1920 → **choix sur image** → `frame.md` + `STORYBOARD.md` + grille 15 points.
4. Séquence **F01 seule** validée, puis les 12 autres → sous-compositions + `assemble.sh` (coupe uniquement, sortie au noir).
5. 2 musiques CC0, 3-4 options, ducking, SFX calés sur les gestes, **−14 LUFS / −1 dBTP**, contrôle final.
6. Livraison `missa-tv-360-pub-59s_9x16.mp4`, puis déclinaison 16:9 (K) après validation.

**Éléments que le propriétaire fournira plus tard** (à demander à ce moment-là, sans rien inventer) :
`[VOIX]`, les 2 pistes CC0, `[CAPTURES_APP]` (téléphone portrait + Android TV), `[QR_CODE]`,
`[LIEN_TELECHARGEMENT]`, `[MODES_DE_PAIEMENT]`, `[CONDITIONS_OFFRE]`, version transparente du logo.
