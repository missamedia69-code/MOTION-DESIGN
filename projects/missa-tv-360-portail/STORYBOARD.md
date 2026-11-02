# MISSA TV 360 — « Ton envie fait le programme » (59 secondes)

**Master :** [`livrables/missa-tv-360-portail.mp4`](../../livrables/missa-tv-360-portail.mp4) — **59,000 s**, portrait 1080 × 1920, 30 i/s. Ce film remplace la direction « portail sombre / néon » : c'est désormais un **collage éditorial lumineux**, avec des aplats crème, bleu cobalt, jaune, corail et vert, des ombres découpées et des transitions au rythme de la musique. Le mouvement part des **vraies captures de l'application**, non de faux écrans reconstitués. La voix est moins déclamatoire, plus conversationnelle, avec de la place pour respirer.

| Temps | Récit et mise en scène | Voix (verbatim) |
| --- | --- | --- |
| 00–06 | **Accroche.** Soleil jaune, titre « CE SOIR, TU CHOISIS. » ; capture réelle des films qui glisse vers la rubrique musique. Le premier écran entre dès les premières images. | « Ce soir, tu as envie de quoi ? Pose-toi, on va trouver. » |
| 06–16 | **Problème.** Trois fiches s'entassent : une appli de plus, un autre abonnement, et toujours la même question. Elles s'effacent devant « ON PEUT FAIRE PLUS SIMPLE. » | « Tu connais ces soirs où tu ouvres une appli, puis une autre. Les abonnements s'accumulent, et toi, tu cherches encore... On peut faire plus simple. » |
| 16–29 | **Solution.** Deux tickets qui montrent **uniquement** « 2 000 XAF / mois » et « 10 000 XAF / an » ; vraie image de la box **NET**, accompagnée de **Wi-Fi + Internet** et de la télé, la tablette, le téléphone. | « Avec Missa TV trois cent soixante, tu choisis : deux mille francs le mois, ou dix mille l'année. » / « Avec ta box NET, le Wi-Fi et Internet, ça suit sur la télé, la tablette ou ton téléphone. » |
| 29–46 | **Univers.** 29–35 : l'interface films coulisse vers la capture mangas, tandis que les rangées d'affiches se remplacent avec un geste de swipe. 35–40,55 : catalogue musical, puis gros plan fidèle de la quatrième capture sur le lecteur, avec une chanteuse en photo découpée. 40,55–46 : photo du joueur et étiquettes jeux vidéo/podcasts/radio. | « Un film, une série, un manga... choisis l'histoire qui te fait plaisir. » / « De la musique, des shorts-dramas... tu changes d'ambiance quand tu veux. » / « Et pour changer, il y a aussi les jeux vidéo, les podcasts et la radio. » |
| 46–53 | **Petit débit.** Une ligne pointillée devient continue ; à l'écran : « ON GARDE LE FIL. » et « PENSÉ POUR UN FLUX STABLE. » | « Même avec un petit débit, le flux est pensé pour rester stable. Tu gardes le fil. » |
| 53–59 | **Invitation.** « TON ENVIE FAIT LE PROGRAMME. » ; trois vignettes issues de l'application, bouton « TÉLÉCHARGE L’APPLI », rappel des deux tarifs et **QR À VENIR** explicitement fictif. | « Télécharge Missa TV trois cent soixante. Ce soir, c'est toi qui choisis. » |

## Animation d'interface et workflow

- `assets/app-films.png`, `app-mangas.png`, `app-music.png`, `app-player.png` sont les **quatre captures fournies par le client**, conservées telles quelles. Les glissements, recadrages, zooms et changements d'écran sont des animations GSAP dans `index.html` ; l'image réelle reste identifiable.
- `prepare_ui.py` recadre exclusivement des pixels existants pour créer `ui-films-row.png`, `ui-mangas-row.png`, `ui-music-player.png` et `app-player-focus.png`. Ce dernier est exactement la région `(57, 185)–(474, 453)` de `app-player.png` ; le titre du jeu hors sujet dans la séquence musicale n'est pas repris. Aucune jaquette ni commande du lecteur n'est inventée.
- Les photographies et la box viennent des assets déjà présents ; la typographie et les aplats structurent un **nouvel univers visuel** plutôt que de remaquiller l'ancien. Le groove à 110 BPM, les percussions légères, les papiers froissés et les clics d'interface sont synthétisés de manière déterministe par `sound.py`.
- Neuf nouvelles prises de voix ont été régénérées dans `.cache/vo59-editorial/`. Elles **ne sont pas accélérées** au mixage. Le français est proche et simple ; pas de marqueur de dialecte forcé ou d'accent caricaturé.

## Limites éditoriales

- Les seuls prix affichés sont **2 000 XAF/mois** et **10 000 XAF/an**, sans compteurs qui passent par d'autres montants. La box affiche **NET**, jamais MTN ; la connexion Internet est explicitement requise.
- « Pensé pour un flux stable même avec un petit débit » répond au brief, **mais cette performance reste à confirmer avant diffusion commerciale**. Pas de « garanti », pas de « testé en zone rurale », pas d'affirmation de lecture vidéo en 2G.
- Aucune URL officielle n'a été fournie : le graphisme **« QR À VENIR » est non scannable**. Il faudra intégrer un vrai code seulement une fois le lien validé. L'identité logo provient de la composition existante et peut être remplacée si le fichier de marque définitif est fourni.

## Contrôle du master

- `./scripts/hf check projects/missa-tv-360-portail` : **0 erreur**, 8 recommandations de structure sans blocage, **29/29 textes conformes WCAG AA** ; aucune alerte runtime ni de disposition après correction.
- Rendu `delivery` : **1770 images / 59,000 s**, vidéo H.264 1080 × 1920 à 30 i/s, audio AAC stéréo 44,1 kHz. Décode intégralement sans erreur ; 23 photogrammes extraits du MP4 final et inspectés, notamment les quatre captures, les prix, la box NET, le faible débit et le CTA.
- Mix `ebur128` : environ **−16,6 LUFS intégrés / −2,7 dBTP**. Aucun chevauchement de voix entre chapitres ; la dernière phrase se termine avant 59 s.

## Reproduction (depuis la racine du dépôt)

```bash
python3 projects/missa-tv-360-portail/prepare_ui.py
./scripts/hf check projects/missa-tv-360-portail
./scripts/hf render projects/missa-tv-360-portail --quality delivery \
  --output .cache/rendus/missa-tv-360-portail-editorial-silent.mp4
python3 projects/missa-tv-360-portail/sound.py
# Replacer les neuf prises de voix dans .cache/vo59-editorial/ :
# s1,s2,s3a,s3b,s4a,s4b,s4c,s5,s6.mp3 (non versionnées, conformément à .gitignore).
python3 projects/missa-tv-360-portail/mix.py
# → livrables/missa-tv-360-portail.mp4, exactement 59,000 s
```
