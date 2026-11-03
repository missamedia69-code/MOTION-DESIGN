"""Tests hors-ligne du Laboratoire (protocole, compositeur, paillasse, MCP, HTTP)."""
from __future__ import annotations

import io
import json
import os
import sys
import threading
import unittest
import urllib.request
from contextlib import redirect_stdout
from unittest import mock
from http.server import ThreadingHTTPServer

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

from engine import presets, render  # noqa: E402
from lab import bench, composer, mcp, server, spec as spec_mod  # noqa: E402


def tiny(**overrides):
    base = {
        "title": "TestLab",
        "canvas": "720p",
        "preset": "mp4-web",
        "duration": 1.5,
        "data": [{"label": "A", "value": 3}, {"label": "B", "value": 7}],
    }
    base.update(overrides)
    return base


class ProtocolTest(unittest.TestCase):
    def test_defaults_and_metrics(self):
        s = spec_mod.validate(tiny())
        self.assertEqual(s["name"], "testlab")
        self.assertEqual(s["style"]["background"], "#0B1020")
        self.assertEqual(s["metrics"], {"count": 2, "total": 10.0, "max": 7.0,
                                        "mean": 5.0, "best_label": "B"})
        self.assertEqual(s["duration"], 1.5)

    def test_rejects_bad_data(self):
        for bad in ([], [{"label": "A", "value": "x"}],
                    [{"label": "A", "value": -1}],
                    [{"label": f"L{i}", "value": i} for i in range(13)]):
            with self.assertRaises(SystemExit):
                spec_mod.validate(tiny(data=bad))

    def test_rejects_unknown_instrument_and_bad_color(self):
        with self.assertRaises(SystemExit):
            spec_mod.validate(tiny(canvas="42x17"))
        with self.assertRaises(SystemExit):
            spec_mod.validate(tiny(style={"accent": "jaune"}))

    def test_short_duration_clamped(self):
        s = spec_mod.validate(tiny(duration=0.2))
        self.assertEqual(s["duration"], 1.0)

    def test_schema_has_example(self):
        self.assertEqual(spec_mod.schema()["example"]["name"], "demo-ventes")


class ComposerTest(unittest.TestCase):
    def setUp(self):
        self.spec = spec_mod.validate(tiny(duration=1.0))  # cas limite
        self.proj = composer.compose(self.spec)

    def test_four_scenes_and_bar_count(self):
        self.assertEqual(len(self.proj["scenes"]), 4)
        bars = [l for l in self.proj["scenes"][2]["layers"]
                if l["type"] == "shape" and l["anim"] == "grow_y"]
        self.assertEqual(len(bars), len(self.spec["data"]))
        self.assertEqual(self.proj["_lab"]["scene_types"],
                         ["hook", "kpi", "bars", "cta"])

    def test_every_layer_has_valid_window_and_anim(self):
        for si, scene in enumerate(self.proj["scenes"]):
            self.assertGreater(scene["duration"], 0)
            for li, layer in enumerate(scene["layers"]):
                self.assertGreater(layer["out"], layer["in"], f"scène {si} calque {li}")
                self.assertIn(layer["anim"], render.ANIMS)
                self.assertIn(layer["type"], ("text", "shape", "image"))

    def test_render_dry_run_from_memory(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            render.render_project_data(self.proj, os.path.join(REPO, ".cache", "lab-test"),
                                       "lab-test", export_name="mp4-web",
                                       out_path=os.path.join(REPO, ".cache", "lab-test", "out.mp4"),
                                       dry_run=True)
        self.assertIn("xfade", buf.getvalue())


class BenchTest(unittest.TestCase):
    def test_dry_run_experiment(self):
        rec = bench.run_experiment(tiny(), dry_run=True)
        self.assertEqual(rec["status"], "dry-run")
        self.assertIsNone(rec["artifact"])
        self.assertEqual(rec["scenes"], 4)

    def test_invalid_experiment_is_recorded_as_error(self):
        rec = bench.run_experiment(tiny(data=[]), dry_run=True)
        self.assertEqual(rec["status"], "error")
        self.assertIn("ERREUR de protocole", rec["error"])

    def test_registry_lists_experiments(self):
        rec = bench.run_experiment(tiny(), dry_run=True)
        self.assertIn(rec["id"], [r["id"] for r in bench.list_runs()])

    @mock.patch.object(bench, "run_experiment")
    def test_submit_is_non_blocking(self, _mocked):
        queued = bench.submit(tiny())
        self.assertEqual(queued["status"], "queued")
        self.assertEqual(bench.get(queued["id"])["status"], "queued")


class McpTest(unittest.TestCase):
    def test_initialize_and_tools_list(self):
        r = mcp.handle({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
        self.assertEqual(r["result"]["protocolVersion"], mcp.PROTOCOL_VERSION)
        r = mcp.handle({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
        names = [t["name"] for t in r["result"]["tools"]]
        self.assertIn("lab_run", names)
        self.assertIn("lab_artifact", names)

    def test_notification_has_no_response(self):
        self.assertIsNone(mcp.handle({"jsonrpc": "2.0", "method": "notifications/initialized"}))

    def test_tool_call_validate_and_run_dry(self):
        r = mcp.handle({"jsonrpc": "2.0", "id": 3, "method": "tools/call",
                        "params": {"name": "lab_validate", "arguments": {"spec": tiny()}}})
        payload = json.loads(r["result"]["content"][0]["text"])
        self.assertTrue(payload["valid"])
        r = mcp.handle({"jsonrpc": "2.0", "id": 4, "method": "tools/call",
                        "params": {"name": "lab_run",
                                   "arguments": {"spec": tiny(), "dry_run": True}}})
        payload = json.loads(r["result"]["content"][0]["text"])
        self.assertEqual(payload["status"], "dry-run")


class HttpTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.httpd = ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
        cls.thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f"http://127.0.0.1:{cls.httpd.server_address[1]}"

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()

    def _get(self, path):
        with urllib.request.urlopen(self.base + path, timeout=10) as r:
            return json.loads(r.read().decode())

    def test_health_instruments_schema(self):
        self.assertTrue(self._get("/api/health")["ok"])
        self.assertIn("canvas", self._get("/api/instruments")["instruments"])
        self.assertIn("example", self._get("/api/schema"))

    def test_post_dry_run_and_list(self):
        req = urllib.request.Request(
            self.base + "/api/runs?dry=1", data=json.dumps(tiny()).encode(),
            headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=20) as r:
            rec = json.loads(r.read().decode())
        self.assertEqual(rec["status"], "dry-run")
        self.assertIn(rec["id"], [x["id"] for x in self._get("/api/runs")])


if __name__ == "__main__":
    unittest.main(verbosity=2)
