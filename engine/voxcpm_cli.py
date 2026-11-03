#!/usr/bin/env python3
"""Adaptateur local VoxCPM2 pour `./md vo --backend voxcpm`.

Exécuté par segment de VO. Le paquet ``voxcpm`` et le modèle VoxCPM2
(huggingface.co/openbmb/VoxCPM2) doivent être installés **sur un poste disposant
d'un accès HuggingFace** — ce n'est pas le cas du sandbox de ce dépôt.

L'API exacte du paquet variant selon les versions, on essaie successivement
quelques points d'entrée courants et on échoue avec un message explicite plutôt
que de deviner silencieusement.
"""
from __future__ import annotations

import argparse
import os
import sys


def main() -> int:
    ap = argparse.ArgumentParser(description="Synthétise un segment VO avec VoxCPM2")
    ap.add_argument("--text", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--model", default="openbmb/VoxCPM2",
                    help="identifiant HuggingFace ou chemin local du modèle")
    ap.add_argument("--reference", default="",
                    help="fichier audio de référence pour le clonage (optionnel)")
    args = ap.parse_args()

    try:
        from voxcpm import VoxCPM  # type: ignore
    except ImportError:
        sys.exit(
            "ERREUR : paquet 'voxcpm' absent.\n"
            "  → pip3 install voxcpm\n"
            "  → modèle : huggingface.co/openbmb/VoxCPM2 (hôte non autorisé dans le sandbox)\n"
            "  → voir docs/VOIX-TTS.md"
        )

    try:
        model = VoxCPM.from_pretrained(args.model)
    except Exception as exc:
        sys.exit(f"ERREUR : chargement du modèle '{args.model}' impossible : {exc}")

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    kwargs = {"reference": args.reference} if args.reference else {}
    for method in ("tts_to_file", "generate", "synthesize", "tts"):
        fn = getattr(model, method, None)
        if callable(fn):
            try:
                fn(args.text, args.out, **kwargs)
            except TypeError:
                fn(args.text, args.out)
            if os.path.isfile(args.out) and os.path.getsize(args.out) > 0:
                print(f"✅ {args.out} ({os.path.getsize(args.out)} octets, via {method})")
                return 0
    sys.exit(
        "ERREUR : API VoxCPM non reconnue ou aucun fichier produit.\n"
        "  → adapter engine/voxcpm_cli.py à la version installée du paquet."
    )


if __name__ == "__main__":
    sys.exit(main())
