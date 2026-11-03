# Échantillons du Laboratoire — MISSA TV 360

Trois spécifications prêtes à l'emploi, une par format de diffusion. Elles
utilisent uniquement des assets versionnés (`assets/images/logo-missa.png`,
`assets/fonts/Montserrat-*.ttf`) et des données fictives.

| Fichier | Canvas | Résolution | Accent | Transition | Logo |
|---|---|---|---|---|---|
| `reels-abonnes.json` | `9x16` | 1080×1920 | jaune `#FFD400` | `fade` | oui |
| `chaine-360.json` | `16x9` | 1920×1080 | vert `#22C55E` | `slideleft` | oui |
| `box-usages.json` | `1x1` | 1080×1080 | jaune `#FFD400` | `fadeblack` | non |

`session.json` décrit la session MCP complète : découverte des instruments,
validation du protocole sur le Reels, trois `lab_run`, puis lecture du registre.

## Rejouer la session

```bash
python3 scripts/lab-connect.py \
    --session lab/samples/session.json \
    --report livrables/lab/session.json
```

Le client ouvre `python3 -m lab.mcp` en sous-processus, dialogue en JSON-RPC 2.0
sur stdio (`initialize` → `tools/list` → `tools/call`), et journalise chaque
expérience dans `livrables/lab/session.json`. Aucun serveur HTTP n'est requis.

## Un seul format

```bash
./md lab run lab/samples/reels-abonnes.json            # rendu réel
./md lab run lab/samples/chaine-360.json --dry-run     # compilation seule
```

## Adapter les données

Copier un échantillon, modifier `title`, `narrative` (`hook`, `insight`, `cta`)
et les lignes `data` (1 à 12 paires `label` / `value` ≥ 0). Le schéma complet
est obtenu par `./md lab schema` ou l'outil MCP `lab_schema`. Chaque rendu crée
une expérience identifiable (`<nom>-<id>.mp4`) et son `project.json` dans
`.cache/lab/<id>/`.
