#!/usr/bin/env python3
"""key-notes — native desktop notes app.

Usage:
    pip3 install pywebview
    python3 main.py
"""

import http.server
import json
import mimetypes
import socket
import threading
import urllib.parse
from pathlib import Path

try:
    import webview
except ImportError:
    print("Error: pywebview is not installed.")
    print("Run:   pip3 install pywebview")
    raise SystemExit(1)

PORT = 8765


def find_free_port(start: int) -> int:
    port = start
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", port)) != 0:
                return port
        port += 1
BASE_DIR = Path(__file__).parent
NOTES_DIR = BASE_DIR / "notes"

DEFAULT_NOTES = [
    ("note-01", """# Design Principles

A checklist of high-level concepts for building successful, useful apps.

## Core Principles

- [ ] **User need first** — Solve a real problem, not a theoretical one
- [ ] **Simplest solution** — Choose the simplest architecture that works
- [ ] **Fast feedback** — Get something in front of users early
- [ ] **Composable** — Build small, focused pieces that work together
- [ ] **Fail loudly** — Errors should be visible and informative

## Design Checklist

- [ ] Is the core user journey obvious?
- [ ] Does every feature serve the primary use case?
- [ ] Can the UI be understood without documentation?
- [ ] Are error states handled gracefully?
- [ ] Is performance acceptable on a slow connection?

## Architecture Heuristics

- Prefer boring technology
- Optimise for deletability
- Data outlives code — design your schema carefully
- Name things for what they do, not what they are
"""),
    ("note-02", """# Ask for Help?

Decision tree for when to seek direction during development.

```mermaid
flowchart TD
    A[Stuck on a problem] --> B{Spent 30+ minutes?}
    B -- No --> C[Keep trying]
    B -- Yes --> D{Understand the problem?}
    D -- No --> E[Write down<br/>what is unclear]
    D -- Yes --> F{Tried 3+ approaches?}
    E --> G[Ask for help]
    F -- No --> H[Try another approach]
    F -- Yes --> G
    G --> I[Share: what you tried,<br/>what happened,<br/>what you expected]
```

## Before Asking

1. Write down the problem in plain English
2. State what you expected to happen
3. State what actually happened
4. List what you have tried
5. Find the smallest reproducible case
"""),
    ("note-03", "# Note 3\n\n"),
    ("note-04", "# Note 4\n\n"),
    ("note-05", "# Note 5\n\n"),
    ("note-06", "# Note 6\n\n"),
    ("note-07", "# Note 7\n\n"),
    ("note-08", "# Note 8\n\n"),
    ("note-09", "# Note 9\n\n"),
    ("note-10", "# Note 10\n\n"),
]


def get_title(content: str) -> str:
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    return "Untitled"


class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # suppress access logs

    def send_json(self, data, status=200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path

        if path in ("/", "/index.html"):
            data = (BASE_DIR / "index.html").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        elif path == "/api/notes":
            notes = []
            for i in range(1, 11):
                nid = f"note-{i:02d}"
                f = NOTES_DIR / f"{nid}.md"
                content = f.read_text("utf-8") if f.exists() else ""
                notes.append({"id": nid, "title": get_title(content) or f"Note {i}"})
            self.send_json(notes)

        elif path.startswith("/api/notes/"):
            nid = path[len("/api/notes/"):]
            f = NOTES_DIR / f"{nid}.md"
            if f.exists():
                self.send_json({"id": nid, "content": f.read_text("utf-8")})
            else:
                self.send_json({"error": "not found"}, 404)

        elif path.startswith("/static/"):
            filename = path[len("/static/"):]
            static_file = BASE_DIR / "static" / filename
            if static_file.exists():
                data = static_file.read_bytes()
                mime = mimetypes.guess_type(filename)[0] or "application/octet-stream"
                self.send_response(200)
                self.send_header("Content-Type", mime)
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
            else:
                self.send_error(404)

        else:
            self.send_error(404)

    def do_POST(self):
        if self.path.startswith("/api/notes/"):
            nid = self.path[len("/api/notes/"):]
            length = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(length))
            (NOTES_DIR / f"{nid}.md").write_text(data.get("content", ""), "utf-8")
            self.send_json({"status": "ok"})
        else:
            self.send_error(404)


def main():
    NOTES_DIR.mkdir(exist_ok=True)
    for nid, content in DEFAULT_NOTES:
        path = NOTES_DIR / f"{nid}.md"
        if not path.exists():
            path.write_text(content, "utf-8")

    # Start HTTP server on a background daemon thread
    port = find_free_port(PORT)
    server = http.server.ThreadingHTTPServer(("127.0.0.1", port), Handler)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()

    # Open native desktop window (blocks until closed)
    webview.create_window(
        "key-notes",
        f"http://localhost:{port}",
        width=980,
        height=700,
        min_size=(700, 520),
        background_color="#0a0a0a",
        text_select=True,
    )
    webview.start(debug=True)


if __name__ == "__main__":
    main()
