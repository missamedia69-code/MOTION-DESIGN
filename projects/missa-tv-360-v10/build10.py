# MISSA TV 360 v10 — construit les compositions 16:9 et 9:16, les sous-titres et la piste voix.
# Usage (depuis la racine du dépôt) :
#   python3 projects/missa-tv-360-v10/build10.py          # index.html (16:9) + projet 9:16 + .srt
#   python3 projects/missa-tv-360-v10/build10.py --vo     # + piste voix .cache/audio10/vo.wav (Kokoro, local)
import html, json, os, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
V916 = os.path.join(ROOT, "projects", "missa-tv-360-v10-9x16")

# Script voix off VALIDÉ (DA v2, section 0) — ne pas reformuler.
# start = instant de départ de la phrase dans le master 60 s (scènes calées dessus).
VO = [
    (0.4,  "Et si tout ton divertissement tenait dans une seule application ?", "Et si tout ton divertissement tenait dans une seule application ?"),
    (3.8,  "Voici Missa TV 360 !", "Voici Missa Tévé trois-cent-soixante !"),
    (6.2,  "Des milliers de films, des séries, des mangas, du sport, des documentaires et des centaines de chaînes en direct !",
           "Des milliers de films, des séries, des mangas, du sport, des documentaires et des centaines de chaînes en direct !"),
    (12.1, "Des radios du monde entier, des podcasts et toute ta musique préférée !", "Des radios du monde entier, des podcasts et toute ta musique préférée !"),
    (16.1, "Et le plus intéressant ? Même avec une connexion limitée, profite d'un streaming optimisé pour rester stable !",
           "Et le plus intéressant ? Même avec une connexion limitée, profite d'un streaming optimisé pour rester stable !"),
    (22.7, "Une simple box Wi-Fi, une connexion Internet… et tu accèdes à tout ton univers de divertissement !",
           "Une simple box oui-fi, une connexion Internet... et tu accèdes à tout ton univers de divertissement !"),
    (29.0, "Sur téléphone, tablette ou télévision !", "Sur téléphone, tablette ou télévision !"),
    (31.8, "Et ce n'est pas tout ! Après le téléchargement, profite de 24 heures entièrement gratuites pour tester l'application !",
           "Et ce n'est pas tout ! Après le téléchargement, profite de vingt-quatre heures entièrement gratuites pour tester l'application !"),
    (38.6, "Et ça coûte combien ?", "Et ça coûte combien ?"),
    (40.5, "Seulement mille francs CFA par mois ! Ou dix mille francs pour toute l'année !",
           "Seulement mille francs cé èf a par mois ! Ou dix mille francs pour toute l'année !"),
    (44.3, "Oui, toute une année, avec deux mois offerts !", "Oui, toute une année, avec deux mois offerts !"),
    (46.9, "Pourquoi chercher ailleurs ?", "Pourquoi chercher ailleurs ?"),
    (48.9, "Missa TV 360 ! Tout ton divertissement, une seule application, un petit prix !",
           "Missa Tévé trois-cent-soixante ! Tout ton divertissement, une seule application, un petit prix !"),
    (54.3, "Télécharge maintenant !", "Télécharge maintenant !"),
]

# Sous-titres incrustés : découpés sur les respirations de la voix ; chiffres en chiffres (règle DA).
NB = " "
SUBS = [
    (0.4, 3.45, "Et si tout ton divertissement tenait dans une seule application ?"),
    (3.8, 5.85, "Voici Missa TV 360 !"),
    (6.2, 9.0, "Des milliers de films, des séries, des mangas, du sport,"),
    (9.1, 11.75, "des documentaires et des centaines de chaînes en direct !"),
    (12.1, 15.55, "Des radios du monde entier, des podcasts et toute ta musique préférée !"),
    (16.1, 17.35, "Et le plus intéressant ?"),
    (17.45, 19.15, "Même avec une connexion limitée,"),
    (19.25, 22.35, "profite d'un streaming optimisé pour rester stable !"),
    (22.7, 25.9, "Une simple box Wi-Fi, une connexion Internet…"),
    (26.1, 28.6, "et tu accèdes à tout ton univers de divertissement !"),
    (29.0, 31.1, "Sur téléphone, tablette ou télévision !"),
    (31.8, 32.7, "Et ce n'est pas tout !"),
    (32.8, 34.1, "Après le téléchargement,"),
    (34.2, 37.95, f"profite de 24{NB}heures entièrement gratuites pour tester l'application !"),
    (38.6, 39.9, "Et ça coûte combien ?"),
    (40.5, 42.45, f"Seulement 1{NB}000{NB}francs CFA par mois !"),
    (42.55, 44.05, f"Ou 10{NB}000{NB}francs pour toute l'année !"),
    (44.3, 46.4, "Oui, toute une année, avec deux mois offerts !"),
    (46.9, 48.2, "Pourquoi chercher ailleurs ?"),
    (48.9, 50.45, "Missa TV 360 !"),
    (50.55, 53.75, "Tout ton divertissement, une seule application, un petit prix !"),
    (54.3, 56.6, "Télécharge maintenant !"),
]


