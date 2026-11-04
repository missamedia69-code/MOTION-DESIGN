# Dépôt des fichiers fournis par l'utilisateur

Dépose ici les éléments décidés au tour 3. Tant qu'ils ne sont pas présents,
le montage utilise des **placeholders** clairement identifiés (carrés gris pour
les vignettes, logo texte, audio silencieux de référence).

## Audio de la voix off

Le template vocal annoncé (`assets/audio/Voive Template.mp3`) n'est jamais
arrivé dans le workspace. En attendant, une **VO de travail** a été générée
avec la voix **`voice-02`** (féminine francophone) sélectionnée par audition
après que `voice-00` a été jugée trop éloignée du timbre souhaité :

- `voix-off.mp3` — prise continue de référence (44,32 s), pour écouter le
  timbre ; non utilisée au montage.
- `vo/seq-01…06.mp3` — 6 segments **rognés** des silences TTS (49,50 s au
  total), posés sur la timeline ; voir `../TIMING.md`.
- `vo/raw/seq-01…06.mp3` — segments bruts avant rognage.
- Pour fournir une vraie VO : déposer `voix-off.mp3` ou `voix-off.wav` ici,
  puis relancer `../timing/trim_silence.py` et `../timing/generate.py`.
- Optionnel : `musique.mp3` (décision actuelle : **aucune musique**, SFX seuls).

## Pack de marque

- `logo.png` (ou `.svg` converti en PNG transparent) — version HD du logo MISSA TV 360.
- `charte.md` / `charte.json` — couleurs exactes (`#RRGGBB`), polices, règles d'usage.
- `captures/` — captures réelles de l'application si disponibles :
  écran d'accueil / essai 24 h, page QR code de blocage, champ du code d'activation,
  navigation dans le catalogue.
- `vignettes/` — visuels pour les 10 univers (films, manga, séries, short drama,
  TV & radio, lives, sport, documentaires, enfants, jeux vidéo). Des placeholders
  typographiques seront utilisés à défaut.

## Note Git

Les images (`*.png`, `*.jpg`) sont versionnées par le dépôt ; les fichiers audio
(`*.mp3`, `*.wav`, …) sont ignorés par `.gitignore`. Ils restent donc locaux au
workspace, sauf demande explicite de les ajouter avec `git add -f`.
