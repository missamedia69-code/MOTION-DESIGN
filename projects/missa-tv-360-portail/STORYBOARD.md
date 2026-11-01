# MISSA TV 360 — « Le monde s’ouvre »

**Nouvelle vidéo indépendante de la v9.** Format portrait 1080 × 1920, 30 i/s, 37 s. Une même porte lumineuse relie des univers cinéma, musique et jeu ; palette cobalt / jaune de marque / vert signal. Le montage suit exactement 3 + 5 + 7 + 10 + 7 + 5 secondes.

| Temps | Séquence | Traitement et informations à l'écran | Voix française |
| --- | --- | --- | --- |
| 00–03 | Hook | Logo officiel dans une tuile jaune ; « LE MONDE S’OUVRE. » en pop + fade up ; portail du salon. | « Missa TV trois cent soixante ! » |
| 03–08 | Problème | Trois factures arrivent, s'empilent puis rétrécissent ; « TU PAYES ENCORE TROP CHER ? », « ÇA SUFFIT. ». | « Marre de payer cher pour presque rien ? Stop, hein ! » |
| 08–15 | Solution | Compteurs prix 2 000 XAF/mois et 10 000 XAF/an ; « LE MONDE EN FACE DE VOUS. » ; Android TV / tablette / téléphone ; box Wi-Fi NET. | « Deux mille le mois, dix mille l'an. Le monde en face de toi, avec ta box Wi-Fi ! » |
| 15–25 | Modules | Trois passages photo : films/séries/manga → musique/shorts-dramas → jeux vidéo/podcasts/radio ; mini-produit NET en zoom Ken Burns continu. | « Films, séries, mangas. Musique, shorts-dramas. Jeux vidéo, podcasts, radio ! » |
| 25–32 | Stabilité | Signal orange accidenté → ligne verte continue et coche ; « MÊME CONNEXION FAIBLE ? » → « FLUX STABLE. » ; « PENSÉ POUR LES PETITS DÉBITS ». | « Petit débit ? Pas de panique. Le flux reste stable, même quand ça ralentit. » |
| 32–37 | CTA | Logo officiel ; « TÉLÉCHARGEZ MAINTENANT » ; emplacement QR **explicitement non scannable** ; rappel des prix. | « Missa TV trois cent soixante. Télécharge maintenant ! » |

## Choix éditoriaux

- Le logo **MTN n'apparaît pas** : la box reste **NET**, comme demandé lors de la correction précédente. Le Ken Burns de la séquence 4 s'applique à son image.
- Faute de preuve ou de conditions de test, la vidéo n'affirme pas « garanti », « testé en zone rurale » ni la lecture vidéo en 2G. Elle conserve le bénéfice demandé (« petit débit », « flux stable ») sans présenter une certification non fournie. À faire valider avant diffusion commerciale.
- Aucun lien de téléchargement n'a été fourni : le carré en fin de film est un **emplacement QR**, pas un faux code qui mènerait ailleurs. Le remplacer dès que l'URL officielle sera disponible.
- Portraits et univers générés pour ce film ; logo et photographie du produit repris de la bibliothèque du dépôt. Voix sélectionnée lors de la v9 (français), musique et effets synthétiques originaux dans `sound.py`.

## Contrôle du master

- `hf check` : réussi, 0 erreur de composition / layout / motion ; contraste 40/40.
- Rendu : 37,000 s, H.264 1080 × 1920, 30 i/s, AAC stéréo 44,1 kHz ; qualité `delivery`.
- Mix : environ −16,6 LUFS intégrés et −1,9 dBTP (mesure `ebur128`).
- Contrôle visuel : images prélevées dans le **MP4 final** aux secondes 1,6 / 7,2 / 10,5 / 13,4 / 17 / 20 / 23,5 / 29,8 / 35,5.

## Production

```bash
# Depuis la racine du dépôt, une fois HyperFrames installé :
./scripts/hf check projects/missa-tv-360-portail
./scripts/hf render projects/missa-tv-360-portail --quality delivery \
  --output .cache/rendus/missa-tv-360-portail-silent.mp4
python3 projects/missa-tv-360-portail/sound.py
# La VO .cache/vo10/s1..s6.mp3 est générée avec la voix choisie dans la session.
python3 projects/missa-tv-360-portail/mix.py
# → livrables/missa-tv-360-portail.mp4
```
