# MISSA TV 360 — « Ton divertissement mérite mieux »

**Nouvelle campagne / nouveau brief, 59,000 secondes à 30 i/s.** Ce projet remplace les exports narratifs « Ton écran » ; ses plans, sa voix off, son conducteur, son mix et les montants en **FCFA** sont nouveaux. L'ancien dossier reste dans le dépôt uniquement pour les captures, polices et primitives musicales réutilisées. Les exports ci-dessous sont des **maquettes de validation** ; ils ne sont pas autorisés pour diffusion commerciale tant que les points de contrôle n'ont pas été validés.

## Conducteur éditable

| Début–fin | Plan / montage | Script voix off |
|---|---|---|
| 00–05 s | Recherche/zapping, salon contemporain fictif ; tension discrète. | « Tu cherches toujours quelque chose de nouveau à regarder ? » |
| 05–11 s | Choix limité, graphismes abstraits non assimilables à une interface produit. | « Quand le choix est limité, le divertissement perd vite son goût. » |
| 11–17 s | Révélation MISSA TV 360, montée musicale, première capture **réelle**. | « Découvre MISSA TV 360 : ton univers de divertissement, à portée de main ! » |
| 17–29 s | Films, séries, onglet documentaires, mangas ; onglet TV Direct. | « Des milliers de films, séries, documentaires et mangas, sans oublier des centaines de chaînes télévisées. » |
| 29–37 s | Photo urbaine fictive + capture réelle de l'onglet audio. | « Et pour écouter, retrouve aussi des podcasts et des milliers de stations radio. » |
| 37–47 s | Tarifs sur deux cartes successives : **2 000 FCFA / mois**, **10 000 FCFA / an**. | « Et tout ça, avec une formule à deux mille francs CFA par mois, ou dix mille francs CFA pour toute l’année. » |
| 47–54 s | Diversité/émotion, portrait contemporain fictif. | « Fais le choix de la diversité. Ton divertissement mérite mieux ! » |
| 54–59 s | Signature typographique provisoire, CTA sans faux QR ni URL. | « Télécharge MISSA TV 360 dès maintenant ! » |

Le texte complet des sous-titres, les huit bornes et leurs horodatages se modifient dans [`timeline.py`](timeline.py). Le slogan **« Ton divertissement mérite mieux. Passe à MISSA TV 360 ! »** traverse les scènes finales ; l'injonction « Passe à… » est écrite à l'écran sans remplacer la phrase de voix off fournie pour la conclusion. Les seules appellations de prix affichées sont exactement `2 000 FCFA / mois` et `10 000 FCFA / an`. Les montants sont prononcés en toutes lettres. **« Des milliers », « des centaines » et « des milliers de stations » sont des assertions du brief qui restent à prouver avant diffusion.**

## Livrables

| Fichier dans `livrables/` | Contenu |
|---|---|
| `MISSA_TV_360_PUB_59S_16x9.mp4` | Master 1920×1080, H.264/AAC, voix féminine + musique/FX, sous-titres incrustés. |
| `MISSA_TV_360_PUB_59S_9x16.mp4` | Recomposition verticale **1080×1920**, non recadrée du master. |
| `MISSA_TV_360_PUB_59S_1x1.mp4` | Recomposition carrée **1080×1080**, non recadrée du master. |
| `MISSA_TV_360_PUB_59S_16x9_SANS_VOIX.mp4` | Master 16:9 **sans voix ni sous-titres incrustés**, avec musique et effets, pour localisation. |
| `MISSA_TV_360_PUB_59S_fr.srt` | 15 sous-titres français exportables séparément ; version identique dans les trois cadrages avec voix. |
| `MISSA_TV_360_COUVERTURE_16x9.jpg` | Miniature 1920×1080 sans sous-titres, construite sur la révélation et la vraie capture client. |
| `PISTES_SEPAREES_59S/VOIX_59S.wav`, `MUSIQUE_59S.wav`, `EFFETS_59S.wav` | Trois stems PCM 24 bits / 48 kHz de 59,000 s, dont la voix seule. |
| `MISSA_TV_360_VALIDATION_59S.json` | Vérification automatique : dimensions, 1770 images, 30 i/s, 59,000 s, audio, 15 cues et points à approuver. |

Les prises de voix source (`assets/voice/*.mp3`), les images fictives (`assets/photos/*.jpg`), les scripts [`film.py`](film.py), [`sound.py`](sound.py), [`build.py`](build.py) et le conducteur sont présents dans ce projet. La variante sans voix a une composition spécifique, sans sous-titres incrustés : ce n'est pas une simple piste mise en sourdine.

## Reproduction

Depuis la racine du dépôt, après installation de `python3`, `numpy`, `pillow`, `ffmpeg` et `ffprobe` :

```bash
python3 projects/missa-tv-360-diversite/build.py --check   # inspecter les exports existants
python3 projects/missa-tv-360-diversite/build.py --render  # remonter les pistes et les quatre vidéos
python3 projects/missa-tv-360-diversite/film.py --ratio landscape --at 14,39,56  # images-tests
```

`film.py` crée **1 770 images** par ratio à 30 i/s ; le décor, le placement des éléments, les prix et la typographie sont recomposés dans chaque ratio. Les caches de travail restent sous `.cache/diversite-*` et ne sont pas des livrables. Le mix vise environ **−14 LUFS intégrés**, avec la musique abaissée sous les prises de parole. `sound.py` produit une composition instrumentale afro-urbaine/électronique sans paroles avec percussions, nappes, effet de zapping, sweeps légers et signature finale ; aucun enregistrement musical tiers n'est utilisé.

## Vérifications obligatoires avant toute publication

1. Obtenir la **confirmation écrite des prix**, devises, conditions, disponibilité, durée de validité et plateformes desservies ; les chiffres affichés reprennent le brief, pas un tarif vérifié.
2. Valider les volumes du catalogue (films, séries, chaînes TV et radios). Les captures fournies ne prouvent pas les « milliers »/« centaines » annoncés. **Aucune grille TV ni page documentaire n'a été fabriquée** : seuls leurs onglets réellement capturés sont montrés. Les catalogues en capture peuvent changer.
3. Vérifier les **droits d'usage des affiches de films/mangas et visuels de clips** visibles dans les captures fournies. Remplacer/flouter les affiches non autorisées avant diffusion commerciale.
4. Substituer le **logo officiel**, la couleur de marque certifiée et le véritable lien de téléchargement approuvé. La signature « MISSA TV 360 » n'est qu'une composition typographique provisoire. Aucun QR code ou URL n'a été inventé.
5. Confirmer les droits commerciaux de la **voix de synthèse sélectionnée** et des **deux photographies fictives générées** pour cette maquette. La voix `voice-09` est féminine, sélectionnée pour un usage publicitaire, en français naturel ; l'option `fr-CM` n'était pas disponible. **Ne pas la présenter comme une voix à l'accent camerounais certifié.** Remplacer par une comédienne/voix locale si la validation régionale l'exige.
6. Obtenir l'approbation finale de la marque sur le texte, la musique, les visuels et toutes les mentions avant diffusion.

Les mentions « MAQUETTE » et « À CONFIRMER » restent visibles en bas des films tant que les validations ci-dessus manquent. Aucun fichier de ce dossier ne doit être qualifié de prêt à la diffusion commerciale.
