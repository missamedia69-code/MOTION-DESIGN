# RAPPORT — ÉTAPE 0 (préparation) · 4 novembre 2026

## 0. Changement de base

Le cahier des charges **v2.0 « TON ÉCRAN MÉRITE MIEUX » (59,0 s, 1080×1920)** **remplace** le spot
50 s précédent. L'ancien projet `projects/missa-tv-360-promo-50s/` est **archivé en l'état**, sans
aucune modification de ses fichiers ni réutilisation de ses 10 images générées par IA (interdites
par la section A de la v2.0). L'ancien MP4 reste livré à `livrables/missa-tv-360-promo-50s.mp4`
à titre d'archive uniquement.

Conséquences acceptées de la v2.0 (elle remplace les choix antérieurs) :
- **durée 50 s → 59,0 s** ;
- **prix : tarif réel de l'application — `XAF 1 000 / mois` et `XAF 10 000 / an`**
  (révision 1.1 du 04/11 : **2 mois offerts**, et non 7) ;
- **« SFX seuls, aucune musique » → 2 morceaux CC0 fournis par l'utilisateur** (tension + élan) ;
- **images générées / mosaïque → typographie animée, interfaces réelles, vecteurs** ;
- **VO produite par l'agent → VO produite par l'utilisateur** (`voix.mp3`) ;
- **QR/activation code → CTA « Télécharger » + lien/QR officiels à fournir**.

## 1. Dépôt de référence et atelier

| Élément | Résultat |
|---|---|
| Dépôt de référence | `github.com/cblain100-prog/motion-design-claude-code`, HEAD `a89fc54` — cloné, puis **vendored** dans `studio-59s/` (`.claude/`, `patterns/`, `templates/`, `examples/ligne-du-temps-v8/`, `AGENTS.md`, `package.json`, `package-lock.json`). 442 fichiers / 6,2 Mo ; les 31 Mo d'`examples/` lourds n'ont pas été copiés. |
| CLI | **`npm ci` → 119 paquets, `npx hyperframes --version` = `0.8.82`** (figé, jamais `@latest`, jamais global). |
| `.env` | créé depuis `.env.example`, **aucune clé**. `.claude/settings.json` (télémétrie désactivée) conservé. |
| Polices | **7 fichiers WOFF2 SIL OFL** dans `assets/fonts/` : Instrument Sans 400/500/600/700, Space Mono 400/700, Big Shoulders 800. ⚠️ `new-project.sh --fonts` utilise **jsDelivr (hôte non autorisé)** : les polices ont donc été obtenues via **`@fontsource/*` sur registry.npmjs.org** (hôte autorisé), même licence OFL, sans `--fonts`. |
| Projet | créé par `bash .claude/skills/motion-design/scripts/new-project.sh missa-tv-360-pub-59s` → `studio-59s/missa-tv-360-pub-59s/`. |
| SFX | **20 MP3 + `manifest.json` + `CREDITS.md`** de `.claude/skills/media-use/audio/assets/sfx/` (Pixabay Content License), disponibles localement. |
| Sécurité | **aucun push, aucune publication, aucune clé, aucun envoi** (section D.1). Aucune commande interdite lancée. |

## 2. Adaptations 9:16 de la section D.2 — appliquées et contrôlées

| # | Adaptation | État |
|---|---|---|
| 1 | `meta.json` → `1080 × 1920`, `30 fps` | ✅ |
| 2 | `data-width/data-height/data-duration` sur la racine de chaque composition | ✅ pour le gabarit ; **à contrôler séquence par séquence** à l'étape 4 |
| 3 | `frame.md` → `unit: 1080×1920`, bande de sous-titre **y 1280→1400**, 38 caractères, `numeral-jumbo` en Big Shoulders | ✅ |
| 4 | `STORYBOARD.md` → `format: 1080x1920`, `duration: "59.0s"` | ✅ |
| 5 | `render-styleframes.py --width 1080 --height 1920` | prêt (étape 3) |
| 6 | `assemble.sh` → **que la coupe** : `LEAK_AT=""`, `IRIS_AT=""`, `PAPER=""`, SVG repassé en `1080×1920`, accents jaune `#F5BB00` | ✅ |
| 7 | `npx hyperframes render --quality looks/delivery` | prêt ; ⚠️ **`--resolution portrait` n'existe pas en 0.8.82** — le 9:16 vient de la composition |
| 8 | contrôle sur le VRAI rendu, planche contact toutes les 0,5 s | à faire (étape 5) ; ⚠️ **`validate --caption-zone` n'existe pas en 0.8.82** → `npx hyperframes check` + contrôle manuel des fractions `x0 0.07 / x1 0.93 / y0 0.667 / y1 0.73` |

