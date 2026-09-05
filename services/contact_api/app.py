#!/usr/bin/env python3
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from clinic.security import InputSanitizer


class RateLimiter:
    def __init__(self, limit: int, window_sec: int) -> None:
        self.limit = limit
        self.window_sec = window_sec
        self.hits: dict[str, list[float]] = {}

    def allow(self, key: str) -> bool:
        now = time.time()
        bucket = [t for t in self.hits.get(key, []) if now - t < self.window_sec]
        if len(bucket) >= self.limit:
            self.hits[key] = bucket
            return False
        bucket.append(now)
        self.hits[key] = bucket
        return True


class ContactValidator:
    def validate(self, payload: dict) -> dict[str, str]:
        if payload.get("company"):
            raise ValueError("spam")
        return {
            "name": InputSanitizer.plain_text(payload.get("name", ""), 120),
            "email": InputSanitizer.email(payload.get("email", "")),
            "phone": InputSanitizer.phone(payload.get("phone", "")),
            "message": InputSanitizer.plain_text(payload.get("message", ""), 5000),
        }


class InquiryStore:
    def __init__(self, inbox: Path) -> None:
        self.inbox = inbox
        self.inbox.mkdir(parents=True, exist_ok=True)

    def save(self, data: dict[str, str], ip: str) -> None:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        safe_ip = re.sub(r"[^0-9a-fA-F:.]", "", ip)[:45] or "unknown"
        path = self.inbox / f"{stamp}_{safe_ip.replace(':', '-')}.json"
        record = {"received_at": stamp, "ip": safe_ip, **data}
        path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
        path.chmod(0o600)


class ContactService:
    MAX_BODY = 8192

    def __init__(self) -> None:
        self.allowed_origin = os.environ.get("ALLOWED_ORIGIN", "https://clinic.example.com").rstrip("/")
        self.inbox = Path(os.environ.get("CONTACT_INBOX", "/var/lib/clinic-inquiries"))
        self.store = InquiryStore(self.inbox)
        self.validator = ContactValidator()
        self.rate = RateLimiter(limit=5, window_sec=900)

    def _client_ip(self, handler: BaseHTTPRequestHandler) -> str:
        forwarded = handler.headers.get("X-Forwarded-For", "")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return handler.client_address[0]

    def _origin_ok(self, handler: BaseHTTPRequestHandler) -> bool:
        origin = handler.headers.get("Origin", "").rstrip("/")
        referer = handler.headers.get("Referer", "")
        if origin:
            return origin == self.allowed_origin
        if referer:
            return referer.startswith(self.allowed_origin + "/")
        return False

    def handle(self, handler: BaseHTTPRequestHandler) -> None:
        if handler.path != "/api/contact":
            handler.send_error(404)
            return
        if handler.command != "POST":
            handler.send_error(405)
            return
        if handler.headers.get("Content-Type", "").split(";")[0].strip().lower() != "application/json":
            self._json(handler, 415, {"error": "Unsupported media type"})
            return
        if handler.headers.get("X-Requested-With") != "XMLHttpRequest":
            self._json(handler, 403, {"error": "Forbidden"})
            return
        if not self._origin_ok(handler):
            self._json(handler, 403, {"error": "Forbidden"})
            return
        ip = self._client_ip(handler)
        if not self.rate.allow(ip):
            self._json(handler, 429, {"error": "Too many requests. Try again later."})
            return
        length = int(handler.headers.get("Content-Length", "0") or "0")
        if length <= 0 or length > self.MAX_BODY:
            self._json(handler, 400, {"error": "Invalid request"})
            return
        raw = handler.rfile.read(length)
        try:
            payload = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self._json(handler, 400, {"error": "Invalid JSON"})
            return
        if not isinstance(payload, dict):
            self._json(handler, 400, {"error": "Invalid payload"})
            return
        try:
            clean = self.validator.validate(payload)
        except ValueError as exc:
            msg = "Invalid submission" if str(exc) == "spam" else str(exc).capitalize()
            code = 400 if str(exc) != "spam" else 403
            self._json(handler, code, {"error": msg})
            return
        self.store.save(clean, ip)
        self._json(handler, 200, {"ok": True})

    def _json(self, handler: BaseHTTPRequestHandler, code: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        handler.send_response(code)
        handler.send_header("Content-Type", "application/json; charset=utf-8")
        handler.send_header("Content-Length", str(len(body)))
        handler.send_header("Cache-Control", "no-store")
        handler.send_header("X-Content-Type-Options", "nosniff")
        handler.end_headers()
        handler.wfile.write(body)


class ContactHandler(BaseHTTPRequestHandler):
    service = ContactService()

    def log_message(self, fmt: str, *args) -> None:
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

    def do_POST(self) -> None:
        self.service.handle(self)

    def do_OPTIONS(self) -> None:
        if self.path != "/api/contact":
            self.send_error(404)
            return
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", self.service.allowed_origin)
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-Requested-With")
        self.send_header("Access-Control-Max-Age", "600")
        self.end_headers()


def main() -> None:
    host = os.environ.get("CONTACT_API_HOST", "127.0.0.1")
    port = int(os.environ.get("CONTACT_API_PORT", "8789"))
    server = ThreadingHTTPServer((host, port), ContactHandler)
    server.serve_forever()


if __name__ == "__main__":
    main()
