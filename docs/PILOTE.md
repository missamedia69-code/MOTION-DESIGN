# Manuel du pilote — moteur MOTION-DESIGN v2

Tu pilotes un moteur **générique** de vidéos publicitaires motion design : toute
marque, tout produit, toute devise. Tu décris, le moteur anime : aucun code de
rendu à écrire, seulement du JSON.

## Connexion

| Voie | Commande |
|---|---|
| MCP (recommandé) | `.mcp.json` à la racine → serveur `motion-design` (`python3 -m lab.mcp`) |
| CLI | `./md cockpit`, `./md ad`, `./md lint`, `./md apercu`, `./md render` |
| HTTP | `./md lab serve` (laboratoire données → vidéo) |

## Recevoir les éléments de l'utilisateur

À chaque pub, l'utilisateur dépose dans `entrees/` (upload GitHub sur `main`, ou pièces
jointes) :

- **l'audio complet de la pub** (voix + musique mixées), qui fixe la durée et le rythme ;
- **les logos** de la marque ;
- **les détails en `.txt`** : offre, arguments, prix, contacts, ton ;
- **des vidéos et images complémentaires**.

Procédure :

1. `git pull origin main`, puis **`md_intake`** (ou `./md entrees`). Tu obtiens la durée et
   les respirations de l'audio, la transcription si Whisper est disponible, la palette
   du logo, le contenu des détails, la liste des médias et un **brief pré-rempli**
   (`audio_master`, `sync`, `duration`, `logo`, `style` d'après le logo, `media`).
2. **Lis les détails texte** et complète le brief : `hook` (≤ 8 mots), `benefits`
   (2 à 4), `offer`, `proof`, `cta`, `url`, légendes des `media`. Choisis le `template`.
3. Si une transcription est disponible, aligne les scènes sur ce qui est dit avec
   `cuts` (une coupe par changement de scène). Sinon, `sync: true` coupe sur les
   respirations.
4. Marque récurrente : `md_intake` avec `brand: "nom"` crée `brands/nom.json` d'après le
   logo et copie les fichiers dans `assets/`. Ensuite, `"brand": "nom"` suffit.
5. `md_lint` → `md_preview` → `md_render`.

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
  "brand": "ma-marque",
  "canvas": "9x16",
  "audio_master": "entrees/pub-complete.mp3",
  "logo": "entrees/logo.png",
  "hook": "Et si tout devenait plus simple ?",
  "product": {"image": "entrees/produit.png", "name": "Le Produit", "tagline": "Pensé pour vous"},
  "media": [
    {"file": "entrees/ambiance.jpg", "caption": "Partout avec vous"},
    {"file": "entrees/demo.mp4", "caption": "Prise en main en 2 minutes", "start": 3}
  ],
  "benefits": ["Livraison en 24 h", "Satisfait ou remboursé", "Sans abonnement"],
  "proof": {"value": 5000, "prefix": "+", "label": "clients satisfaits"},
  "offer": {"price": 29, "old_price": 49, "currency": "€", "label": "aujourd'hui", "badge": "-40 %"},
  "cta": "J'en profite",
  "url": "votre-site.com"
}
```

| Template | Scènes | Usage |
|---|---|---|
| `promo` | accroche → produit → médias → bénéfices → preuve → offre → CTA | présenter un produit |
| `offre` | accroche → offre → bénéfices → CTA (rythme plus rapide) | soldes, promo limitée |
| `annonce` | accroche → produit → bénéfices → CTA | lancement, nouveauté |
| `preuve` | accroche → chiffre clé → bénéfices → CTA | preuve sociale |

Une scène sans contenu est sautée. Avec `audio_master`, la durée est celle de l'audio ;
sans audio, `duration` ajuste le rythme (6, 15 ou 30 s). `scenes` impose un ordre précis,
et `media` ajoute une scène par vidéo ou image complémentaire. Le compositeur adapte la
mise en page à chaque format.

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

`brands/<nom>.json` (un kit par client) → `"brand": "<nom>"` puis jetons `$accent`, `$background`,
`$text`, `$muted`, `$on_accent`, `$font.title`, `$font.body`, `$logo`. Un jeton
inconnu est une erreur explicite. Nouvelle marque : `md_intake` avec `brand` (déduit du
logo), ou copier `brands/neutre.json`. Sans kit, le brief peut porter ses couleurs dans
`style`.

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
