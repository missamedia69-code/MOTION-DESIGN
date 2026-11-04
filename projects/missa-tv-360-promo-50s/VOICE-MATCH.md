# Transfert de timbre

> ⚠️ Transfert d'**enveloppe spectrale**, pas clonage d'identité.
> La prosodie, l'accent et l'identité du locuteur ne sont pas reproduits.

## Empreinte de la référence

- Fichier : `../../assets/audio/Voive Template.mp3`
- Durée : 24.02 s · F0 médian : 294.0 Hz
- Centre spectral : 4015.0 Hz · RMS : 0.189
- graves 0-300 : 13.2 %
- bas-medium 300-1000 : 27.0 %
- medium 1000-3000 : 15.9 %
- aigus 3000-8000 : 21.5 %

## Empreinte de la VO source

- Fichier : `assets/voix-off.mp3`
- Durée : 44.32 s · F0 médian : 203.2 Hz
- Centre spectral : 2324.0 Hz · RMS : 0.0999

## Sortie

`assets/voix-off-matched.mp3` — VO dont l'enveloppe
spectrale a été ramenée vers celle de la référence.

## État

Transfert appliqué. Écouter la sortie et comparer à la VO d'origine ; si le résultat est métallique, réduire l'amplitude du ratio dans le script.

Transfert appliqué aux **6 segments** → `assets/vo-matched/` ; les durées sont inchangées, `TIMING.md` et `subtitles.srt` restent valables.

Correction de hauteur : **×1.2** — plafonnée à 1.20 pour éviter un effet « voix de dessin animé ».
