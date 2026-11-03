#!/usr/bin/env python3
"""Contrôle la cohérence des skills du moteur.

Vérifie que chaque entrée de skills-lock.json existe dans les trois répertoires
(.agents/skills canonique, .claude/skills liens symboliques, agent/skills copies),
qu'aucun répertoire orphelin ne traîne, et que le verrou est valide.

Usage : python3 scripts/check-skills.py   (ou make skills-check)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
LOCK = REPO / "skills-lock.json"
CANONICAL = REPO / ".agents" / "skills"
MIRRORS = [REPO / ".claude" / "skills", REPO / "agent" / "skills"]


def main() -> int:
    if not LOCK.is_file():
        print("✗ skills-lock.json absent")
        return 1

    try:
        lock = json.loads(LOCK.read_text())["skills"]
    except (json.JSONDecodeError, KeyError) as exc:
        print(f"✗ skills-lock.json invalide : {exc}")
        return 1

    errors: list[str] = []
    for name in sorted(lock):
        canonical = CANONICAL / name
        if not (canonical / "SKILL.md").is_file():
            errors.append(f".agents/skills/{name} : SKILL.md manquant ou non répertoire")
        for mirror in MIRRORS:
            rel = mirror.relative_to(REPO)
            target = mirror / name
            if not target.exists():
                errors.append(f"{rel}/{name} : absent")
            elif not (target / "SKILL.md").is_file():
                errors.append(f"{rel}/{name} : SKILL.md inaccessible (lien cassé ?)")
        link = MIRRORS[0] / name
        if link.exists() and not link.is_symlink():
            errors.append(f".claude/skills/{name} : devrait être un lien symbolique")

    locked = set(lock)
    for directory in (CANONICAL, *MIRRORS):
        if not directory.is_dir():
            errors.append(f"{directory.relative_to(REPO)} : répertoire absent")
            continue
        extras = {p.name for p in directory.iterdir()} - locked
        for name in sorted(extras):
            errors.append(f"{directory.relative_to(REPO)}/{name} : absent du lock")

    print(f"── Skills : {len(lock)} entrées dans le lock, 3 miroirs attendus ──")
    if errors:
        for err in errors:
            print(f"  ✗ {err}")
        print(f"\n✗ {len(errors)} anomalie(s).")
        return 1
    print("✅ Cohérence OK (lock, .agents/skills, .claude/skills, agent/skills).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
