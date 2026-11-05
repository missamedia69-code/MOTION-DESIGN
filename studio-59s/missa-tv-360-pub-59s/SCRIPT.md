# SCRIPT — MISSA TV 360 · « TON ÉCRAN MÉRITE MIEUX » · 59,0 s

> **ÉTAPE 1 / ✅ POINT D'ARRÊT 1 LEVÉ le 4 novembre 2026** — réponse « Validé, on passe à la voix ».
> Ce fichier reprend **mot pour mot** les textes G.2 et G.3 du cahier des charges v2.0 fourni par le
> propriétaire, et propose les 5 concepts demandés par la méthode.
>
> ⚠️ **RÉVISION 1.1 du 4 novembre 2026** (retour sur le WIP) : **3 corrections tarifaires et
> aucune autre modification du texte** — « Deux mille francs CFA par mois. » →
> **« Mille francs CFA par mois. »**, « Sept mois offerts ! » → **« Deux mois offerts ! »**,
> et à l'écran `XAF 2 000` → **`XAF 1 000`**. L'application ne pratique pas 7 mois offerts :
> l'année à 10 000 au lieu de 12 × 1 000 = 12 000 équivaut à **2 mois offerts**.
> Le reste du texte reste validé **mot pour mot** ; le point d'arrêt 1 reste levé.
>
> ⚠️ **RÉVISION 1.2 du 4 novembre 2026** — demande « améliore ce texte ». Le propriétaire réécrit
> l'accroche et deux images ; français corrigé, lignes vides normalisées (détail au §8).
> **Point d'arrêt 1 RÉOUVERT** : ce texte attend sa validation avant l'enregistrement de la voix.
> Les tarifs de la révision 1.1 (**XAF 1 000 / mois · XAF 10 000 / an · 2 mois offerts**) restent
> inchangés.
>
> ⚠️ **RÉVISION 1.3 du 4 novembre 2026** — retour du propriétaire : « on ne paye pas forcément
> chaque premier du mois » et « on est ensemble wesh est mieux pour la pub ». **Aucune date de
> prélèvement** n'est donc affirmée, et **« On est ensemble, wesh ! »** est retenu (tournure
> régionale validée par le propriétaire, locuteur natif à Douala — G.5). Détail au §9.
> Voir `DECISIONS.md` pour les 5 réponses, `SPEC-V2.md` pour les règles,
> `RAPPORT-ETAPE-0.md` pour les éléments manquants.

## 1. Cinq concepts (une ligne chacun)

1. **« Le ticket, puis la grille »** *(retenu, direction A du cahier des charges)* — un ticket d'abonnement sans fin imprime toujours la même chose ; un pivot sur noir ouvre la grille des univers MISSA, et le film se termine sur un ticket propre « ACTIVÉ ».
2. **« Le premier du mois »** — un calendrier qui se répète à l'identique douze fois, jusqu'à ce qu'une case jaune casse la boucle et déplie l'application.
   > ⚠️ **Révision 1.3** : ce concept est **écarté** — aucune date de prélèvement n'est garantie (§9).
3. **« La télécommande qui ne change rien »** — sept pressions sur OK, sept fois la même chaîne ; le huitième bouton, jaune, ouvre les milliers de contenus.
4. **« Mille francs »** — le prix d'abord, en très grand, puis retour en arrière sur la frustration : « et toi, tu paies combien pour la même chose ? ».
5. **« On est ensemble »** — un chœur de voix et de points lumineux (radios, chaînes, podcasts) qui s'allument de Douala au monde, porté par l'appel/réponse.

> Le cahier des charges **impose déjà le concept 1** (« LE TICKET, PUIS LA GRILLE », section E.1)
> et le nom de code « TON ÉCRAN MÉRITE MIEUX ». Les concepts 2 à 5 sont proposés pour satisfaire
> l'étape 1 de la méthode ; ils ne remplacent pas le choix du propriétaire.

## 2. Version « mise en scène » (G.2) — temps cibles PROVISOIRES

> Tous les temps seront **recalés sur `onsets.json`** après réception de `voix.mp3` (une animation
> tombe sur un mot, jamais après). ≈163 mots pour 59 s (révision 1.3), gag muet et pivot muet inclus.

