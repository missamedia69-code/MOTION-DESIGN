# MISSA TV 360 — « L’appli en vrai » (59 secondes)

**Master :** [`livrables/missa-tv-360-portail.mp4`](../../livrables/missa-tv-360-portail.mp4) — **59,000 s**, 1080 × 1920, 30 i/s. Cette nouvelle proposition abandonne le collage clair, les photos d’exemple et le visuel de box généré. Elle adopte les couleurs et la logique **de l’application réelle** : noir profond, jaune de navigation, vert discret, grandes typographies, gros plans sur les quatre captures fournies par le client. Aucune photo de salle, chanteuse ou joueur ne subsiste dans le film ni dans les assets du projet.

| Temps | Visuel / idée | Voix (verbatim) |
| --- | --- | --- |
| 00–06 | **Accroche :** vraie capture films dès le début, glissement vers la rubrique musique ; « CE SOIR, TU AS ENVIE DE QUOI ? » | « Ce soir, tu as envie de quoi ? Pose-toi, on va trouver. » |
| 06–16 | **Problème :** « UNE APPLI. PUIS UNE AUTRE. » ; ouvrir, chercher, recommencer → « PLUS SIMPLE ? ». Typographie seule, sans factures fictives. | « Tu connais ces soirs où tu ouvres une appli, puis une autre. Les abonnements s'accumulent, et toi, tu cherches encore... On peut faire plus simple. » |
| 16–29 | **Solution :** prix fixes **2 000 XAF/mois** et **10 000 XAF/an** ; box **NET** en illustration vectorielle, marquée comme telle, et prérequis **Wi-Fi + Internet** ; télé, tablette, téléphone. | « Avec Missa TV trois cent soixante, tu choisis : deux mille francs le mois, ou dix mille l'année. » / « Avec ta box NET, le Wi-Fi et Internet, ça suit sur la télé, la tablette ou ton téléphone. » |
| 29–35,05 | **Regarder :** capture films → capture mangas ; vrai zoom sur le **bouton Documentaires** (visible dans la capture du client). Aucune page de catalogue documentaire n’est inventée. | **« Films, séries, mangas, documentaires... choisis ce qui te plaît. »** |
| 35,05–40,55 | **Télé + musique :** zoom sur le véritable onglet **TV Direct**, puis sur la capture musique et le lecteur vidéo recadré depuis la quatrième capture. Aucun faux logo de chaîne ni faux programme. | **« Chaînes de télé, musique, shorts-dramas... tu changes d'ambiance. »** |
| 40,55–46 | **Autres envies :** quatrième capture originale, puis vrais onglets Podcasts et Radio, plus le texte Jeux vidéo. | « Et pour changer, il y a aussi les jeux vidéo, les podcasts et la radio. » |
| 46–53 | **Petit débit :** tracé cassé → ligne continue ; « PENSÉ POUR UN FLUX STABLE » et non une garantie de performance. | « Même avec un petit débit, le flux est pensé pour rester stable. Tu gardes le fil. » |
| 53–59 | **Invitation :** vignettes issues des vraies captures, téléchargement, rappel des prix et **QR À VENIR** non scannable. | « Télécharge Missa TV trois cent soixante. Ce soir, c'est toi qui choisis. » |

## Images, voix et workflow

- **Seules les captures originales du client** `app-films.png`, `app-mangas.png`, `app-music.png`, `app-player.png` et leurs recadrages fidèles sont utilisées comme images. `prepare_ui.py` génère les rangées films/mangas, le lecteur et trois zooms de navigation `ui-nav-docs.png`, `ui-nav-tv.png`, `ui-nav-audio.png`. Les onglets Documentaires et TV Direct **existent bien dans les captures**, mais leurs pages de résultats n’ont pas été fournies : le film ne prétend pas en montrer le contenu.
- La box **NET** est une **illustration graphique**, non une photographie ni un modèle de matériel certifié. Les anciennes photos/illustrations d’exemple et l’ancien logo recréé ont été retirés des assets de ce projet.
- Le mix percussif et la voix précédemment appréciés sont préservés hors de **29–40,6 s**. Dans cet intervalle, seules **deux phrases de la même voix sélectionnée** sont remplacées pour mentionner clairement *documentaires* et *chaînes de télé*. Les recouvrements de 0,17 à 0,33 s assurent une transition audio douce, sans accélération de voix. `sound.py` ne modifie que quelques effets synchronisés aux nouveaux swipes/zooms.
- Le mix conserve la bande-son du master précédent depuis le commit `c7ee4ad` (dans l’historique Git, pas dans `livrables/`). `mix.py` sait la récupérer automatiquement si son cache temporaire manque. Les deux clips nouveaux sont attendus dans `.cache/vo59-revision/{s4a-short,s4b-short}.mp3`.

## Précautions éditoriales

- **Prix** : 2 000 XAF/mois et 10 000 XAF/an, toujours fixes à l’image. La box porte **NET** ; le Wi-Fi **et une connexion Internet** sont requis.
- « Pensé pour un flux stable même avec un petit débit » correspond au brief, mais **reste à confirmer avant toute diffusion commerciale**. Ni « garanti », ni « testé en zone rurale », ni lecture vidéo en 2G ne sont affirmés.
- Faute d’URL officielle, « QR À VENIR » est un **emplacement non scannable**. Aucun lien inventé.

## Contrôle du nouveau master

- HyperFrames `check` : **0 erreur**, 10 recommandations de structure/découverte de médias non bloquantes ; **37/37 textes conformes WCAG AA** ; aucune erreur runtime ni de mise en page.
- **59,000 s exactement** (1770 images), H.264 1080 × 1920 / 30 i/s, AAC stéréo 44,1 kHz. Décodage intégral sans erreur, **19 photogrammes du MP4 final** contrôlés (dont Documentaires, TV Direct, tarifs, NET, QR).
- Audio : environ **−16,6 LUFS intégrés / −2,6 dBTP**. La bande-son hors des deux répliques révisées reste celle du master apprécié.
- `livrables/` contient **uniquement ce master**, sans anciennes versions.

## Reproduction

```bash
# Depuis la racine du dépôt, avec les dépendances installées :
python3 projects/missa-tv-360-portail/prepare_ui.py
./scripts/hf check projects/missa-tv-360-portail
./scripts/hf render projects/missa-tv-360-portail --quality delivery \
  --output .cache/rendus/missa-tv-360-portail-product-silent.mp4
python3 projects/missa-tv-360-portail/sound.py
# Fournir deux prises dans .cache/vo59-revision/ :
# s4a-short.mp3 « Films, séries, mangas, documentaires... choisis ce qui te plaît. »
# s4b-short.mp3 « Chaînes de télé, musique, shorts-dramas... tu changes d'ambiance. »
python3 projects/missa-tv-360-portail/mix.py
# → livrables/missa-tv-360-portail.mp4 (59,000 s)
```
