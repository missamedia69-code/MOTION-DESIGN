"""Tests hors réseau de la bibliothèque d'éléments (engine/elements.py)."""
from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from engine import elements  # noqa: E402


class ElementsTest(unittest.TestCase):
    def test_recherche_en_francais(self):
        self.assertEqual(elements._groups("télé"), [["television", "tv"]])
        self.assertIn("download", elements._terms("Télécharger"))
        self.assertEqual(elements._groups("popcorn"), [["popcorn"]])

    def test_classement_nom_avant_mots_cles(self):
        g = elements._groups("ballon foot")
        foot = elements._score("soccer ball", ["football", "ball"], g)
        laine = elements._score("yarn", ["ball", "knit"], g)
        self.assertGreater(foot, laine)
        self.assertEqual(elements._score("calendar", [], elements._groups("popcorn")), 0)

    def test_svg_iconify_recolore(self):
        data = {"width": 24, "height": 24, "icons": {"tv": {"body": '<path stroke="currentColor" d="M0 0h1"/>'}},
                "aliases": {"television": {"parent": "tv"}}}
        svg = elements._iconify_svg(data, "television", "#3dff6e", 256)
        self.assertIn('viewBox="0 0 24 24"', svg)
        self.assertIn('stroke="#3dff6e"', svg)
        self.assertIn('width="256"', svg)
        with self.assertRaises(KeyError):
            elements._iconify_svg(data, "inconnu", None, 64)

    def test_licences_tracees(self):
        with tempfile.TemporaryDirectory() as d:
            elements._licences_append([{"fichier": "a.svg", "source": "tabler", "origine": "x", "licence": "MIT"}], d)
            elements._licences_append([{"fichier": "a.svg", "source": "tabler", "origine": "y", "licence": "MIT"},
                                       {"fichier": "b.png", "source": "fluent-3d", "origine": "z", "licence": "MIT"}], d)
            rows = json.load(open(os.path.join(d, "licences.json")))
            self.assertEqual(sorted(r["fichier"] for r in rows), ["a.svg", "b.png"])
            self.assertIn("| `b.png` | fluent-3d |", open(os.path.join(d, "LICENCES.md")).read())

    def test_sources_et_kits_coherents(self):
        for k, v in elements.SOURCES.items():
            self.assertIn(v["licence"], elements.LICENCES_OK | {"vérifiée"}, k)
            self.assertIn(v["style"], elements.STYLES, k)
        for name, ids in elements.KITS.items():
            for i in ids:
                self.assertIn(i.split(":", 1)[0], elements.SOURCES, f"{name}: {i}")

    def test_iconvault_refuse_logos_de_marques(self):
        self.assertEqual(elements._vault_ok("simple-icons"), (False, "logos de marques"))
        self.assertFalse(elements._vault_ok("logos")[0])

    def test_ids_invalides(self):
        with tempfile.TemporaryDirectory() as d:
            r = elements.get(["sans-source", "inconnue:truc"], dest=d)
            self.assertEqual(r["recuperes"], [])
            self.assertEqual(set(r["erreurs"]), {"sans-source", "inconnue:truc"})


if __name__ == "__main__":
    unittest.main()
