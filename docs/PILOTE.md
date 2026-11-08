# Manuel du pilote — moteur MOTION-DESIGN v2

Tu pilotes un moteur de **vidéos publicitaires motion design**. Tu décris, le
moteur anime : aucun code de rendu à écrire, seulement du JSON.

## Connexion

| Voie | Commande |
|---|---|
| MCP (recommandé) | `.mcp.json` à la racine → serveur `motion-design` (`python3 -m lab.mcp`) |
| CLI | `./md cockpit`, `./md ad`, `./md lint`, `./md apercu`, `./md render` |
| HTTP | `./md lab serve` (laboratoire données → vidéo) |

## Recevoir les éléments de l'utilisateur

L'utilisateur dépose ses fichiers dans `entrees/` (upload GitHub sur `main`, voir
`entrees/README.md`) ou les joint au message.

1. `git pull origin main` pour récupérer les dépôts récents.
2. `./md install entrees/*` range chaque fichier dans `assets/` (images, audio, vidéos,
   polices), le valide et met à jour l'inventaire.
3. Si l'utilisateur donne ses couleurs et polices, créer `brands/<marque>.json` à partir de
   `brands/neutre.json`, puis utiliser `"brand": "<marque>"`.
4. Référencer les fichiers par leur chemin (`assets/images/produit.png`) dans le brief.

## La boucle de vol (5 gestes)

1. **Tableau de bord** : `md_cockpit` liste les formats, exports, animations,
   courbes, kits de marque, templates pub, polices, assets et projets.
2. **Composer** :
   - pub classique → `md_ad_compose` avec un **brief** (voir plus bas) ;
   - montage sur mesure → écrire un `project.json` (docs/SPEC-PROJET.md).
3. **Contrôler** : `md_lint`. Corrige toutes les `errors`, puis les `warnings`.
   Chaque remarque donne le champ exact (`scenes[2].layers[1].size`).
4. **Regarder** : `md_preview` renvoie une **planche contact** (images clés du
   brouillon). Vérifie la hiérarchie, les chevauchements et la lisibilité, puis
   ajuste. Les scènes inchangées sortent du cache : itérer coûte peu.
5. **Livrer** : `md_render` avec `preset: "mp4-social"` et
   `formats: ["9x16", "1x1", "16x9"]`. Donne les chemins `outputs[].path` à
   l'utilisateur.

## Brief publicitaire (le plus rapide)

```json
{
  "template": "promo",
  "brand": "missa",
  "canvas": "9x16",
  "duration": 15,
  "hook": "Votre télé vous coûte trop cher ?",
  "product": {"image": "assets/images/box-mtn-cutout.png", "name": "La Box MISSA TV",
              "tagline": "Toute la télé africaine, partout"},
  "benefits": ["Plus de 300 chaînes", "Installation offerte", "Sans engagement"],
  "proof": {"value": 10000, "prefix": "+", "label": "familles abonnées", "stars": 5},
  "offer": {"price": 1000, "old_price": 2000, "currency": "FCFA", "label": "par mois",
            "badge": "-50 %", "deadline": "Jusqu'à dimanche"},
  "cta": "Je m'abonne",
  "url": "missa.tv",
  "music": {"file": "assets/audio/ma-musique.mp3", "loop": true},
  "voiceover": "projects/ma-pub/vo/voix.mp3"
}
```

| Template | Scènes | Usage |
|---|---|---|
| `promo` | accroche → produit → bénéfices → preuve → offre → CTA | présenter un produit |
| `offre` | accroche → offre → bénéfices → CTA (rythme plus rapide) | soldes, promo limitée |
| `annonce` | accroche → produit → bénéfices → CTA | lancement, nouveauté |
| `preuve` | accroche → chiffre clé → bénéfices → CTA | preuve sociale |

Une scène sans contenu est sautée. `duration` ajuste le rythme pour tomber sur
6, 15 ou 30 s. Le compositeur adapte la mise en page à chaque format.

## Règles de mise en scène publicitaire

