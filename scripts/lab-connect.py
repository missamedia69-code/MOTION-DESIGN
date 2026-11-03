#!/usr/bin/env python3
"""Client MCP : se connecte au Laboratoire et exécute une session d'outils.

C'est exactement le geste d'une IA « laborantin » : dialogue JSON-RPC 2.0 sur
stdio avec `lab.mcp`, sans serveur HTTP ni dépendance externe.

    python3 scripts/lab-connect.py --session lab/samples/session.json \
        --report livrables/lab/session.json

Une étape peut référencer un fichier d'échantillon via `spec_file`.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class LabClient:
    def __init__(self) -> None:
        self.proc = subprocess.Popen(
            [sys.executable, "-m", "lab.mcp"], cwd=REPO,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL, text=True, bufsize=1,
        )
        self.idx = 0

    def _send(self, method: str, params: dict | None = None, notify: bool = False) -> dict | None:
        self.idx += 1
        msg = {"jsonrpc": "2.0", "method": method}
        if params is not None:
            msg["params"] = params
        if not notify:
            msg["id"] = self.idx
        assert self.proc.stdin is not None
        self.proc.stdin.write(json.dumps(msg, ensure_ascii=False) + "\n")
        self.proc.stdin.flush()
        if notify:
            return None
        assert self.proc.stdout is not None
        while True:
            line = self.proc.stdout.readline()
            if not line:
                raise RuntimeError("le serveur MCP a fermé la connexion")
            resp = json.loads(line)
            if resp.get("id") == self.idx:
                if "error" in resp:
                    raise RuntimeError(resp["error"])
                return resp["result"]

    def initialize(self) -> dict:
        result = self._send("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "lab-connect", "version": "1.0"},
        })
        self._send("notifications/initialized", {}, notify=True)
        return result

    def tools(self) -> list[str]:
        return [t["name"] for t in self._send("tools/list", {})["tools"]]

    def call(self, name: str, arguments: dict) -> dict:
        result = self._send("tools/call", {"name": name, "arguments": arguments})
        text = result["content"][0]["text"]
        try:
            payload = json.loads(text)
        except ValueError:
            payload = {"text": text}
        if result.get("isError"):
            raise RuntimeError(str(payload))
        return payload

    def close(self) -> None:
        if self.proc.stdin:
            self.proc.stdin.close()
        self.proc.wait(timeout=10)


def summarize(label: str, tool: str, payload: dict) -> str:
    if tool == "lab_instruments":
        i = payload["instruments"]
        return (f"{len(i['canvas'])} canvas · {len(i['exports'])} exports · "
                f"{len(i['animations'])} animations · {len(i['fonts'])} polices")
    if tool == "lab_validate":
        return "valide · " + json.dumps(payload["spec"]["metrics"], ensure_ascii=False)
    if tool == "lab_run":
        return (f"{payload['status']} · {payload.get('scenes')} scènes · "
                f"{payload.get('duration_s')} s · {payload.get('resolution')} · "
                f"{payload.get('artifact') or payload.get('error')}")
    if tool == "lab_runs":
        return f"{len(payload)} expériences dans le registre"
    return json.dumps(payload, ensure_ascii=False)[:160]


def main() -> None:
    ap = argparse.ArgumentParser(description="Client MCP du Laboratoire")
    ap.add_argument("--session", default="lab/samples/session.json")
    ap.add_argument("--report", help="écrit le rapport JSON complet de la session")
    args = ap.parse_args()

    session_path = args.session if os.path.isabs(args.session) else os.path.join(REPO, args.session)
    with open(session_path, encoding="utf-8") as f:
        session = json.load(f)

    client = LabClient()
    info = client.initialize()
    tools = client.tools()
    print(f"🔌 Connecté à {info['serverInfo']['name']} v{info['serverInfo']['version']} "
          f"(MCP {info['protocolVersion']})")
    print(f"   {len(tools)} outils : {', '.join(tools)}\n")

    report = {"session": session.get("name"), "protocol": info["protocolVersion"], "steps": []}
    for step in session["steps"]:
        label, tool = step["label"], step["tool"]
        arguments = dict(step.get("arguments") or {})
        if step.get("spec_file"):
            p = step["spec_file"]
            p = p if os.path.isabs(p) else os.path.join(REPO, p)
            with open(p, encoding="utf-8") as f:
                arguments["spec"] = json.load(f)
        payload = client.call(tool, arguments)
        print(f"  ▶ {label:<34} {summarize(label, tool, payload)}")
        report["steps"].append({"label": label, "tool": tool,
                                "result": {k: payload.get(k) for k in
                                           ("status", "artifact", "scenes", "layers",
                                            "duration_s", "resolution", "bytes", "error")}
                                if tool == "lab_run" else {"ok": True}})
    client.close()

    if args.report:
        path = args.report if os.path.isabs(args.report) else os.path.join(REPO, args.report)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"\n📋 Rapport : {os.path.relpath(path, REPO)}")


if __name__ == "__main__":
    main()
