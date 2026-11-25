"""Vérification de la VIDÉO RENDUE (l'« œil » du moteur).

Le contrôle `lint` juge le project.json avant le rendu ; ce module juge l'image
finale, comme le ferait un directeur artistique : il appelle `look.py` (skill
motionmaxxing, Apache-2.0, ~4 300 mouvements mesurés sur des films pros) puis
traduit ses mesures en verdicts lisibles et en corrections concrètes.

Contrôles :
  G0  la vidéo existe, se décode, bouge, a la bonne durée (et du son si attendu)
  G2  pas d'image vide (plus de 3 images unies d'affilée)
  G3  carton de fin court (image figée finale ≤ 1,4 s, dernier plan ≤ 25 % du film)
  + énergie du mouvement comparée aux films pros (médiane 6,8 ; IQR 4,4–9,8)
  + passages figés (image inchangée ≥ 0,6 s) et absence de coupes franches
  + volume (LUFS, crête) quand il y a du son

Sorties : un dict (verdict, gates, remarques, chemins de la planche contact).
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOOK = os.path.join(REPO, ".agents", "skills", "motionmaxxing", "scripts", "look.py")

HUMAN_BAND = (4.4, 9.8)       # énergie du mouvement des films pros (IQR)
MAX_STILL = 1.0               # au-delà, un passage figé est signalé (secondes)


def _parse_still(report: str) -> list[tuple[float, float]]:
    m = re.search(r"^still\s+(.*)$", report, re.M)
    if not m or "none" in m.group(1):
        return []
    out = []
    for a, b in re.findall(r"([\d.]+)-([\d.]+)s", m.group(1)):
        out.append((float(a), float(b)))
    return out


def _parse_cuts(report: str) -> int:
    m = re.search(r"^cuts\s+(\d+)", report, re.M)
    return int(m.group(1)) if m else 0


def verify(video: str, out_dir: str | None = None, expect: float | None = None,
           expect_audio: bool = False) -> dict:
    """Analyse une vidéo rendue. Retourne un rapport (verdict OK / À CORRIGER)."""
    if not os.path.isfile(video):
        raise SystemExit(f"ERREUR : vidéo introuvable : {video}")
    if not os.path.isfile(LOOK):
        raise SystemExit("ERREUR : look.py absent (skill motionmaxxing non installé : "
                         ".agents/skills/motionmaxxing/scripts/look.py)")
    stem = os.path.splitext(os.path.basename(video))[0]
    out_dir = out_dir or os.path.join(REPO, ".cache", "verifications", stem)
    os.makedirs(out_dir, exist_ok=True)
    cmd = [sys.executable, LOOK, video, "--out", out_dir]
    if expect:
        cmd += ["--expect", f"{float(expect):.3f}"]
    if expect_audio:
        cmd += ["--expect-audio"]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    report = proc.stdout + proc.stderr
    if proc.returncode not in (0, 3):
        raise SystemExit(f"ERREUR : analyse impossible ({proc.returncode})\n{report[-1500:]}")
    try:
        with open(os.path.join(out_dir, "gates.json"), encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        data = {"gates": []}

    gates = [{"id": g["id"], "nom": g["name"], "statut": g["status"], "détail": g["detail"]}
             for g in data.get("gates", [])]
    remarks: list[dict] = []

    def add(level: str, msg: str, fix: str):
        remarks.append({"niveau": level, "message": msg, "correction": fix})

    for g in gates:
        if g["statut"] == "FAIL":
            add("erreur", f"{g['id']} {g['nom']} : {g['détail']}", {
                "G0": "vérifier la durée attendue, le son et que l'image bouge",
                "G2": "remplir les images vides (fond vivant, coupe plus tôt)",
                "G3": "raccourcir le carton de fin (≤ 1,4 s immobile) ou le dernier plan",
            }.get(g["id"], "corriger avant livraison"))

    energy = data.get("motion_mean_luma_diff")
    if isinstance(energy, (int, float)):
        lo, hi = HUMAN_BAND
        if energy < lo:
            add("alerte", f"image trop calme : énergie du mouvement {energy:.1f} "
                          f"(films pros : {lo}–{hi}, médiane 6,8)",
                "ajouter une caméra par scène (\"camera\": \"push_in\"), des entrées "
                "land/whip/mask, des coupes franches (\"cut\"), un fond qui vit")
        elif energy > hi * 1.6:
            add("alerte", f"image très agitée : énergie {energy:.1f} (films pros : {lo}–{hi})",
                "laisser respirer : un seul point focal en mouvement à la fois")

    stills = [(a, b) for a, b in _parse_still(report) if b - a >= MAX_STILL]
    if stills:
        spans = ", ".join(f"{a:.1f}–{b:.1f} s" for a, b in stills[:6])
        add("alerte", f"{len(stills)} passage(s) figé(s) ≥ {MAX_STILL:g} s : {spans}",
            "aucune image morte : une chose vivante par plan (idle drift/float, caméra)")

    cuts = _parse_cuts(report)
    dur = float(data.get("duration") or 0)
    if dur >= 6 and cuts == 0:
        add("info", "aucune coupe franche détectée : uniquement des fondus/glissés",
            "les pros coupent en plein mouvement : \"transitions\": {\"type\": \"cut\"}")

    loud = data.get("loudness") or {}
    if isinstance(loud, dict) and loud.get("integrated_lufs") is not None:
        lufs = float(loud["integrated_lufs"])
        if abs(lufs + 14) > 2.5:
            add("alerte", f"volume intégré {lufs:.1f} LUFS (cible réseaux sociaux : -14)",
                "exporter en mp4-social (normalisation -14 LUFS)")
        tp = loud.get("true_peak_dbfs")
        if tp is not None and float(tp) > -1:
            add("alerte", f"crête {float(tp):.1f} dBTP (> -1 : risque de saturation)",
                "baisser le gain ou activer la normalisation")

    verdict = "À CORRIGER" if any(r["niveau"] == "erreur" for r in remarks) else (
        "À AMÉLIORER" if any(r["niveau"] == "alerte" for r in remarks) else "OK")
    files = {k: os.path.join(out_dir, f) for k, f in
             (("planche", "sheet.jpg"), ("avant_coupes", "mid.jpg"), ("coupes", "strips.jpg"))
             if os.path.isfile(os.path.join(out_dir, f))}
    return {"video": os.path.relpath(video, REPO) if video.startswith(REPO) else video,
            "verdict": verdict, "duree": dur, "coupes": cuts,
            "energie_mouvement": energy, "bande_pros": list(HUMAN_BAND),
            "gates": gates, "remarques": remarks, "fichiers": files,
            "rapport_brut": report.strip()}


def print_report(r: dict) -> None:
    icon = {"OK": "✅", "À AMÉLIORER": "🟡", "À CORRIGER": "❌"}[r["verdict"]]
    print(f"── Vérification · {r['video']} · {r['duree']:.2f} s · {r['coupes']} coupe(s) ──")
    for g in r["gates"]:
        mark = "✅" if g["statut"] == "PASS" else ("❌" if g["statut"] == "FAIL" else "ℹ")
        print(f"  {mark} {g['id']} {g['nom']} : {g['détail']}")
    if r["energie_mouvement"] is not None:
        lo, hi = r["bande_pros"]
        print(f"  ℹ énergie du mouvement : {r['energie_mouvement']:.1f} (films pros {lo}–{hi})")
    for rem in r["remarques"]:
        mark = {"erreur": "❌", "alerte": "⚠", "info": "ℹ"}[rem["niveau"]]
        print(f"  {mark} {rem['message']}\n      → {rem['correction']}")
    if r["fichiers"].get("planche"):
        print(f"  🖼  planche : {os.path.relpath(r['fichiers']['planche'], REPO)}")
    print(f"{icon} {r['verdict']}")
