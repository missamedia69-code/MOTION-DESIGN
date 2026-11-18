# Mixage : voix fournie (avec sa musique) INCHANGÉE + bruitages discrets calés sur l'animation.
# Sortie : rendu/audio-mix.wav (48 kHz stéréo) + pistes séparées voix / bruitages.
import os, numpy as np, soundfile as sf, librosa
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR = 48000
voice, _ = librosa.load(os.path.join(HERE, "assets/voix.wav"), sr=SR, mono=True)
N = len(voice)
fx = np.zeros(N)
def load(n): y, _ = librosa.load(os.path.join(HERE, "sfx/wav", n + ".wav"), sr=SR, mono=True); return y
def put(n, t, g):
    y = load(n) * g; i = int(t * SR); j = min(N, i + len(y))
    if i < N: fx[i:j] += y[: j - i]
db = lambda d: 10 ** (d / 20)
for t in [2.78, 3.90, 8.30, 13.58, 16.12, 20.42, 22.66, 24.92, 29.32]: put("whoosh", t, db(-14))
put("impact", 2.95, db(-12)); put("impact", 3.50, db(-10))
for t in [0.02, 0.70, 1.40, 4.55, 4.70, 5.05, 5.20, 5.40, 7.30, 8.87, 9.07, 9.36, 10.43, 11.52, 11.82, 13.02,
          15.48, 15.83, 20.61, 21.25, 21.85, 23.63, 25.59, 27.22, 27.42, 28.32, 30.80, 31.94]: put("pop", t, db(-15))
for t in [0.37, 1.08, 1.59]: put("click", t, db(-12))
put("beep", 2.06, db(-22))
for i in range(12): put("key", 14.66 + 0.74 * i / 11, db(-16))
for k in range(7): put("tick", 23.30 + 0.24 * k, db(-18))
put("chime", 22.85, db(-14)); put("chime", 28.55, db(-14))
put("riser", 28.70, db(-16)); put("final_impact", 29.50, db(-11))
mix = voice + fx
peak = np.abs(mix).max()
if peak > 0.98: mix *= 0.98 / peak
os.makedirs(os.path.join(HERE, "rendu"), exist_ok=True)
st = lambda x: np.stack([x, x], 1)
sf.write(os.path.join(HERE, "rendu/audio-mix.wav"), st(mix), SR, subtype="PCM_24")
sf.write(os.path.join(HERE, "rendu/piste-voix.wav"), st(voice), SR, subtype="PCM_24")
sf.write(os.path.join(HERE, "rendu/piste-bruitages.wav"), st(fx), SR, subtype="PCM_24")
print("mix ok", round(N / SR, 3), "s, crête", round(float(peak), 3))
