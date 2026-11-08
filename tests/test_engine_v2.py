"""Tests du moteur v2 : easing, unités, marques, texte cinétique, lint, pub, rendu, cockpit MCP."""
from __future__ import annotations

import io
import json
import os
import shutil
import sys
import tempfile
import unittest
from contextlib import redirect_stdout

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

from engine import (ads, brand, easing, ffmpeg, frames, layout, lint, presets,  # noqa: E402
                    probe, project, render, text)
from lab import mcp  # noqa: E402


def quiet(fn, *a, **kw):
    buf = io.StringIO()
    with redirect_stdout(buf):
        res = fn(*a, **kw)
    return res, buf.getvalue()


class EasingTest(unittest.TestCase):
    def test_endpoints(self):
        for name in easing.EASINGS:
            self.assertAlmostEqual(easing.evaluate(name, 0.0), 0.0, places=3, msg=name)
            self.assertAlmostEqual(easing.evaluate(name, 1.0), 1.0, places=3, msg=name)

    def test_back_out_overshoots(self):
        self.assertGreater(max(easing.evaluate("back_out", k / 20) for k in range(21)), 1.0)

    def test_expression_substitution(self):
        e = easing.ease("ease_out", easing.progress("t", 0.5, 0.6))
        self.assertNotIn("@", e)
        self.assertIn("PI", easing.ease("elastic_out", "t"))
        with self.assertRaises(SystemExit):
            easing.ease("wobble", "t")


class UnitsAndBrandTest(unittest.TestCase):
    def test_units(self):
        W, H = 1080, 1920
        self.assertEqual(layout.to_px("50%", "x", W, H), 540)
        self.assertEqual(layout.to_px("50%", "y", W, H), 960)
        self.assertEqual(layout.to_px("10vmin", "x", W, H), 108)
        self.assertEqual(layout.to_px("10vh", "x", W, H), 192)
        self.assertEqual(layout.to_px("12px", "x", W, H), 12)
        self.assertEqual(layout.to_px(33, "x", W, H), 33)
        with self.assertRaises(SystemExit):
            layout.to_px("12em", "x", W, H)

    def test_normalize_tokens_and_units(self):
        proj = {"brand": "missa", "canvas": "9x16", "duration": 2, "layers": [
            {"type": "text", "text": "Prix : $9.99", "color": "$accent", "font": "$font.title",
             "size": "5vmin", "pos": ["50%", "25%"], "box": {"padding": ["2vw", 10]}}]}
        out = layout.normalize(proj, presets.canvas("9x16"))
        l0 = out["layers"][0]
        self.assertEqual(l0["color"], "#FFD400")
        self.assertEqual(l0["font"], "Montserrat-Black.ttf")
        self.assertEqual(l0["text"], "Prix : $9.99")  # pas un jeton
        self.assertEqual(l0["pos"], [540, 480])
        self.assertEqual(l0["size"], 54)
        self.assertAlmostEqual(l0["box"]["padding"][0], 21.6)

    def test_unknown_token_and_brand(self):
        with self.assertRaises(SystemExit):
            brand.resolve_project({"brand": "missa", "layers": [{"color": "$nope"}]})
        with self.assertRaises(SystemExit):
            brand.load("marque-inexistante")
        with self.assertRaises(SystemExit):  # jeton sans kit
            brand.resolve_project({"layers": [{"color": "$accent"}]})


class TextTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_tokens_share_frame(self):
        from PIL import Image
        spec = {"text": "Une offre\nexceptionnelle ici", "size": 40, "split": "word",
                "box": {"color": "#ff0000"}}
        paths = text.render_text_tokens(spec, self.tmp, "t")
        self.assertEqual(len(paths), 1 + 4)  # pastille + 4 mots
        sizes = set()
        for p in paths:
            with Image.open(p) as im:
                sizes.add(im.size)
        self.assertEqual(len(sizes), 1)
        self.assertEqual(len(text.render_text_tokens({"text": "a b\nc", "split": "line"},
                                                     self.tmp, "l")), 2)

    def test_too_many_tokens(self):
        with self.assertRaises(SystemExit):
            text.render_text_tokens({"text": "x" * 60, "split": "char"}, self.tmp, "c")

    def test_counter_frames(self):
        from PIL import Image
        pattern, n = text.render_counter_frames({"to": 2500, "count_duration": 1, "size": 30},
                                                self.tmp, "c", 10)
        self.assertEqual(n, 11)
        self.assertEqual(Image.open(pattern % 0).size, Image.open(pattern % 10).size)
        self.assertEqual(text.format_number(12345.5, 1), "12 345,5")

    def test_shapes_and_gradient(self):
        from PIL import Image
        for kind in text.SHAPE_KINDS:
            p = text.render_shape_png({"kind": kind, "w": 50, "h": 40, "gradient": ["#000", "#fff"]},
                                      os.path.join(self.tmp, f"{kind}.png"))
            self.assertEqual(Image.open(p).size, (50, 40))
        with self.assertRaises(SystemExit):
            text.render_shape_png({"kind": "star"}, os.path.join(self.tmp, "x.png"))
        g = text.render_gradient_png({"gradient": ["#000000", "#ffffff"], "angle": 90}, 100, 10,
                                     os.path.join(self.tmp, "g.png"))
        img = Image.open(g)
        self.assertLess(img.getpixel((0, 5))[0], 10)
        self.assertGreater(img.getpixel((99, 5))[0], 245)


