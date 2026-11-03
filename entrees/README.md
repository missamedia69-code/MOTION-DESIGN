# Déposer les éléments officiels MISSA TV 360

Les vidéos « Ton écran mérite mieux » sont **des maquettes**, avec placeholders explicites. Pour finaliser une diffusion commerciale, déposer les éléments validés dans ce dossier sur la branche de la conversation **`arena/906c7c4f-motion-design`** (pas sur une ancienne branche) :

1. **Logo officiel** SVG ou PNG transparent, et confirmation « MISSA TV 360 » ou « MISSA TV 360+ ».
2. **`res/values/colors.xml`** contenant `missaYellowPrimary`, ou sa valeur hexadécimale confirmée.
3. **URL officielle de téléchargement** dans un simple fichier texte ; le QR ne sera généré *qu’après* validation de cette URL.
4. **Conditions d’offre**, renouvellement éventuel, taxes, modes de paiement, validation de l’équivalence « sept mois offerts ».
5. **Confirmation des volumes annoncés** : milliers de films/séries/documentaires/mangas et de radios, centaines de chaînes en direct ; confirmation des droits d’utilisation des images d’affiches présentes dans vos captures.
6. **Autorisation commerciale des voix** choisies ou enregistrements de comédiens autorisés ; confirmation éditoriale de la formulation sur le faible débit.
7. Si disponibles, captures authentiques des **pages** TV Direct et Documentaires (les seules captures actuelles ne montrent que les onglets). Un contact de support est facultatif.

Depuis GitHub : choisir la branche ci-dessus, ouvrir `entrees/`, puis « Add file » → « Upload files ». Depuis un clone local, `git add entrees/` puis `git commit` et `git push origin arena/906c7c4f-motion-design`. Ne placez **aucun mot de passe, jeton, secret ou donnée personnelle non nécessaire** dans ces fichiers.

Les fichiers générés, scripts et prompts du spot sont dans `projects/missa-tv-360-ton-ecran/` ; le [rapport de validation](../projects/missa-tv-360-ton-ecran/RAPPORT.md) décrit les blocages de publication.
