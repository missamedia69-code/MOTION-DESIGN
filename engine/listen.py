"""Écoute de l'audio de la pub : ce qui est dit, et QUAND (au mot près).

Ordre de préférence :
  1. transcription locale faster-whisper (horodatage par mot, hors ligne une fois
     le modèle téléchargé ; modèle : MD_WHISPER_MODEL, défaut « base ») ;
  2. texte fourni (`script.txt`) calé sur les respirations de l'audio
     (intake.align_script), mots répartis au débit ;
  3. rien : seules les respirations et la durée sont connues.

Le résultat est mis en cache (.cache/transcriptions/<empreinte>.json).
Sortie : {"source", "language", "duration", "phrases": [{start, end, text, words:[{w, start, end}]}]}
"""
from __future__ import annotations

import hashlib
import json
import os
import re

from . import intake, probe

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(REPO, ".cache", "transcriptions")


def _key(path: str, extra: str = "") -> str:
    st = os.stat(path)
    return hashlib.sha1(f"{os.path.abspath(path)}|{st.st_size}|{st.st_mtime_ns}|{extra}".encode()).hexdigest()[:16]


def available() -> bool:
    if os.environ.get("MD_WHISPER", "1") == "0":     # désactivation explicite (tests, hors ligne)
        return False
    try:
        import faster_whisper  # noqa: F401
        return True
    except ImportError:
        return False


def _even_words(text: str, start: float, end: float) -> list[dict]:
    words = text.split()
    if not words:
        return []
    weights = [max(2, len(w)) for w in words]
    tot, acc, out = sum(weights), start, []
    for w, k in zip(words, weights):
        d = (end - start) * k / tot
        out.append({"w": w, "start": round(acc, 3), "end": round(acc + d, 3)})
        acc += d
    return out


def _group_phrases(words: list[dict], max_gap: float = 0.45, max_len: float = 6.5) -> list[dict]:
    """Regroupe les mots en phrases : ponctuation forte, silence, ou longueur."""
    phrases, cur = [], []
    for i, w in enumerate(words):
        cur.append(w)
        nxt = words[i + 1] if i + 1 < len(words) else None
        end_punct = re.search(r"[.!?…]$", w["w"])
        gap = (nxt["start"] - w["end"]) if nxt else 9
        too_long = cur[-1]["end"] - cur[0]["start"] > max_len and re.search(r"[,;:]$", w["w"])
        if not nxt or end_punct or gap > max_gap or too_long:
            phrases.append({"start": cur[0]["start"], "end": cur[-1]["end"],
                            "text": " ".join(x["w"] for x in cur).strip(), "words": cur})
            cur = []
    return phrases


def transcribe(audio: str, script: str | None = None, language: str = "fr",
               model: str | None = None, force: bool = False) -> dict:
    audio = os.path.abspath(audio)
    dur = float(probe.probe(audio).get("duration") or 0)
    model = model or os.environ.get("MD_WHISPER_MODEL", "base")
    os.makedirs(CACHE, exist_ok=True)
    cache = os.path.join(CACHE, _key(audio, f"{model}|{language}|{hashlib.sha1((script or '').encode()).hexdigest()[:8]}") + ".json")
    if os.path.isfile(cache) and not force:
        with open(cache, encoding="utf-8") as f:
            return json.load(f)

    result = None
    if script and script.strip():
        # Le texte fourni fait foi ; les mots sont calés au débit dans chaque phrase.
        phrases = intake.align_script(script, audio, dur)
        for p in phrases:
            p["words"] = _even_words(p["text"], p["start"], p["end"])
        result = {"source": "script.txt calé sur les respirations", "language": language,
                  "duration": dur, "phrases": phrases}
        if available():
            # Affinage : les débuts de phrase prennent l'horodatage réel du mot reconnu.
            try:
                heard = _whisper(audio, language, model)
                hw = [w for p in heard for w in p["words"]]
                if hw:
                    for p in result["phrases"]:
                        near = min(hw, key=lambda w: abs(w["start"] - p["start"]))
                        if abs(near["start"] - p["start"]) < 0.8:
                            shift = near["start"] - p["start"]
                            p["start"] = round(near["start"], 3)
                            p["words"] = [{**w, "start": round(w["start"] + shift, 3),
                                           "end": round(w["end"] + shift, 3)} for w in p["words"]]
                    result["source"] += " + reconnaissance vocale (faster-whisper)"
            except Exception as exc:  # noqa: BLE001
                result["note"] = f"reconnaissance indisponible : {exc}"
    elif available():
        try:
            result = {"source": f"reconnaissance vocale locale (faster-whisper {model})",
                      "language": language, "duration": dur,
                      "phrases": _whisper(audio, language, model)}
        except Exception as exc:  # noqa: BLE001
            result = {"source": "aucune", "language": language, "duration": dur, "phrases": [],
                      "note": f"transcription impossible : {exc}"}
    else:
        result = {"source": "aucune", "language": language, "duration": dur, "phrases": [],
                  "note": "ni script.txt ni faster-whisper (pip install faster-whisper)"}
    result["breaths"] = intake.breath_points(audio)
    with open(cache, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=1)
    return result


def _whisper(audio: str, language: str, model: str) -> list[dict]:
    from faster_whisper import WhisperModel

    m = WhisperModel(model, device="cpu", compute_type="int8")
    segs, _ = m.transcribe(audio, language=language, word_timestamps=True, vad_filter=True,
                           beam_size=5)
    words = []
    for s in segs:
        for w in (s.words or []):
            t = w.word.strip()
            if t:
                words.append({"w": t, "start": round(w.start, 3), "end": round(w.end, 3)})
    return _group_phrases(words)
