# MISSA TV 360 — « Ton monde s’ouvre » (59 secondes)

Master : [`livrables/missa-tv-360-portail.mp4`](../../livrables/missa-tv-360-portail.mp4), **59,000 s exactement**, portrait 1080 × 1920, 30 i/s. Création distincte de la v9, en six chapitres. La révision fait entrer **l’application réelle dès la première seconde** : captures fournies par le client dans des cadres animés, raccordées à des univers photo. Couleurs inspirées de la palette panafricaine (vert, jaune, terre corail), empreintes textiles **sur les bords** et accents typographiques ; la texture ne masque pas les captures. Un groove afro-électronique démarre à l’image zéro et les effets ponctuent l’apparition des interfaces.

| Temps | Chapitre | Texte et action à l'écran | Voix (verbatim) |
| --- | --- | --- | --- |
| 00–06 | Accroche | L’interface films apparaît tout de suite, puis glisse vers la musique ; logo, pastilles « FILMS / MANGAS / MUSIQUES », « TON MONDE S’OUVRE. » et « LE DIVERTISSEMENT À TON RYTHME. » | « Missa TV trois cent soixante... ton monde s'ouvre ! » |
| 06–16 | Problème | Trois abonnements/factures s'accumulent. « ENCORE UN ABONNEMENT ? » → « ÇA SUFFIT. » | « Tu paies encore un abonnement, puis un autre... et au final, tu regardes toujours la même chose. Chaque fin de mois, ça pèse sur le portefeuille. Franchement, ça suffit, hein ! » |
| 16–29 | Solution | « LE MONDE EN FACE DE TOI. » ; 2 000 XAF/mois ou 10 000 XAF/an ; box NET, **Wi-Fi + Internet**, puis Android TV, tablette et téléphone. | « Deux mille francs le mois, dix mille francs l'année : c'est toi qui choisis. » / « Avec ta box Wi-Fi et Internet, tu regardes sur ta télé, ta tablette ou ton téléphone. » |
| 29–46 | Univers | 29–34,9 : la capture films passe aux mangas sur la scène cinéma ; 34,9–40,1 : catalogue musical puis gros plan fidèle de la capture du lecteur sur la scène musicale ; 40,1–46 : jeux vidéo/podcasts/radio. | « Films, séries, mangas... pose-toi et choisis ton histoire ! » / « Musique, shorts-dramas : suis ton envie du moment. » / « Jeux vidéo, podcasts, radio... chacun trouve son truc ! » |
| 46–53 | Petit débit | « PETIT DÉBIT ? ÇA CONTINUE. » ; signal irrégulier → ligne fluide → « FLUX STABLE. » | « Même avec un petit débit, le flux reste stable. Tu continues tranquille, hein ! » |
| 53–59 | Appel à l’action | Logo ; « TON MONDE T’ATTEND. » ; « TÉLÉCHARGE MAINTENANT » ; emplacement QR non scannable ; rappel des deux prix. | « Ton monde t'attend. Télécharge maintenant, on est ensemble ! » |

## Cohérence et provenance

- Tutoiement du début à la fin ; français oral naturel (« ça suffit, hein », « pose-toi », « on est ensemble »), sans caricature.
- **Quatre captures du client intégrées** : `assets/app-films.png`, `app-mangas.png`, `app-music.png`, `app-player.png`. `app-player-focus.png` est un simple recadrage de la dernière image pour isoler le lecteur, sans retoucher ni inventer son interface. L’écran du jeu visible ailleurs dans la capture originale n’est pas présenté comme du contenu musical.
- Les photos d’univers et le visuel de box/identité proviennent des assets de la composition précédente ; la musique et les effets sont synthétisés par `sound.py`. Les vrais écrans ne sont pas recolorés : les accents panafricains sont ajoutés **autour**.
- Les tarifs sont **2 000 XAF/mois** et **10 000 XAF/an**. Les cartes bougent, mais leurs chiffres restent fixes : aucun montant intermédiaire trompeur pendant l’animation. La box porte **NET**, jamais MTN, et l’histoire précise **Wi-Fi + Internet** sans suggérer qu’une box seule donne accès au catalogue.
- La formulation « flux stable avec un petit débit » répond au brief, **mais demande confirmation avant diffusion commerciale**. Aucune affirmation « garanti », « testé en zone rurale » ou « vidéo en 2G » sans preuve.
- Pas d’URL de téléchargement officielle : le dernier plan indique **« EMPLACEMENT QR »**, non scannable. Si le client fournit le lien, il faudra remplacer cet emplacement et vérifier le vrai code.

## Contrôle de la révision avec captures

- `./scripts/hf check projects/missa-tv-360-portail` : **0 erreur**, 7 avertissements de structure, **29/29 textes conformes WCAG AA**.
- Master final : **59,000 s** (1770 images), H.264 1080 × 1920 / 30 i/s et AAC stéréo ; rendu `delivery`.
- Mix contrôlé avec `ebur128` : environ **−16,5 LUFS intégrés** et **−1,0 dBTP**.
- Les neuf prises de voix sont entièrement dans leurs scènes et ne se chevauchent pas ; seule la phrase du problème est ajustée à **1,12×**.
- **Quatorze photogrammes du MP4 final** inspectés visuellement : 0,5 / 1,8 / 4,5 / 8,8 / 18,4 / 27,5 / 30,4 / 33,0 / 35,8 / 38,5 / 39,5 / 43,0 / 50,7 / 57,5 s. L’application est visible à 0,5 s ; films → mangas vers 32 s ; catalogue musical → extrait du lecteur vers 38 s. Le logo, les prix, le badge NET et le QR fictif restent lisibles.

## Production

```bash
# Depuis la racine du dépôt, après installation des dépendances :
./scripts/hf check projects/missa-tv-360-portail
./scripts/hf render projects/missa-tv-360-portail --quality delivery \
  --output .cache/rendus/missa-tv-360-portail-silent.mp4
python3 projects/missa-tv-360-portail/sound.py
# Prises de voix à fournir dans .cache/vo59/ : s1,s2,s3a,s3b,s4a,s4b,s4c,s5,s6.mp3.
# mix.py accélère uniquement s2 de 1,12× pour conserver la respiration des 10 s.
python3 projects/missa-tv-360-portail/mix.py
# → livrables/missa-tv-360-portail.mp4 (remplace le master précédent de 59 s)
```
