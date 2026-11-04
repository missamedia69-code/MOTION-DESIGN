# CAHIER DES CHARGES v2.0 — « TON ÉCRAN MÉRITE MIEUX »

> Source : document intégral fourni par le propriétaire le **4 novembre 2026** (sections A → N + annexe CSV).
> Ce fichier en est la **fiche de référence opérationnelle** : il consigne toutes les valeurs et règles
> contraignantes. En cas de doute, le texte intégral fourni par l'utilisateur fait foi.
> **STATUT : REMPLACE la version précédente (spot 50 s construit avec des images générées par IA).**
>
> ⚠️ **RÉVISION 1.1 — 4 novembre 2026 (retour du propriétaire sur le WIP)** : l'application facture **XAF 1 000 / mois** et **XAF 10 000 / an** ; 12 × 1 000 = **12 000**, l'écart de 2 000 XAF = **2 MOIS OFFERTS** (et non 7). À l'oral/sous-titre : « mille francs CFA » / « dix mille francs CFA ». « Moins de trente francs par jour » reste exact (10 000 / 365 = 27,4). Toute mention antérieure de 2 000 / 24 000 / 14 000 / 7 mois est **caduque**.

## 0. Identité

| | |
|---|---|
| Nom de code | TON ÉCRAN MÉRITE MIEUX |
| Nature | **FILM DE MOTION DESIGN** : typographie animée, interfaces réelles de l'app, formes vectorielles, objets-ponts, caméra jamais à l'arrêt |
| Interdit | **Aucune photo, aucune image générée par IA, aucun personnage photoréaliste** |
| Seul élément humain | la voix off (ton africain), **produite par l'utilisateur** |
| Format maître | **9:16 · 1080×1920 · 30 i/s · 59,0 s EXACTES** |
| Méthode | dépôt `cblain100-prog/motion-design-claude-code` (skill `motion-design`, **HyperFrames 0.8.82 figé**, `patterns/STORYBOARD-CRAFT.md`, `patterns/PATTERNS.md`), 5 étapes + vérification |

## A. Objectif, cible, ton

- **Objectif** : faire installer MISSA TV 360 et convaincre de s'abonner. **Captiver dès les 3 premières secondes**. Comprendre en < 60 s : (1) on paie déjà pour un contenu pauvre et répétitif, (2) MISSA TV 360 donne bien plus dans une seule application, (3) prix très bas : **XAF 1 000 / mois · XAF 10 000 / an**.
- **Cible** : foyers urbains/périurbains d'Afrique francophone (zone XAF), 18-45 ans, télé/vidéos/radio/musique sur téléphone, tablette, Android TV. **Lisible SANS LE SON** (sous-titre mot à mot en permanence).
- **Twist** : « en Afrique on paie chaque mois pour… toujours la même chose ». **SANS JAMAIS nommer, montrer ou évoquer un opérateur ou une marque** : décodeur, chaînes, logos génériques. Pivot sur noir « On mérite mieux ! ».
- **Ton** : chaleureux, rythmé, complice, fier ; humour léger (gag muet de la télécommande) ; appel/réponse narrateur ↔ petit chœur (« On mérite mieux ! », « On est ensemble ! »). **Aucun cliché de pauvreté ou d'exotisme** : moderne, premium, aspirationnel.
- **Promesse** : « MISSA TV 360 : ton écran mérite mieux. »

## B. Chiffres et faits (calculs vérifiés, à utiliser tels quels)

| Donnée | Valeur |
|---|---|
| Mensuel | **1 000 XAF** |
| Annuel | **10 000 XAF** |
| 12 mois × 1 000 | **12 000 XAF** |
| Économie annuelle | **2 000 XAF = 2 MOIS OFFERTS** (l'année coûte le prix de 10 mois) |
| 10 000 / 365 | **27,4 XAF/jour → « moins de trente francs par jour »** |
| 10 000 / 12 | ~833 XAF/mois (désormais exact) → **toujours ne pas le dire dans le spot** |

- **Format monétaire OBLIGATOIRE À L'ÉCRAN** : préfixe `XAF` + espace fine pour les milliers → `XAF 1 000 / mois`, `XAF 10 000 / an`.
- **À l'oral ET dans le sous-titre** : « mille francs CFA », « dix mille francs CFA ». Variante `FCFA 1 000` à valider par le propriétaire ; **ne jamais mélanger les deux écritures dans une même vidéo**.
- **Contenu annoncé (formulations du propriétaire, à ne pas gonfler)** : des **MILLIERS** de films, séries, documentaires, mangas ; des **CENTAINES** de chaînes de télévision en direct ; des podcasts ; des **MILLIERS** de chaînes de radio.
- **Univers réels de l'app** (interfaces à l'écran) : Films & Mangas, Séries, Documentaires, Courts-métrages, Enfants, TV Direct, Sports, Musiques, Podcasts, Radio, Jeux rétro. Disponible sur téléphone, tablette, Android TV.
- **À l'écran, les quantités en MOTS** (« MILLIERS », « CENTAINES »), jamais de chiffre précis non vérifié.

