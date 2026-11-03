"""Paillasse HTTP du Laboratoire : API JSON + interface web pour le technicien.

Aucune dépendance externe (stdlib uniquement). Le serveur écoute sur 0.0.0.0
et toutes les URLs du navigateur sont **relatives** (compatible preview Arena).

    ./md lab serve --port 8080
    curl -X POST localhost:8080/api/runs -d @spec.json
"""
from __future__ import annotations

import argparse
import json
import mimetypes
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from lab import bench, instruments, spec as spec_mod  # noqa: E402

HTML = """<!doctype html>
<html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>MOTION-DESIGN · Laboratoire</title>
<style>
:root{--bg:#080d18;--panel:#101a2e;--line:#20304c;--fg:#eaf1ff;--mut:#8fa6c8;--acc:#ffd400}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);
font:15px/1.5 ui-monospace,SFMono-Regular,Menlo,monospace}
header{padding:18px 26px;border-bottom:1px solid var(--line);display:flex;gap:14px;align-items:baseline}
header b{font-size:19px;letter-spacing:.06em}header span{color:var(--mut);font-size:12px}
main{display:grid;grid-template-columns:minmax(320px,1fr) minmax(320px,1fr);gap:20px;padding:22px;max-width:1400px;margin:auto}
@media(max-width:900px){main{grid-template-columns:1fr}}
section{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:18px}
h2{margin:0 0 12px;font-size:13px;text-transform:uppercase;letter-spacing:.12em;color:var(--acc)}
textarea{width:100%;min-height:330px;background:#070c16;color:var(--fg);border:1px solid var(--line);
border-radius:8px;padding:12px;font:12px/1.5 ui-monospace,monospace;resize:vertical}
button{margin-top:12px;background:var(--acc);color:#101010;border:0;border-radius:8px;
padding:10px 18px;font-weight:700;cursor:pointer}button.ghost{background:transparent;color:var(--mut);border:1px solid var(--line)}
#status{margin-top:12px;padding:10px;border-radius:8px;background:#070c16;border:1px solid var(--line);white-space:pre-wrap;font-size:12px;min-height:44px}
table{width:100%;border-collapse:collapse;font-size:12px}td,th{padding:7px 6px;border-bottom:1px solid var(--line);text-align:left}
th{color:var(--mut);font-weight:400}a{color:var(--acc)}.pill{padding:2px 7px;border-radius:10px;background:#1b2a44;font-size:11px}
.done{color:#6ee7a8}.error{color:#ff8f8f}.running{color:var(--acc)}
small{color:var(--mut)}
</style></head><body>
<header><b>⚗ MOTION-DESIGN LAB</b><span>échantillons → protocole → instruments → expérience → artefact</span></header>
<main>
<section>
  <h2>1 · Échantillon de données</h2>
  <small>Modifiez les valeurs puis lancez l'expérience. Une IA peut poster le même JSON sur <b>/api/runs</b>.</small>
  <textarea id="spec" spellcheck="false"></textarea>
  <button id="run">▶ Lancer l'expérience</button>
  <button id="dry" class="ghost">Dry-run (sans rendu)</button>
  <button id="example" class="ghost">Recharger l'exemple</button>
  <div id="status">Prêt.</div>
</section>
<section>
  <h2>2 · Instruments</h2><div id="instruments">…</div>
  <h2 style="margin-top:22px">3 · Expériences</h2>
  <table><thead><tr><th>ID</th><th>État</th><th>Artefact</th></tr></thead><tbody id="runs"></tbody></table>
  <p><small><a href="/api/schema">/api/schema</a> · <a href="/api/health">/api/health</a> ·
  <a href="/api/instruments">/api/instruments</a> · <a href="/api/runs">/api/runs</a></small></p>
</section>
</main>
<script>
const $=id=>document.getElementById(id);
async function loadExample(){$('spec').value=JSON.stringify(await (await fetch('api/example')).json(),null,2)}
async function instruments(){
  const d=await (await fetch('api/instruments')).json();
  $('instruments').innerHTML=`<small>canvas : ${Object.keys(d.instruments.canvas).join(', ')}<br>
  exports : ${Object.keys(d.instruments.exports).join(', ')}<br>
  polices : ${d.moteur.polices_disponibles} · animations : ${d.instruments.animations.length}<br>
  scènes : ${d.scene_types.join(' → ')}</small>`;
}
async function runs(){
  const d=await (await fetch('api/runs')).json();
  $('runs').innerHTML=d.map(r=>`<tr><td>${r.id}</td><td class="${r.status}">${r.status}</td>
    <td>${r.artifact?`<a href="api/runs/${r.id}/artifact">${r.artifact.split('/').pop()}</a>`:(r.error||'—')}</td></tr>`).join('')||'<tr><td colspan="3"><small>Aucune expérience.</small></td></tr>';
}
async function launch(dry){
  $('status').textContent='Expérience en cours…';
  try{
    const body=JSON.parse($('spec').value);
    const res=await fetch('api/runs'+(dry?'?dry=1':''),{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
    const out=await res.json();
    if(!res.ok){$('status').textContent='Erreur : '+JSON.stringify(out);return}
    let rec;
    for(let i=0;i<180;i++){
      rec=await (await fetch('api/runs/'+out.id)).json();
      if(['done','dry-run','error'].includes(rec.status))break;
      await new Promise(r=>setTimeout(r,1000));
    }
    $('status').textContent=JSON.stringify({status:rec.status,scenes:rec.scenes,layers:rec.layers,
      artifact:rec.artifact,duration_s:rec.duration_s,error:rec.error},null,2);
    runs();
  }catch(e){$('status').textContent='Erreur : '+e}
}
$('run').onclick=()=>launch(false);$('dry').onclick=()=>launch(true);$('example').onclick=loadExample;
loadExample();instruments();runs();setInterval(runs,4000);
</script></body></html>"""


