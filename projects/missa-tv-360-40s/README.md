# MISSA TV 360 — pub motion design 9:16 (33,4 s)

Pub verticale 1080×1920, 30 i/s, **calée sur la voix fournie** (`assets/voix.wav`, 33,4 s, utilisée telle quelle avec sa musique).
Texte et éléments demandés : [SCRIPT-ET-ELEMENTS.md](SCRIPT-ET-ELEMENTS.md).

## Scènes

| Temps | Scène | Mix 2D / 3D |
|---|---|---|
| 0,0–3,0 | Accroche « Tu paies chaque mois… » | Télé 3D grise qui zappe sur la même rediff, ticket « PAYÉ » qui défile, titre glitch |
| 3,0–4,0 | « On mérite mieux ! » | Typo qui claque, onde de choc jaune |
| 4,0–8,5 | Révélation | Logo en relief qui pivote, objets 3D (clap, popcorn, micro, casque, pellicule), pilule verte |
| 8,5–13,8 | Catalogue | Téléphone en perspective avec l'appli qui défile, objets 3D par univers, étiquettes néon |
| 13,8–16,3 | Recherche | Loupe 3D, frappe « Horizon 2030 », résultats, affiche + « Regarder », tampon « IL EST LÀ ! » |
| 16,3–20,6 | Technique | Box WiFi et ondes citron, jauge de débit, lecture fluide, barre de données |
| 20,6–22,8 | Écrans | Téléphone → tablette → télé |
| 22,8–25,0 | Essai 24 h | Chrono 3D, arc vert, « 24H D'ESSAI », ruban « GRATUIT » |
| 25,0–29,5 | Prix | Cartes 1 000 FCFA / mois et 10 000 FCFA / an, ruban « 2 MOIS OFFERTS ! », cadeau 3D |
| 29,5–33,4 | Appel final | Logo, slogan, bouton « Télécharge maintenant ! », QR code vers missatv.pages.dev |

Sous-titres mot à mot sur toute la durée (mot prononcé en jaune).

## Sources des éléments

- Logo en relief : détouré depuis la bannière fournie (`assets/banniere-logo-3d.png`).
- Vignettes de films : titres fictifs repris de l'affiche fournie (`assets/affiche-9x16.png`).
- Objets 3D : Microsoft Fluent Emoji 3D, licence MIT (`assets/elements/LICENCES.md`).
- Bruitages : synthétisés par `sfx/generate.py` (aucun fichier externe).
- Polices : Montserrat et Nunito (SIL OFL).

## Fabrication (depuis ce dossier)

```bash
python3 tools/align.py      # calage mot à mot voix ↔ script.txt → words.json
python3 tools/build.py      # composition.tpl → index.html + missa-tv-360-pub.srt
python3 sfx/generate.py     # bruitages
python3 tools/mix.py        # voix inchangée + bruitages → rendu/audio-mix.wav
HYPERFRAMES_BROWSER_PATH=/opt/pw-browsers/chromium npx --yes hyperframes@0.8.142 render . --quality delivery -o ../../.cache/rendus/m40-9x16-video.mp4
ffmpeg -i ../../.cache/rendus/m40-9x16-video.mp4 -i rendu/audio-mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 256k -shortest rendu/missa-tv-360-pub-9x16.mp4
```
