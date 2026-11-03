# MISSA TV 360 — Rapport de production et validation

**Statut : maquettes de validation créative et technique, NON prêtes pour diffusion commerciale** tant que les éléments et droits énumérés plus bas ne sont pas confirmés. Direction conçue depuis A–G.2 du brief du 2/11/2026. Les sections **H–N ont été proposées par l’agent** dans [`SPEC-H-N.md`](SPEC-H-N.md), faute de suite du document d’origine.

## Livraisons

| Fichier dans `livrables/` | Durée / format | Poids / vidéo moyenne |
|---|---|---|
| `MISSA_TV_360_PUB_59S_9x16.mp4` | **59,000 s**, 1080×1920, **1770** images | 17,4 Mo / 2,1 Mb/s |
| `MISSA_TV_360_PUB_59S_16x9.mp4` | **59,000 s**, 1920×1080, **1770** images ; **mise en page dédiée** | 12,6 Mo / 1,45 Mb/s |
| `MISSA_TV_360_PUB_59S_1x1.mp4` | **59,000 s**, 1080×1080, **1770** images ; **mise en page dédiée** | 10,4 Mo / 1,15 Mb/s |
| `MISSA_TV_360_PUB_30S_9x16.mp4` | **30,000 s**, 1080×1920, **900** images ; voix et montage autonomes | 9,1 Mo / 2,16 Mb/s |
| `MISSA_TV_360_PUB_15S_9x16.mp4` | **15,000 s**, 1080×1920, **450** images ; voix et montage autonomes | 5,1 Mo / 2,45 Mb/s |
| `MISSA_TV_360_PUB_{59,30,15}S_fr.srt` | Sous-titres correspondant au texte incrusté | 23 / 11 / 6 cartouches |
| `PISTES_SEPAREES_59S/VOIX_59S.wav` | **59,000 s**, 48 kHz, mono PCM **24 bits** | 8,5 Mo |
| `PISTES_SEPAREES_59S/MUSIQUE_59S.wav` | **59,000 s**, 48 kHz, stéréo PCM **24 bits** | 17,0 Mo |
| `PISTES_SEPAREES_59S/EFFETS_59S.wav` | **59,000 s**, 48 kHz, stéréo PCM **24 bits** | 17,0 Mo |

Toutes les vidéos sont H.264 30 i/s + AAC 48 kHz, environ 258 kb/s. Les sous-titres sont brûlés dans les cinq vidéos, en plus des fichiers SRT séparés. `livrables/` ne contient **plus d’ancienne publicité**. Les fichiers bruts de voix choisis sont conservés dans `assets/voice/` pour la reproductibilité de cette maquette ; cela **n’établit pas de licence de diffusion**.

### Écart technique explicite

Le brief visait **12–16 Mb/s** pour la vidéo. Les exports livrés sont encodés en **H.264 CRF 18, qualité perceptuelle élevée, avec un débit moyen plus bas (1,15 à 2,45 Mb/s)** car les scènes photographiques, aplats et interfaces se compressent efficacement. La cible de débit n’est **pas atteinte**. Si un diffuseur l’exige contractuellement, fournir des exports de diffusion à 12–16 Mb/s **hors du dépôt** après validation des éléments officiels ; ne pas présenter ces maquettes comme conformes à cette cible.

## Conception

- **Accroche (0–3 s)** : « TU PAIES ENCORE ? », frustration familière sans opérateur nommé ou montré. La marque n’apparaît **qu’à 14,00 s** après l’appel du chœur et **0,36 s de coupure totale**. Drop sonore à 14,00 s.
- **Une famille fictive récurrente**, digne et moderne, photographie cinématographique sans texte généré. Montages distincts pour 9:16 / 16:9 / 1:1. Mouvement léger sur **chaque photo** et transitions au tempo original de **120 BPM**. Les portraits de référence, six photographies et **prompts complets** sont dans `assets/photos/`, `assets/references/` et [`PROMPTS.md`](PROMPTS.md).
- Les vues de l’application sont **uniquement les quatre captures réelles** et leurs recadrages réels : films, mangas, musiques puis le lecteur vidéo de la quatrième capture. Les onglets Documentaires, TV Direct, Podcasts et Radio existent dans ces captures ; aucune grille de chaînes ni page de catalogue de documentaires n’est inventée. Les familles et les cartes tarifaires sont des visuels de campagne, **pas des captures d’écran de fonctionnalités inexistantes**.
- Le logo typographique jaune/vert à l’écran est **un recadrage de la capture de l’application**, explicitement provisoire. Le vieux logo bleu/vert et l’ancienne photo du matériel MTN ne sont pas utilisés. Aucune box n’est montrée ; Internet est mentionné comme prérequis.
- Les affirmations « des milliers » de films/séries/documentaires/mangas, « des centaines » de chaînes TV et « des milliers » de radios sont reprises **du brief du propriétaire**, sans accès à un inventaire indépendant. Leur exactitude doit être approuvée avant achat média.
- Le prix reste **XAF 2 000 / mois**, **XAF 10 000 / an**. Économie calculée : 12×2 000−10 000 = **XAF 14 000**, soit le coût de **sept mensualités** ; 10 000/365 ≈ **27,4 XAF/jour**, donc « moins de 30 francs par jour ». Ces équivalences supposent l’application des deux tarifs déclarés sur douze mois : **conditions, taxes, renouvellement et offre à confirmer** avant utilisation de « offerts ».
- La voix exprime le petit débit en termes prudents : **« un flux pensé pour rester stable »**, avec **Internet**. Aucune mesure réseau ni garantie technique n’est attestée.

