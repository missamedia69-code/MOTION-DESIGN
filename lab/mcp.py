"""Serveur MCP stdio : une IA se connecte au labo comme un laborantin.

Protocole JSON-RPC 2.0 sur stdin/stdout, sans dépendance externe. Un client
MCP (Claude Code, Cursor, …) peut alors appeler les instruments :

    {"command":"python3","args":["-m","lab.mcp"]}

Outils exposés : lab_instruments, lab_schema, lab_example, lab_validate,
lab_run, lab_submit, lab_status, lab_runs, lab_artifact.
"""
from __future__ import annotations

import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from lab import bench, instruments, spec as spec_mod  # noqa: E402
from engine import probe  # noqa: E402

PROTOCOL_VERSION = "2024-11-05"

TOOLS = [
    {"name": "lab_instruments", "description": "Liste les instruments disponibles (canvas, exports, polices, animations, assets).",
     "inputSchema": {"type": "object", "properties": {}}},
    {"name": "lab_schema", "description": "Retourne le protocole d'entrée attendu et un exemple complet.",
     "inputSchema": {"type": "object", "properties": {}}},
    {"name": "lab_example", "description": "Retourne un échantillon de données prêt à soumettre.",
     "inputSchema": {"type": "object", "properties": {}}},
    {"name": "lab_validate", "description": "Valide et normalise un protocole sans rien rendre.",
     "inputSchema": {"type": "object", "properties": {"spec": {"type": "object"}}, "required": ["spec"]}},
    {"name": "lab_run", "description": "Exécute une expérience : données en entrée → vidéo en sortie. Bloquant (rendu complet).",
     "inputSchema": {"type": "object", "properties": {
         "spec": {"type": "object"},
         "dry_run": {"type": "boolean", "description": "true = valider le montage sans produire de fichier"}}, "required": ["spec"]}},
    {"name": "lab_submit", "description": "Soumet une expérience en tâche de fond et retourne son id (non bloquant).",
     "inputSchema": {"type": "object", "properties": {"spec": {"type": "object"}}, "required": ["spec"]}},
    {"name": "lab_status", "description": "État détaillé d'une expérience (status, artefact, logs, erreur).",
     "inputSchema": {"type": "object", "properties": {"id": {"type": "string"}}, "required": ["id"]}},
    {"name": "lab_runs", "description": "Liste des dernières expériences.",
     "inputSchema": {"type": "object", "properties": {"limit": {"type": "integer"}}}},
    {"name": "lab_artifact", "description": "Chemin et métadonnées de l'artefact vidéo d'une expérience.",
     "inputSchema": {"type": "object", "properties": {"id": {"type": "string"}}, "required": ["id"]}},
]


def call_tool(name: str, args: dict) -> dict:
    """Exécute un outil. Retourne le payload `result` MCP."""
    def text(payload) -> dict:
        return {"content": [{"type": "text",
                             "text": json.dumps(payload, ensure_ascii=False, indent=2)}]}

    try:
        if name == "lab_instruments":
            return text(instruments.inventory())
        if name == "lab_schema":
            return text(spec_mod.schema())
        if name == "lab_example":
            return text(spec_mod.example())
        if name == "lab_validate":
            return text({"valid": True, "spec": spec_mod.validate(args["spec"])})
        if name == "lab_run":
            return text(bench.run_experiment(args["spec"], dry_run=bool(args.get("dry_run", False))))
        if name == "lab_submit":
            return text(bench.submit(args["spec"]))
        if name == "lab_status":
            rec = bench.get(args["id"])
            return text(rec or {"error": "expérience inconnue"})
        if name == "lab_runs":
            return text(bench.list_runs(limit=int(args.get("limit", 30))))
        if name == "lab_artifact":
            rec = bench.get(args["id"])
            if not rec or not rec.get("artifact"):
                return text({"error": "artefact indisponible"})
            path = os.path.join(REPO, rec["artifact"])
            return text({"path": rec["artifact"],
                         "url": f"/api/runs/{rec['id']}/artifact",
                         "probe": probe.probe(path) if os.path.isfile(path) else {"error": "fichier absent"}})
        return {"content": [{"type": "text", "text": f"Outil inconnu : {name}"}], "isError": True}
    except SystemExit as exc:
        return {"content": [{"type": "text", "text": str(exc)}], "isError": True}
    except Exception as exc:  # noqa: BLE001
        return {"content": [{"type": "text", "text": f"{type(exc).__name__}: {exc}"}], "isError": True}


def handle(msg: dict) -> dict | None:
    """Traite un message JSON-RPC. None = notification (pas de réponse)."""
    method = msg.get("method", "")
    mid = msg.get("id")
    params = msg.get("params") or {}

    if method == "initialize":
        result = {
            "protocolVersion": PROTOCOL_VERSION,
            "capabilities": {"tools": {"listChanged": False}},
            "serverInfo": {"name": "motion-design-lab", "version": "1.0.0"},
        }
    elif method == "ping":
        result = {}
    elif method == "tools/list":
        result = {"tools": TOOLS}
    elif method == "tools/call":
        result = call_tool(params.get("name", ""), params.get("arguments") or {})
    elif method.startswith("notifications/"):
        return None
    else:
        if mid is None:
            return None
        return {"jsonrpc": "2.0", "id": mid,
                "error": {"code": -32601, "message": f"Méthode inconnue : {method}"}}

    if mid is None:
        return None
    return {"jsonrpc": "2.0", "id": mid, "result": result}


def main() -> None:
    """Boucle stdio : une requête JSON par ligne, une réponse par ligne."""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except ValueError:
            sys.stderr.write("lab.mcp : ligne JSON invalide ignorée\n")
            continue
        response = handle(msg)
        if response is not None:
            sys.stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
