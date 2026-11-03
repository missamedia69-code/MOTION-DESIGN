"""CLI du Laboratoire (`./md lab <action>`)."""
from __future__ import annotations

import json
import os
import sys


def _load_input(path: str | None) -> dict:
    if path:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    if not sys.stdin.isatty():
        return json.loads(sys.stdin.read() or "{}")
    raise SystemExit("ERREUR : fournir --input <spec.json> ou piper du JSON.")


def main(args) -> None:
    from lab import bench, instruments, mcp, server, spec as spec_mod

    action = args.action
    if action == "serve":
        server.serve(args.host, args.port)
        return
    if action == "mcp":
        mcp.main()
        return
    if action == "schema":
        print(json.dumps(spec_mod.schema(), ensure_ascii=False, indent=2))
        return
    if action == "example":
        print(json.dumps(spec_mod.example(), ensure_ascii=False, indent=2))
        return
    if action == "instruments":
        print(json.dumps(instruments.inventory(), ensure_ascii=False, indent=2))
        return
    if action == "runs":
        print(json.dumps(bench.list_runs(limit=args.limit), ensure_ascii=False, indent=2))
        return
    if action == "status":
        rec = bench.get(args.id)
        print(json.dumps(rec or {"error": "expérience inconnue"}, ensure_ascii=False, indent=2))
        return
    if action == "demo":
        raw = spec_mod.example()
        raw["canvas"] = "720p"
        raw["preset"] = "mp4-web"
        raw["duration"] = 2.0
    elif action == "run":
        raw = _load_input(args.input)
    else:
        raise SystemExit(f"ERREUR : action '{action}' inconnue")

    rec = bench.run_experiment(raw, dry_run=args.dry_run)
    if args.dry_run:
        rec["logs"] = rec["logs"][-8:]
    print(json.dumps(rec, ensure_ascii=False, indent=2))
    if rec["status"] == "error":
        raise SystemExit(1)
    if rec.get("artifact"):
        print(f"\n🎬 Artefact : {rec['artifact']}")
