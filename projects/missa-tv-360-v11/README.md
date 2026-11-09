# MISSA TV 360 — spot v11 (style du storyboard : bleu nuit, néon vert, étiquettes jaunes)

Refonte visuelle de la v10 d'après les nouveaux éléments de `entrees/` (`00_storyboard_complete.png` + images 02 à 16),
sur la **voix fournie `entrees/Pub Missa TV.wav`, utilisée telle quelle** (aucune coupe, aucun effet, aucun changement de volume).

Durée : 54,36 s (voix 50,4 s + 4 s de fin : bouton « Télécharge maintenant ! » puis carte « Le divertissement sans limite ! »).

## Images du storyboard utilisées (agrandies, dans des cartes encadrées)

02 interface TV · 03 famille · 04 films & séries · 05 sport · 07 musique · 10 multi-écrans.
Les autres plans (24 h, prix, « Pourquoi chercher ailleurs ? », icônes, bouton, carte de fin) sont **recréés en animation**
dans le même style, avec du texte net.

**Non reprises volontairement** :
- 06 « Enfants » : Minions et Pat' Patrouille = personnages protégés → carte « Mangas & animés » sans personnage.
- 08 « TV en direct » : vrais logos de chaînes (Canal+, TF1, beIN, BBC…) → mosaïque de chaînes fictives.
- 09 « 4K » : contredit la voix (« même avec une connexion limitée ») et la limite 720p/480p de la DA → scène « streaming stable ».

## Fabrication (depuis la racine du dépôt)

```bash
python3 projects/missa-tv-360-v11/align11.py     # voix fournie → tmap.json (calage phrase par phrase)
python3 projects/missa-tv-360-v11/build11.py     # index.html 16:9 + projet 9:16 + .srt
python3 projects/missa-tv-360-v11/audio11.py     # musique originale + effets, recalés
HYPERFRAMES_BROWSER_PATH=/opt/pw-browsers/chromium npx hyperframes render projects/missa-tv-360-v11 --quality delivery -o .cache/rendus/v11-16x9-video.mp4
HYPERFRAMES_BROWSER_PATH=/opt/pw-browsers/chromium npx hyperframes render projects/missa-tv-360-v11-9x16 --quality delivery -o .cache/rendus/v11-9x16-video.mp4
bash projects/missa-tv-360-v11/mix11.sh          # voix fournie inchangée + musique (ducking) + effets
```

## À fournir

Conditions de l'essai gratuit · lien / QR code / WhatsApp de téléchargement · conditions d'abonnement (affichés entre crochets).
