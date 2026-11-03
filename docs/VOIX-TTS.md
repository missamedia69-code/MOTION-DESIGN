# Voix off & TTS — comparatif vérifié et intégration

Dépôts proposés pour la partie **voix** du pipeline, vérifiés via l'API GitHub le
2026-11-03. Les liens de la liste d'origine ont été corrigés (deux pointaient vers
`github.com/topics/voice-design` ou un README au lieu du dépôt).

> ⚠️ Aucun de ces projets n'est un **skill agent** (`SKILL.md`) : ils ne
> s'installent pas avec `npx skills add`. Ce sont des applications / moteurs TTS.
> `VoiceStudio` et `voicebox` contiennent quelques `SKILL.md`, mais ce sont des
> skills de développement interne (FastAPI, Vite, release notes), sans rapport
> avec la génération de voix.

---

## 1. Comparatif

| Dépôt | Licence | ⭐ / volume | Langues & moteurs | Français | Contrainte principale |
|---|---|---|---|---|---|
| [`debpalash/VoiceStudio`](https://github.com/debpalash/VoiceStudio) | **AGPL-3.0** | ~99,7k · 189 Mo | 16+ moteurs, 646 langues, clonage, doublage vidéo, transcription, livres audio | ✅ | **Copyleft fort** : à éviter pour un usage commercial fermé. CPU possible, GPU recommandé |
| [`jamiepine/voicebox`](https://github.com/jamiepine/voicebox) | MIT | ~59,3k · 100 Mo | 8 moteurs TTS, 23 langues, clonage, dictée, effets audio, Whisper STT | ✅ (23 langues) | App desktop locale, modèles à télécharger |
| [`msrbuilds/voice-studio`](https://github.com/msrbuilds/voice-studio) | MIT | 223 · 4 Mo | VibeVoice, Kokoro, Chatterbox, OmniVoice, VoxCPM2, Qwen3-TTS + Whisper (`.srt`/`.vtt`) | ✅ via Chatterbox / OmniVoice / VoxCPM2 | **Modèles HuggingFace** (hors hôtes autorisés du sandbox), 1 environnement isolé par moteur |
| [`OpenBMB/VoxCPM`](https://github.com/OpenBMB/VoxCPM) | Apache-2.0 | ~41k · 4 Mo | VoxCPM2 : 2B params, 30 langues, voice design, clonage, 48 kHz | ✅ **listé explicitement** | Poids 2B sur HuggingFace, GPU conseillé |
| [`mrpeng4/AI-voice-generator`](https://github.com/mrpeng4/AI-voice-generator) | **aucune** | 0 · < 1 Mo | `edge-tts` (voix neuronales Microsoft Edge), export MP3, script multi-voix | ✅ (`fr-FR-*Neural`) | **Service en ligne Microsoft** (hors hôtes autorisés) ; pas de licence, 0 étoile → à éviter en production |
| [`timoncool/speech-studio`](https://github.com/timoncool/speech-studio) | non standard | 198 · 32 Mo | App native Rust/C++, 5 moteurs locaux, clonage, transcription, [README français](https://github.com/timoncool/speech-studio/blob/main/README.fr.md) | ✅ (interface traduite) | Conçue pour **GPU NVIDIA** ; modèles téléchargés au 1er lancement ; licence à vérifier avant usage commercial |

**Corrections par rapport à la liste reçue** : `OpenBMB/VoxCPM` → lien réel du
dépôt (pas le topic `voice-design`) ; `timoncool/speech-studio` → racine du dépôt
(le lien fourni était le `README.fr.md`).

---

## 2. Contrainte sandbox de ce dépôt

Le moteur MOTION-DESIGN ne peut joindre que `github.com`, `codeload.github.com`,
`api.github.com`, `registry.npmjs.org`, `pypi.org` et `files.pythonhosted.org`.
Conséquences :

- **HuggingFace est bloqué** → aucun modèle local (`VoxCPM2`, `OmniVoice`,
  `Kokoro`, `Chatterbox`, `Qwen3-TTS`, `Whisper`) ne peut être téléchargé ici.
- **Le service `edge-tts` est bloqué** → `mrpeng4/AI-voice-generator` ne
  fonctionnera pas dans le sandbox (il fonctionnera sur un poste avec Internet).
- Aucun GPU n'est garanti ; les moteurs 1–2B sont de toute façon irréalistes ici.

➡️ Pour produire une VO **maintenant**, la voie praticable est l'outil vocal
intégré à l'agent (`add_voice` → `generate_speech`) : il ne nécessite ni modèle
local ni accès réseau supplémentaire. Pour une chaîne **reproductible hors
sandbox**, voir §4.

---

## 3. Ce que le moteur attend déjà

La pub `projects/missa-tv-360-v9` est câblée pour 6 segments de VO :
`projects/missa-tv-360-v9/mix9.sh` mixe `.cache/vo9/s1.mp3` … `s6.mp3` avec les
décalages `adelay` suivants :

| Clip | Départ | Texte (caption de `index.html`) |
|---|---|---|
| `s1` | 0,20 s | « Eh mon frère ! Chaque mois tu payes l'abonnement télé, et à la fin tu ne trouves même rien à regarder ? Ça fait mal au cœur, hein ! » |
| `s2` | 8,35 s | « Laisse-moi te montrer le vrai truc : Missa TV 360 ! » |
| `s3` | 13,97 s | « Avec ta box WiFi et ta connexion Internet : +3 000 chaînes et +9 000 films & séries. Et même avec un petit débit, le flux reste stable ! » |
| `s4` | 22,52 s | « Du football aux grands films, des séries africaines aux programmes du monde entier : une autre dimension ! » |
| `s5` | 31,70 s | « Arrête de gaspiller ton argent pour ce qui ne te plaît même pas. Passe à Missa TV 360 ! » |
| `s6` | 38,20 s | « Missa TV 360 : tu te connectes, tu choisis, tu profites ! 5 000 francs seulement par an. On est ensemble ! » |

Rappel de la convention maison : voix **conversationnelle** validée par le
client, logo toujours carré, livrables remis en artefact (pas de `output/`).

---

## 4. Recommandation

| Besoin | Choix conseillé |
|---|---|
| VO immédiate dans ce sandbox | Outil vocal intégré à l'agent → 6 MP3 dans le dossier des VO, puis `mix9.sh` |
| Chaîne reproductible et **libre de droits** sur ton poste | `OpenBMB/VoxCPM` (Apache-2.0, français confirmé, voice design) ou `msrbuilds/voice-studio` (MIT + Whisper pour les `.srt`) — à installer hors sandbox, modèles HuggingFace nécessaires |
| Démarrage rapide sans GPU, en ligne | `edge-tts` directement (`pip install edge-tts`, voix `fr-FR-HenriNeural` / `fr-FR-DeniseNeural`) plutôt que le wrapper `mrpeng4` sans licence |
| Studio complet clonage + doublage | `jamiepine/voicebox` (MIT) ; `debpalash/VoiceStudio` (AGPL-3.0) seulement si le copyleft est acceptable |
| App native sans Python | `timoncool/speech-studio` (README FR), mais GPU NVIDIA et licence à clarifier |

Exemple de génération reproductible **sur un poste connecté** (à ne pas lancer
dans le sandbox) :

```bash
pip install edge-tts
edge-tts --voice fr-FR-HenriNeural --text "Laisse-moi te montrer le vrai truc : Missa TV 360 !" \
  --write-media .cache/vo9/s2.mp3
```

Les chemins `.cache/vo9/s*.mp3` sont ceux attendus par `mix9.sh` ; les médias ne
sont pas versionnés (`.gitignore`), la VO se régénère à partir des captions.

---

## 5. Intégration dans le moteur : `./md vo`

La VO est devenue **déclarative**, comme le montage : elle vit dans
`projects/<nom>/vo.json` (un manifeste par projet), et `./md vo` génère les clips
attendus par le mixage ffmpeg. Aucun modèle n'est téléchargé par le dépôt.

```bash
./md vo missa-tv-360-v9 --dry-run          # 6 commandes, 0 fichier, 0 réseau ✅
./md vo missa-tv-360-v9 --check-mix mix9.sh  # les starts calent sur les adelay
./md vo missa-tv-360-v9 --mix             # affiche les adelay ffmpeg dérivés
make vo P=missa-tv-360-v9 DRY=1           # raccourci Makefile
make test                                  # 14 tests hors-ligne
```

**Sur un poste connecté** (seul endroit où les backends fonctionnent) :

```bash
pip3 install edge-tts                       # backend par défaut, service Microsoft
./md vo missa-tv-360-v9                     # → .cache/vo9/s1.mp3 … s6.mp3
./md vo missa-tv-360-v9 --force            # régénérer même si les clips existent
./md vo missa-tv-360-v9 --backend voxcpm --model /chemin/VoxCPM2 --voice ma_voix.wav
```

### Manifeste `vo.json`

```json
{
  "backend": "edge-tts",
  "voice": "fr-FR-HenriNeural",
  "rate": "-4%",
  "out_dir": ".cache/vo9",
  "format": "mp3",
  "segments": [{ "id": "s1", "start": 0.2, "text": "Eh mon frère ! …" }]
}
```

- `start` = **instant de placement dans le mix** (`adelay` de `mix9.sh`), pas
  forcément le `data-start` de la scène : les deux diffèrent légèrement sur v9.
- Le manifeste de `missa-tv-360-v9` est fourni, avec les 6 textes extraits des
  captions et les 6 décalages du mix ; `--check-mix` valide cet alignement.
- Pour repartir d'une composition neuve :
  `./md vo <projet> --from-captions --write-script` lit les `<div class="cap">`
  de `index.html` et écrit `vo.json` (à ajuster ensuite avec `--check-mix`).

### Deux backends

| Backend | Commande générée | Pré-requis |
|---|---|---|
| `edge-tts` (défaut) | `edge-tts --voice … --text … --rate=-4% --write-media …` | `pip3 install edge-tts` + **accès au service Microsoft** |
| `voxcpm` | `python3 engine/voxcpm_cli.py --text … --out … [--model …] [--reference …]` | `pip3 install voxcpm` + modèle VoxCPM2 (HuggingFace), GPU conseillé |

`--rate` utilise la forme `--rate=-4%` (sinon argparse prend `-4%` pour une
option). Les commandes sont des **argv sans shell** : apostrophes, `&` et
`+3 000` des textes publicitaires passent sans échappement manuel.

### Comportement dans ce sandbox

`edge-tts` s'installe depuis PyPI (hôte autorisé), donc `--dry-run` et les tests
tournent ici. Mais un lancement réel échoue : le service Microsoft n'est pas
joignable. `./md vo` détecte ce type d'erreur et répond explicitement :

```
ERREUR : échec sur le segment 's1' (backend edge-tts).
→ Le service Microsoft Edge TTS est injoignable depuis cet environnement.
  Lancez `./md vo` sur un poste avec Internet, ou utilisez l'outil
  vocal intégré à l'agent (docs/VOIX-TTS.md §2 et §4).
```

`--dry-run`, `--mix`, `--check-mix`, `--from-captions` et `make test` ne requièrent
ni réseau ni modèle : ce sont les portes d'entrée sûres pour préparer une VO ici
avant de la générer ailleurs. Les clips `.mp3` restent non versionnés
(`.gitignore`), conformément à la convention du dépôt.

---

Annuaires connexes : [RESSOURCES-MOTION.md](RESSOURCES-MOTION.md) ·
procédure audio : [plan-skills.md](plan-skills.md) (§3, étape 6) ·
mixage : `./scripts/hf` / `hyperframes-audio`.
