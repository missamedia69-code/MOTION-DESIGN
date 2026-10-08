"""Moteur de rendu : compile project.json en commandes ffmpeg et produit le livrable.

Modèle :
  projet = 1..n scènes ; scène = fond + calques (image, texte, forme, vidéo) ;
  chaque calque a une fenêtre [in, out] et une animation ;
  les scènes sont chaînées en xfade ; l'audio est mixé sur la timeline globale.
"""
from __future__ import annotations

import json
import os
import re
import time

from . import ffmpeg, presets, probe, text

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ANIMS = ["none", "fade", "fade_up", "fade_down", "fade_left", "fade_right",
         "slide_up", "slide_down", "slide_left", "slide_right", "pop",
         "grow_x", "grow_y", "kenburns_in", "kenburns_out",
         "kenburns_pan_left", "kenburns_pan_right"]


# ── Utilitaires ──────────────────────────────────────────────────────────────

def resolve_path(p: str, project_dir: str) -> str:
    """Résout un chemin média : absolu, relatif au projet, à la racine, ou par nom dans assets/."""
    if os.path.isabs(p):
        return p if os.path.exists(p) else _fail(f"Fichier introuvable : {p}")
    for base in (project_dir, REPO, os.path.join(REPO, "assets")):
        cand = os.path.join(base, p)
        if os.path.exists(cand):
            return os.path.abspath(cand)
    hits = []
    assets_root = os.path.join(REPO, "assets")
    for root, _, files in os.walk(assets_root):
        if os.path.basename(p) in files:
            hits.append(os.path.join(root, os.path.basename(p)))
    if hits:
        return hits[0]
    _fail(f"Fichier introuvable : {p} (cherché dans le projet, la racine et assets/)")


def _fail(msg: str):
    raise SystemExit(f"ERREUR : {msg}")


def _clamp(v, lo, hi):
    return max(lo, min(hi, v))