## C. Éléments à fournir par le propriétaire — NE RIEN INVENTER

> **Tant qu'un élément manque, l'agent affiche un PLACEHOLDER visible et le signale dans son rapport final.**

| Élément | État |
|---|---|
| `[LOGO_OFFICIEL]` | ✅ **RÉSOLU le 04/11 par le propriétaire** (« le logo est dans asset ») : `assets/images/logo-missa.png` → copié en `assets/img/logo-officiel.png` (1254×1254 RGB, fond jaune **opaque**, md5 `d25e681177516b4218cc91f6cc1f4e73`). Forme retenue : **« MISSA TV 360 »** (pastille verte « 360 », sans « + »). ⚠️ C'est l'identité bleu/vert sur jaune ; le CDC évoque par ailleurs l'identité d'app « mot jaune + 360+ ». **Utilisé tel quel, sans mélange ni reconstruction.** Une version transparente reste à fournir si besoin. |
| `[HEX_JAUNE]` | ✅ **RÉSOLU SANS INVENTER** : `#F5BB00`, `missaYellowPrimary`, `app/src/main/res/values/colors.xml:127` du dépôt public `missamedia69-code/MISSA_TV_360_PLUS` (`1da53ac`). |
| `[CAPTURES_APP]` | À fournir : captures **récentes** téléphone portrait **ET** Android TV, dans `assets/img/ui/`, **après** correction T01 (bouton « Plus d'infos » sans libellé), T02 (chevauchement Accueil/360+), T03 (badge « EN DIRECT » sur univers vide). Ne pas filmer ces défauts. |
| `[LIEN_TELECHARGEMENT]` + `[QR_CODE]` | À fournir : lien officiel court + QR généré depuis ce lien. |
| `[MODES_DE_PAIEMENT]` | À confirmer. |
| `[CONDITIONS_OFFRE]` | À confirmer (conditions, durée, renouvellement ; mention en petit à l'écran final). |
| `[VOIX]` | À fournir : `assets/audio/voix.mp3` (ElevenLabs **par l'utilisateur**, ou comédien local). **Aucune clé API demandée ni stockée.** |
| `[MUSIQUES_CC0]` | À fournir : **2 morceaux CC0 choisis par l'utilisateur** (tension 0→16,0 ; élan 16,0→59). |

## D. Cadre technique

### D.1 Règles non négociables (AGENTS.md du dépôt de référence)
- **CLI local figé uniquement** : `npx hyperframes ...` depuis le dépôt. Jamais `@latest`, jamais d'installation globale.
- **Ne JAMAIS lancer** : `feedback`, `publish`, `cloud`, `lambda`, `cloudrun`, `auth`, `upgrade`, `skills update`, `npx skills add`, sauf demande explicite.
- **`.env` VIDE** à la racine ; n'y écrire aucune clé. Aucune clé d'API.
- **media-use** : toujours `--local-only`, jamais de musique générée (`--no-bgm`) ; musique = CC0 fournie ; SFX = `.claude/skills/media-use/audio/assets/sfx/`.
- **Rien ne quitte la machine** : pas d'envoi, pas de publication, **pas de push**.
- Projet à la racine du dépôt : `bash .claude/skills/motion-design/scripts/new-project.sh missa-tv-360-pub-59s --fonts` (Instrument Sans, Space Mono, Big Shoulders, SIL OFL).
- **Points d'arrêt** (validations utilisateur) : après le script, la voix, le choix de la direction, le storyboard, la première séquence, le choix de la musique.

### D.2 Les 8 adaptations 9:16 — appliquées dans ce projet
1. `meta.json` : `width 1080`, `height 1920`, `fps 30`. ✅
2. Racine de chaque composition : `data-width="1080" data-height="1920" data-duration="59"`. **Ne pas coder 1920×1080 en dur dans `#root`**. ✅ (à contrôler sur chaque séquence)
3. `frame.md` : `unit: 1080×1920` ; bande de sous-titre recalculée (D.3). ✅
4. `STORYBOARD.md` : `format: 1080x1920`, `duration: "59.0s"`. ✅
5. Styleframes : `python3 .claude/skills/motion-design/scripts/render-styleframes.py <projet> --width 1080 --height 1920`.
6. `assemble.sh` : **QUE la coupe** — `LEAK_AT=""`, `IRIS_AT=""`, `PAPER=""` ; SVG d'iris éventuel repassé en `1080×1920`. Sortie finale au noir. ✅
7. Rendu : `npx hyperframes render --output renders/missa-tv-360-pub-59s_9x16.mp4` (`--quality looks` pour validation, `delivery` pour livraison). ⚠️ `--resolution portrait` **n'existe pas en 0.8.82** : le ratio vient de la composition.
8. **À VÉRIFIER sur le VRAI rendu** : planche contact toutes les 0,5 s (M). ⚠️ `npx hyperframes validate --caption-zone` **n'existe pas en 0.8.82** : remplacé par `npx hyperframes check` + contrôle manuel des fractions.

### D.3 Zones de sécurité 9:16
- Libres : **~200 px en haut, ~440 px en bas, ~120 px à droite**.
- **Sous-titre** : bande centrée **y 1280 → 1400**, marges latérales **80 px**, **60 à 64 px**, **38 caractères max par morceau** (une phrase longue se découpe en morceaux qui se remplacent), **mot par mot sur ses temps**.
- Fractions de contrôle : `x0 0.07 · x1 0.93 · y0 0.667 · y1 0.73`.
- Le sous-titre reprend la phrase de la voix **EN TOUTES LETTRES** (y compris « mille francs CFA »). Le prix chiffré `XAF 1 000` n'apparaît **que dans les cartes de prix**.

### D.4 Livrables
1. `missa-tv-360-pub-59s_9x16.mp4` — 1080×1920, 30 i/s, **59,0 s**.
2. `missa-tv-360-pub-59s_16x9.mp4` — recomposition dédiée, **après validation du 9:16** (K).
3. `sous-titres.srt` français (copie des mots minutés) + **pistes séparées** (voix, musique, bruitages) en **WAV 48 kHz**.
4. Dossier projet complet : `SCRIPT.md`, `DIRECTIONS.md`, `frame.md`, `STORYBOARD.md`, `onsets.json`, séquences HTML, scripts de mix.

## E. Directions (étape 3 : 3 directions × 3 styleframes PNG 1080×1920, choix sur image)
- **A (recommandée) « LE TICKET, PUIS LA GRILLE »** : ticket de caisse très long, caméra qui descend ; douleur sur papier gris désaturé ; PIVOT SUR NOIR ; monde MISSA noir + jaune + interfaces ; fin qui rime avec un ticket propre « ACTIVÉ ».
- **B « LA TÉLÉCOMMANDE GÉANTE »** : plus ludique, risque = moins de preuve produit.
- **C « LA CARTE D'AFRIQUE QUI S'ALLUME »** : poétique, points seulement, **aucune frontière dessinée**.

**Deux mondes (A)** — Monde 1 : papier `#E9E4D6` sur ardoise `#1B1E22`, encre noire Space Mono, tampon rouge brique `#B5473A`, grain fin, **aucun jaune**. Monde 2 : noir `#0B0B0C`, jaune `#F5BB00`, vert 360/offert `#009E49`, vert actif `#2FD37A`, rouge LIVE `#E53935` uniquement, motifs wax **originaux** en filigrane 5-8 %.

**Objets-ponts** (F01→F02 tampon→bouton OK ; … ; F12→F13 case « OFFERT »→bouton « Télécharger ») : un objet change de rôle à chaque couture.

**Règles communes** : un seul mot clé par phrase en petite BOÎTE d'accent + 3-4 pics soulignés ; jamais de mot géant ; une seule chose à regarder ; zoom franc dans UN seul sens ; **événement toutes les 0,5-1 s** (0,1-0,3 s dans les 3 premières secondes) ; caméra jamais à l'arrêt > 0,5 s ; 3 niveaux de profondeur ; **0 à 4 coupes franches, 0 à 2 fondus** ; apparitions trop grandes (×1,1 à ×6) et floues (6-12 px) qui se posent en ≤ 0,2 s ; n'animer QUE `translate/scale/rotate/opacity` (jamais `top/left/width/height`, jamais le letter-spacing, pas de `backdrop-filter`) ; tout élément part à `opacity 0`. **Négatifs** : diaporama, écran de veille, objet dédoublé, logo en première image, photo/image IA.

## F. Charte (frame.md)
- Couleurs par **rôle**, un seul accent (jaune), tout le reste en neutres. Valeurs : `canvas #0B0B0C`, `canvas-2 #141416`, `paper #E9E4D6`, `ardoise #1B1E22`, `ink #F4F1EA`, `ink-dark #1A1815`, `accent #F5BB00`, `négatif #B5473A`, `vert 360 #009E49`, `vert actif #2FD37A`, `live #E53935`.
- Typo : titres/prix **Big Shoulders 800** ; texte/sous-titre **Instrument Sans 600 (60-64 px)** ; ticket/chiffres **Space Mono 400/700** ; `numeral-jumbo` Big Shoulders **≤ 300 px**.
- **2 ou 3 moments typographiques max**, 84 px, centrés, **sans sous-titre pendant ce temps** : « ON MÉRITE MIEUX. » (F05), « UNE SEULE APPLICATION. » (F10), « TON ÉCRAN MÉRITE MIEUX. » (F13).
- Interfaces reconstruites **d'après `[CAPTURES_APP]`** (fond noir, pilules arrondies, sélection jaune, focus vert, barre des 12 univers, hero + bouton jaune « Regarder », rangées de vignettes, mini-lecteur radio persistant, badge LIVE). **Titres, vignettes, stations, chaînes FICTIFS ET ORIGINAUX** : aucune affiche réelle, aucun logo de chaîne/radio/club/film, aucun personnage protégé.
- Géométrie : Monde 1 = ticket 640 u de large, **≥ 4 000 u de long**, centré, 3 stations. Monde 2 = grille verticale, **source unique `reference/grille.html`** recopiée à l'identique par chaque séquence.

## G. Script et voix
- 6 temps : accroche concrète/datée → gag muet 2-3 s → diagnostic 3 douleurs → pivot sur noir → solution/bénéfices → marque/CTA. **Premier mot = cible ou douleur (« Tu »)**, première image = le ticket, **jamais le logo**.
- Voir `SCRIPT.md` pour les deux versions intégrales (mise en scène + à coller dans ElevenLabs).
- Voix : Eleven v4, langue **Français réglée à la main**, Stabilité 40-50 %, Similarité 80-90 %, 2-3 prises, **forfait payant obligatoire pour usage commercial**. Aucune balise de pause ; chiffres EN TOUTES LETTRES ; ponctuation/`...`/retours à la ligne font les pauses. Narrateur homme 35-45 ans, chaud, posé puis énergique, **accent français d'Afrique centrale ou de l'Ouest NATUREL**, 0:00-0:16 ironique et las, ≥ 0:17 énergie/fierté. Chœur optionnel 3 voix (homme, femme, jeune). Expressions locales avec modération, **toute tournure régionale validée par un locuteur natif**. Prononciation : MISSA = « mi-sa » (écrire « Mi-sa » si le moteur bute, le sous-titre affiche toujours MISSA) ; TV = « télé » ou « té-vé » de façon constante ; 360 = « trois cent soixante ».

## H. Storyboard — 13 séquences, somme = 59,0 s

| Id | Début | Fin | Durée | Type | Monde | Idée VO |
|---|---|---|---|---|---|---|
| F01 | 0.0 | 4.5 | 4.5 | hook | papier | Tu paies… |
| F02 | 4.5 | 7.0 | 2.5 | hook (gag muet) | papier | (silence) |
| F03 | 7.0 | 11.0 | 4.0 | pain_point | papier | mêmes chaînes, mêmes séries |
| F04 | 11.0 | 15.0 | 4.0 | pain_point | papier | mêmes pubs, l'argent s'en va |
| F05 | 15.0 | 16.8 | 1.8 | pivot | noir | On mérite mieux ! |
| F06 | 16.8 | 22.0 | 5.2 | payoff | noir-MISSA | Voici MISSA TV 360 |
| F07 | 22.0 | 28.0 | 6.0 | demo | noir-MISSA | films, séries, docs, mangas |
| F08 | 28.0 | 34.0 | 6.0 | demo | noir-MISSA | chaînes en direct |
| F09 | 34.0 | 40.0 | 6.0 | demo | noir-MISSA | podcasts, radios, musique |
| F10 | 40.0 | 44.0 | 4.0 | reassurance | noir-MISSA | téléphone, tablette, télé |
| F11 | 44.0 | 48.5 | 4.5 | offer | noir-MISSA | XAF 1 000 / mois |
| F12 | 48.5 | 54.5 | 6.0 | offer | noir-MISSA | XAF 10 000 / an |
| F13 | 54.5 | 59.0 | 4.5 | cta | noir-MISSA | Télécharger |

**Coupes franches voulues (quota 0-4)** : (1) F05 → noir à 16.0, (2) noir → logo à 16.8 (séquence visible dès sa 1re image), (3) F10 → F11 si le raccord d'objet ne tient pas. **Fondus ≤ 2** (fin au noir de F13). Tout le reste par objet-pont/caméra.
**Tous les temps sont PROVISOIRES** : recalés sur `onsets.json` après la voix (une animation tombe sur un mot, jamais après). Format exact `templates/STORYBOARD-TEMPLATE.md` : `handoff_in`/`handoff_out` numériques avec `cam()`/`dof()`, Word cues, grille 15 points.

## I. Musique, bruitages, mix
- **2 morceaux CC0 fournis par l'utilisateur** (jamais de musique générée). Tension 0:00→0:16,0 minimale/pulsée/sourde, 2-3 dB sous l'élan au plus, **coupée net par l'impact grave de 16.0**. Élan 0:16,0→0:59 rythmé/chaud/percussif (afro/latino si CC0 adapté), **ducking 10-12 dB sous la voix**, remonte entre les phrases. Prendre une partie **PLEINE** du morceau (pas l'intro). Proposer **3-4 options** sur la même voix (`build-music-options.py`), l'utilisateur choisit (**point d'arrêt 6**).
- SFX : `assets/audio/sfx-events.json`, banque `.claude/skills/media-use/audio/assets/sfx/` (Pixabay Content License), calés sur les **GESTES** pas sur les mots. Silences voulus (gag 4.5-7.0 ; noir 16.0-16.8) = silences de **VOIX** : musique coupée à 16.0, bruitages continuent. Voir section I.2 du document intégral pour la liste des ~40 événements.
- Mix sur le **VRAI fichier** : **-14 LUFS intégrés, crête vraie -1 dBTP**, durée **59,0 s**, voix au premier plan.

## J. Textes à l'écran
- Sous-titre mot à mot **tout le film**, SAUF les 3 moments typographiques (F05, F10, F13) et le gag muet (F02).
- **Un mot clé en boîte d'accent par phrase** : F01 « paies » (rouge brique) · F03 « mêmes » · F04 « pubs » · F06 « seule » (jaune) · F07 « milliers » · F08 « centaines » · F09 « milliers » · F10 « seule » · F11 « mille » · F12 « offerts » · F13 « mérites ».
- **Pics soulignés (3-4 en tout)** : « même chose » (F01), « déjà vues » (F03), « trente » (F12), « mérites » (F13).
- Textes « décor » autorisés (liste fermée) : lignes du ticket, étiquettes de chaînes, compteurs, noms d'univers, prix, « OFFERT », « moins de XAF 30 / jour », « Télécharger », `[LIEN_TELECHARGEMENT]`, `[CONDITIONS_OFFRE]`. **Aucun autre texte.**

## K. Déclinaisons — APRÈS validation du 9:16
16:9 (1920×1080, recomposition dédiée, ticket horizontal, sous-titre y 890-980) · 30 s · 15 s · 3 accroches alternatives A/B/C (mesure : rétention à 3 s et 10 s).

## L. Conformité
1. **Aucun opérateur/décodeur/forfait/marque tiers** nommé, montré ou suggéré.
2. **Véracité** des promesses pour un nouvel utilisateur au moment de la diffusion ; pas de « tout est inclus » / « sans rien faire » si configuration requise ; éviter « gratuit », « illimité », « sans pub » sauf si exact.
3. **Droits** : aucune affiche réelle, aucun logo de chaîne/radio/club/ligue/artiste/anime, aucun personnage protégé ; titres/stations fictifs ; pas d'affiche suggestive.
4. **Voix** : forfait ElevenLabs payant ; jamais cloner une voix réelle sans accord écrit ; ou comédien sous contrat.
5. **Musique/SFX** : CC0 vérifié page par page ; SFX sous Pixabay Content License.
6. **Offre** : tarifs, durée, renouvellement, moyens de paiement confirmés avant publication.
7. **Enfants** : univers Enfants montré par icônes + contrôle parental (PIN), **aucun enfant à l'image**.
8. Réglementation publicitaire du pays de diffusion.
9. Sécurité AGENTS.md (aucune clé, aucune publication, aucun envoi).
10. Nom de marque « MISSA TV 360 » / « 360+ » / « PLUS » : **décision du propriétaire** ; le film utilise la forme du `[LOGO_OFFICIEL]` fourni.

## M. Plan d'exécution (points d'arrêt)
- **ÉTAPE 0** — préparation : lire AGENTS.md/SKILL.md/PATTERNS/STORYBOARD-CRAFT/templates + exemple `ligne-du-temps-v8` ; `.env` vide ; `npm ci` ; `new-project.sh` ; appliquer les 8 adaptations 9:16 ; **demander EN UNE SEULE FOIS ce qui manque (section C)**.
- **ÉTAPE 1 — SCRIPT (arrêt 1)** : 5 concepts en une ligne, puis G.2 en 2 versions dans `SCRIPT.md` ; l'utilisateur corrige mot à mot ; **ne rien fabriquer avant sa validation**.
- **ÉTAPE 2 — VOIX (arrêt 2)** : donner G.3 + réglages G.4 ; attendre `voix.mp3` ; `onsets.py --no-whisper` → `CUTS/TAIL/TOTAL` → `MUSIC= bash build-audio.sh` → `mots.py` → `onsets.py --transcript` → `onsets.json` ; recaler tous les temps de H.
- **ÉTAPE 3 — STORYBOARD (arrêts 3 et 4)** : `DIRECTIONS.md` 3 directions × 3 styleframes 1080×1920 → **choix sur image** ; `frame.md` **sans aucun `{{`** ; `reference/grille.html` source unique ; `STORYBOARD.md` au format du modèle, relais écrits 2× à l'identique ; grille 15 points.
- **ÉTAPE 4 — ANIMATION (arrêt 5)** : d'abord **F01 seule** → validation ; puis sous-agent par séquence ; `opacity 0`, `immediateRender:false`, ids commençant par une lettre, jamais `style.visibility="visible"`, pas de `<template>` à côté de la racine, `npx hyperframes validate` sur chaque séquence ; `assemble.sh` ; sortie au noir.
- **ÉTAPE 5 — MUSIQUE/SFX/VÉRIFICATION (arrêt 6 : choix musique)** : `analyze-music.py`, 3-4 options, SFX I.2 ; **contrôle du VRAI rendu** (`check-frames.py`, planche contact 0,5 s, raccords image par image, volume, 59,0 s, bande sûre).
- **Rapport final** : séquences terminées/non terminées justifiées, résultats des contrôles, placeholders restants, décisions attendues, chemins livrés.

## N. Grille de contrôle (15 points)
1. Étape toutes les 0,5 s ; jamais > 1 s sans événement ; 0,1-0,3 s dans les 3 premières secondes · 2. Caméra jamais à l'arrêt > 0,5 s hors silence écrit · 3. Apparition ≤ 0,2 s, trop grande et floue · 4. Image devance son mot de 0,1-0,6 s ; texte synchrone à 0,1 s · 5. Chaque couture nomme son objet-pont, jamais deux copies · 6. ≤ 4 coupes, ≤ 2 fondus, aucune coupe sur image vide · 7. ≥ 3 verbes joués par un objet (paies = tampon, s'en va = pièces, offerts = tampons verts) · 8. Moitié des plans sur 3 niveaux de profondeur · 9. `handoff_out = handoff_in` · 10. Premier mot = cible/douleur, 1re image = ticket, pas le logo · 11. Lisible sans le son, bande sûre, contraste · 12. Un seul accent (jaune) réservé au monde 2, négatif = rouge brique · 13. Rime F11/F13 avec le geste du ticket F01 · 14. Fin : un seul bouton, curseur d'un seul mouvement, 2-3 s d'image vivante, noir à 59,0 · 15. Aucune marque tierce, aucune affiche réelle, aucune image IA, montants `XAF 1 000` / `XAF 10 000`, calculs de B respectés.
