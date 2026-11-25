# entrees/ — déposez ici les éléments de la pub

**Le minimum : l'audio de la pub et le logo.** Le moteur fait le reste.

| Élément | Obligatoire | Conseil |
|---|---|---|
| **Audio de la pub** (.mp3, .wav…) — voix + musique mixées, ou voix seule | oui | la vidéo dure exactement l'audio ; chaque phrase dite devient une scène |
| **Logo** (PNG transparent, avec « logo » dans le nom) | oui | les couleurs de la pub sont déduites du logo |
| `script.txt` — le texte dit, une phrase par ligne | conseillé | le texte à l'écran sera exactement celui-ci |
| `details.txt` — réglages « clé : valeur » | non | voir ci-dessous |
| Images / vidéos (`produit.png`, ambiance…) | non | un fichier nommé `produit…` devient le produit mis en scène ; les autres illustrent les phrases |

Exemple de `details.txt` :

```
Marque : Lumio TV
Site : lumio.tv
Bouton : Télécharger l'app
Style : energique        (ou premium, doux)
Couleur : #FF5C39        (sinon : celle du logo)
Sous-titres : oui
Formats : 9x16,1x1,16x9
```

Puis : `./md pub` (ou l'outil MCP `md_pub` pour un agent IA). Voir `AGENTS.md`.