def _fitted_size(info: dict, fit: str, W: int, H: int, explicit_scale) -> tuple[int, int]:
    iw, ih = info.get("width") or W, info.get("height") or H
    if explicit_scale:
        w = explicit_scale.get("w")
        h = explicit_scale.get("h")
        if w and h:
            return int(w) // 2 * 2, int(h) // 2 * 2
        if w:
            return int(w) // 2 * 2, max(2, int(ih * (int(w) / iw)) // 2 * 2)
        if h:
            return max(2, int(iw * (int(h) / ih)) // 2 * 2), int(h) // 2 * 2
    if fit == "cover" or fit == "stretch":
        return W, H
    if fit == "original":
        return iw // 2 * 2, ih // 2 * 2
    # contain (défaut)
    r = min(W / iw, H / ih, 1.0) if (iw > W or ih > H) else min(W / iw, H / ih)
    return max(2, int(iw * r) // 2 * 2), max(2, int(ih * r) // 2 * 2)


def _scale_filter(fit: str, fw: int, fh: int) -> str:
    if fit == "cover":
        return f"scale={fw}:{fh}:force_original_aspect_ratio=increase,crop={fw}:{fh},setsar=1"
    if fit == "stretch":
        return f"scale={fw}:{fh},setsar=1"
    return f"scale={fw}:{fh},setsar=1"


def _pos_expr(pos, cx_default: str, cy_default: str):
    """Retourne (x_base, y_base) comme chaînes d'expression overlay (centre → coin)."""
    if pos in (None, "center"):
        return "(W-w)/2", "(H-h)/2"
    if pos == "top":
        return "(W-w)/2", "H*0.14-h/2"
    if pos == "bottom":
        return "(W-w)/2", "H*0.86-h/2"
    if pos == "top_third":
        return "(W-w)/2", "H*0.33-h/2"
    if pos == "bottom_third":
        return "(W-w)/2", "H*0.72-h/2"
    if isinstance(pos, (list, tuple)) and len(pos) >= 2:
        return f"{float(pos[0])}-w/2", f"{float(pos[1])}-h/2"
    _fail(f"Position inconnue : {pos!r} (center|top|bottom|top_third|bottom_third|[x,y])")


# ── Construction du graphe d'une scène ───────────────────────────────────────

class SceneGraph:
    def __init__(self):
        self.inputs: list[list[str]] = []
        self.filters: list[str] = []
        self.n_video_inputs = 0

    def add_input(self, args: list[str]) -> int:
        self.inputs.append(args)
        idx = len(self.inputs) - 1
        self.n_video_inputs += 1
        return idx


def build_scene_graph(scene: dict, canvas: dict, project_dir: str, cache_dir: str,
                      scene_idx: int, transparent_bg: bool = False) -> tuple[SceneGraph, str, float]:
    """Construit inputs+filtres d'une scène. Retourne (graphe, label vidéo, durée)."""
    W, H, FPS = int(canvas["width"]), int(canvas["height"]), float(canvas["fps"])
    D = float(scene.get("duration", canvas.get("duration", 5)))
    g = SceneGraph()

    # ── Fond ──
    bg = scene.get("background", "#000000" if not transparent_bg else "transparent")
    if bg in ("transparent", None) and transparent_bg:
        i = g.add_input(["-f", "lavfi", "-t", f"{D}", "-i", f"color=c=black@0:s={W}x{H}:r={FPS}"])
        g.filters.append(f"[{i}:v]format=rgba,setsar=1[bg]")
    elif isinstance(bg, str) and re.match(r"^(#|0x)?[0-9a-fA-F]{6}$", bg):
        i = g.add_input(["-f", "lavfi", "-t", f"{D}", "-i", f"color=c={bg}:s={W}x{H}:r={FPS}"])
        g.filters.append(f"[{i}:v]format=rgba,setsar=1[bg]")
    else:  # image de fond
        p = resolve_path(bg, project_dir)
        i = g.add_input(["-loop", "1", "-framerate", f"{FPS}", "-t", f"{D}", "-i", p])
        g.filters.append(f"[{i}:v]{_scale_filter('cover', W, H)},setsar=1[bg]")

    prev = "bg"
    for li, layer in enumerate(scene.get("layers", [])):
        tag = f"s{scene_idx}l{li}"
        prev = _add_layer(g, layer, li, tag, canvas, D, project_dir, cache_dir, prev)

    g.filters.append(f"[{prev}]format=yuv420p" if not transparent_bg else f"[{prev}]format=rgba")
    # dernière instruction : renommer la sortie
    g.filters[-1] += "[vout]"
    return g, "vout", D


def _add_layer(g: SceneGraph, layer: dict, li: int, tag: str, canvas: dict, D: float,
               project_dir: str, cache_dir: str, prev: str) -> str:
    W, H, FPS = int(canvas["width"]), int(canvas["height"]), float(canvas["fps"])
    ltype = layer.get("type", "image")
    if ltype not in ("image", "text", "video", "shape"):
        _fail(f"Calque {li} : type inconnu '{ltype}' (image|text|video|shape)")
    anim = layer.get("anim", "none")
    if anim not in ANIMS:
        _fail(f"Calque {li} : animation inconnue '{anim}'. Dispo : {', '.join(ANIMS)}")

    t_in = float(layer.get("in", 0))
    t_out = float(layer.get("out", D))
    L = t_out - t_in
    if L <= 0:
        _fail(f"Calque {li} : out doit être > in")

    # ── Préparation de la source ──
    fit = layer.get("fit")
    gen_path = None
    if ltype == "text":
        gen_path = text.render_text_png(layer, os.path.join(cache_dir, f"{tag}_text.png"),
                                        W, H, project_dir)
        src, kind = gen_path, "image"
        fit = fit or "original"
    elif ltype == "shape":
        gen_path = text.render_shape_png(layer, os.path.join(cache_dir, f"{tag}_shape.png"))
        src, kind = gen_path, "image"
        fit = fit or "original"
    elif ltype == "image":
        src = resolve_path(layer["file"], project_dir)
        kind = "image"
        fit = fit or ("original" if not layer.get("full_bleed") else "cover")
        fit = fit or "contain"
    else:
        src = resolve_path(layer["file"], project_dir)
        kind = "video"
        fit = fit or "cover"

    info = probe.probe(src)
    if "error" in info:
        _fail(f"Calque {li} : média illisible {src} ({info['error']})")
    fw, fh = _fitted_size(info, fit if fit != "original" else "original", W, H, layer.get("scale"))

    fi = _clamp(float(layer.get("fade_in", 0.5)), 0.01, L / 2) if anim.startswith("fade") or anim == "pop" else 0.0
    fo = _clamp(float(layer.get("fade_out", 0.5)), 0.01, L / 2) if anim.startswith("fade") else 0.0
    ad = float(layer.get("anim_duration", 0.6))  # durée slide/pop
    chain: list[str] = []
    local = f"min(max(t,0)/{ad},1)"  # progression anim 0→1 (timeline locale)

    if kind == "image" and anim.startswith("kenburns"):
        n = max(2, round(L * FPS))
        i = g.add_input(["-framerate", f"{FPS}", "-i", src])
        up_w, up_h = W * 2, H * 2
        chain.append(f"scale={up_w}:{up_h}:force_original_aspect_ratio=increase,crop={up_w}:{up_h},setsar=1")
        zc = f"z='1+0.22*on/{n - 1}'" if anim == "kenburns_in" else \
             f"z='1.22-0.22*on/{n - 1}'" if anim == "kenburns_out" else "z='1.18'"
        if anim == "kenburns_pan_left":
            xy = f"x='(iw-iw/zoom)*(1-on/{n - 1})':y='(ih-ih/zoom)/2'"
        elif anim == "kenburns_pan_right":
            xy = f"x='(iw-iw/zoom)*(on/{n - 1})':y='(ih-ih/zoom)/2'"
        else:
            xy = "x='(iw-iw/zoom)/2':y='(ih-ih/zoom)/2'"
        chain.append(f"zoompan={zc}:{xy}:d={n}:s={W}x{H}:fps={FPS}")
        chain.append(f"setpts=N/{FPS}/TB")
        if fit not in (None, "cover"):  # recadrage final si besoin
            chain.append(_scale_filter(fit or "cover", W, H))
        fw, fh = W, H
    elif kind == "video":
        src_in = float(layer.get("src_in", 0))
        i = g.add_input(["-i", src])
        chain.append(f"trim=start={src_in}:duration={L},setpts=PTS-STARTPTS,fps={FPS}")
        chain.append(_scale_filter(fit, fw, fh))
    else:
        i = g.add_input(["-loop", "1", "-framerate", f"{FPS}", "-t", f"{L}", "-i", src])
        chain.append(_scale_filter(fit, fw, fh))

    chain.append("format=rgba")

    # ── Animations applicables en pré-overlay (fade alpha, pop, grow) ──
    if fi:
        chain.append(f"fade=t=in:st=0:d={fi}:alpha=1")
    if fo:
        chain.append(f"fade=t=out:st={L - fo}:d={fo}:alpha=1")
    if anim == "pop":
        s = f"(0.86+0.14*min(t/{ad},1))"
        chain.append(f"crop=w='iw*{s}':h='ih*{s}':x='(iw-out_w)/2':y='(ih-out_h)/2'")
        chain.append(f"scale={fw}:{fh}")
    if anim == "grow_x":
        dg = float(layer.get("anim_duration", L))
        chain.append(f"crop=w='max(2,iw*min(t/{dg},1))':h=ih:x=0:y=0")
    if anim == "grow_y":
        dg = float(layer.get("anim_duration", L))
        chain.append(f"crop=h='max(2,ih*min(t/{dg},1))':w=iw:x=0:y='ih-out_h'")

    # Décalage vers la position temporelle dans la scène
    chain.append(f"setpts=PTS+{t_in}/TB")
    g.filters.append(f"[{i}:v]{','.join(chain)}[{tag}]")

    # ── Overlay avec position + animation de placement ──
    xb, yb = _pos_expr(layer.get("pos"), None, None)
    p = f"min(max(t-{t_in},0)/{ad},1)"  # progression en timeline scène
    amp = float(layer.get("amplitude", 80))
    x, y = xb, yb
    if anim in ("fade_up", "slide_up"):
        y = f"({yb})+{amp}*(1-{p})"
    elif anim in ("fade_down", "slide_down"):
        y = f"({yb})-{amp}*(1-{p})"
    elif anim in ("fade_left", "slide_left"):
        x = f"({xb})+{amp + W}*(1-{p})"
    elif anim in ("fade_right", "slide_right"):
        x = f"({xb})-{amp + W}*(1-{p})"
    needs_frame_eval = anim in ("fade_up", "fade_down", "fade_left", "fade_right",
                                "slide_up", "slide_down", "slide_left", "slide_right")
    ev = ":eval=frame" if needs_frame_eval else ""
    g.filters.append(
        f"[{prev}][{tag}]overlay=x='{x}':y='{y}':repeatlast=0:eof_action=pass{ev}[{tag}o]")
    return f"{tag}o"


# ── Audio ────────────────────────────────────────────────────────────────────

def collect_audio(proj: dict, D: float, project_dir: str):
    """Retourne [(path, t_in, volume, fade_in, fade_out, duration_fichier)]."""
    out = []
    a = proj.get("audio")
    if isinstance(a, str):
        a = {"file": a}
    if a:
        out.append((resolve_path(a["file"], project_dir), float(a.get("in", 0)),
                    float(a.get("volume", 1.0)), float(a.get("fade_in", 0.5)),
                    float(a.get("fade_out", 1.0)), None))
    for sc in proj.get("scenes", []):
        pass  # audio géré au niveau projet uniquement (v1)
    for layer in proj.get("layers", []):  # projet mono-scène
        if layer.get("type") == "audio":
            out.append((resolve_path(layer["file"], project_dir), float(layer.get("in", 0)),
                        float(layer.get("volume", 1.0)), float(layer.get("fade_in", 0)),
                        float(layer.get("fade_out", 0)), None))
    resolved = []
    for path, t_in, vol, fi, fo, _ in out:
        info = probe.probe(path)
        fdur = info.get("duration") or 0
        resolved.append((path, t_in, vol, fi, fo, fdur))
    return resolved


def audio_filters(audio_items, video_input_count: int, D: float) -> list[str]:
    filters = []
    labels = []
    for j, (path, t_in, vol, fi, fo, fdur) in enumerate(audio_items):
        idx = video_input_count + j
        ms = int(t_in * 1000)
        end = min(t_in + fdur, D) if fdur else D
        parts = [f"adelay={ms}:all=1", f"volume={vol}"]
        if fi:
            parts.append(f"afade=t=in:st={t_in}:d={fi}")
        if fo:
            parts.append(f"afade=t=out:st={max(end - fo, t_in)}:d={fo}")
        filters.append(f"[{idx}:a]aresample=48000,{','.join(parts)}[a{j}]")
        labels.append(f"[a{j}]")
    if len(labels) == 1:
        filters.append(f"{labels[0]}apad,atrim=0:{D},asetpts=N/SR/TB[aout]")
    else:
        mix = "".join(labels)
        filters.append(f"{mix}amix=inputs={len(labels)}:duration=longest:normalize=0[amix]")
        filters.append(f"[amix]apad,atrim=0:{D},asetpts=N/SR/TB[aout]")
    return filters


# ── Rendu projet ─────────────────────────────────────────────────────────────

def render_project(name: str, export_name: str | None = None, out_path: str | None = None,
                   dry_run: bool = False, fps_override: float | None = None) -> str:
    from . import project as project_mod

    proj, project_dir = project_mod.load(name)
    canvas = presets.canvas(proj.get("canvas", presets.DEFAULT_CANVAS))
    if fps_override:
        canvas["fps"] = fps_override
    if int(canvas["width"]) % 2 or int(canvas["height"]) % 2:
        _fail("Le canvas doit avoir des dimensions paires (requis par H.264).")

    export_name = export_name or proj.get("export", {}).get("preset", presets.DEFAULT_EXPORT)
    exp = presets.export(export_name)
    alpha_export = export_name in ("mov-alpha",) or (export_name == "webm-vp9" and proj.get("transparent"))

    scenes = proj.get("scenes") or [proj]
    if len(scenes) > 1 and alpha_export:
        _fail("L'export avec canal alpha ne supporte qu'une seule scène (v1).")

    out_dir = os.path.join(REPO, "output")
    os.makedirs(out_dir, exist_ok=True)
    default_file = f"{name}-{export_name}{exp['ext']}"
    out_path = out_path or proj.get("export", {}).get("filename")
    if out_path and not os.path.isabs(out_path):
        out_path = os.path.join(out_dir, out_path)
    out_path = out_path or os.path.join(out_dir, default_file)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    cache_dir = os.path.join(REPO, ".cache", name)
    os.makedirs(cache_dir, exist_ok=True)

    tr = proj.get("transitions", {})
    tr_type = tr.get("type", "fade")
    tr_dur = float(tr.get("duration", 0.5))
    if tr_type not in presets.XFADE_TRANSITIONS:
        _fail(f"Transition inconnue : {tr_type}. Dispo : {', '.join(presets.XFADE_TRANSITIONS)}")

    t0 = time.time()
    if len(scenes) == 1:
        # ── Une seule scène : graphe direct vers l'export ──
        sc = scenes[0]
        D = float(sc.get("duration", canvas.get("duration", 5)))
        g, _, _ = build_scene_graph(sc, canvas, project_dir, cache_dir, 0,
                                    transparent_bg=alpha_export)
        audio_items = collect_audio(proj, D, project_dir) if not alpha_export else []
        args: list[str] = []
        for inp in g.inputs:
            args += inp
        for a_path, *_ in audio_items:
            args += ["-i", a_path]
        filters = list(g.filters)
        if audio_items:
            filters += audio_filters(audio_items, g.n_video_inputs, D)
        if export_name == "gif":
            filters += _gif_chain(canvas, exp)
            vmap = "[vgif]"
        else:
            vmap = "[vout]"
        args += ["-filter_complex", ";".join(filters), "-map", vmap]
        if audio_items and export_name != "gif":
            args += ["-map", "[aout]"]
        args += ["-t", f"{D}"]
        args += exp["args"] if export_name != "gif" else []
        args += [out_path]
        _execute(args, dry_run)
    else:
        # ── Multi-scènes : rendus intermédiaires puis chaînage xfade ──
        clips = []
        for si, sc in enumerate(scenes):
            D_i = float(sc.get("duration", canvas.get("duration", 5)))
            clip = os.path.join(cache_dir, f"scene{si}.mp4")
            g, _, _ = build_scene_graph(sc, canvas, project_dir, cache_dir, si)
            args = []
            for inp in g.inputs:
                args += inp
            args += ["-filter_complex", ";".join(g.filters), "-map", "[vout]",
                     "-t", f"{D_i}", "-r", f"{canvas['fps']}",
                     "-c:v", "libx264", "-crf", "14", "-preset", "veryfast",
                     "-pix_fmt", "yuv420p", "-an", clip]
            print(f"── Scène {si + 1}/{len(scenes)} ({D_i}s) ──")
            _execute(args, dry_run)
            clips.append((clip, D_i))

        # Durées réelles de transition à chaque frontière (transition de la scène précédente)
        bounds = []
        for k in range(1, len(clips)):
            t_k = scenes[k - 1].get("transition", {})
            bounds.append((t_k.get("type", tr_type), float(t_k.get("duration", tr_dur))))
        total = sum(d for _, d in clips) - sum(d for _, d in bounds)
        args = []
        for c, _ in clips:
            args += ["-i", c]
        audio_items = collect_audio(proj, total, project_dir)
        for a_path, *_ in audio_items:
            args += ["-i", a_path]

        filters = []
        off = clips[0][1] - bounds[0][1]
        prev_lbl = "0:v"
        for k in range(1, len(clips)):
            tk_type, tk_dur = bounds[k - 1]
            if k > 1:
                off = off + clips[k - 1][1] - tk_dur
            lbl = f"x{k}" if k < len(clips) - 1 else "vchain"
            filters.append(f"[{prev_lbl}][{k}:v]xfade=transition={tk_type}:duration={tk_dur}:offset={off}[{lbl}]")
            prev_lbl = lbl
        if audio_items:
            filters += audio_filters(audio_items, len(clips), total)
        if export_name == "gif":
            filters.append("[vchain]format=yuv420p[vout]")
            filters += _gif_chain(canvas, exp)
            vmap = "[vgif]"
        else:
            filters.append("[vchain]format=yuv420p[vout]")
            vmap = "[vout]"
        args += ["-filter_complex", ";".join(filters), "-map", vmap]
        if audio_items and export_name != "gif":
            args += ["-map", "[aout]"]
        args += ["-t", f"{total}"]
        args += exp["args"] if export_name != "gif" else []
        args += [out_path]
        _execute(args, dry_run)

    if not dry_run:
        info = probe.probe(out_path)
        manifest = {
            "projet": name,
            "sortie": os.path.relpath(out_path, REPO),
            "export": export_name,
            "canvas": canvas,
            "duree_s": info.get("duration"),
            "poids": probe.fmt_size(info.get("size", 0)),
            "rendu_le": time.strftime("%Y-%m-%d %H:%M:%S"),
            "temps_rendu_s": round(time.time() - t0, 1),
        }
        with open(os.path.join(project_dir, "manifest.json"), "w") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        print(f"\n✅ Sortie : {os.path.relpath(out_path, REPO)}  "
              f"({manifest['duree_s']}s · {manifest['poids']} · rendu en {manifest['temps_rendu_s']}s)")
    return out_path


def _gif_chain(canvas: dict, exp: dict) -> list[str]:
    fps = exp.get("gif_fps", 15)
    w = min(exp.get("gif_width", 640), int(canvas["width"]))
    return [
        f"[vout]fps={fps},scale={w}:-1:flags=lanczos,split[g0][g1]",
        "[g0]palettegen=stats_mode=diff[pal]",
        "[g1][pal]paletteuse=dither=bayer:bayer_scale=5:diff_mode=rectangle[vgif]",
    ]


def _execute(args: list, dry_run: bool):
    if dry_run:
        ffmpeg.dry_run(args)
    else:
        ffmpeg.run(args)