class LintTest(unittest.TestCase):
    def test_errors_and_warnings(self):
        proj = {"canvas": "9x16", "duration": 3, "background": "#ffffff", "layers": [
            {"type": "text", "text": "Hi", "size": 10, "color": "#fefefe", "pos": [540, 1850],
             "anim": "wobble"},
            {"type": "image", "file": "introuvable.png"},
            {"type": "text", "text": "Tard", "in": 5}]}
        rep = lint.lint(proj, REPO)
        self.assertFalse(rep["ok"])
        wheres = {e["where"] for e in rep["errors"]}
        self.assertIn("projet.layers[0].anim", wheres)
        self.assertIn("projet.layers[1].file", wheres)
        self.assertIn("projet.layers[2].in", wheres)
        msgs = " ".join(w["message"] for w in rep["warnings"])
        self.assertIn("illisible", msgs)
        self.assertIn("contraste", msgs)
        self.assertIn("zone masquée", msgs)

    def test_transition_too_long(self):
        proj = {"canvas": "720p", "scenes": [
            {"duration": 1, "layers": [], "transition": {"type": "fade", "duration": 2}},
            {"duration": 1, "layers": []}]}
        self.assertFalse(lint.lint(proj, REPO)["ok"])
        with self.assertRaises(SystemExit):
            quiet(render.render_project_data, proj, REPO, "t-bad", dry_run=True)

    def test_contrast(self):
        self.assertAlmostEqual(lint.contrast("#000000", "#ffffff"), 21.0)


class AdsTest(unittest.TestCase):
    def test_all_templates_all_formats_clean(self):
        for tpl in ads.TEMPLATES:
            for fmt in ("9x16", "1x1", "4x5", "16x9"):
                b = dict(ads.example(), template=tpl)
                rep = lint.lint(ads.compose(b, canvas=fmt), REPO, fmt)
                self.assertTrue(rep["ok"], (tpl, fmt, rep["errors"]))
                self.assertEqual(rep["warnings"], [], (tpl, fmt))

    def test_duration_target_and_plan(self):
        b = dict(ads.example(), duration=15)
        p = ads.compose(b)
        _, total = render.scene_starts(p, p["scenes"])
        self.assertAlmostEqual(total, 15, delta=0.3)
        self.assertEqual(p["_ad"]["plan"], ["hook", "product", "benefits", "proof", "offer", "cta"])
        minimal = ads.compose({"hook": "Bonjour", "cta": "Go"})
        self.assertEqual(minimal["_ad"]["plan"], ["hook", "cta"])

    def test_bad_brief(self):
        for bad in ({}, {"hook": "x", "template": "nope"}, {"hook": "x", "canvas": "3x7"},
                    {"hook": "x", "benefits": list("abcdef")}):
            with self.assertRaises(SystemExit):
                ads.compose(bad)

    def test_audio_graph_ducking(self):
        b = dict(ads.example(), music={"file": "assets/audio/Voive Template.mp3", "loop": True},
                 voiceover="assets/audio/Voive Template.mp3", duration=6)
        _, out = quiet(render.render_project_data, ads.compose(b), REPO, "t-duck",
                       canvas_override="720p", dry_run=True)
        self.assertIn("sidechaincompress", out)
        self.assertIn("loudnorm=I=-14", out)   # preset mp4-social
        self.assertIn("-stream_loop", out)


