# entrees/ — déposez ici vos fichiers sources

Déposez dans ce dossier les éléments à intégrer aux vidéos :
logo original (PNG/SVG), photos produits, jingle audio, etc.

## Méthode recommandée : interface web GitHub

1. Sur GitHub, ouvrez le dépôt puis choisissez la branche
   `arena/71cd3126-motion-design` (sélecteur de branche en haut à gauche).
2. Entrez dans ce dossier `entrees/`.
3. Bouton **« Add file » → « Upload files »**, glissez-déposez vos fichiers.
4. **« Commit changes »** directement sur la branche.
5. Dans le chat Arena, dites simplement « c'est déposé ».

L'agent récupère les fichiers (git fetch), les intègre et re-rend la vidéo.

## Depuis un clone local (alternative)

```bash
git checkout arena/71cd3126-motion-design
cp ~/mon-logo.png entrees/
git add entrees/          # pour une vidéo ou un audio : git add -f
git commit -m "apport logo original"
git push origin arena/71cd3126-motion-design
```

## Notes

- La branche `main` fonctionne aussi : l'agent sait y piocher les fichiers.
- Le `.gitignore` du dépôt exclut `*.mp4`/`*.mp3`… : l'interface web GitHub
  ne respecte pas .gitignore (donc aucun blocage), mais depuis un clone local
  il faut `git add -f` pour forcer l'ajout d'une vidéo ou d'un audio.
- Les formats conseillés : PNG/SVG pour les logos, JPG/PNG/WEBP pour les
  photos, MP3/WAV pour l'audio.
