# Script — MISSA TV 360 · promo 50 s · 9:16

> **Version 3** (tour 7) : « En Afrique » dit explicitement dans l'accroche.
> **Version 2** (tour 6) : nouvel angle imposé — « ici, on paie pour n'avoir rien
> à regarder » → la box WiFi / la connexion suffisent, la recherche dans l'app
> donne accès à tout, l'app reste stable en faible débit et économise les données.
> Référence : [BRIEF.md](BRIEF.md). Découpage et répartition du CTA validés au tour 4.
> **Aucune musique** : VO + SFX synthétisés. Sous-titres complets et synchronisés.
> **Texte graphique allégé** : vignettes sans libellés, noms des catégories
> uniquement dans les sous-titres. Depuis le tour 9, la grille utilise les
> **10 images générées** de `images/*.jpg` (plus les pictogrammes).
>
> ⚠️ Les timecodes ci-dessous sont la maquette initiale. La VO a été mesurée
> après rognage des silences TTS : voir **[TIMING.md](TIMING.md)** pour la
> timeline exacte de 50,00 s et **[subtitles.srt](subtitles.srt)** pour les
> 20 repères réellement calés sur l'audio (voix **`voice-02`**, féminine).

## Texte de la voix off (à enregistrer / à générer)

**~118 mots · ~50 s · débit ~2,4 mots/s · ton énergique, direct, complice.**

| Temps | Texte VO | Idée couverte |
|---|---|---|
| 00:00–00:05 | En Afrique, on paie… et on n'a rien à regarder. MISSA TV 360 change ça. | Douleur « on paie pour ne rien avoir », ancrée en Afrique |
| 00:05–00:20 | Avec votre box WiFi ou votre connexion, tapez un film, une série, un manga : une recherche, et c'est là. Chaînes télé, radio, lives, sport, documentaires, enfants, jeux vidéo — tout dans la même appli. | Box / connexion · recherche · panoplie de contenus |
| 00:20–00:28 | Et même avec un faible débit, ça reste stable. Pas de coupures, et l'appli économise vos données. | Faible débit · stabilité · économie de données |
| 00:28–00:34 | Vingt-quatre heures pour tout essayer. Gratuitement. Ouvrez, cherchez, regardez. | Essai 24 h |
| 00:34–00:44 | Après, prenez votre code. Un mois, deux, trois, comme vous voulez — ou l'année à dix mille francs. Scannez, saisissez, c'est reparti. | Code · durées · prix annuel · activation |
| 00:44–00:50 | MISSA TV 360. Activez votre code. Et ne ratez plus rien. | Signature + CTA |

**Répartition inchangée** : la VO ne dit que le prix annuel ; `1 000 XAF / mois`
et `10 000 XAF / an` sont à l'écran. Les liens TV / mobile-tablette ne sont pas
lus : la page QR code est seulement montrée.

## Sous-titres complets (20 repères)

`entrée → sortie | texte` · 1 à 2 lignes max · bande basse sur voile sombre.

| # | Timecode | Sous-titre |
|---|---|---|
| 1 | 00:00.3 → 00:02.0 | En Afrique, on paie… |
| 2 | 00:02.0 → 00:04.0 | et on n'a rien à regarder. |
| 3 | 00:04.0 → 00:05.0 | MISSA TV 360 change ça. |
| 4 | 00:05.0 → 00:07.8 | Avec votre box WiFi ou votre connexion, |
| 5 | 00:07.8 → 00:10.6 | tapez un film, une série, un manga : |
| 6 | 00:10.6 → 00:13.2 | une recherche, et c'est là. |
| 7 | 00:13.2 → 00:16.0 | Chaînes télé, radio, lives, sport, |
| 8 | 00:16.0 → 00:18.2 | documentaires, enfants, jeux vidéo — |
| 9 | 00:18.2 → 00:20.0 | tout dans la même appli. |
| 10 | 00:20.0 → 00:22.6 | Et même avec un faible débit, |
| 11 | 00:22.6 → 00:25.2 | ça reste stable. Pas de coupures, |
| 12 | 00:25.2 → 00:28.0 | et l'appli économise vos données. |
| 13 | 00:28.0 → 00:30.8 | Vingt-quatre heures pour tout essayer. |
| 14 | 00:30.8 → 00:34.0 | Gratuitement. Ouvrez, cherchez, regardez. |
| 15 | 00:34.0 → 00:36.8 | Après, prenez votre code. |
| 16 | 00:36.8 → 00:39.8 | Un mois, deux, trois, comme vous voulez — |
| 17 | 00:39.8 → 00:42.2 | ou l'année à dix mille francs. |
| 18 | 00:42.2 → 00:44.0 | Scannez, saisissez, c'est reparti. |
| 19 | 00:44.0 → 00:46.4 | MISSA TV 360. Activez votre code. |
| 20 | 00:46.4 → 00:49.6 | Et ne ratez plus rien. |

## Texte graphique à l'écran (allégé)

| Temps | Séquence | Éléments conservés |
|---|---|---|
| 00:00–00:05 | Accroche | Logo qui pop sur explosion jaune · aucun libellé |
| 00:05–00:20 | Mosaïque 2×5 | **10 images générées sans texte** (`images/*.jpg` : films, manga, séries, short drama, TV & radio, lives, sport, docs, enfants, jeux vidéo) · barre de recherche animée |
| 00:20–00:28 | Faible débit | Icône signal faible + indicateur de données, **sans texte** |
| 00:28–00:34 | Essai | Badge `24 H` uniquement |
| 00:34–00:44 | Prix & activation | `1 000 XAF / MOIS` · `10 000 XAF / AN` · page QR code recréée · champ de code qui se remplit |
| 00:44–00:50 | Signature | Plein écran jaune · logo · `ACTIVEZ VOTRE CODE` |

Supprimés par rapport à la v1 : libellés des vignettes, `TV · MOBILE · TABLETTE`,
`1 À 12 MOIS`, `24 H OFFERTES` (→ `24 H`). Les noms des 10 univers restent dans
les sous-titres et la VO ; à l'écran, ce sont les images qui les incarnent.

## Bande SFX (synthétisée, sans musique)

Fichiers WAV générés par `sfx/generate.py` → `sfx/wav/` (voir `sfx/MANIFEST.json`).

| Temps | Fichier | Rôle |
|---|---|---|
| 00:00.0 | `impact.wav` + `whoosh.wav` | Ouverture noir → jaune |
| 00:05 → 00:17 | `pop.wav` × 10, décalés | Chaque pictogramme qui s'allume |
| 00:10.6 | `click.wav` | Validation de la recherche |
| 00:20.0 | `whoosh.wav` + `click.wav` | Transition faible débit |
| 00:28.0 | `tick.wav` × 2 + `chime.wav` | Badge 24 h |
| 00:34 / 00:37 / 00:40 | `click.wav` × 3 | Révélation des prix et durées |
| 00:41.5 | `beep.wav` + `key.wav` × 3 | QR code puis saisie du code |
| 00:44.0 | `final_impact.wav` + `riser.wav` | Signature logo |

Aucun lit musical, aucun jingle.
