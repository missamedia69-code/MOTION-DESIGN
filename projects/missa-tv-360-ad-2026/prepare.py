#!/usr/bin/env python3
"""Read the supplied audio, align the French VO, compose scenes and place SFX."""
from pathlib import Path
import json
from engine import ads, intake, probe, render

ROOT=Path(__file__).resolve().parent
AUDIO="entrees/Pub Missa TV.wav"
LOGO="entrees/Missa_TV_360_logo_1x1.png"
BANNER="entrees/Missa TV 360+ Entertainment Banner.png"

def main():
 for path in (AUDIO,LOGO,BANNER):
  if not Path(path).is_file(): raise SystemExit(f"Élément source manquant : {path}")
 info=probe.probe(AUDIO); duration=float(info.get("duration") or 0)
 if duration<=0: raise SystemExit("Impossible de lire la durée du WAV.")
 script=(ROOT/"script.txt").read_text(encoding="utf-8")
 breaths=intake.breath_points(AUDIO)
 aligned=intake.align_script(script,AUDIO,duration,breaths)
 brief={
  "name":"missa-tv-360-ad-2026","title":"MISSA TV 360 — Ton écran mérite mieux",
  "template":"promo","brand":"missa","canvas":"9x16","preset":"mp4-social",
  "duration":duration,"audio_master":AUDIO,"logo":LOGO,
  "hook":"TON ÉCRAN MÉRITE MIEUX",
  "subhook":"TOUT TON DIVERTISSEMENT, EN UN SEUL ENDROIT",
  "product":{"image":LOGO,"name":"MISSA TV 360","tagline":"Des milliers de contenus. Une seule application."},
  "media":[
   {"file":"projects/missa-tv-360-ad-2026/generated/catalogue.png","caption":"FILMS • SÉRIES • MANGAS • DOCUMENTAIRES","duration":4.3,"move":"kenburns_in"},
   {"file":BANNER,"caption":"CENTAINES DE CHAÎNES TV EN DIRECT","duration":4.0,"move":"kenburns_pan_right"},
   {"file":"projects/missa-tv-360-ad-2026/generated/appareils.png","caption":"TÉLÉPHONE • TABLETTE • TÉLÉVISION","duration":4.0,"move":"kenburns_pan_left"},
   {"file":"projects/missa-tv-360-ad-2026/generated/faible-debit.png","caption":"STABLE MÊME AVEC UNE CONNEXION LIMITÉE","duration":4.0,"move":"kenburns_in"}
  ],
  "benefits_title":"TOUT EST LÀ",
  "benefits":[
   "Films, séries, mangas, documentaires",
   "TV en direct, radios et podcasts",
   "Sport, musique et jeux vidéo",
   "Stable même à faible débit"
  ],
  "offer":{"price":10000,"old_price":12000,"currency":" XAF","label":"par an • ou 1 000 XAF / mois","badge":"2 MOIS OFFERTS","deadline":"MOINS DE 30 XAF PAR JOUR"},
  "cta_title":"24 H POUR DÉCOUVRIR","signature":"ON EST ENSEMBLE, WESH !",
  "cta":"TÉLÉCHARGE MISSA TV 360","subtitles":True,"script":aligned,
  "style":{"background_style":"gradient","transition":"smoothleft"}
 }
 project=ads.compose(brief)
 starts,total=render.scene_starts(project,project["scenes"])
 names=[s.get("_scene","scene") for s in project["scenes"]]
 starts_by_name=dict(zip(names,starts))
 def at(scene,offset=.12):
  return max(0.0,min(total-.15,starts_by_name.get(scene,0.0)+offset))
 project["sfx"]=[
  {"file":"projects/missa-tv-360-ad-2026/sfx/impact.wav","at":at("hook"),"volume":.25,"role":"sfx"},
  {"file":"projects/missa-tv-360-ad-2026/sfx/whoosh.wav","at":at("product",.16),"volume":.18,"role":"sfx"},
  {"file":"projects/missa-tv-360-ad-2026/sfx/rise.wav","at":at("media:0",.18),"volume":.16,"role":"sfx"},
  {"file":"projects/missa-tv-360-ad-2026/sfx/pop.wav","at":at("media:1",.18),"volume":.18,"role":"sfx"},
  {"file":"projects/missa-tv-360-ad-2026/sfx/whoosh.wav","at":at("media:2",.18),"volume":.15,"role":"sfx"},
  {"file":"projects/missa-tv-360-ad-2026/sfx/sparkle.wav","at":at("media:3",.18),"volume":.16,"role":"sfx"},
  {"file":"projects/missa-tv-360-ad-2026/sfx/click.wav","at":at("benefits",.35),"volume":.12,"role":"sfx"},
  {"file":"projects/missa-tv-360-ad-2026/sfx/impact.wav","at":at("offer",.22),"volume":.20,"role":"sfx"},
  {"file":"projects/missa-tv-360-ad-2026/sfx/sparkle.wav","at":at("cta",.22),"volume":.18,"role":"sfx"}
 ]
 ROOT.mkdir(parents=True,exist_ok=True)
 (ROOT/"brief.json").write_text(json.dumps(brief,ensure_ascii=False,indent=2),encoding="utf-8")
 (ROOT/"project.json").write_text(json.dumps(project,ensure_ascii=False,indent=2),encoding="utf-8")
 (ROOT/"script-aligne.json").write_text(json.dumps(aligned,ensure_ascii=False,indent=2),encoding="utf-8")
 manifest={"project":"missa-tv-360-ad-2026","audio_master":AUDIO,"duration_seconds":round(duration,3),
  "sample_rate":info.get("sample_rate"),"channels":info.get("channels"),"breath_points":breaths,
  "scene_starts":{k:round(v,3) for k,v in starts_by_name.items()},"sfx_count":len(project["sfx"]),
  "subtitles_phrases":len(aligned),"media":[m["file"] for m in brief["media"]]}
 (ROOT/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
 print(json.dumps(manifest,ensure_ascii=False,indent=2))

if __name__=="__main__": main()
