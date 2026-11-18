# Calage mot à mot de la voix fournie (assets/voix.wav) sur le texte (script.txt)
# sans modèle de reconnaissance : voix de référence espeak-ng (mot par mot, horodatée)
# puis DTW sur MFCC entre la référence et la voix fournie. Produit words.json.
import json, os, re, subprocess, tempfile, numpy as np, librosa, soundfile as sf
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR, HOP = 16000, 160
lines = [l.strip() for l in open(os.path.join(HERE, "script.txt"), encoding="utf-8") if l.strip()]
def tts(text):
    with tempfile.NamedTemporaryFile(suffix=".wav") as f:
        subprocess.run(["espeak-ng", "-v", "fr", "-s", "190", "-w", f.name, text], check=True)
        y, sr = sf.read(f.name); y = librosa.resample(y.astype(float), orig_sr=sr, target_sr=SR)
    # retire les silences de bord
    yt, _ = librosa.effects.trim(y, top_db=35); return yt
spoken = lambda w: w.replace("MISSA", "Missa").replace("TV", "Télé").replace("360", "trois cent soixante")
ref, words, t = [], [], 0.0
for li, line in enumerate(lines):
    for w in line.split():
        core = re.sub(r"[^\wÀ-ÿ'’-]", "", w)
        if not core:
            if words: words[-1]["w"] += " " + w
            continue
        y = tts(spoken(core)); ref.append(y)
        words.append({"line": li, "w": w, "rs": t, "re": t + len(y) / SR}); t += len(y) / SR
        ref.append(np.zeros(int(0.03 * SR))); t += 0.03
    ref.append(np.zeros(int(0.25 * SR))); t += 0.25
ref = np.concatenate(ref)
new, _ = librosa.load(os.path.join(HERE, "assets/voix.wav"), sr=SR)
def feat(y):
    m = librosa.feature.mfcc(y=y, sr=SR, n_mfcc=20, hop_length=HOP)[1:]
    return (m - m.mean(1, keepdims=True)) / (m.std(1, keepdims=True) + 1e-6)
_, wp = librosa.sequence.dtw(X=feat(ref), Y=feat(new), metric="cosine")
wp = wp[::-1]; tr, tn = wp[:, 0] * HOP / SR, wp[:, 1] * HOP / SR
mp = lambda x: float(np.interp(x, tr, tn))
for w in words:
    w["s"], w["e"] = round(mp(w["rs"]), 3), round(mp(w["re"]), 3); del w["rs"], w["re"]
out = {"duration": round(len(new) / SR, 3), "lines": [], "words": words}
for li, line in enumerate(lines):
    ws = [w for w in words if w["line"] == li]
    out["lines"].append({"text": line, "s": ws[0]["s"], "e": ws[-1]["e"]})
json.dump(out, open(os.path.join(HERE, "words.json"), "w"), ensure_ascii=False, indent=1)
for l in out["lines"]: print(f'{l["s"]:6.2f}-{l["e"]:6.2f}  {l["text"]}')

# Recalage : chaque début de phrase est accroché à la fin de respiration la plus proche (≤ 0,45 s)
import subprocess as sp
log = sp.run(["ffmpeg", "-hide_banner", "-i", os.path.join(HERE, "assets/voix.wav"), "-af",
              "highpass=f=200,lowpass=f=4000,silencedetect=noise=-30dB:d=0.08", "-f", "null", "-"],
             capture_output=True, text=True).stderr
ends = [float(x) for x in re.findall(r"silence_end: ([0-9.]+)", log)]
for li, L in enumerate(out["lines"]):
    if li == 0: continue
    ws = [w for w in words if w["line"] == li]
    near = min(ends, key=lambda e: abs(e - L["s"]))
    if abs(near - L["s"]) <= 0.45 and near < ws[-1]["e"] - 0.3:
        a0, b = L["s"], ws[-1]["e"]; k = (b - near) / (b - a0)
        for w in ws:
            w["s"] = round(near + (w["s"] - a0) * k, 3); w["e"] = round(near + (w["e"] - a0) * k, 3)
        L["s"] = ws[0]["s"]
json.dump(out, open(os.path.join(HERE, "words.json"), "w"), ensure_ascii=False, indent=1)
print("--- après recalage")
for l in out["lines"]: print(f'{l["s"]:6.2f}-{l["e"]:6.2f}  {l["text"][:40]}')
