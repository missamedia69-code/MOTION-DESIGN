# entrees/ — déposez ici les éléments de la pub en cours

Le moteur est générique : n'importe quelle marque, n'importe quel produit.
À chaque pub, déposez :

1. **L'audio complet de la pub** (voix + musique déjà mixées, .mp3 ou .wav). La vidéo
   se cale dessus : même durée, coupes sur les respirations.
2. **Les logos de la marque** (PNG transparent ; mettez « logo » dans le nom). Les
   couleurs de la vidéo en sont déduites.
3. **Les détails en texte** (`details.txt`) : accroche souhaitée, arguments, offre, prix,
   site, ton.
4. **Des vidéos et images complémentaires** (produit, ambiance, démonstration). Une scène
   chacune.

L'agent lance `./md entrees` (ou l'outil MCP `md_intake`) pour tout analyser, puis
compose la pub.

## Méthode 1 — interface web GitHub (la plus simple)

1. Ouvrez le dépôt sur GitHub, branche **`main`**.
2. Entrez dans ce dossier `entrees/`.
3. **« Add file » → « Upload files »**, puis glissez-déposez vos fichiers.
4. **« Commit changes »** directement sur `main`.
5. Dites à l'agent : « c'est déposé dans entrees/, fais la pub ».

Avant une nouvelle pub, demandez à l'agent de **vider `entrees/`**.

L'interface web accepte aussi les vidéos et les sons (`.mp4`, `.mp3`), que git
ignore d'habitude.

## Méthode 2 — dans la conversation

Joignez les fichiers directement au message de l'agent (images surtout). Précisez ce
que c'est : « logo », « photo produit », « musique de fond ».

## Méthode 3 — depuis un clone local

```bash
cp ~/mon-logo.png ~/produit.png entrees/
git add -f entrees/       # -f pour inclure aussi vidéos et sons
git commit -m "Éléments pub : logo + produit"
git push origin main
```

## Bien nommer ses fichiers

Des noms explicites aident l'agent : `logo-marque.png`, `produit-detoure.png`,
`pub-complete.mp3`, `details.txt`, `demo-produit.mp4`.

## Exemple de `details.txt`

```
Marque : Ma Marque
Produit : Le Produit (photo : produit.png)
Accroche : Et si tout devenait plus simple ?
Arguments : livraison en 24 h ; satisfait ou remboursé ; sans abonnement
Offre : 29 € au lieu de 49 €, jusqu'à dimanche
Appel à l'action : J'en profite
Site : votre-site.com
Format : 9:16 (Reels/TikTok), plus une version 1:1
Ton : dynamique, chaleureux
```
