#!/usr/bin/env python3
"""Minutage PROVISOIRE à partir de onsets.py --no-whisper.

Le vrai minutage mot à mot viendra de mots.py/Whisper sur la voix définitive
`assets/audio/voix.mp3` (modèle non téléchargeable dans ce sandbox). En attendant,
on répartit DÉTERMINISTEMENT les mots de CHAQUE SÉQUENCE (tableau G.2 validé)
sur les phrases détectées par l'énergie À L'INTÉRIEUR DE CETTE SÉQUENCE.
Les mots restent donc dans la bonne séquence, ce qui rend le WIP lisible.

Produit : onsets.json, sous-titres.srt, TIMING-PROVISOIRE.md
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = json.loads((ROOT / "onsets-temporaire.json").read_text())
SCRIPT = (ROOT / "SCRIPT.md").read_text()
phrases = SRC["phrases"]

# --- 1. séquences recalées (somme = 59,00 s) -------------------------------
S = [
    ("F01", "accroche-ticket", 0.00, 4.00), ("F02", "gag-telecommande", 4.00, 6.52),
    ("F03", "memes-chaines-series", 6.52, 11.07), ("F04", "pubs-argent", 11.07, 14.48),
    ("F05", "pivot-noir", 14.48, 16.53), ("F06", "revelation-logo", 16.53, 22.11),
    ("F07", "films-series-docs-mangas", 22.11, 27.80), ("F08", "chaines-direct", 27.80, 34.55),
    ("F09", "podcasts-radios-musique", 34.55, 40.62), ("F10", "une-seule-application", 40.62, 43.07),
    ("F11", "prix-mensuel", 43.07, 48.38), ("F12", "prix-annuel", 48.38, 55.16),
    ("F13", "appel-a-l-action", 55.16, 59.00),
]

# --- 2. texte VO de chaque séquence (tableau G.2 de SCRIPT.md) -------------
vo = []
for line in SCRIPT.splitlines():
    if not line.startswith("| `["):
        continue
    cell = line.strip().strip("|").split("|")[-1]
    chunks = re.findall(r"«(.*?)»", cell)
    txt = " ".join(chunks)
    txt = re.sub(r"\*+", "", txt)
    txt = re.sub(r"\s+", " ", txt).strip()
    vo.append(txt)
assert len(vo) == len(S), f"G.2 : {len(vo)} lignes pour {len(S)} séquences"

def tokens(text):
    out = []
    for w in text.split():
        if re.fullmatch(r"[^\wÀ-ÿ]+", w) and out:
            out[-1] += w
        else:
            out.append(w)
    return out

def allocate(words, group):
    """Répartit `words` sur les phrases de `group` au prorata de leur durée."""
    if not group or not words:
        return {i: [] for i in group}
    spans = [max(0.05, phrases[i]["end"] - phrases[i]["start"]) for i in group]
    tot = sum(spans)
    raw = [len(words) * s / tot for s in spans]
    counts = [int(x) for x in raw]
    reste = len(words) - sum(counts)
    for k in sorted(range(len(group)), key=lambda k: raw[k] - counts[k], reverse=True)[:reste]:
        counts[k] += 1
    res, idx = {}, 0
    for i, n in zip(group, counts):
        res[i] = words[idx:idx + n]
        idx += n
    return res

# --- 3..On attribue chaque phrase à sa séquence ---------------------------
assign = {}
for si, (fid, name, a, b) in enumerate(S):
    group = [i for i, p in enumerate(phrases) if a <= p["start"] < b]
    assign.update(allocate(tokens(vo[si]), group))

# --- 4. onsets.json --------------------------------------------------------
out_phrases, out_words = [], []
for i, p in enumerate(phrases):
    chunk = assign.get(i, [])
    if not chunk:
        out_phrases.append({**p, "text": "", "words": []})
        continue
    wts = [min(14, max(2, len(re.sub(r"[^\wÀ-ÿ]", "", w)) + 1)) for w in chunk]
    tw = sum(wts)
    ws, cur = [], p["start"]
    for k, (w, wt) in enumerate(zip(chunk, wts)):
        e = p["end"] if k == len(chunk) - 1 else cur + (p["end"] - p["start"]) * wt / tw
        item = {"w": w, "s": round(cur, 3), "e": round(min(e, p["end"]), 3)}
        ws.append(item)
        out_words.append(item)
        cur = e
    out_phrases.append({**p, "text": " ".join(chunk), "words": ws, "frame": next(
        (f for f, _, a, b in S if a <= p["start"] < b), "F13")})

data = {
    "audio": "assets/audio/voix-temporaire.mp3",
    "duration": SRC["duration"],
    "provisional": True,
    "method": "onsets.py --no-whisper + répartition déterministe PAR SÉQUENCE (G.2) ; Whisper indisponible",
    "replace_with": "assets/audio/voix.mp3 + mots.py + onsets.py --transcript",
    "stats": SRC["stats"],
    "phrases": out_phrases,
    "words": out_words,
}
(ROOT / "onsets.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")

# --- 5. sous-titres.srt -----------------------------------------------------
def ts(t):
    h = int(t // 3600); m = int(t // 60) % 60; s = t % 60
    return f"{h:02d}:{m:02d}:{s:06.3f}".replace(".", ",")

lines, k = [], 0
for p in out_phrases:
    if not p["text"]:
        continue
    k += 1
    lines += [str(k), f"{ts(p['start'])} --> {ts(p['end'])}", p["text"], ""]
(ROOT / "sous-titres.srt").write_text("\n".join(lines))

# --- 6. tableau de recalage -------------------------------------------------
cuts = [p["cut_point"] for p in phrases if p.get("cut_point")]
def snap(t):
    return min(cuts, key=lambda c: abs(c - t)) if cuts else t

rec = ["# TIMING PROVISOIRE — 13 séquences recalées sur les silences de la VO de travail",
       "",
       "> `onsets.json` est **provisoire** : mots répartis par séquence, pas transcrits.",
       "> À refaire sur `assets/audio/voix.mp3` avec `mots.py` + `onsets.py --transcript`.",
       "", "| Id | Cible CDC | Point de coupe | Début | Fin | Durée | Mots VO |",
       "|---|---|---|---|---|---|---|"]
prev = 0.0
for i, (fid, name, a, b) in enumerate(S):
    end = 59.0 if i == len(S) - 1 else snap(b)
    n = sum(len(assign.get(k, [])) for k, p in enumerate(phrases) if a <= p["start"] < b)
    rec.append(f"| {fid} | {a:.1f} → {b:.1f} | {end if i < len(S)-1 else 'fin 59,0'} | "
               f"{prev:.2f} | {end:.2f} | {end-prev:.2f} s | {n} |")
    prev = end
rec += ["", f"- VO de travail : **{SRC['duration']:.2f} s** pour une cible de **59,00 s** "
        f"(écart {SRC['duration']-59:+.2f} s résorbé par coupe dans un silence).",
        f"- {len(phrases)} phrases détectées, {len(out_words)} mots minutés, {k} cues SRT.",
        "- Silences > 0,4 s repérés par `onsets.py` : autant de plans avec leur propre action."]
(ROOT / "TIMING-PROVISOIRE.md").write_text("\n".join(rec) + "\n")

# --- 7. coupes réelles partagées avec le générateur et l'audio --------------
# wip_build.py et wip_audio.py importent ce module : une seule source de vérité
# pour les 13 fenêtres, afin que sous-titres, images et SFX ne se décalent pas.
cl = ["# GÉNÉRÉ par tools/timing-provisoire.py — ne pas éditer à la main.",
      "# Fenêtres réelles des 13 séquences, calées sur les silences de la VO.",
      "S = ["]
prev = 0.0
for i, (fid, name, a, b) in enumerate(S):
    end = 59.0 if i == len(S) - 1 else snap(b)
    cl.append(f'    ("{fid}", {prev:.2f}, {end:.2f}),')
    prev = end
cl.append("]")
(ROOT / "render" / "wip_cuts.py").write_text("\n".join(cl) + "\n")

print(f"✅ {len(out_words)} mots · {len(out_phrases)} phrases · {k} cues SRT · 13 séquences")
for fid, _, a, b in S:
    n = sum(len(assign.get(k, [])) for k, p in enumerate(phrases) if a <= p["start"] < b)
    print(f"   {fid} {a:5.2f}-{b:5.2f} : {n:2d} mots")