`assemble.sh` : `FIRST_FRAME="F01-accroche-ticket"`, `END_CARD="F13-appel-a-l-action"`, `TOTAL="59.0"`.
`build-audio.sh` : `TOTAL="59.0"` (`TAIL` recalé après réception de la voix).

## 3. Faisabilité du rendu dans le sandbox (vérifiée, pas supposée)

`npx hyperframes doctor` signalait au départ : FFmpeg ✗, FFprobe ✗, **Chrome Headless Shell ✗**.
`npx hyperframes browser ensure` échoue (téléchargement depuis un CDN non autorisé :
`Client network socket disconnected before secure TLS connection`).

**Solution retenue, uniquement via les hôtes autorisés :**
- `@sparticuz/chromium@153.0.0` (npm) → binaire Chromium 153 décompressé + ses libs NSS/NSPR ;
  piloté avec succès par `puppeteer-core` (dépendance déjà présente) ; `HYPERFRAMES_BROWSER_PATH` positionné.
- `@ffprobe-installer/linux-x64@5.1.0` (npm) → `ffprobe` ; `imageio-ffmpeg` → `ffmpeg`.
- `studio-59s/env.sh` exporte `PATH`, `LD_LIBRARY_PATH`, `HYPERFRAMES_BROWSER_PATH` et les 4 variables
  anti-télémétrie. **`studio-59s/setup.sh`** recrée tout l'environnement en une commande.

**Résultats :**
- `npx hyperframes doctor` → ✓ **FFmpeg**, ✓ **FFprobe**, ✓ **Chrome (env)**, ✓ version 0.8.82.
  Restent en ✗ **uniquement des options non requises** : whisper-cpp (transcription), Kokoro TTS,
  MusicGen BGM (musique générée interdite de toute façon), Docker (non utilisé).
- **Rendu de fumée réel** : composition minimale 1080×1920 → `/tmp/hf-smoke.mp4`
  **H.264 · 1080×1920 · 30/1 fps · 2,000 s**, produit par `npx hyperframes render` 0.8.82.
  Le test a été supprimé ensuite. ✅ **Le pipeline HyperFrames fonctionne de bout en bout.**
- Réserve : le gabarit d'exemple charge GSAP depuis **jsDelivr** (bloqué). Pour les vraies séquences,
  GSAP sera chargé **localement** depuis `node_modules/gsap/dist/gsap.min.js` (présent dans les 119 paquets).

## 4. Section C — état des éléments à fournir (question groupée UNIQUE)

| Élément | État | Ce qui sera affiché en attendant |
|---|---|---|
| `[HEX_JAUNE]` | ✅ **RÉSOLU SANS RIEN INVENTER** : `#F5BB00` — `missaYellowPrimary`, `app/src/main/res/values/colors.xml:127`, dépôt public `missamedia69-code/MISSA_TV_360_PLUS` (`1da53ac`). | — |
| `[LOGO_OFFICIEL]` | ✅ **RÉSOLU le 04/11** : le propriétaire a répondu « le logo est dans asset ». `assets/images/logo-missa.png` (= `entrees/Logo Missa TV`, même md5) copié en `assets/img/logo-officiel.png`. Forme **« MISSA TV 360 »** retenue. ⚠️ PNG 1254×1254 à fond jaune **opaque** (pas de transparence) et identité bleu/vert : cf. `assets/img/README.md`. | — |
| `[CAPTURES_APP]` | ❌ **manquant** : aucune capture récente téléphone portrait ni Android TV, et les correctifs T01/T02/T03 ne sont pas confirmés. **Aucune interface ne sera dessinée de mémoire.** | `[CAPTURES_APP]` en placeholder visible |
| `[LIEN_TELECHARGEMENT]` + `[QR_CODE]` | ❌ **manquant** (le dépôt applicatif ne contient qu'un QR d'exemple `example_qr.png`, non officiel). | `[LIEN_TELECHARGEMENT]` / `[QR_CODE]` |
| `[MODES_DE_PAIEMENT]` | ❌ **manquant** | `[MODES_DE_PAIEMENT]` |
| `[CONDITIONS_OFFRE]` | ❌ **manquant** (mention en petit sur F13) | `[CONDITIONS_OFFRE]` |
| `[VOIX]` | ❌ **manquant** : `assets/audio/voix.mp3` attendu. Le template `assets/audio/Voive Template.mp3` (24,02 s) et les VO générées de l'ancien projet existent mais **ne sont pas la voix du film**. | `[VOIX]` + silence de référence |
| `[MUSIQUES_CC0]` | ❌ **manquant** : 2 morceaux (tension + élan), licence CC0 vérifiée page par page. | `[MUSIQUE TENSION]` / `[MUSIQUE ELAN]` + silence |
| SFX | ✅ 20 MP3 Pixabay fournis par media-use | — |
| Polices OFL | ✅ 7 WOFF2 | — |
| Univers / tarifs / calculs | ✅ repris tels quels du cahier des charges | — |

