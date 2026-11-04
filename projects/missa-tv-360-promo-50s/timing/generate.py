#!/usr/bin/env python3
"""Recale la timeline 50 s sur la VO réellement générée.

Mesure les 6 segments MP3 **après** rognage des silences TTS
(`trim_silence.py`), répartit les respirations (silences visuels) pour atteindre
exactement 50 s sans accélérer ni ralentir la voix, puis écrit :
  - `TIMING.md` : tableau de production
  - `subtitles.srt` : les 20 sous-titres recalés sur les durées mesurées

    python3 projects/missa-tv-360-promo-50s/timing/trim_silence.py
    python3 projects/missa-tv-360-promo-50s/timing/generate.py
"""
from __future__ import annotations

from pathlib import Path

import av

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
VO_DIR = PROJECT / "assets" / "vo"

# id, titre, début prévu, fin prévue, nombre de sous-titres
PLAN = [
    ("01", "Accroche « En Afrique »", 0.0, 5.0, 3),
    ("02", "Mosaïque des 10 univers", 5.0, 20.0, 6),
    ("03", "Faible débit / données", 20.0, 28.0, 3),
    ("04", "Essai 24 h", 28.0, 34.0, 2),
    ("05", "Prix + activation", 34.0, 44.0, 4),
    ("06", "Signature", 44.0, 50.0, 2),
]

CUES = [
    "En Afrique, on paie…",
    "et on n'a rien à regarder.",
    "MISSA TV 360 change ça.",
    "Avec votre box WiFi ou votre connexion,",
    "tapez un film, une série, un manga :",
    "une recherche, et c'est là.",
    "Chaînes télé, radio, lives, sport,",
    "documentaires, enfants, jeux vidéo —",
    "tout dans la même appli.",
    "Et même avec un faible débit,",
    "ça reste stable. Pas de coupures,",
    "et l'appli économise vos données.",
    "Vingt-quatre heures pour tout essayer.",
    "Gratuitement. Ouvrez, cherchez, regardez.",
    "Après, prenez votre code.",
    "Un mois, deux, trois, comme vous voulez —",
    "ou l'année à dix mille francs.",
    "Scannez, saisissez, c'est reparti.",
    "MISSA TV 360. Activez votre code.",
    "Et ne ratez plus rien.",
]


def duration(path: Path) -> float:
    with av.open(str(path)) as container:
        return round(float(container.duration) / av.time_base, 2)


def stamp(t: float) -> str:
    h = int(t // 3600)
    m = int(t % 3600 // 60)
    s = int(t % 60)
    ms = int(round((t - int(t)) * 1000))
    if ms == 1000:
        s, ms = s + 1, 0
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def main() -> None:
    rows = []
    cursor = 0.0
    for sid, title, planned_start, planned_end, n_cues in PLAN:
        vo_dur = duration(VO_DIR / f"seq-{sid}.mp3")
        start = max(planned_start, cursor)
        vo_end = start + vo_dur
        end = max(planned_end, vo_end)
        rows.append({"id": sid, "title": title, "start": round(start, 2),
                     "vo_dur": vo_dur, "vo_end": round(vo_end, 2),
                     "hold": round(end - vo_end, 2), "end": round(end, 2),
                     "n_cues": n_cues})
        cursor = end

    continuous = duration(PROJECT / "assets" / "voix-off.mp3")
    lines = [
        "# Timeline de production — 50 s · 9:16",
        "",
        "> Généré par `timing/generate.py` à partir des **durées réelles** des 6",
        "> segments VO (`assets/vo/seq-*.mp3`). La voix n'est ni accélérée ni",
        "> ralentie : les respirations sont des silences visuels occupés par les",
        "> animations, les SFX et les mains sur les plans.",
        "",
        f"**VO totale : {sum(r['vo_dur'] for r in rows):.2f} s** · "
        f"**respirations : {sum(r['hold'] for r in rows):.2f} s** · "
        f"**durée finale : {rows[-1]['end']:.2f} s**",
        "",
        "| Ség. | Séquence | Début | VO (durée) | Fin VO | Respiration | Fin |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        lines.append(
            f"| {r['id']} | {r['title']} | {r['start']:.2f} s | "
            f"{r['vo_dur']:.2f} s | {r['vo_end']:.2f} s | "
            f"{r['hold']:.2f} s | {r['end']:.2f} s |")
    lines += [
        "",
        "## Sous-titres",
        "",
        "`subtitles.srt` contient les 20 repères, redistribués dans chaque segment",
        "au prorata de la longueur du texte. Les respirations ne portent aucun",
        "sous-titre. Si la VO est réenregistrée, relancer ce script suffit à tout",
        "recaler.",
        "",
        "## Piste audio",
        "",
        "Poser `seq-01…06.mp3` aux instants `Début` du tableau ; mixer les 10 SFX",
        "de `sfx/wav/` selon `SCRIPT.md`.",
        "",
        f"`assets/voix-off.mp3` est la prise continue de référence ({continuous:.2f} s),",
        "conservée pour écouter le timbre : elle n'est **pas** utilisée au montage,",
        "car elle ne permet pas de placer les respirations aux bons endroits.",
        "Les segments bruts (avant rognage des silences TTS) restent dans",
        "`assets/vo/raw/` ; `trim_silence.py` régénère les versions propres.",
        "",
    ]
    (PROJECT / "TIMING.md").write_text("\n".join(lines), encoding="utf-8")

    srt = []
    idx = 0
    cue_i = 0
    for r in rows:
        texts = CUES[cue_i:cue_i + r["n_cues"]]
        cue_i += r["n_cues"]
        weights = [len(t) for t in texts]
        total = sum(weights)
        cumul = 0
        for text, w in zip(texts, weights):
            idx += 1
            t0 = r["start"] + r["vo_dur"] * cumul / total
            cumul += w
            t1 = r["start"] + r["vo_dur"] * cumul / total
            srt += [str(idx), f"{stamp(t0)} --> {stamp(t1)}", text, ""]
    (PROJECT / "subtitles.srt").write_text("\n".join(srt), encoding="utf-8")
    print(f"✅ TIMING.md · sous-titres {idx} · VO {sum(r['vo_dur'] for r in rows):.2f} s"
          f" · respirations {sum(r['hold'] for r in rows):.2f} s"
          f" · total {rows[-1]['end']:.2f} s")


if __name__ == "__main__":
    main()
