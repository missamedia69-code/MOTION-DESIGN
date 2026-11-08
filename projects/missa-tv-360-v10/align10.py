# Aligne la voix fournie (entrees/Pub Missa TV.wav) sur la timeline d'origine de la composition
# (voix de référence calée phrase par phrase, .cache/audio10/vo-ref.wav) par DTW sur MFCC.
# Produit tmap.json : carte monotone temps_composition -> temps_audio_fourni (+ tenue finale).
# Usage (racine du dépôt) : python3 projects/missa-tv-360-v10/align10.py
import json, os, numpy as np, librosa
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = "entrees/Pub Missa TV.wav"
REF = ".cache/audio10/vo-ref.wav"
SPEECH_END_OLD = 55.4   # fin de « Télécharge maintenant ! » dans la timeline d'origine
HOLD = 2.6              # tenue finale du bouton après la fin de la voix (s)
sr, hop = 16000, 160
def feat(y):
    m = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=20, hop_length=hop)
    return (m - m.mean(1, keepdims=True)) / (m.std(1, keepdims=True) + 1e-6)
ref, _ = librosa.load(REF, sr=sr); new, _ = librosa.load(SRC, sr=sr)
_, wp = librosa.sequence.dtw(X=feat(ref), Y=feat(new), metric="cosine")
wp = wp[::-1]
to, tn = wp[:, 0] * hop / sr, wp[:, 1] * hop / sr
end_new = len(new) / sr
grid = np.round(np.arange(0, 60.001, 0.1), 2)
M = np.maximum.accumulate(np.interp(grid, to, tn))
tail = grid > SPEECH_END_OLD
M[tail] = end_new + (grid[tail] - SPEECH_END_OLD) * HOLD / (60 - SPEECH_END_OLD)
M[grid <= SPEECH_END_OLD] = np.minimum(M[grid <= SPEECH_END_OLD], end_new)
json.dump({"source": SRC, "duration": round(end_new + HOLD, 2), "old": grid.tolist(), "new": [round(float(x), 3) for x in M]},
          open(os.path.join(HERE, "tmap.json"), "w"))
print("tmap.json : durée", round(end_new + HOLD, 2), "s")
