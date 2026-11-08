# MISSA TV 360 — spot 60 s (v10, DA version 2 « essai gratuit 24 h »)

Pub construite à partir des éléments déposés dans `entrees/` :
`MISSA TV 360 — Direction artistique du motion design publicitaire` (storyboard 14 scènes, script VO validé),
`Missa_TV_360_logo_1x1.png` (logo, détouré automatiquement), `icone_tele.png`, bannière et affiche (références de couleurs et de composition).

## Livrables (`livrables/`)

| Fichier | Format |
|---|---|
| `missa-tv-360-v10-16x9.mp4` | master 1920×1080, 30 i/s, 60 s, H.264 + AAC 192 kb/s, −14 LUFS |
| `missa-tv-360-v10-9x16.mp4` | vertical 1080×1920 (WhatsApp statut, TikTok, Reels) |
| `missa-tv-360-v10-*-leger-720p.mp4` | export léger ~1,5 Mb/s (connexion limitée) |
| `missa-tv-360-v10.srt` | sous-titres séparés, calés sur la voix |

## Chaîne de fabrication (depuis la racine du dépôt)

```bash
python3 projects/missa-tv-360-v10/build10.py --vo     # index.html 16:9 + projet 9:16 + .srt + voix (Kokoro local)
python3 projects/missa-tv-360-v10/audio10.py          # musique originale 116 BPM + effets sonores
HYPERFRAMES_BROWSER_PATH=/opt/pw-browsers/chromium npx hyperframes render projects/missa-tv-360-v10 --quality delivery -o .cache/rendus/v10-16x9-video.mp4
HYPERFRAMES_BROWSER_PATH=/opt/pw-browsers/chromium npx hyperframes render projects/missa-tv-360-v10-9x16 --quality delivery -o .cache/rendus/v10-9x16-video.mp4
bash projects/missa-tv-360-v10/mix10.sh               # mixage (ducking) + MP4 finaux + versions légères
```

La source unique est `composition.tpl` ; `index.html` et `projects/missa-tv-360-v10-9x16/` sont **générés** par `build10.py`.

## Respect de la DA

- Script VO lu **mot pour mot** (14 phrases), prononciations imposées (« trois-cent-soixante », « vingt-quatre », « cé-èf-a », « oui-fi »).
- Chiffres toujours en chiffres à l'écran (1 000 / 10 000 FCFA, 24 H), y compris dans les sous-titres.
- « GRATUIT » réservé à l'essai 24 h (scène 8), « OFFERTS » aux 2 mois (scène 11).
- Badge 360 : 3 tours seulement (logo, carte annuelle, appel à l'action).
- Rideau diagonal aux 3 endroits prévus ; cadre-écran pour entrer dans l'appli ; morphing cadran → « ? ».
- Affiches, chaînes et programmes **fictifs** ; aucun logo de magasin d'applications.

## Points provisoires à remplacer

- **Voix off** : voix de synthèse locale (Kokoro, voix française féminine `ff_siwis`), en attendant l'enregistrement
  prévu par la DA (voix jeune, accent d'Afrique centrale). Pour l'intégrer : remplacer `.cache/audio10/vo.wav`
  (mêmes départs de phrases, voir `vo.json`) puis relancer `mix10.sh`.
- **Police** : Product Sans n'est pas dans le dépôt → Montserrat (titres) + Nunito (textes), du même style arrondi.
- **Mentions entre crochets** (non inventées, comme demandé par la DA) : conditions de l'essai gratuit,
  lien / QR code / WhatsApp de téléchargement, conditions d'abonnement.
- Les promesses (streaming stable à faible débit, essai 24 h entièrement gratuit) doivent être tenues par l'appli avant diffusion.