**Politique placeholder** : conformément à la section C, tout élément manquant apparaît
**littéralement à l'écran** (entre crochets) dans les séquences concernées, et sera **listé dans le
rapport final**. Aucun logo, aucune URL, aucun QR, aucune condition d'offre, aucun moyen de
paiement, aucune capture et aucune station n'est inventé.

## 5. Points d'arrêt à respecter (section D.1 / M)

| # | Après | État |
|---|---|---|
| 1 | **Script** (`SCRIPT.md`) | ✅ **LEVÉ le 04/11** — « Validé, on passe à la voix », aucune correction |
| 2 | Voix (`voix.mp3` + `onsets.json`) | ⏸ **ouvert** — VO de travail temporaire autorisée pour le minutage ; vraie voix attendue avant tout rendu final |
| 3 | Choix de la direction (3 × 3 styleframes) | à venir |
| 4 | Storyboard + grille 15 points | à venir |
| 5 | Première séquence F01 | à venir |
| 6 | Choix de la musique (3-4 options) | à venir |

## 6. Fichiers livrés à ce stade

- `studio-59s/missa-tv-360-pub-59s/SPEC-V2.md` — fiche de référence opérationnelle du cahier des charges.
- `studio-59s/missa-tv-360-pub-59s/SCRIPT.md` — **étape 1 validée**, 5 concepts + G.2 + G.3 + réglages voix.
- `studio-59s/missa-tv-360-pub-59s/DECISIONS.md` — **les 5 réponses du propriétaire** à la question groupée unique.
- `studio-59s/missa-tv-360-pub-59s/assets/img/logo-officiel.png` + `assets/img/README.md` — logo officiel désigné.
- `studio-59s/missa-tv-360-pub-59s/RAPPORT-ETAPE-0.md` — ce rapport.
- `studio-59s/missa-tv-360-pub-59s/{meta.json, hyperframes.json, frame.md, STORYBOARD.md, assemble.sh, build-audio.sh, build-music-options.py, DIRECTIONS.md, assets/audio/sfx-events.json}` — gabarits adaptés au 9:16 / 59 s.
- `studio-59s/missa-tv-360-pub-59s/assets/fonts/*.woff2` — 7 polices OFL.
- `studio-59s/env.sh`, `studio-59s/setup.sh` — environnement de rendu reproductible.
- `studio-59s/` — méthode HyperFrames vendored (AGENTS.md, skills, patterns, templates, exemple phare).

**Aucun MP4 du nouveau film, aucun styleframe, aucune séquence HTML et aucun push à ce stade.**

---

## 7. Réponses à la question groupée unique (04/11) — voir `DECISIONS.md`

| Question | Réponse |
|---|---|
| Section C | **« le logo est dans asset »** → `[LOGO_OFFICIEL]` résolu ; les 6 autres éléments restent en **placeholder visible**. |
| `[VOIX]` | **VO de travail temporaire** autorisée pour le minutage ; `voix.mp3` attendu avant tout rendu final. |
| `[MUSIQUES_CC0]` | **Le propriétaire fournit les 2 morceaux** ; en attendant `MUSIC=""` et pistes en silence. |
| Point d'arrêt 1 | ✅ **Script validé mot à mot** ; révision 1.1 du 04/11 : 3 expressions tarifaires corrigées, le reste inchangé. |
| Marque (L.10) | **« MISSA TV 360 »** (sans « + » ni « PLUS »). |

## 8. Étape 2 amorcée (minutage PROVISOIRE)

| Fichier | Résultat |
|---|---|
| `assets/audio/voix-temporaire.mp3` | VO de repère générée à partir du texte **G.3 validé**, **59,544 s**, 24 kHz mono. **Ce n'est pas la voix du film.** Non versionnée (`.mp3` ignoré). |
| `onsets-temporaire.json` | `onsets.py --no-whisper` → **47 phrases**, points de coupe dans les silences, seuil −40 dBFS, silences > 0,4 s repérés. |
| `onsets.json` | **PROVISOIRE** (`"provisional": true`) : 150 mots répartis **déterministement** sur les 47 phrases au prorata de leur durée. |
| `sous-titres.srt` | 45 cues, copie des mots minutés. |
| `TIMING-PROVISOIRE.md` | les **13 séquences recalées** sur les points de coupe (F01 0→4,00 ; F02 4,00→6,52 ; … ; F13 55,16→59,00). |
| `tools/timing-provisoire.py` | script reproductible de la répartition. |