| Temps | Séquence | Voix |
|---|---|---|
| `[0.0-4.5]` | **F01 Accroche** | « Tu paies. Chaque mois, des abonnements coûteux pour ne rien avoir. Et chaque soir... la même chose. Des contenus creux. » |
| `[4.5-7.0]` | **F02 GAG MUET** | *(aucune voix, 2,5 s)* |
| `[7.0-11.0]` | **F03 Douleurs 1 et 2** | « Les mêmes chaînes. Les mêmes séries, déjà vues. » |
| `[11.0-15.0]` | **F04 Douleur 3** | « Les mêmes pubs. Tu ne fais qu'empiler l'argent sur l'argent. » |
| `[15.0-16.0]` | **F05 Pivot** puis **NOIR 16.0 → 16.8** (silence, impact grave à 16.0) | **CHŒUR** : « On mérite mieux ! » |
| `[16.8-22.0]` | **F06 Révélation** | « Voici Missa TV trois cent soixante. Tout ton divertissement, dans une seule application. » |
| `[22.0-28.0]` | **F07 Films, séries, documentaires, mangas** | « Des milliers de films. Des séries à n'en plus finir. Des documentaires, des mangas… » |
| `[28.0-34.0]` | **F08 Télévision en direct** | « Des centaines de chaînes de télévision en direct. Le sport, l'info, les enfants… tout y est. » |
| `[34.0-40.0]` | **F09 Podcasts, radios, musique** | « Des podcasts. Des milliers de radios d'Afrique et du monde. Et ta musique, partout avec toi. » |
| `[40.0-44.0]` | **F10 Appareils** | « Téléphone, tablette ou télé. Une seule application. Zéro prise de tête. » |
| `[44.0-48.5]` | **F11 Prix mensuel** | « Et le prix ? Mille francs CFA par mois. Oui, tu as bien entendu. » |
| `[48.5-54.5]` | **F12 Prix annuel** | « Ou dix mille francs CFA pour toute l'année. Deux mois offerts ! Moins de trente francs par jour. » |
| `[54.5-59.0]` | **F13 Appel à l'action** | « Missa TV trois cent soixante. Télécharge, et regarde enfin ce que tu mérites ! » puis **CHŒUR** : « On est ensemble ! » |

**Structure en 6 temps** : accroche concrète et datée (F01) → gag muet 2,5 s (F02) → diagnostic 3 douleurs (F03-F04) → pivot sur noir (F05) → solution et bénéfices (F06-F10) → marque et CTA (F11-F13).
**Premier mot** = la douleur de la cible (« Tu paies »). **Première image** = le ticket qui sort de la fente, **jamais le logo**.

## 3. Texte À COLLER dans ElevenLabs (G.3) — aucune mise en scène

> Pas de balise de pause : la ponctuation, les `...` et les retours à la ligne font les pauses.
> Peu de balises de jeu. **Chiffres EN TOUTES LETTRES.** Langue réglée **MANUELLEMENT sur Français**.
> Une ligne vide marque le gag muet et le pivot ; le montage allonge ensuite ces silences en
> coupant **seulement dans les silences**.

```
Tu paies.
Chaque mois, des abonnements coûteux pour ne rien avoir.

Et chaque soir... la même chose. Des contenus creux.

Les mêmes chaînes.
Les mêmes séries, déjà vues.
Les mêmes pubs.
Tu ne fais qu'empiler l'argent sur l'argent.

On mérite mieux !

Voici Missa TV trois cent soixante.
Tout ton divertissement, dans une seule application.
Des milliers de films.
Des séries à n'en plus finir.
Des documentaires, des mangas...
Des centaines de chaînes de télévision en direct.
Le sport, l'info, les enfants... tout y est.
Des podcasts.
Des milliers de radios d'Afrique et du monde.
Et ta musique, partout avec toi.
Téléphone, tablette ou télé.
Une seule application.
Zéro prise de tête.
Et le prix ?
Mille francs CFA par mois.
Oui, tu as bien entendu.
Ou dix mille francs CFA pour toute l'année.
Deux mois offerts !
Moins de trente francs par jour.
Missa TV trois cent soixante.
Télécharge, et regarde enfin ce que tu mérites !

On est ensemble, wesh !
```

## 4. Réglages et direction de la voix (G.4 / G.5)

| Réglage | Valeur |
|---|---|
| Modèle | Eleven v4 |
| Langue | **Français, réglée à la main** |
| Stabilité | 40 à 50 % |
| Similarité | 80 à 90 % |
| Prises | 2 ou 3, déposer la meilleure dans `assets/audio/voix.mp3` |
| Commercial | **forfait ElevenLabs PAYANT obligatoire** |
| Alternative | comédien local enregistré, même fichier `voix.mp3`, même pipeline |

- **Narrateur** : homme 35-45 ans, chaud, posé puis énergique ; **accent français d'Afrique centrale ou de l'Ouest, NATUREL** (pas caricatural), sourire audible. 0:00 → 0:16 ironique et un peu las ; à partir de 0:17 énergie et fierté.
- **Chœur (option)** : « On mérite mieux ! » et « On est ensemble ! » par 3 voix différentes superposées (homme, femme, jeune). Version minimale : narrateur seul, plus d'intensité.
- **Expressions locales** : avec modération (« on est ensemble ») ; toute tournure régionale (camfranglais, nouchi, pidgin) **validée par un locuteur natif** avant enregistrement (le propriétaire, basé à Douala, peut le faire).
- **Prononciation** : MISSA = « mi-sa » (si le moteur bute, écrire « Mi-sa » dans le texte à coller ; **le sous-titre affiche toujours MISSA**) ; TV = « télé » ou « té-vé » de façon **constante** ; 360 = « trois cent soixante ».
- **L'agent ne demande JAMAIS de clé ElevenLabs** et n'en stocke aucune.

