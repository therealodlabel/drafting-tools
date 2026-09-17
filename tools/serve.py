#!/usr/bin/env python3
"""Static server for the SolveSpace web build.
Usage: serve.py DIR PORT [--no-isolation]
By default sends COOP/COEP headers, which threaded (pthread/OpenMP) wasm builds need
for SharedArrayBuffer. --no-isolation omits them (to reproduce a naive deployment).
"""
import functools, http.server, sys

d, port = sys.argv[1], int(sys.argv[2])
iso = "--no-isolation" not in sys.argv


class H(http.server.SimpleHTTPRequestHandler):
    extensions_map = {**http.server.SimpleHTTPRequestHandler.extensions_map,
                      ".wasm": "application/wasm", ".js": "text/javascript"}

    def end_headers(self):
        if iso:
            self.send_header("Cross-Origin-Opener-Policy", "same-origin")
            self.send_header("Cross-Origin-Embedder-Policy", "require-corp")
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, *a):
        pass


http.server.ThreadingHTTPServer(("127.0.0.1", port), functools.partial(H, directory=d)).serve_forever()