# Carte de temps vers l'audio fourni (align10.py) : toute la timeline est recalée sur la voix fournie.
_TM = json.load(open(os.path.join(HERE, "tmap.json"))) if os.path.exists(os.path.join(HERE, "tmap.json")) else None
END = _TM["duration"] if _TM else 60.0


def M(t):
    if not _TM:
        return t
    import bisect
    o, n = _TM["old"], _TM["new"]
    i = min(max(bisect.bisect_right(o, t) - 1, 0), len(o) - 2)
    return round(n[i] + (n[i + 1] - n[i]) * (t - o[i]) / (o[i + 1] - o[i]), 3)


def subs_t():
    return [(M(a), M(b), t) for a, b, t in SUBS]


def remap_clips(src):
    import re
    def f(m):
        a, d = float(m.group(1)), float(m.group(2))
        if a == 0 and d == 60:
            return f'data-start="0" data-duration="{END}"'
        na = M(a)
        return f'data-start="{na}" data-duration="{round(M(a + d) - na, 3)}"'
    return re.sub(r'data-start="([\d.]+)" data-duration="([\d.]+)"', f, src)


def subs_html():
    out = []
    for i, (a, b, t) in enumerate(subs_t()):
        out.append(f'<div id="sub{i}" class="sub clip" data-start="{a}" data-duration="{round(b - a, 2)}" data-track-index="{20 + i % 2}"><span>{html.escape(t)}</span></div>')
    return "\n      ".join(out)


def srt():
    def ts(x):
        ms = int(round(x * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
    return "\n".join(f"{i + 1}\n{ts(a)} --> {ts(b)}\n{t.replace(NB, ' ')}\n" for i, (a, b, t) in enumerate(subs_t()))


def build():
    src = remap_clips(open(os.path.join(HERE, "composition.tpl"), encoding="utf-8").read())
    tm = json.dumps({"old": _TM["old"], "new": _TM["new"]}) if _TM else "null"
    src = src.replace("__SUBS__", subs_html()).replace("__TMAP__", tm)
    with open(os.path.join(HERE, "index.html"), "w", encoding="utf-8") as f:
        f.write(src.replace("__FMT__", "h").replace("__W__", "1920").replace("__H__", "1080"))
    os.makedirs(V916, exist_ok=True)
    for d in ("assets", "vendor"):
        shutil.copytree(os.path.join(HERE, d), os.path.join(V916, d), dirs_exist_ok=True)
    for fn in ("hyperframes.json", "package.json", "meta.json"):
        if os.path.exists(os.path.join(HERE, fn)):
            shutil.copy(os.path.join(HERE, fn), os.path.join(V916, fn))
    with open(os.path.join(V916, "index.html"), "w", encoding="utf-8") as f:
        f.write(src.replace("__FMT__", "v").replace("__W__", "1080").replace("__H__", "1920"))
    with open(os.path.join(HERE, "missa-tv-360-v10.srt"), "w", encoding="utf-8") as f:
        f.write(srt())
    print("index.html 16:9 + 9:16 + .srt OK")


def voice():
    """Voix off locale (Kokoro ONNX, voix ff_siwis). Modèle : github.com/thewh1teagle/kokoro-onnx (releases)."""
    import numpy as np, soundfile as sf
    from kokoro_onnx import Kokoro
    mdir = os.environ.get("KOKORO_DIR", "/root/kokoro")
    k = Kokoro(os.path.join(mdir, "kokoro-v1.0.onnx"), os.path.join(mdir, "voices-v1.0.bin"))
    sr = 24000
    track = np.zeros(int(60 * sr))
    meta = []
    for i, (start, text, say) in enumerate(VO):
        s, sr = k.create(say, voice="ff_siwis", speed=1.12, lang="fr-fr")
        idx = np.where(np.abs(s) > 0.01)[0]
        s = s[max(0, idx[0] - int(0.02 * sr)): idx[-1] + int(0.06 * sr)]
        i0 = int(start * sr); i1 = min(len(track), i0 + len(s))
        track[i0:i1] += s[: i1 - i0]
        nxt = VO[i + 1][0] if i + 1 < len(VO) else 60
        meta.append({"start": start, "end": round(start + len(s) / sr, 2), "text": text})
        assert start + len(s) / sr <= nxt, f"phrase {i + 1} déborde sur la suivante"
    os.makedirs(os.path.join(ROOT, ".cache/audio10"), exist_ok=True)
    sf.write(os.path.join(ROOT, ".cache/audio10/vo.wav"), track, sr)
    with open(os.path.join(HERE, "vo.json"), "w", encoding="utf-8") as f:
        json.dump({"backend": "kokoro-onnx", "voice": "ff_siwis", "speed": 1.12, "lines": meta}, f, ensure_ascii=False, indent=1)
    print("vo.wav OK")


if __name__ == "__main__":
    build()
    if "--vo" in sys.argv:
        voice()