## 5. Sous-titre (règle de transcription)

Le sous-titre reprend **la phrase de la voix EN TOUTES LETTRES**, mot par mot, y compris
« mille francs CFA » et « dix mille francs CFA ». Le prix chiffré `XAF 1 000` / `XAF 10 000`
n'apparaît **que dans les cartes de prix** (F11, F12). Bande y 1280 → 1400, marges 80 px,
60-64 px, **38 caractères maximum par morceau**, une phrase longue se découpe en morceaux qui se
remplacent. **Aucun sous-titre** pendant F02 (gag muet) et les 3 moments typographiques F05, F10, F13.

## 6. Point d'arrêt 1 — relevé le 4 novembre 2026

- [x] Validation **mot à mot** des deux textes ci-dessus : **« Validé, on passe à la voix »**.
      Révision 1.1 : seules les 3 expressions tarifaires ont été corrigées. **Révision 1.2 :
      le texte a été remanié par le propriétaire → validation mot pour mot À RENOUVELER.**
- [x] Forme de marque : **« MISSA TV 360 »** (sans « + » ni « PLUS »).
- [x] Écriture monétaire : **`XAF 1 000` / `XAF 10 000`** (défaut du CDC, variante `FCFA` non retenue).
- [x] Logo officiel : le propriétaire a indiqué « le logo est dans asset » → `assets/img/logo-officiel.png`.
- [x] Chœur : **version minimale retenue** — une seule voix, y compris « On mérite mieux ! » et
      « On est ensemble ! » (le propriétaire synthétise en local, une seule prise).
- [ ] Éléments restants de la section C : voir `DECISIONS.md` et `RAPPORT-ETAPE-0.md`.

**Étape suivante : voix (point d'arrêt 2).** Une VO de travail temporaire est autorisée pour caler
`onsets.json` ; `assets/audio/voix.mp3` reste attendu et sera substituée avant tout rendu final.


## 7. Étape 2 — texte remis pour synthèse locale (04/11)

Le propriétaire a indiqué : « donne moi le texte à utiliser, je te donne la voix, j'ai un logiciel en
local qui permet de la synthétiser ». **`[VOIX]` passe donc de "attendu" à "en cours de production"**,
sans aucune clé API, sans envoi, sans service cloud : la voix est produite sur sa machine.

| Livrable | Contenu |
|---|---|
| `VOIX-A-SYNTHETISER.txt` | **le texte à coller**, pur, mot pour mot = G.3 ci-dessus (**révisions 1.1 + 1.2 + 1.3**). ≈163 mots. |
| `VOIX-CONSIGNES.md` | langue/français, direction de voix, prononciation (MISSA, TV, 360, CFA), format du fichier `assets/audio/voix.mp3`, une seule ligne à trancher (« offerts » / « gratuits »), format JSON des timings mot à mot. |

Deux points restent ouverts au moment de la synthèse :
1. **« Deux mois offerts ! » ou « Deux mois gratuits ! »** — une seule ligne ; le sous-titre et F12
   seront alignés sur le choix réellement enregistré.
2. **Timings mot à mot** — si le logiciel local exporte `{"words":[{"w","s","e"}]}`, `onsets.py
   --transcript` donne le vrai `onsets.json` sans Whisper (modèle non téléchargeable ici). Sinon le
   minutage reste provisoire sur `onsets.py --no-whisper`.

**Point d'arrêt 2 toujours ouvert** jusqu'à réception de `voix.mp3` : la VO de travail
`assets/audio/voix-temporaire.mp3` reste en place dans le WIP v2, le placeholder `[VOIX]` reste
visible à l'écran.


## 8. Révision 1.2 — amélioration du texte VO (04/11)

Le propriétaire a proposé une nouvelle accroche et deux images, et demandé « améliore ce texte ».
**Ses idées sont conservées** ; seuls le français, la ponctuation et le rythme de synthèse sont
corrigés.

| Ta version | Version améliorée | Pourquoi |
|---|---|---|
| « Tu paies, chaque mois des abonnements **couteux** pour ne rien avoir. » | « **Tu paies. Chaque mois,** des abonnements **coûteux** pour ne rien avoir. » | deux phrases au lieu d'une virgule qui relie deux propositions ; accent sur *coûteux*. ⚠️ **1.3** : « chaque premier du mois » **retiré** (aucune date de prélèvement garantie, exactitude L.2). L'accroche reste concrète sans être datée. Le premier mot reste **« Tu »**. |
| « Et chaque soir... la même chose, des **contenues** vides, » | « Et chaque soir... la même chose. **Des contenus creux.** » | *contenus* est masculin (pas *contenues*) ; « contenus vides » est un pléonasme, *creux* est plus juste ; virgule finale → point. |
| « Tu ne fais que **mettre l'argent sur de l'argent**. » | « Tu ne fais qu'**empiler l'argent sur l'argent**. » | *empiler* rend l'image lisible à l'oral et évite la répétition « de l'argent / de l'argent ». |
| « On est ensemble **whech** ! » | « **On est ensemble, wesh !** » | ⚠️ **1.3** : le propriétaire a tranché « wesh est mieux pour la pub ». Tournure régionale **validée** par un locuteur natif (Douala) au sens de G.5 ; virgule pour la pause à l'oral. |
| une ligne vide entre **chaque** phrase | lignes vides **uniquement** pour le gag muet, le pivot et le chœur final | un TTS marque une pause longue à chaque ligne vide : avec 20+ lignes vides, le texte dépasse largement 59,0 s. Les simples retours à la ligne restent des pauses courtes. |

**Deux points restant à trancher avant d'enregistrer (après la révision 1.3) :**
1. **« Deux mois offerts ! »** ou **« Deux mois gratuits ! »** (déjà signalé en 1.1) ;
2. **« pour ne rien avoir »** : formulation très absolue, gardée telle quelle. Variante moins
   attaquable si souhaitée : « pour rien de neuf ». Aucun opérateur ni marque n'est nommé (L.1 OK).
   Le point « whech / wesh » est **tranché** en 1.3.

**Conséquence sur le minutage** : l'accroche gagne environ 8 mots (≈22 mots en F01 contre 12 en
1.1). Au débit actuel, F01 passerait de 4,0 s à ~5,5-6,0 s. Ce n'est pas un problème : les
13 séquences seront **recalées sur `voix.mp3`** à réception de la voix, en gardant le gag muet
(2-3 s), le pivot sur noir et la durée totale **59,0 s**. Si tu veux absolument garder F01 à 4 s,
une accroche resserrée est proposée dans `VOIX-CONSIGNES.md`.

