# MISSA TV 360 — spot 53 s (v10, DA version 2 « essai gratuit 24 h »)

Pub construite à partir des éléments déposés dans `entrees/` :
**`Pub Missa TV.wav`** (voix off fournie, 50,4 s, utilisée telle quelle),
`MISSA TV 360 — Direction artistique du motion design publicitaire` (storyboard 14 scènes, script VO validé),
`Missa_TV_360_logo_1x1.png` (logo, détouré automatiquement), `icone_tele.png`, bannière et affiche (références de couleurs et de composition).

## Livrables (`livrables/`)

| Fichier | Format |
|---|---|
| `missa-tv-360-v10-16x9.mp4` | master 1920×1080, 30 i/s, 52,96 s (voix 50,4 s + tenue finale 2,6 s), H.264 + AAC 192 kb/s |
| `missa-tv-360-v10-9x16.mp4` | vertical 1080×1920 (WhatsApp statut, TikTok, Reels) |
| `missa-tv-360-v10-*-leger-720p.mp4` | export léger ~1,5 Mb/s (connexion limitée) |
| `missa-tv-360-v10.srt` | sous-titres séparés, calés sur la voix |

## Chaîne de fabrication (depuis la racine du dépôt)

```bash
python3 projects/missa-tv-360-v10/align10.py          # aligne la voix fournie sur la timeline → tmap.json
python3 projects/missa-tv-360-v10/build10.py          # index.html 16:9 + projet 9:16 + .srt, recalés via tmap.json
python3 projects/missa-tv-360-v10/audio10.py          # musique originale 116 BPM + effets, recalés via tmap.json
HYPERFRAMES_BROWSER_PATH=/opt/pw-browsers/chromium npx hyperframes render projects/missa-tv-360-v10 --quality delivery -o .cache/rendus/v10-16x9-video.mp4
HYPERFRAMES_BROWSER_PATH=/opt/pw-browsers/chromium npx hyperframes render projects/missa-tv-360-v10-9x16 --quality delivery -o .cache/rendus/v10-9x16-video.mp4
bash projects/missa-tv-360-v10/mix10.sh               # voix fournie inchangée + musique (ducking) + effets → MP4 finaux
```

La source unique est `composition.tpl` (écrite sur une timeline de référence de 60 s). `tmap.json` (alignement
DTW de la voix fournie sur cette référence) déplace chaque scène, animation, sous-titre et effet sonore à
l'instant où la phrase correspondante est dite. `index.html` et `projects/missa-tv-360-v10-9x16/` sont **générés**.
`align10.py` a besoin de la voix de référence `.cache/audio10/vo-ref.wav` (`build10.py --vo`, puis copie).

**La voix fournie n'est pas modifiée** : ni coupe, ni changement de vitesse, ni compression, ni égalisation,
ni changement de volume. Seule conversion : 24 kHz mono → 48 kHz stéréo (canal dupliqué) pour l'AAC.

## Respect de la DA

- Voix off fournie par le client (`entrees/Pub Missa TV.wav`), utilisée telle quelle ; scènes et sous-titres calés phrase par phrase dessus.
- Chiffres toujours en chiffres à l'écran (1 000 / 10 000 FCFA, 24 H), y compris dans les sous-titres.
- « GRATUIT » réservé à l'essai 24 h (scène 8), « OFFERTS » aux 2 mois (scène 11).
- Badge 360 : 3 tours seulement (logo, carte annuelle, appel à l'action).
- Rideau diagonal aux 3 endroits prévus ; cadre-écran pour entrer dans l'appli ; morphing cadran → « ? ».
- Affiches, chaînes et programmes **fictifs** ; aucun logo de magasin d'applications.

## Points provisoires à remplacer

- **Police** : Product Sans n'est pas dans le dépôt → Montserrat (titres) + Nunito (textes), du même style arrondi.
- **Mentions entre crochets** (non inventées, comme demandé par la DA) : conditions de l'essai gratuit,
  lien / QR code / WhatsApp de téléchargement, conditions d'abonnement.
- Les promesses (streaming stable à faible débit, essai 24 h entièrement gratuit) doivent être tenues par l'appli avant diffusion.
