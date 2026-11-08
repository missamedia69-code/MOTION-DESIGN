# Manuel du laborantin (agent IA)

> Pour produire des **vidéos publicitaires** (brief, montage libre, multi-formats,
> aperçus en image), utiliser les outils `md_*` du même serveur MCP. Voir
> [docs/PILOTE.md](../docs/PILOTE.md). Ce manuel couvre le laboratoire
> « données chiffrées → vidéo ».

Tu es connecté au **Laboratoire MOTION-DESIGN**. Ton travail : transformer des
**données** en une **vidéo motion design**, sans écrire de code de rendu.

## Règle d'or

Ne fabrique jamais un `project.json` à la main si tu peux décrire les données.
Décris l'échantillon, laisse le protocole et le compositeur faire le montage.

## Boucle de travail (5 gestes)

1. **Regarder les instruments** → `lab_instruments` (canvas, exports, polices,
   animations, assets disponibles, version ffmpeg).
2. **Prendre un protocole** → `lab_schema` + `lab_example`.
3. **Préparer l'échantillon** → remplace `data` par les données de l'utilisateur,
   ajuste `title`, `narrative`, `style`, `canvas`.
4. **Valider** → `lab_validate` (ou `lab_run` avec `dry_run: true`). Corrige les
   erreurs de protocole avant de consommer du temps de rendu.
5. **Lancer l'expérience** → `lab_run` (bloquant) ou `lab_submit` puis
   `lab_status` → `lab_artifact`. Remets le MP4 à l'utilisateur.

## Outils MCP

| Outil | Entrée | Sortie |
|---|---|---|
| `lab_instruments` | — | inventaire des instruments |
| `lab_schema` | — | champs attendus + exemple |
| `lab_example` | — | échantillon complet |
| `lab_validate` | `spec` | spec normalisée + métriques |
| `lab_run` | `spec`, `dry_run?` | expérience complète (artefact) |
| `lab_submit` | `spec` | `{"id": …}` (tâche de fond) |
| `lab_status` | `id` | état, logs, erreur, métriques |
| `lab_runs` | `limit?` | dernières expériences |
| `lab_artifact` | `id` | chemin + sonde du média |

Connexion : `python3 -m lab.mcp` (JSON-RPC 2.0 sur stdio, aucune dépendance).
Alternative sans MCP : API HTTP `POST /api/runs` (voir `docs/LAB-MOTION.md`).

## Ce que fait le compositeur avec tes données

| Scène | Contenu | Mouvement |
|---|---|---|
| 1 · `hook` | accroche + titre + logo | barre `grow_x`, texte `fade_up`/`fade` |
| 2 · `kpi` | somme calculée + insight + « n points · pic : … » | chiffre `pop`, textes décalés |
| 3 · `bars` | **une barre par ligne de données**, valeurs et labels | `grow_y` en cascade |
| 4 · `cta` | appel à l'action + logo | pastille `pop`, texte `fade_up` |

Les hauteurs des barres sont proportionnelles à `value / max`. Les métriques
(`total`, `max`, `mean`, `best_label`) sont calculées par le protocole, pas à
deviner.

## Contraintes à respecter

- `data` : 1 à 12 lignes, `label` chaîne, `value` nombre fini **≥ 0**.
- Couleurs `style.*` au format `#RRGGBB`.
- `canvas` et `preset` doivent exister dans `lab_instruments` ; sinon le
  protocole refuse avec la liste des valeurs valides.
- `brand.logo` doit pointer un fichier existant (sinon : le retirer).
- `duration` est ramenée entre 1 et 10 s ; 4 scènes → durée finale
  `4 × duration − 1,5 s` de transitions.
- Le rendu est **muet** : pour une voix off, utiliser ensuite `./md vo`
  (`docs/VOIX-TTS.md`) puis mixer avec ffmpeg.

## Diagnostic

| Symptôme | Cause | Geste |
|---|---|---|
| `ERREUR de protocole` | champ invalide | `lab_validate` et lire le message |
| `status: error` + logs ffmpeg | police/asset manquant ou canvas impair | `lab_instruments`, retirer `brand.logo` |
| `status: dry-run` | `dry_run: true` | relancer sans le flag |
| Artefact absent | expérience encore `running` | `lab_status` jusqu'à `done` |
| `ModuleNotFoundError: PIL` | dépendances du moteur absentes | `make bootstrap` ou `pip3 install pillow av imageio-ffmpeg` |

## Session prête à rejouer

`scripts/lab-connect.py` ouvre le serveur MCP en sous-processus et exécute un
fichier d'étapes, exactement comme le ferait un agent :

```bash
python3 scripts/lab-connect.py --session lab/samples/session.json \
    --report livrables/lab/session.json
```

`lab/samples/` contient trois specs (9x16, 16x9, 1x1) et la session qui les
enchaîne ; une étape référence sa spec par `spec_file`. Le rapport final
contient `status`, `artifact`, `resolution`, `duration_s` et `bytes` pour chaque
`lab_run`. Pour une seule expérience : `./md lab run lab/samples/reels-abonnes.json`.

## Exemple de session minimale (MCP)

```json
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"agent","version":"1"}}}
{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"lab_validate","arguments":{"spec":{"title":"Test","data":[{"label":"A","value":3},{"label":"B","value":7}]}}}}
{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"lab_run","arguments":{"spec":{"title":"Test","canvas":"720p","data":[{"label":"A","value":3},{"label":"B","value":7}]}}}}
{"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"lab_artifact","arguments":{"id":"<id retourné>"}}}}
```
