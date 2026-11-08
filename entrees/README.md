# entrees/ — déposez ici les éléments de vos pubs

Logo, photos produit (PNG détouré de préférence), vidéos, musique, voix off, polices…
L'agent les récupère, les range dans `assets/` (`./md install entrees/*`) et les
utilise dans le brief ou le montage.

## Méthode 1 — interface web GitHub (la plus simple)

1. Ouvrez le dépôt sur GitHub, branche **`main`**.
2. Entrez dans ce dossier `entrees/`.
3. **« Add file » → « Upload files »**, puis glissez-déposez vos fichiers.
4. **« Commit changes »** directement sur `main`.
5. Dites à l'agent : « c'est déposé dans entrees/, fais une pub avec ».

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

Des noms explicites aident l'agent : `logo-marque.png`, `produit-box-detoure.png`,
`musique-energique.mp3`, `voix-off-15s.mp3`.

## Ce qu'il faut fournir pour une pub

| Élément | Format conseillé | Obligatoire ? |
|---|---|---|
| Accroche, bénéfices, offre, appel à l'action | du texte, dans le message | oui (au moins l'accroche) |
| Logo | PNG transparent, ≥ 600 px | conseillé |
| Photo produit | PNG détouré, ≥ 1000 px | pour les templates `promo` et `annonce` |
| Couleurs et polices de la marque | codes #RRGGBB, fichiers .ttf/.otf | pour créer un kit `brands/` |
| Musique | MP3/WAV libre de droits | conseillé |
| Voix off | MP3/WAV, ou un texte à faire lire par la TTS | optionnel |
| Prix, chiffres | dans le message | pour les templates `offre` et `preuve` |
