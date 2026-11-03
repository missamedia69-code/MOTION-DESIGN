"""Paillasse : orchestre une expérience (protocole → montage → rendu → artefact).

Une expérience est reproductible : mêmes données + même spec = même montage.
Le registre des expériences vit dans `.cache/lab/registry.json` (intermédiaire,
non versionné) ; l'artefact, lui, est remis dans `livrables/lab/`.
"""
from __future__ import annotations

import contextlib
import io
import json
import os
import threading
import time
import traceback
import uuid

from engine import presets, probe, render

from . import composer, spec as spec_mod

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAB_CACHE = os.path.join(REPO, ".cache", "lab")
DELIVERABLES = os.path.join(REPO, "livrables", "lab")
REGISTRY_PATH = os.path.join(LAB_CACHE, "registry.json")

RUNS: dict[str, dict] = {}
_LOCK = threading.Lock()


def _persist() -> None:
    os.makedirs(LAB_CACHE, exist_ok=True)
    with _LOCK:
        snapshot = dict(RUNS)
    with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2, ensure_ascii=False)


def _load_registry() -> None:
    if not os.path.isfile(REGISTRY_PATH):
        return
    try:
        with open(REGISTRY_PATH, encoding="utf-8") as f:
            data = json.load(f)
        with _LOCK:
            RUNS.update(data)
    except (OSError, ValueError):
        pass


def new_id() -> str:
    return uuid.uuid4().hex[:12]


def run_experiment(raw: dict, *, dry_run: bool = False, run_id: str | None = None,
                   out_dir: str | None = None) -> dict:
    """Exécute une expérience complète. `dry_run` ne produit aucun fichier."""
    rid = run_id or new_id()
    record: dict = {
        "id": rid,
        "status": "running",
        "submitted_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "dry_run": dry_run,
        "logs": [],
    }
    with _LOCK:
        RUNS[rid] = record

    try:
        spec = spec_mod.validate(raw)
        project = composer.compose(spec)
        record["spec"] = spec
        record["scenes"] = len(project["scenes"])
        record["layers"] = sum(len(s["layers"]) for s in project["scenes"])

        ext = presets.export(spec["preset"])["ext"]
        if dry_run:
            out_path = os.path.join(LAB_CACHE, f"dry-{rid}{ext}")
        else:
            base = out_dir or DELIVERABLES
            os.makedirs(base, exist_ok=True)
            out_path = os.path.join(base, f"{spec['name']}-{rid}{ext}")

        run_dir = os.path.join(LAB_CACHE, rid)
        if not dry_run:
            os.makedirs(run_dir, exist_ok=True)

        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            render.render_project_data(
                project, run_dir, f"lab-{rid}",
                export_name=spec["preset"], out_path=out_path, dry_run=dry_run,
            )
        record["logs"] = [line for line in buf.getvalue().splitlines() if line.strip()][-20:]

        if dry_run:
            record["status"] = "dry-run"
            record["artifact"] = None
        else:
            info = probe.probe(out_path)
            record["status"] = "done"
            record["artifact"] = os.path.relpath(out_path, REPO)
            record["bytes"] = info.get("size")
            record["duration_s"] = info.get("duration")
            record["resolution"] = f"{info.get('width')}x{info.get('height')}"
            with open(os.path.join(run_dir, "project.json"), "w", encoding="utf-8") as f:
                json.dump(project, f, indent=2, ensure_ascii=False)
        record["finished_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
    except SystemExit as exc:
        record["status"] = "error"
        record["error"] = str(exc)
    except Exception as exc:  # noqa: BLE001
        record["status"] = "error"
        record["error"] = f"{type(exc).__name__}: {exc}"
        record["trace"] = traceback.format_exc(limit=4)

    with _LOCK:
        RUNS[rid] = record
    if not dry_run:
        _persist()
    return record


def submit(raw: dict, **kwargs) -> dict:
    """Lance une expérience en tâche de fond (API HTTP)."""
    rid = new_id()
    with _LOCK:
        RUNS[rid] = {"id": rid, "status": "queued",
                     "submitted_at": time.strftime("%Y-%m-%d %H:%M:%S")}
    thread = threading.Thread(target=run_experiment, args=(raw,),
                              kwargs={"run_id": rid, **kwargs}, daemon=True)
    thread.start()
    return {"id": rid, "status": "queued"}


def get(run_id: str) -> dict | None:
    with _LOCK:
        rec = RUNS.get(run_id)
        return dict(rec) if rec else None


def list_runs(limit: int = 30) -> list[dict]:
    with _LOCK:
        records = list(RUNS.values())
    fields = ("id", "status", "submitted_at", "finished_at", "artifact", "error", "dry_run")
    return [{k: r.get(k) for k in fields} for r in records[-limit:][::-1]]


_load_registry()