⚠️ **État de cohérence** : `VOIX-A-SYNTHETISER.txt`, G.2, G.3 et ce §8 sont en **1.2**.
`onsets.json`, `sous-titres.srt`, `index.html`, la VO de travail et le **WIP v2 déjà rendu**
portent encore la VO 1.1 : ils seront régénérés en une seule passe avec `voix.mp3`, conformément
au point d'arrêt 2. **Aucun nouveau rendu n'est lancé avant ta validation.**


## 9. Révision 1.3 — exactitude et ancrage local (04/11)

Retour du propriétaire : **« on ne paye pas forcément chaque premier du mois, on est ensemble wesh
est mieux pour la pub »**. Deux corrections, toutes deux appliquées à `VOIX-A-SYNTHETISER.txt`,
G.2 et G.3 :

| Retour | Décision | Portée |
|---|---|---|
| « on ne paye pas forcément chaque premier du mois » | **« Chaque premier du mois » → « Chaque mois »**. Aucune date de prélèvement n'est affirmée. | L'exigence « accroche **datée** » de la section A est **délibérément écartée** au profit de l'**exactitude** (L.2). L'accroche reste **concrète** (« Tu paies », « des abonnements coûteux ») et le premier mot reste « Tu ». Le concept 2 « Le premier du mois » est écarté (§1). |
| « on est ensemble wesh est mieux pour la pub » | **« On est ensemble, wesh ! »** | Tournure régionale **validée par le propriétaire**, locuteur natif à Douala → **G.5 satisfait**. La virgule marque la pause pour le TTS ; le sous-titre mot à mot reprendra « wesh ». À l'oral « wèch », sans épeler les lettres. |

**Cohérence image / son** : le ticket de F01 affichait `1er DU MOIS` dans `render/wip_build.py`
et `index.html`. Il devient **`ABONNEMENTS`** (aucune date) — le faux rendez-vous de facturation
disparaît aussi de l'image. Le tampon `RENOUVELÉ`, lui, reste (pas de date).

**État de cohérence** : `onsets.json`, `sous-titres.srt`, `TIMING-PROVISOIRE.md` et la VO de
travail portent encore la VO **1.1** (« premier du mois », sans « wesh »), et le **WIP v2 déjà
rendu** affiche l'ancien libellé du ticket. Ils seront tous régénérés en une seule passe à
réception de `voix.mp3`. **Aucun rendu lancé maintenant** : attendre la validation du dernier
point « offerts / gratuits » et le fichier audio.
