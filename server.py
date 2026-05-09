"""
Preisvergleich – HTTP-Server (stdlib, keine externen Deps nötig)

Usage:
  python3 server.py
  → http://localhost:8765

Optional eBay API (kostenlose Registrierung auf developer.ebay.com):
  export EBAY_CLIENT_ID=deine_app_id
  export EBAY_CLIENT_SECRET=dein_cert_id
  python3 server.py
"""
from __future__ import annotations

import json
import pathlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from config import PORT, SOURCE_CONFIGS
from price_agents import PriceMasterAgent

HTML_FILE = pathlib.Path(__file__).parent / "preisvergleich.html"
agent = PriceMasterAgent()


class PriceCompareHandler(BaseHTTPRequestHandler):

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path

        if path in ("/", "/index.html"):
            self._serve_html()
        elif path == "/api/search":
            params = parse_qs(parsed.query)
            q = params.get("q", [""])[0].strip()
            sources_param = params.get("sources", [""])[0]
            sources = [s for s in sources_param.split(",") if s] or None
            result = agent.search(q, sources)
            self._json(result)
        elif path == "/api/sources":
            sources_info = [
                {
                    "id": k,
                    "name": v["name"],
                    "type": v["type"],
                    "color": v["color"],
                    "enabled": v.get("enabled", True),
                }
                for k, v in SOURCE_CONFIGS.items()
            ]
            self._json({"sources": sources_info})
        elif path == "/api/health":
            self._json({"status": "ok", "port": PORT})
        else:
            self.send_error(404, "Nicht gefunden")

    def _json(self, data: dict) -> None:
        body = json.dumps(data, ensure_ascii=False, default=str).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _serve_html(self) -> None:
        try:
            body = HTML_FILE.read_bytes()
        except FileNotFoundError:
            self.send_error(404, "preisvergleich.html nicht gefunden")
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt: str, *args: object) -> None:
        print(f"  [{self.address_string()}] {fmt % args}")


if __name__ == "__main__":
    print(f"Preisvergleich-Tool gestartet → http://localhost:{PORT}")
    print("Strg+C zum Beenden\n")
    with ThreadingHTTPServer(("", PORT), PriceCompareHandler) as httpd:
        httpd.serve_forever()
