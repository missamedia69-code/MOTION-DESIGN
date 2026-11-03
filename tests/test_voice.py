"""Tests hors-ligne de engine.voice (aucun appel réseau, aucun modèle)."""
from __future__ import annotations

import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest import mock

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

from engine import voice  # noqa: E402


SAMPLE_HTML = """\
<div id="root" data-duration="20">
  <div id="cap1" class="cap clip" data-start="0.2" data-duration="8">Bonjour &amp; bienvenue !</div>
  <div id="cap2" class="cap clip" data-start="8.3" data-duration="5">Missa TV 360</div>
</div>
"""

SAMPLE_MIX = 'ffmpeg -i a.mp4 -i s1.mp3 -i s2.mp3 -filter_complex "[1:a]adelay=200|200[v1];[2:a]adelay=8350|8350[v2]"'


def base_script(**overrides):
    data = {
        "project": "test",
        "backend": "edge-tts",
        "voice": "fr-FR-HenriNeural",
        "out_dir": ".cache/vo-test",
        "format": "mp3",
        "segments": [
            {"id": "s1", "start": 0.2, "text": "Bonjour & bienvenue !"},
            {"id": "s2", "start": 8.35, "text": "Missa TV 360"},
        ],
    }
    data.update(overrides)
    return data


class ParseCaptionsTest(unittest.TestCase):
    def test_extracts_text_starts_and_entities(self):
        with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as f:
            f.write(SAMPLE_HTML)
            path = f.name
        try:
            segs = voice.parse_captions(path)
        finally:
            os.unlink(path)
        self.assertEqual([s["id"] for s in segs], ["s1", "s2"])
        self.assertEqual(segs[0]["text"], "Bonjour & bienvenue !")
        self.assertEqual(segs[0]["start"], 0.2)
        self.assertEqual(segs[1]["start"], 8.3)

    def test_real_project_has_six_segments(self):
        path = os.path.join(REPO, "projects", "missa-tv-360-v9", "index.html")
        self.assertEqual(len(voice.parse_captions(path)), 6)


class ValidateTest(unittest.TestCase):
    def test_valid_script_passes(self):
        voice.validate_script(base_script())

    def test_rejects_duplicate_ids(self):
        data = base_script(segments=[{"id": "s1", "text": "a"}, {"id": "s1", "text": "b"}])
        with self.assertRaises(SystemExit):
            voice.validate_script(data)

    def test_rejects_empty_text_and_bad_backend(self):
        with self.assertRaises(SystemExit):
            voice.validate_script(base_script(segments=[{"id": "s1", "text": "  "}]))
        with self.assertRaises(SystemExit):
            voice.validate_script(base_script(backend="inconnu"))

    def test_rejects_absolute_out_dir(self):
        with self.assertRaises(SystemExit):
            voice.validate_script(base_script(out_dir="/tmp/vo"))


class CommandTest(unittest.TestCase):
    def test_edge_tts_argv(self):
        cmd = voice.build_command({"text": "Salut !"}, ".cache/vo9/s1.mp3",
                                  "edge-tts", "fr-FR-HenriNeural", "-4%")
        self.assertEqual(cmd[0], "edge-tts")
        self.assertIn("--voice", cmd)
        self.assertIn("fr-FR-HenriNeural", cmd)
        self.assertIn("Salut !", cmd)
        self.assertIn("--rate=-4%", cmd)  # forme = pour une valeur négative
        self.assertNotIn("--format", cmd)  # option inexistante dans edge-tts
        self.assertEqual(cmd[cmd.index("--write-media") + 1], ".cache/vo9/s1.mp3")

    def test_voxcpm_uses_local_adapter(self):
        cmd = voice.build_command({"text": "Salut !"}, "/tmp/s1.mp3",
                                  "voxcpm", "ma_voix.wav")
        self.assertTrue(cmd[1].endswith(os.path.join("engine", "voxcpm_cli.py")))
        self.assertIn("--reference", cmd)
        self.assertIn("ma_voix.wav", cmd)


class MixTest(unittest.TestCase):
    def test_mix_delays(self):
        self.assertEqual(voice.mix_delays_from_text(SAMPLE_MIX), [0.2, 8.35])

    def test_check_mix_reports_drift(self):
        buf = io.StringIO()
        with tempfile.NamedTemporaryFile("w", suffix=".sh", delete=False, encoding="utf-8") as f:
            f.write(SAMPLE_MIX)
            path = f.name
        try:
            with redirect_stdout(buf):
                voice.check_mix([{"id": "s1", "start": 1.0}, {"id": "s2", "start": 8.35}], path)
            self.assertIn("⚠ s1", buf.getvalue())
        finally:
            os.unlink(path)


class DryRunTest(unittest.TestCase):
    def _args(self, **overrides):
        args = dict(name="missa-tv-360-v9", script=None, from_captions=False,
                    write_script=False, backend=None, voice=None, rate=None,
                    model=None, out_dir="/tmp/md-vo-should-not-exist", dry_run=True,
                    force=False, mix=False, check_mix=None)
        args.update(overrides)
        return SimpleNamespace(**args)

    def test_dry_run_creates_nothing_and_skips_preflight(self):
        out = "/tmp/md-vo-should-not-exist"
        buf = io.StringIO()
        with mock.patch.object(voice, "check_backend",
                               side_effect=AssertionError("pré-vérification appelée en dry-run")):
            with redirect_stdout(buf):
                voice.generate(self._args(out_dir=out))
        text = buf.getvalue()
        self.assertIn("dry-run", text)
        self.assertIn("edge-tts", text)
        self.assertIn("s6.mp3", text)
        self.assertFalse(os.path.exists(out))

    def test_from_captions_dry_run(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            voice.generate(self._args(from_captions=True))
        self.assertIn("6 captions extraites", buf.getvalue())

    def test_mix_hints(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            voice.generate(self._args(mix=True))
        self.assertIn("adelay=38200|38200", buf.getvalue())


class ManifestTest(unittest.TestCase):
    def test_committed_vo_json_matches_mix_delays(self):
        pdir = os.path.join(REPO, "projects", "missa-tv-360-v9")
        with open(os.path.join(pdir, "vo.json"), encoding="utf-8") as f:
            data = json.load(f)
        voice.validate_script(data)
        delays = voice.mix_delays(os.path.join(pdir, "mix9.sh"))[:len(data["segments"])]
        self.assertEqual([s["start"] for s in data["segments"]], delays)


if __name__ == "__main__":
    unittest.main(verbosity=2)
