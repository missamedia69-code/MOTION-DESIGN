# MISSA TV 360 — publicité 3D
Projet indépendant, synchronisé sur le WAV fourni (33,404 secondes).

- Master : 9:16, 1080×1920, 30 i/s.
- Audio : voix originale conservée ; SFX ajoutés et exportés en pistes séparées.
- Animation : Three.js r160/WebGL pour les géométries 3D, GSAP pour les trajectoires et la synchronisation.
- Éléments : logo 3D transparent, QR, vignettes fictives et objets 3D sous licence MIT, avec leurs notices.

## Rebuild
Depuis ce dossier avec Node 22, Python 3.11 et FFmpeg :
```bash
npm install
cp node_modules/three/build/three.min.js vendor/three.min.js
python -m pip install numpy==1.26.4 librosa==0.10.2.post1 soundfile==0.12.1
python tools/build.py
python sfx/generate.py
python tools/mix.py
npx --yes hyperframes@0.8.142 browser ensure
npx --yes hyperframes@0.8.142 check
npx --yes hyperframes@0.8.142 render --fps 30 --quality delivery --output ../../sortie/video-sans-audio.mp4
```
Le workflow GitHub Actions produit le MP4 final avec audio, la déclinaison 720p, le SRT, les pistes WAV, la couverture et la planche contact dans `sortie/`.
