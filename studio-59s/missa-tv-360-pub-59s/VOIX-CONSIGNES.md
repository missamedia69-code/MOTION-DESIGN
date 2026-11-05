# VOIX — consignes de synthèse locale · 4 novembre 2026

> Le texte à coller est **`VOIX-A-SYNTHETISER.txt`** (texte pur, sans balise, sans mise en scène).
> Il reprend **mot pour mot** le G.3 de `SCRIPT.md`, avec la révision 1.1 des tarifs.
> Le propriétaire synthétise la voix avec son logiciel local et fournit le fichier.

> ⚠️ **RÉVISION 1.2 du 4 novembre 2026** — `VOIX-A-SYNTHETISER.txt` contient le texte **amélioré**
> (accroche réécrite, « contenus creux », « empiler l'argent sur l'argent », « On est ensemble ! »).
> Le détail des corrections est au §8 de `SCRIPT.md`. **Trois points à trancher avant d'enregistrer**
> sont listés au §3 bis ci-dessous. Le texte attend ta validation mot pour mot (point d'arrêt 1 réouvert).

## 1. Fichier à produire

`assets/audio/voix.mp3` (ou `.wav`) — **mono**, 48 kHz si le logiciel le permet, **une seule prise**,
sans musique, sans bruitage, sans silence artificiel en tête ni en queue.
Le fichier reste **local** : `*.mp3` / `*.wav` sont ignorés par Git (aucune clé, aucun envoi).

## 2. Réglages et direction (G.4 / G.5)

| Réglage | Valeur |
|---|---|
| Langue | **Français, réglée à la main** |
| Voix | Homme 35-45 ans, chaude et posée ; **accent français d'Afrique centrale ou de l'Ouest naturel**, jamais caricatural, sourire audible |
| Jeu | 0:00 → 0:16 ironique, un peu las ; à partir de 0:17 énergie et fierté |
| Chœur | **Une seule voix suffit**, y compris pour « On mérite mieux ! » et « On est ensemble ! » (version minimale autorisée par G.4) |
| Stabilité / similarité | 40-50 % / 80-90 % si le logiciel expose ces paramètres |

**Prononciation** : MISSA = « mi-sa » (écrire `Mi-sa` si le moteur bute, le sous-titre affiche toujours
MISSA) · TV = « télé » **ou** « té-vé », de façon **constante** · 360 = « trois cent soixante » ·
CFA = lettres « C-F-A ». **Tous les chiffres sont déjà en toutes lettres** dans le texte.

**Débit** : parler naturellement, **≈164 mots** pour une cible de **59,0 s**. Ne pas forcer la durée :
le montage coupe **uniquement dans les silences**, jamais en accélérant la voix. Les **lignes vides**
marquent le gag muet (~2,5 s), le pivot (~0,8 s) et le chœur final — **ne pas en ajouter entre
chaque phrase**, sinon le TTS dépasse 59,0 s. **Ne pas les allonger soi-même**.

## 3. Une seule ligne à trancher avant d'enregistrer

Le texte livré dit **« Deux mois offerts ! »** : c'est la formulation du script validé, et la section
L.2 déconseille « gratuit » sauf si exact. Le propriétaire a dit « 2 mois gratuits » dans son retour.

- Si tu gardes **« Deux mois offerts ! »** → rien à changer, l'écran affiche `2 MOIS OFFERTS`.
- Si tu préfères **« Deux mois gratuits ! »** → remplace **uniquement cette ligne** et préviens-moi :
  j'alignerai le sous-titre mot à mot et la carte de prix F12.

Rappel du calcul : **12 × 1 000 = 12 000**, l'année coûte **10 000** → écart **2 000 XAF = 2 mois**.

## 3 bis. Révision 1.2 — à trancher avant d'enregistrer

1. **« Deux mois offerts ! »** (texte livré, cohérent avec `2 MOIS OFFERTS` à l'écran) ou
   **« Deux mois gratuits ! »** (mot employé dans ton retour) → une seule ligne à remplacer.
2. **« whech »** : coquille corrigée en **« On est ensemble ! »**. Si tu voulais **« wesh »**,
   dis-le : c'est une tournure régionale que G.5 fait valider par un locuteur natif (toi, à Douala).
3. **« pour ne rien avoir »** : gardé tel quel, mais c'est une affirmation très absolue. Variante
   plus prudente : **« pour rien de neuf »**. Aucun opérateur ni marque n'est nommé (L.1 respecté).

**Accroche resserrée** (si tu veux garder F01 à ~4 s au lieu de ~5,5-6 s) :

```
Tu paies.
Chaque premier du mois, cher, pour rien de neuf.

Et chaque soir... la même chose.

Les mêmes chaînes.
```

Sinon, garde le texte livré : je recalerai les 13 séquences sur `voix.mp3` en conservant le gag
muet, le pivot noir et la durée totale de **59,0 s**.

## 4. Timings mot à mot — fortement recommandé

`mots.py` exige le CLI Whisper, dont le modèle n'est pas téléchargeable dans ce sandbox. Si ton
logiciel exporte les timestamps mot par mot, dépose **aussi** un JSON :

```json
{"words":[{"w":"Tu","s":0.00,"e":0.16},{"w":"paies.","s":0.16,"e":0.50}]}
```

Les clés `word` / `start` / `end` sont également acceptées. Je l'injecte directement avec
`onsets.py --transcript` → **vrai `onsets.json`**, sans Whisper. Sans ce fichier, je recale sur les
silences avec `onsets.py --no-whisper` et le minutage restera provisoire.

## 5. Ce que je fais à réception

1. `onsets.py` (avec transcript si fourni) → `onsets.json` définitif, 13 fenêtres recalées.
2. `render/wip_cuts.py`, `sous-titres.srt`, `index.html` et les SFX réalignés sur la vraie voix.
3. Substitution de la VO de travail par `voix.mp3`, nouveau rendu **59,0 s**, contrôle du vrai MP4.
4. Le point d'arrêt 2 sera alors levé ; resteront les points 3 à 6 (styleframes, storyboard, F01,
   musiques CC0, mix −14 LUFS / −1 dBTP).