## Qualité vérifiée

- `ffprobe` : durées exactes **59,000 / 30,000 / 15,000 s**, résolution propre à chaque composition, 30 i/s, nombres d’images attendus, son AAC 48 kHz. **Décodage intégral des cinq MP4 sans erreur**.
- Mesure EBU R128 **après encodage AAC** : 59 s portrait **−14,0 LUFS / −1,5 dBTP**, 30 s **−14,1 LUFS / −1,6 dBTP**, 15 s **−14,2 LUFS / −1,5 dBTP**. Les deux autres formats 59 s utilisent le même mix 59 s.
- Contrôles programmatiques : scènes sans trou jusqu’à la dernière image, chaque SRT **≤2 lignes**, lignes portrait à 56 px ≤826 px de largeur dans une zone utile de 850 px ; formule tarifaire vérifiée. **18 photogrammes extraits du MP4 final** et les trois mises en page inspectées.
- Les sons de musique et d’effets sont générés par des fonctions originales de `audio.py` (synthèse instrumentale et bruits), sans sample ni morceau du commerce. Voix sélectionnées pendant la session pour quatre rôles (narrateur masculin, Papa, Maman, Kévin) ; l’accent régional exact et l’âge audible du personnage enfant restent à approuver par une personne francophone de la cible.

## Éléments BLOQUANTS avant diffusion commerciale

1. `[LIEN_TELECHARGEMENT]` URL validée → ensuite seulement produire un **vrai QR** ; dans la maquette, l’espace QR **est vide**, avec « QR À VENIR · LIEN À FOURNIR ». Aucune URL ni numéro WhatsApp inventé.
2. `[LOGO_OFFICIEL]` SVG ou PNG transparent et confirmation de la graphie « MISSA TV 360 » / « MISSA TV 360+ » ; le lockup présent est un extrait authentique mais non un fichier logo certifié.
3. `[HEX_JAUNE]` : fournir le vrai `missaYellowPrimary` de `res/values/colors.xml` (absent du dépôt). **#F4B800** est un échantillon provisoire de la capture, pas une donnée de charte.
4. `[CONDITIONS_OFFRE]` et `[MODES_DE_PAIEMENT]`, notamment validité de « sept mois offerts » en communication commerciale, taxes / durée / renouvellement. `[CONTACT]` facultatif.
5. `[VOIX_AUTORISEE]` : conditions écrites autorisant les voix synthétiques choisies pour l’usage publicitaire ; contrôle de l’accent et du timbre du personnage enfant. Tant que ce point manque, **ne pas diffuser comme publicité autorisée**.
6. Vérifier auprès du propriétaire **les volumes du catalogue** ainsi que le droit de montrer les **affiches de films et visuels tiers présents dans ses propres captures** ; vérifier la qualité de lecture en faible débit avant d’en faire une promesse opérationnelle.

## Reproduction

```bash
python3 projects/missa-tv-360-ton-ecran/timeline.py
python3 projects/missa-tv-360-ton-ecran/audio.py
python3 projects/missa-tv-360-ton-ecran/render.py --ratio portrait --version 59 --crf 18 --output .cache/ton-ecran-video/59-portrait-silent.mp4
python3 projects/missa-tv-360-ton-ecran/render.py --ratio landscape --version 59 --crf 18 --output .cache/ton-ecran-video/59-landscape-silent.mp4
python3 projects/missa-tv-360-ton-ecran/render.py --ratio square --version 59 --crf 18 --output .cache/ton-ecran-video/59-square-silent.mp4
python3 projects/missa-tv-360-ton-ecran/render.py --ratio portrait --version 30 --crf 18 --output .cache/ton-ecran-video/30-portrait-silent.mp4
python3 projects/missa-tv-360-ton-ecran/render.py --ratio portrait --version 15 --crf 18 --output .cache/ton-ecran-video/15-portrait-silent.mp4
python3 projects/missa-tv-360-ton-ecran/assemble.py
```

`audio.py` utilise `ffmpeg`, NumPy et les prises voix `assets/voice/`. Les rendus silencieux et mixes temporaires restent dans `.cache/` et ne sont pas livrés. Les fichiers source utiles, prompts et scripts sont versionnés sur la branche Arena.