⚠️ **Limite documentée** : `mots.py` exige le CLI **Whisper** (`openai-whisper`) et un modèle à télécharger
depuis un hôte non autorisé ; `npx hyperframes doctor` confirme `whisper-cpp` absent. Le minutage
**mot à mot exact** sera donc refait sur la vraie voix avec `mots.py` + `onsets.py --transcript` dès que
`voix.mp3` sera déposé (ou sur un poste connecté). D'ici là, tout repère temporel est **provisoire**.
La VO de travail dépasse la cible de **+0,48 s** : l'écart sera résorbé par une coupe dans un silence
(`CUTS`/`TAIL` de `build-audio.sh`), jamais en accélérant la voix.

**Point d'arrêt 2 reste OUVERT** : `assets/audio/voix.mp3` attendu. Aucun styleframe ni
`STORYBOARD.md` définitif avant la voix, conformément à la méthode.

Le minutage provisoire a été **amélioré** : les mots sont désormais répartis **par séquence** à
partir du tableau G.2 validé (et non plus globalement sur les 47 phrases), pour que les sous-titres
restent dans la bonne séquence. 150 mots, 43 cues SRT.

---

## 9. Version d'évaluation (WIP) demandée le 04/11

Le propriétaire a demandé de **générer la vidéo pour évaluer l'avancement** et de la mettre dans
`livrables/`. Une version **non diffusable** a donc été produite avec les éléments disponibles,
**sans attendre la voix définitive ni franchir les points d'arrêt 3 à 6** :

- `index.html` mono-composition HyperFrames (13 scènes vectorielles, 563 tweens GSAP local,
  36 bandeaux de sous-titre), généré par `render/wip_build.py` ;
- `render/wip_audio.py` → VO de travail recoupée à 59,00 s + 76 SFX, 4 pistes WAV 48 kHz,
  musique en silence ;
- `npx hyperframes render ... --quality draft --workers 2` → **1770 images en 2 min 06** ;
- mux H.264 + AAC → **`livrables/missa-tv-360-pub-59s_9x16_wip.mp4`** (59,000 s, 12 Mo) ;
- `livrables/missa-tv-360-pub-59s_9x16_wip-contact.jpg` (14 vues) et
  `..._planche-05s.jpg` (118 images toutes les 0,5 s) ;
- `livrables/missa-tv-360-pub-59s_9x16_wip.md` : rapport complet, placeholders, contrôles, limites ;
- `apercu/index.html` (port 8091) : lecteur vidéo du WIP + lecteur de la VO de travail.

Contrôles : `validate` 0 erreur / 0 warning, sonde 1080×1920 · 30 fps · 59,000 s, **0 image noire**,
5 images quasi figées isolées, audio non silencieux sur les 6 tranches de 10 s.
Le détail et les **8 limites connues** sont dans le rapport de livraison.

Les **livrables WIP ont ensuite été poussés** sur la branche de session à la demande explicite du
propriétaire (« je ne vois pas ça dans le dossier livrable de github ») : commit `3c60a83`.
Aucune clé, aucune publication, aucun merge vers `main`. Les points d'arrêt 2 à 6 restent ouverts.


---

## 10. Retour du propriétaire sur le WIP — révision 1.1 (04/11)

Trois corrections et une demande de refonte, formulées après visionnage de la version d'évaluation :

| Point | Retour | Traitement |
|---|---|---|
| **Paroles / tarifs** | « l'application n'offre pas 7 mois gratuits » ; mensuel **1 000 F**, annuel **10 000 F** « au lieu de 12 000 », donc **2 mois offerts** | `SPEC-V2.md` (B, H, J, N), `SCRIPT.md` (G.2/G.3), `DECISIONS.md`, `apercu/index.html`, `render/wip_build.py`, `index.html` : **toutes les anciennes valeurs remplacées**. VO de travail corrigée sur les 2 phrases fautives, `onsets.json`/SRT recalculés (149 mots, 40 cues). |
| **Informations manquantes** | « il y a certaines informations qui manquent … je vais te les fournir plus tard » | **Rien n'est inventé.** Tous les éléments de la section C restent en **placeholder visible** ; la liste est rappelée dans le rapport de livraison. Aucune question posée maintenant. |
| **Visuel** | « trop touffu », « beaucoup d'éléments se répètent », « pas de trucs vraiment élaborés », « épurer et rendre plus professionnel » | WIP **v2** : grille commune (marge 90 / colonne 900), **un seul point focal par plan**, un accent par séquence, filet de progression continu, objets-ponts conservés. 12 tuiles → 3, 40 chaînes → 1 écran, 120 points → 0, 7 barres PUB → 1, 8 pièces → 1, 12 pilules → 1 grille de 8 univers. |
| **Transitions** | « les transitions sont cohérentes » | **Aucune modification** de la structure : 13 séquences, coupes, pivot noir à 16,0, objet-pont point → logo, fondu final au noir. |

