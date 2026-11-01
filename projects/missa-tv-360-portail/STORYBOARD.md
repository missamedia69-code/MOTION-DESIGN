# MISSA TV 360 — « Ton monde s’ouvre » (59 secondes)

Mise à jour de la vidéo `livrables/missa-tv-360-portail.mp4` : **59 s exactement**, portrait 1080 × 1920 à 30 i/s. Le film n'est pas simplement ralenti : les six chapitres, la voix, les animations, la musique et les effets sont recalés. Le texte tutoie le public du début à la fin, avec un français oral naturel et quelques tournures familières (« ça suffit, hein », « pose-toi », « on est ensemble ») sans caricature.

| Temps | Chapitre | Texte et action à l'écran | Voix (verbatim) |
| --- | --- | --- | --- |
| 00–06 | Hook | Logo officiel sur le portail ; « TON MONDE S’OUVRE. » et « LE DIVERTISSEMENT À TON RYTHME. » | « Missa TV trois cent soixante... ton monde s'ouvre ! » |
| 06–16 | Problème | Trois abonnements/factures s'accumulent. « ENCORE UN ABONNEMENT ? » → « ÇA SUFFIT. » | « Tu paies encore un abonnement, puis un autre... et au final, tu regardes toujours la même chose. Chaque fin de mois, ça pèse sur le portefeuille. Franchement, ça suffit, hein ! » |
| 16–29 | Solution | « LE MONDE EN FACE DE TOI. » ; 2 000 XAF/mois ou 10 000 XAF/an ; box NET, **Wi-Fi + Internet**, puis Android TV, tablette et téléphone. | « Deux mille francs le mois, dix mille francs l'année : c'est toi qui choisis. » / « Avec ta box Wi-Fi et Internet, tu regardes sur ta télé, ta tablette ou ton téléphone. » |
| 29–46 | Univers | 29–34,9 : films/séries/manga ; 34,9–40,1 : musique/shorts-dramas ; 40,1–46 : jeux vidéo/podcasts/radio. La box NET reste en zoom Ken Burns. | « Films, séries, mangas... pose-toi et choisis ton histoire ! » / « Musique, shorts-dramas : suis ton envie du moment. » / « Jeux vidéo, podcasts, radio... chacun trouve son truc ! » |
| 46–53 | Stabilité | « PETIT DÉBIT ? ÇA CONTINUE. » ; signal irrégulier → ligne fluide → « FLUX STABLE. » | « Même avec un petit débit, le flux reste stable. Tu continues tranquille, hein ! » |
| 53–59 | CTA | Logo ; « TON MONDE T’ATTEND. » ; « TÉLÉCHARGE MAINTENANT » ; placeholder QR non scannable ; rappel des deux prix. | « Ton monde t'attend. Télécharge maintenant, on est ensemble ! » |

## Cohérence et vérifications éditoriales

- **Un seul point de vue** : le tutoiement (« toi / ta box / tes écrans / télécharge »), sans alterner « vous » et « tu ».
- **Le bon prérequis** : la vidéo dit désormais **box Wi-Fi et connexion Internet** ; elle ne laisse pas entendre qu'une box seule donne accès au catalogue.
- **Tarifs** : exactement 2 000 XAF/mois ou 10 000 XAF/an, selon le nouveau brief. Aucun ancien tarif de la v9.
- La box porte **NET**, jamais MTN, conformément à la demande antérieure.
- Faute de preuves transmises, la vidéo n'affirme ni « garanti », ni « testé en zone rurale », ni la lecture vidéo en 2G. La promesse de stabilité en faible débit, fournie par le brief, reste à confirmer avant diffusion commerciale.
- Aucun lien de téléchargement officiel n'a été fourni. La case en fin de film est explicitement « EMPLACEMENT QR » et **n'est pas scannable**.
- Les quatre univers photo ont été générés pour cette production ; le logo et la photographie de la box proviennent du dépôt. Voix française sélectionnée précédemment pour la v9, afro-électro et SFX synthétiques originaux dans `sound.py`.

## Contrôle du master 59 s

- `hf check` : passe (0 erreur, contraste **25/25** WCAG AA ; 7 avertissements de structure recommandant des sous-compositions, sans impact sur le rendu).
- Master livré : **59,000 s**, H.264 1080 × 1920 / 30 i/s et AAC stéréo 44,1 kHz ; rendu `delivery`.
- Niveau audio : environ **−16,7 LUFS intégrés** et **−1,4 dBTP** (`ebur128`).
- Les neuf prises de voix sont entièrement dans leurs scènes et ne se chevauchent pas ; seule la phrase du problème est ajustée à **1,12×**.
- Dix photogrammes ont été extraits du **MP4 final** (2,4 / 8,9 / 14,9 / 20,5 / 27,6 / 31,9 / 37,5 / 43,5 / 50,8 / 57,6 s) et vérifiés visuellement.

## Production

```bash
# Depuis la racine du dépôt, après installation des dépendances :
./scripts/hf check projects/missa-tv-360-portail
./scripts/hf render projects/missa-tv-360-portail --quality delivery \
  --output .cache/rendus/missa-tv-360-portail-silent.mp4
python3 projects/missa-tv-360-portail/sound.py
# Neuf prises de voix .cache/vo59/s1,s2,s3a,s3b,s4a,s4b,s4c,s5,s6.mp3.
# mix.py accélère uniquement s2 de 1,12× pour conserver la respiration des 10 s.
python3 projects/missa-tv-360-portail/mix.py
# → livrables/missa-tv-360-portail.mp4 (remplace le master 37 s)
```
