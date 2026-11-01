"""Serveur de prévisualisation : index HTML des sorties et rendus de projets."""
from __future__ import annotations

import html
import os
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PAGE = """<!doctype html>
<html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>MOTION-DESIGN — sorties</title>
<style>
 body{{font-family:system-ui,sans-serif;background:#0b0e14;color:#e6e6e6;margin:0;padding:2rem}}
 h1{{font-size:1.1rem;letter-spacing:.2em;color:#8ab4ff}} h2{{font-size:.9rem;color:#7d8590;margin-top:2rem}}
 a{{display:block;color:#e6e6e6;text-decoration:none;padding:.55rem .8rem;margin:.3rem 0;
    background:#151a24;border:1px solid #232a38;border-radius:8px}}
 a:hover{{border-color:#8ab4ff}} .meta{{color:#7d8590;font-size:.8rem;float:right}}
 .empty{{color:#7d8590}}
</style></head><body>
<h1>MOTION-DESIGN — SORTIES</h1>
{body}
</body></html>"""


def _section(title: str, folder: str, rel: str) -> str:
    rows = []
    if os.path.isdir(folder):
        for root, dirs, files in os.walk(folder):
            dirs[:] = [d for d in dirs if not d.startswith(".")]
            for f in sorted(files):
                if f.startswith("."):
                    continue
                p = os.path.join(root, f)
                relp = os.path.relpath(p, REPO)
                size = os.path.getsize(p)
                unit = "Mo" if size > 1048576 else "Ko"
                val = size / 1048576 if size > 1048576 else size / 1024
                rows.append(f'<a href="/{relp}">{html.escape(relp)}'
                            f'<span class="meta">{val:.1f} {unit}</span></a>')
    if not rows:
        rows = ['<div class="empty">— vide —</div>']
    return f"<h2>{title}</h2>" + "\n".join(rows)


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=REPO, **kw)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            body = _section("Sorties (livrées en artefact)", os.path.join(REPO, ".cache", "rendus"), ".cache/rendus")
            body += _section("Rendus de projets", os.path.join(REPO, "projects"), "projects")
            page = PAGE.format(body=body).encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(page)))
            self.end_headers()
            self.wfile.write(page)
            return
        return super().do_GET()

    def log_message(self, fmt, *args):
        pass


def serve(port: int = 8080):
    srv = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    print(f"🎬 Prévisualisation sur http://0.0.0.0:{port}")
    srv.serve_forever()


if __name__ == "__main__":
    import sys
    serve(int(sys.argv[1]) if len(sys.argv) > 1 else 8080)