**Choix de formulation à confirmer plus tard** : le script validé employait « … mois **offerts** » et la section L.2 déconseille « gratuit » sauf si exact ; la révision conserve donc **« 2 MOIS OFFERTS »** (comparaison 12 000 → 10 000). Le propriétaire a dit « 2 mois gratuits » : s'il préfère ce mot, une seule substitution sera faite au moment de la VO définitive.

**Éléments attendus, non demandés maintenant** : `[VOIX]`, 2 `[MUSIQUES_CC0]`, `[CAPTURES_APP]` (téléphone + Android TV), `[QR_CODE]`, `[LIEN_TELECHARGEMENT]`, `[MODES_DE_PAIEMENT]`, `[CONDITIONS_OFFRE]`, version transparente du logo.

Les points d'arrêt **2 à 6 restent ouverts** ; cette révision ne produit toujours qu'une version d'évaluation.


---

## 11. Étape 2 — le propriétaire fournit la voix (04/11)

« donne moi le texte à utiliser, je te donne la voix, j'ai un logiciel en local qui permet de le
synthétiser ». Deux fichiers ajoutés au projet :

- `VOIX-A-SYNTHETISER.txt` : texte G.3 révisé, **≈150 mots (149 minutés dans `onsets.json`)**, pur, prêt à coller ;
- `VOIX-CONSIGNES.md` : réglages, prononciation, format de fichier, choix « offerts / gratuits »,
  format JSON des timings mot à mot.

**Aucune clé, aucun service cloud, aucun envoi** : la synthèse est faite par le propriétaire sur sa
machine, conformément à G.4 (alternative au forfait ElevenLabs payant). À réception de
`assets/audio/voix.mp3` (+ transcript JSON si disponible), le pipeline `onsets.py` recalera les
13 séquences et la VO de travail sera substituée. Le point d'arrêt 2 reste ouvert d'ici là, les
points 3 à 6 également.

**Question Pinterest (04/11)** : le connecteur Pinterest est `unsupported` sur Arena et
`pinterest.com` n'est pas dans les hôtes réseau autorisés. Les éléments manquants ne sont pas des
illustrations mais les assets officiels du propriétaire (section C) ; aucune image tiers ne sera
introduite dans un film intégralement vectoriel. Un moodboard déposé dans `entrees/` ne servirait
qu'à la direction artistique de l'étape 3, jamais au rendu.


---

## 12. Révision 1.2 du texte VO — « améliore ce texte » (04/11)

Le propriétaire a proposé une nouvelle accroche (« des abonnements coûteux pour ne rien avoir »,
« des contenus vides »), une nouvelle image (« mettre l'argent sur de l'argent ») et une chute
« On est ensemble whech ! ». Ses **idées sont conservées** ; la mise en forme a été améliorée :
français corrigé (*coûteux*, *contenus creux*, *empiler*), « chaque premier du mois » rétabli pour
l'accroche datée, virgule finale remplacée, lignes vides normalisées (gag / pivot / chœur final
uniquement, sinon le TTS dépasse 59,0 s), et « whech » traité comme une coquille.

`VOIX-A-SYNTHETISER.txt`, `VOIX-CONSIGNES.md`, `SCRIPT.md` (G.2, G.3, §8) sont en **1.2**.
**Point d'arrêt 1 réouvert** : validation mot pour mot attendue avant enregistrement.

Trois décisions laissées au propriétaire : « offerts / gratuits », « whech / wesh / rien », et
l'éventuel adoucissement de « pour ne rien avoir » en « pour rien de neuf ». Conséquence timing :
l'accroche passe de 12 à ~22 mots, F01 de ~4,0 s à ~5,5-6,0 s ; recalage prévu sur `voix.mp3`.

**Cohérence documentée** : `onsets.json`, `sous-titres.srt`, `index.html`, la VO de travail et le
**WIP v2 déjà rendu** portent encore la VO 1.1. Ils seront régénérés en une seule passe à réception
de `voix.mp3`. Aucun rendu, aucune clé, aucune publication lancés dans cette étape.