class RenderTest(unittest.TestCase):
    """Vrais rendus (petits) : valide que ffmpeg accepte tous les graphes."""

    def test_render_all_motion_features_with_cache(self):
        anims = [a for a in render.ANIMS if not a.startswith("kenburns")]
        layers = []
        for k, a in enumerate(anims):
            layers.append({"type": "shape", "kind": text.SHAPE_KINDS[k % 5], "w": 40, "h": 40,
                           "color": "#ffcc00", "pos": [f"{8 + (k % 6) * 16}%", f"{15 + (k // 6) * 22}%"],
                           "anim": a, "exit": render.EXITS[k % len(render.EXITS)],
                           "idle": render.IDLES[k % len(render.IDLES)], "anim_duration": 0.3})
        proj = {"canvas": {"width": 320, "height": 180, "fps": 10},
                "transitions": {"type": "smoothleft", "duration": 0.3},
                "scenes": [
                    {"duration": 1.2, "background": {"gradient": ["#000000", "#334455"], "angle": 135},
                     "layers": layers},
                    {"duration": 1.2, "background": "#101010", "layers": [
                        {"type": "text", "text": "Mot par mot", "split": "word", "size": 20,
                         "box": {"color": "#ff0000"}, "pos": ["50%", "30%"]},
                        {"type": "counter", "to": 99, "size": 24, "pos": ["50%", "60%"], "anim": "punch",
                         "count_duration": 0.5},
                        {"type": "image", "file": "assets/images/pastille.png", "scale": {"w": 40},
                         "anchor": "top_left", "pos": [0, 0], "rotate": 15, "idle": "sway"}]}]}
        name = "t-v2-render"
        try:
            path, _ = quiet(render.render_project_data, proj, REPO, name, export_name="mp4-web")
            info = probe.probe(path)
            self.assertAlmostEqual(info["duration"], 2.1, delta=0.15)
            self.assertEqual((info["width"], info["height"]), (320, 180))
            _, log = quiet(render.render_project_data, proj, REPO, name, export_name="mp4-web")
            self.assertEqual(log.count("· cache"), 2)
        finally:
            shutil.rmtree(os.path.join(REPO, ".cache", name), ignore_errors=True)

    def test_multi_format_and_preview(self):
        b = dict(ads.example(), template="annonce", duration=6)
        proj = ads.compose(b)
        name = "t-v2-preview"
        try:
            res = frames.preview(proj, REPO, name, count=3, canvas_override="1x1", width=120)
            self.assertEqual(len(res["frames"]), 3)
            self.assertTrue(os.path.isfile(os.path.join(REPO, res["sheet"])))
            self.assertAlmostEqual(res["duration_s"], 6, delta=0.3)
        finally:
            shutil.rmtree(os.path.join(REPO, ".cache", name), ignore_errors=True)
            shutil.rmtree(os.path.join(REPO, ".cache", "apercus", f"{name}-apercu-1x1"),
                          ignore_errors=True)

    def test_ffmpeg_error_is_readable(self):
        with self.assertRaises(SystemExit) as cm:
            ffmpeg.run(["-f", "lavfi", "-i", "color=c=black:s=16x16:d=0.1",
                        "-vf", "filtre_inexistant", "-f", "null", "-"], echo=False)
        self.assertIn("ERREUR ffmpeg", str(cm.exception))
        self.assertIn("filtre_inexistant", str(cm.exception))


