# Clonage du template vocal — ce qui a été tenté

## 1. Le fichier introuvable… était sur GitHub

Le template n'était pas dans le checkout local mais **déposé sur la branche
distante** via « Add files via upload » (commit `0012217`). Récupéré par :

```bash
git fetch origin arena/cc667b6c-motion-design
git merge --ff-only origin/arena/cc667b6c-motion-design
```

Fichier : `assets/audio/Voive Template.mp3` — **24,02 s**, stéréo 48 kHz,
377 Ko, piste `mp3float`.

## 2. Pourquoi un vrai clonage n'est pas possible dans ce sandbox

| Voie | État |
|---|---|
| Modèle local de conversion (VoxCPM2, XTTS, RVC…) | ❌ poids sur `huggingface.co` — requêtes HTTP bloquées ici (`curl` → 000) |
| Fish Audio (skill `fish-audio-tts`) | ❌ `FISH_AUDIO_API_KEY` absente, `api.fish.audio` injoignable ; de plus l'outil exige un `reference_id` créé dans le playground, il ne clone pas à la volée |
| `add_voice` / `generate_speech` de l'agent | ❌ auditionnent des voix systèmes, aucun paramètre d'audio de référence |
| Edge TTS | ❌ service Microsoft injoignable, et aucune fonction de clonage |

→ **Aucun moteur de clonage d'identité n'est exécutable ici.**

## 3. Ce qui a été fait à la place (approximation honnête)

`tools/voice-match.py` réalise un **transfert d'enveloppe spectrale** :
il mesure l'empreinte acoustique de la référence et réapplique son enveloppe
moyenne à la VO `voice-02`, avec une correction de hauteur optionnelle.

```bash
python3 tools/voice-match.py --batch --pitch auto
```

| Mesure | Template | VO `voice-02` |
|---|---|---|
| F0 médian | **294 Hz** | 203 Hz |
| Centre spectral | **4 015 Hz** | 2 324 Hz |
| Aigus 3–8 kHz | 21,5 % | — |

Le template est donc nettement **plus haut et plus brillant**. Correction de
hauteur appliquée : **×1,20** (plafonnée volontairement pour éviter un effet
« voix de dessin animé »).

### Fichiers produits

| Fichier | Rôle |
|---|---|
| `assets/voix-off-timbre-seul.mp3` | enveloppe spectrale seule |
| `assets/voix-off-matched.mp3` | enveloppe + hauteur = **candidat « cloné »** |
| `assets/vo-matched/seq-01…06.mp3` | mêmes traitements sur les 6 segments de montage |
| `assets/comparaison-voix.mp3` | **A/B à écouter** : template → VO d'origine → timbre seul → timbre + hauteur (7 s chacun) |
| `VOICE-MATCH.md` | empreintes acoustiques détaillées |

Les durées sont inchangées : `TIMING.md` et `subtitles.srt` restent valables.

### Limites à ne pas masquer

- Ce n'est **pas** l'identité du locuteur : la prosodie, l'articulation,
  l'accent et le grain personnel ne sont pas reproduits.
- Le F0 de 294 Hz peut être biaisé si le template contient de la musique ou
  plusieurs voix (24 s, stéréo) : à confirmer à l'écoute.
- Le transfert spectral peut donner un rendu métallique ; dans ce cas, réduire
  le plafond du ratio dans `tools/voice-match.py` (actuellement `0.3 … 3.0`).

## 4. Pour un vrai clonage, sur un poste connecté

Le moteur du dépôt sait déjà passer une référence à VoxCPM2 :

```bash
pip3 install voxcpm                     # + modèle VoxCPM2 depuis HuggingFace
./md vo missa-tv-360-promo-50s \
     --backend voxcpm \
     --model /chemin/local/VoxCPM2 \
     --voice "assets/audio/Voive Template.mp3" \
     --script projects/missa-tv-360-promo-50s/vo.json
```

`engine/voxcpm_cli.py` transmet `--reference` au modèle. Alternative cloud :
créer une voix dans le playground Fish Audio puis appeler l'API avec son
`reference_id` (voir `.agents/skills/fish-audio-tts/SKILL.md`).

Dans les deux cas, remplacer ensuite `assets/vo/seq-*.mp3`, puis relancer :

```bash
python3 timing/trim_silence.py
python3 timing/generate.py
```
