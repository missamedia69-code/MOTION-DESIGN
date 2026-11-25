"""Moteur unifié (studio) : éléments fournis → composition HyperFrames."""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)
os.environ.setdefault("MD_WHISPER", "0")   # pas de téléchargement de modèle pendant les tests

from engine import ffmpeg as ff, studio  # noqa: E402

SCRIPT = """Marre de payer un abonnement télé pour ne rien regarder ?
Découvrez Lumio TV.
Plus de 3 000 chaînes et 9 000 films et séries.
Le sport, le cinéma, les séries, les dessins animés : tout est là.
Seulement 29 euros par an au lieu de 49 euros.
Téléchargez Lumio TV maintenant !
"""


def _speechlike(path: str, lines: list[str]) -> float:
    parts, t = [], 0.3
    for line in lines:
        d = max(1.0, len(line) * 0.06)
        parts.append((t, d))
        t += d + 0.55
    total = t + 0.4
    expr = "+".join(f"between(t,{a:.2f},{a + d:.2f})" for a, d in parts)
    subprocess.run([ff.ffmpeg_exe(), "-v", "error", "-y", "-f", "lavfi", "-i",
                    f"anoisesrc=d={total:.2f}:c=pink:a=0.5", "-af",
                    f"bandpass=f=900:w=1400,volume='{expr}':eval=frame", "-ar", "22050", path], check=True)
    return total


class ParsingTest(unittest.TestCase):
    def test_numbers(self):
        n = studio._find_numbers("Plus de 3 000 chaînes et 9 000 films.")
        self.assertEqual([(x["value"], x["plus"], x["label"]) for x in n],
                         [(3000.0, True, "chaînes"), (9000.0, False, "films")])
        m = studio._find_numbers("Seulement vingt-neuf euros par an au lieu de 49 euros")
        self.assertEqual([(x["value"], x["currency"]) for x in m], [(29.0, "€"), (49.0, "€")])
        self.assertEqual(studio._words_to_number(["trois", "mille"]), 3000)

    def test_details(self):
        d = studio.parse_details("Marque : Lumio\nSite: lumio.tv\nBouton : Essayer\nStyle : Premium\n"
                                 "Sous-titres : oui")
        self.assertEqual(d, {"brand_name": "Lumio", "url": "lumio.tv", "cta": "Essayer",
                             "style": "premium", "subtitles": True})

    def test_storyboard_types_from_voice(self):
        lines = [l for l in SCRIPT.splitlines() if l]
        phrases = [{"start": i * 3.0, "end": i * 3.0 + 2.5, "text": t} for i, t in enumerate(lines)]
        sb = studio.storyboard_from_voice(phrases, 18.0, brand_name="Lumio TV")
        self.assertEqual([s["type"] for s in sb], ["hook", "logo", "stat", "benefits", "price", "cta"])
        price = sb[4]
        self.assertEqual((price["price"], price["old_price"], price["currency"]), (29.0, 49.0, "€"))
        self.assertEqual(sb[0]["start"], 0.0)
        self.assertAlmostEqual(sum(s["duration"] for s in sb), 18.0, places=2)


class BuildTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.audio = os.path.join(self.tmp, "pub.wav")
        self.dur = _speechlike(self.audio, [l for l in SCRIPT.splitlines() if l])
        with open(os.path.join(self.tmp, "script.txt"), "w", encoding="utf-8") as f:
            f.write(SCRIPT)
        shutil.copy(os.path.join(REPO, "assets", "images", "demo-logo.png"), os.path.join(self.tmp, "logo.png"))
        with open(os.path.join(self.tmp, "details.txt"), "w", encoding="utf-8") as f:
            f.write("Marque : Lumio TV\nSite : lumio.tv\nBouton : Essayer\n")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)
        for fmt in ("9x16", "16x9"):
            shutil.rmtree(os.path.join(REPO, "projects", f"t-studio-{fmt}"), ignore_errors=True)

    def test_folder_to_composition(self):
        brief = studio.brief_from_folder(self.tmp)
        self.assertTrue(brief["audio"].endswith("pub.wav"))
        self.assertEqual(brief["cta"], "Essayer")
        brief["auto_elements"] = False          # pas de réseau dans les tests
        for fmt in ("9x16", "16x9"):
            plan = studio.build(brief, canvas=fmt, name="t-studio")
            self.assertAlmostEqual(plan["duration"], self.dur, delta=0.1)
            types = [s["type"] for s in plan["storyboard"]]
            self.assertEqual(types[0], "hook")
            self.assertEqual(types[-1], "cta")
            self.assertIn("price", types)
            with open(os.path.join(plan["dir"], "index.html"), encoding="utf-8") as f:
                doc = f.read()
            self.assertIn('data-composition-id="main"', doc)
            self.assertIn('<audio id="snd0"', doc)
            self.assertIn('window.__timelines["main"] = tl;', doc)
            self.assertIn("Essayer", doc)
            self.assertIn("lumio.tv", doc)
            for f in ("vendor/gsap.min.js", "assets/logo.png", "storyboard.json"):
                self.assertTrue(os.path.isfile(os.path.join(plan["dir"], f)), f)
        if os.path.isfile(os.path.join(REPO, "node_modules", ".bin", "hyperframes")):
            self.assertEqual(studio.check(plan["dir"])["errors"], 0)

    def test_explicit_storyboard(self):
        brief = {"audio": self.audio, "logo": os.path.join(self.tmp, "logo.png"), "auto_elements": False,
                 "scenes": [{"type": "hook", "text": "Une accroche"},
                            {"type": "stat", "stats": [{"value": 120, "label": "pays"}]},
                            {"type": "cta", "button": "Go", "url": "x.fr"}]}
        plan = studio.build(brief, canvas="9x16", name="t-studio")
        self.assertEqual([s["type"] for s in plan["storyboard"]], ["hook", "stat", "cta"])
        self.assertEqual(plan["storyboard"][1]["start"], round(self.dur / 3, 3))
        with self.assertRaises(SystemExit):
            studio.build({**brief, "scenes": [{"type": "inconnu"}]}, canvas="9x16", name="t-studio")


if __name__ == "__main__":
    unittest.main()
