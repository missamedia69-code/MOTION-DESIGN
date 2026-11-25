"""Moteur 2.1 : grammaire « pro », caméra, coupes franches, rythme, vérification du rendu."""
import contextlib
import io
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

from engine import ads, beats, ffmpeg as ff, lint, probe, render, verify  # noqa: E402


def quiet(fn, *a, **kw):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        return fn(*a, **kw), buf.getvalue()


class ProMotionTest(unittest.TestCase):
    def test_compose_pro_by_default(self):
        proj = ads.compose(ads.example())
        self.assertEqual(proj["transitions"]["type"], "cut")
        self.assertEqual(proj["_ad"]["motion"], "pro")
        cams = [sc.get("camera") for sc in proj["scenes"]]
        self.assertTrue(all(cams))
        anims = [l.get("anim") for sc in proj["scenes"] for l in sc["layers"]]
        self.assertIn("land", anims)
        self.assertTrue(any(str(a).startswith("mask_") for a in anims))
        self.assertTrue(any(l.get("_glow") for sc in proj["scenes"] for l in sc["layers"]))

    def test_classic_style_kept(self):
        proj = ads.compose(dict(ads.example(), style={"motion": "classique"}))
        self.assertEqual(proj["transitions"]["type"], "smoothleft")
        self.assertFalse(any(sc.get("camera") for sc in proj["scenes"]))

    def test_target_duration_respected_with_cuts(self):
        for d in (6, 15, 30):
            proj = ads.compose(dict(ads.example(), duration=d))
            _, total = render.scene_starts(proj, proj["scenes"])
            self.assertAlmostEqual(total, d, delta=0.35, msg=f"durée {d}")

    def test_lint_knows_new_vocabulary(self):
        proj = ads.compose(ads.example())
        rep = lint.lint(proj, REPO)
        self.assertTrue(rep["ok"], rep["errors"])
        bad = {"canvas": "9x16", "scenes": [{"duration": 2, "camera": "tourne", "layers": []},
                                            {"duration": 2, "layers": []}]}
        self.assertFalse(lint.lint(bad, REPO)["ok"])


class RenderV21Test(unittest.TestCase):
    def test_camera_masks_cut_and_exact_duration(self):
        proj = {"canvas": {"width": 320, "height": 568, "fps": 15}, "export": {"preset": "mp4-web"},
                "transitions": {"type": "cut", "duration": 0.04},
                "scenes": [
                    {"duration": 1.37, "camera": {"move": "push_in", "amount": 0.08}, "motion_blur": True,
                     "background": "#202030",
                     "layers": [{"type": "text", "text": "Deux mots ici", "split": "word", "size": 40,
                                 "color": "#ffffff", "anim": "mask_up"},
                                {"type": "shape", "kind": "circle", "w": 60, "h": 60, "color": "#ff5533",
                                 "pos": ["50%", "75%"], "anim": "land", "in": 0.2}]},
                    {"duration": 1.41, "camera": "rise", "background": "#302020",
                     "layers": [{"type": "text", "text": "Whip", "size": 48, "color": "#ffffff",
                                 "anim": "whip_left"},
                                {"type": "text", "text": "mask", "size": 30, "color": "#ffffff",
                                 "pos": ["50%", "70%"], "anim": "mask_down"}]},
                    {"duration": 1.29, "camera": "drift_right", "background": "#203020",
                     "layers": [{"type": "text", "text": "Fin", "size": 48, "color": "#ffffff",
                                 "anim": "mask_left"}]}]}
        name = "t-v21-render"
        try:
            path, _ = quiet(render.render_project_data, proj, REPO, name)
            info = probe.probe(path)
            expected = 1.37 + 1.41 + 1.29 - 2 * 0.04
            self.assertAlmostEqual(info["duration"], expected, delta=0.1)
            self.assertTrue(os.path.isfile(path + ".events.json"))
            rep = verify.verify(path, expect=expected)
            self.assertIn(rep["verdict"], ("OK", "À AMÉLIORER", "À CORRIGER"))
            self.assertEqual(rep["coupes"], 2)
            self.assertTrue(os.path.isfile(rep["fichiers"]["planche"]))
        finally:
            shutil.rmtree(os.path.join(REPO, ".cache", name), ignore_errors=True)
            for f in os.listdir(os.path.join(REPO, ".cache", "rendus")):
                if f.startswith(name):
                    os.remove(os.path.join(REPO, ".cache", "rendus", f))


class BeatsTest(unittest.TestCase):
    def test_click_track_tempo_and_snap(self):
        d = tempfile.mkdtemp()
        try:
            click = os.path.join(d, "k.wav")
            track = os.path.join(d, "t.wav")
            subprocess.run([ff.ffmpeg_exe(), "-v", "error", "-y", "-f", "lavfi", "-i",
                            "sine=f=60:d=0.08,apad=pad_dur=0.42", "-t", "0.5", click], check=True)
            subprocess.run([ff.ffmpeg_exe(), "-v", "error", "-y", "-stream_loop", "19", "-i", click,
                            "-af", "volume=4", track], check=True)
            r = beats.analyse(track)
            self.assertAlmostEqual(r["bpm"], 120, delta=2)
            self.assertGreaterEqual(len(r["beats"]), 16)
            self.assertEqual(beats.snap([1.03, 7.0], [0.5, 1.0, 1.5], 0.25), [1.0, 7.0])
        finally:
            shutil.rmtree(d, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