- **Accroche en moins de 1,5 s.** 85 % des vidéos sociales sont vues sans le
  son, donc le message doit se lire.
- **Une idée par scène**, au plus 6 à 8 mots à l'écran en même temps.
- **Texte ≥ 2,8vmin** (≈ 30 px en 1080p) ; titres 7 à 10vmin.
- **Zones sûres 9x16** : rien d'important dans les 14 % du haut et les 20 % du
  bas (pseudo et légende TikTok/Reels), ni dans les 12 % de droite (boutons).
- **Contraste ≥ 4,5:1** pour les petits textes. Sur une photo, utilise `box`
  (pastille) ou `shadow`.
- **Mouvement avec intention** : une entrée par élément, en cascade (`in`
  décalés de 0,1 à 0,3 s ou `split` + `stagger`). `idle` seulement sur 1 ou 2
  éléments (produit `float`, bouton `pulse`).
- **Toujours un CTA** à la fin, avec le logo.
- **Son** : musique en `audio` (bouclée). La voix en `voiceover` fait baisser
  la musique automatiquement (ducking). `mp4-social` normalise à -14 LUFS.

## Vocabulaire du mouvement

| Champ | Valeurs |
|---|---|
| `anim` (entrée) | `fade`, `fade_up/down/left/right`, `slide_up/down/left/right` (depuis le hors-champ), `pop`, `scale_in`, `zoom_in`, `punch` (impact 140 %→100 %), `rotate_in`, `grow_x`, `grow_y` (révélation masquée), `kenburns_*` |
| `ease` | `ease_out` (défaut), `ease_in`, `ease_in_out`, `expo_out`, `back_out` (rebond), `back_in`, `elastic_out`, `snap`, `linear` |
| `exit` (sortie) | `fade`, `fade_up`, `fade_down`, `slide_*`, `scale_out` |
| `idle` (continu) | `float`, `drift`, `pulse`, `sway`, `breathe` |
| `anchor` | `center`, `top_left`, `top`, `top_right`, `left`, `right`, `bottom_left`, `bottom`, `bottom_right` |
| Texte | `split: word/line/char` + `stagger`, `box` (pastille), `shadow`, `stroke_width`, `uppercase`, `letter_spacing` |
| `counter` | chiffre qui défile : `from`, `to`, `prefix`, `suffix`, `decimals`, `count_duration` |
| `shape.kind` | `rect`, `circle`, `ring`, `line`, `triangle` (+ `gradient`, `stroke`, `opacity`) |
| `background` | `#hex`, image, `{"gradient": [...], "angle": 135}`, `{"gradient": [...], "type": "radial"}` |

## Unités relatives (un projet, tous les formats)

`"50%"` (axe du champ), `"8vw"`, `"8vh"`, `"6vmin"`, `"6vmax"`, ou pixels.
Exemple : `"pos": ["50%", "40%"], "size": "8vmin"`. Puis
`./md render ma-pub --formats 9x16,1x1,16x9`.

## Kits de marque

`brands/<nom>.json` → `"brand": "missa"` puis jetons `$accent`, `$background`,
`$text`, `$muted`, `$on_accent`, `$font.title`, `$font.body`, `$logo`. Un jeton
inconnu est une erreur explicite. Nouvelle marque : copier `brands/neutre.json`.

## Diagnostic

| Symptôme | Geste |
|---|---|
| `ERREUR de brief pub` | relire le message ; `md_ad_example` donne le schéma |
| `errors` dans `md_lint` | corriger le champ indiqué par `where` |
| `ERREUR ffmpeg …` | le message cite la cause ; vérifier fichiers, polices, unités |
| `jeton de marque inconnu` | `md_brands` pour les jetons disponibles |
| Texte coupé ou trop large | `max_width` (ex. `"84vw"`) ou réduire `size` |
| Rendu lent | `draft: true` pour itérer ; scènes inchangées en cache ; `MD_JOBS=4` |
| Délai dépassé | `MD_FFMPEG_TIMEOUT=3600` |