class IntakeTest(unittest.TestCase):
    """Réception d'une pub : audio complet, logo, détails, médias → brief calé sur l'audio."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        # audio « mixé » de 8 s avec deux respirations nettes (creux d'énergie) à 3 s et 5,5 s
        ffmpeg.run(["-f", "lavfi", "-i",
                    "aevalsrc='0.5*sin(2*PI*220*t)*(1-0.97*(between(t,2.85,3.15)+between(t,5.35,5.65)))'"
                    ":s=44100:d=8", os.path.join(self.tmp, "pub complete.mp3")], echo=False)
        shutil.copy(os.path.join(REPO, "assets/images/demo-logo.png"), os.path.join(self.tmp, "Logo Client"))
        shutil.copy(os.path.join(REPO, "assets/images/demo-produit.png"), os.path.join(self.tmp, "produit.png"))
        ffmpeg.run(["-f", "lavfi", "-i", "testsrc2=s=320x180:d=2", "-pix_fmt", "yuv420p",
                    os.path.join(self.tmp, "plan.mp4")], echo=False)
        with open(os.path.join(self.tmp, "details.txt"), "w") as f:
            f.write("Accroche : Plus simple que jamais\nOffre : 29 €\n")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_scan_and_compose_synced(self):
        from engine import intake
        rep = intake.scan(self.tmp, with_transcript=False)
        self.assertEqual(rep["manquants"], [])
        self.assertAlmostEqual(rep["audio"]["duration_s"], 8, delta=0.1)
        ts = [p["t"] for p in rep["audio"]["breaths"]]
        self.assertTrue(any(abs(t - 3.0) < 0.2 for t in ts), ts)
        self.assertTrue(any(abs(t - 5.5) < 0.2 for t in ts), ts)
        self.assertEqual(rep["logos"][0]["palette"]["accent"].upper()[:3], "#FF")  # orange démo
        self.assertEqual({m["kind"] for m in rep["medias"]}, {"image", "video"})
        self.assertIn("Plus simple", rep["details"][0]["content"])
        b = rep["brief_squelette"]
        self.assertTrue(b["sync"] and b["audio_master"] and b["style"]["accent"])
        b.update(hook="Plus simple que jamais", cta="J'en profite", benefits=["Rapide"],
                 scenes=["hook", "media", "cta"])
        proj = ads.compose(b)
        self.assertEqual(proj["_ad"]["plan"], ["hook", "media:0", "media:1", "cta"])
        starts, total = render.scene_starts(proj, proj["scenes"])
        self.assertAlmostEqual(total, 8, delta=0.1)
        # au moins une coupe calée sur une respiration
        self.assertTrue(any(abs(s - t) < 0.06 for s in starts[1:] for t in ts), (starts, ts))
        self.assertTrue(lint.lint(proj, REPO)["ok"])

    def test_explicit_cuts_and_errors(self):
        b = {"hook": "Test", "cta": "Go", "audio_master": os.path.join(self.tmp, "pub complete.mp3"),
             "media": [{"file": os.path.join(self.tmp, "produit.png")}], "cuts": [2.0, 5.0]}
        proj = ads.compose(b)
        self.assertEqual(render.scene_starts(proj, proj["scenes"])[0], [0.0, 2.0, 5.0])
        with self.assertRaises(SystemExit):
            ads.compose(dict(b, cuts=[2.0]))
        with self.assertRaises(SystemExit):
            ads.compose(dict(b, scenes=["hook", "intro"]))

    def test_brand_kit_from_logo(self):
        from engine import intake
        rep = intake.scan(self.tmp, with_transcript=False)
        kit = intake.brand_from_logo("client", os.path.join(REPO, rep["logos"][0]["file"]))
        self.assertEqual(kit["colors"]["accent"], rep["logos"][0]["palette"]["accent"])
        self.assertGreaterEqual(lint.contrast(kit["colors"]["accent"], kit["colors"]["on_accent"]), 4.5)


class ProjectAndCockpitTest(unittest.TestCase):
    def test_save_validates(self):
        name = "t-v2-save"
        try:
            pj = project.save(name, {"canvas": "720p", "duration": 1, "layers": []})
            self.assertTrue(os.path.isfile(pj))
            with self.assertRaises(SystemExit):
                project.save(name, {"duration": 1, "layers": [{"type": "nope"}]})
            with self.assertRaises(SystemExit):
                project.save(name, {"duration": 1, "layers": []}, overwrite=False)
        finally:
            shutil.rmtree(project.project_dir(name), ignore_errors=True)

    def test_mcp_cockpit(self):
        r = mcp.handle({"jsonrpc": "2.0", "id": 1, "method": "initialize",
                        "params": {"protocolVersion": "2025-06-18"}})
        self.assertEqual(r["result"]["protocolVersion"], "2025-06-18")
        self.assertIn("instructions", r["result"])
        names = {t["name"] for t in mcp.handle({"jsonrpc": "2.0", "id": 2,
                                                 "method": "tools/list"})["result"]["tools"]}
        for n in ("md_cockpit", "md_lint", "md_preview", "md_render", "md_ad_compose",
                  "md_ad_render", "md_project_save", "lab_run"):
            self.assertIn(n, names)
        cap = json.loads(mcp.call_tool("md_cockpit", {})["content"][0]["text"])
        self.assertIn("punch", cap["animations"]["entrees"])
        self.assertIn("demo", [b["name"] for b in cap["marques"]])
        res = mcp.call_tool("md_ad_compose", {"brief": ads.example()})
        payload = json.loads(res["content"][0]["text"])
        self.assertTrue(payload["lint"]["ok"])
        bad = mcp.call_tool("md_lint", {})
        self.assertTrue(bad.get("isError"))


if __name__ == "__main__":
    unittest.main()