class Handler(BaseHTTPRequestHandler):
    server_version = "MotionLab/1.0"

    def log_message(self, fmt: str, *args) -> None:
        sys.stderr.write("  · %s %s\n" % (self.address_string(), fmt % args))

    # ── utilitaires ──────────────────────────────────────────────────────
    def _json(self, payload, code: int = 200) -> None:
        data = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(data)

    def _file(self, path: str) -> None:
        if not os.path.isfile(path):
            self._json({"error": "artefact introuvable"}, 404)
            return
        ctype = mimetypes.guess_type(path)[0] or "application/octet-stream"
        size = os.path.getsize(path)
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(size))
        self.send_header("Content-Disposition", f'inline; filename="{os.path.basename(path)}"')
        self.end_headers()
        with open(path, "rb") as f:
            while chunk := f.read(65536):
                self.wfile.write(chunk)

    def _parts(self) -> list[str]:
        return [p for p in urlparse(self.path).path.split("/") if p]

    # ── GET ──────────────────────────────────────────────────────────────
    def do_GET(self) -> None:
        parts = self._parts()
        if not parts:
            data = HTML.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        if parts == ["api", "health"]:
            return self._json({"ok": True, "lab": "MOTION-DESIGN Lab",
                               "runs": len(bench.list_runs(limit=1000))})
        if parts == ["api", "schema"]:
            return self._json(spec_mod.schema())
        if parts == ["api", "example"]:
            return self._json(spec_mod.example())
        if parts == ["api", "instruments"]:
            return self._json(instruments.inventory())
        if parts == ["api", "runs"]:
            return self._json(bench.list_runs())
        if len(parts) >= 3 and parts[:2] == ["api", "runs"]:
            rec = bench.get(parts[2])
            if not rec:
                return self._json({"error": "expérience inconnue"}, 404)
            if len(parts) == 4 and parts[3] == "artifact":
                return self._file(os.path.join(REPO, rec["artifact"])) if rec.get("artifact") else self._json({"error": "pas d'artefact"}, 404)
            if len(parts) == 4 and parts[3] == "project":
                return self._file(os.path.join(REPO, ".cache", "lab", parts[2], "project.json"))
            return self._json(rec)
        return self._json({"error": "route inconnue", "routes": [
            "/", "/api/health", "/api/schema", "/api/example", "/api/instruments",
            "/api/runs", "/api/runs/<id>", "/api/runs/<id>/artifact",
            "/api/runs/<id>/project"]}, 404)

    # ── POST ─────────────────────────────────────────────────────────────
    def do_POST(self) -> None:
        parts = self._parts()
        if parts != ["api", "runs"]:
            return self._json({"error": "POST attendu sur /api/runs"}, 404)
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length) or b"{}")
        except (ValueError, TypeError) as exc:
            return self._json({"error": f"JSON invalide : {exc}"}, 400)
        dry = "dry=1" in (urlparse(self.path).query or "")
        if dry:
            rec = bench.run_experiment(body, dry_run=True)
            return self._json(rec, 200 if rec["status"] == "dry-run" else 400)
        rec = bench.submit(body)
        return self._json(rec, 202)

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()


def serve(host: str = "0.0.0.0", port: int = 8080) -> None:
    httpd = ThreadingHTTPServer((host, port), Handler)
    print(f"⚗ Laboratoire en écoute : http://{host}:{port}/  (Ctrl+C pour arrêter)")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n⏹ Paillasse arrêtée.")
    finally:
        httpd.server_close()


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Paillasse HTTP MOTION-DESIGN Lab")
    ap.add_argument("--host", default="0.0.0.0")
    ap.add_argument("--port", type=int, default=8080)
    a = ap.parse_args()
    serve(a.host, a.port)
