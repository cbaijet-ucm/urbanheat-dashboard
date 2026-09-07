"""Persistencia local y atómica para los lienzos editables del dashboard."""

from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import re
import tempfile
import threading
from urllib.parse import unquote, urlparse
from urllib.request import urlopen


APP_DIR = Path(__file__).resolve().parents[1]
STORE_DIR = APP_DIR / ".urbanheat_content" / "canvases"
MODEL_COMPARISON_DIR = APP_DIR / "assets" / "generated" / "model_comparison"
HOST = "127.0.0.1"
# 8765 quedó ocupado por una instancia antigua tras los reinicios del dashboard.
# Este puerto identifica únicamente al almacén auxiliar de la instancia actual.
PORT = 8766
MAX_REQUEST_BYTES = 64 * 1024 * 1024
_KEY_PATTERN = re.compile(r"^[\w-]+$", re.UNICODE)
_WRITE_LOCK = threading.RLock()
_SERVER: ThreadingHTTPServer | None = None


def _canvas_path(key: str) -> Path:
    if not _KEY_PATTERN.fullmatch(key):
        raise ValueError("Identificador de lienzo no válido")
    return STORE_DIR / f"{key}.json"


def load_canvas_record(key: str) -> dict | None:
    """Carga el estado canónico de un lienzo, si existe."""
    path = _canvas_path(key)
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(payload, dict) or not isinstance(payload.get("objects"), list):
        return None
    return payload


def _atomic_write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.stem}-", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as stream:
            json.dump(payload, stream, ensure_ascii=False, separators=(",", ":"))
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary_name, path)
    finally:
        if os.path.exists(temporary_name):
            os.unlink(temporary_name)


class _ContentStoreHandler(BaseHTTPRequestHandler):
    server_version = "UrbanHeatContentStore/1"

    def _headers(self, status: int, content_type: str = "application/json; charset=utf-8") -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()

    def _reply(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _asset_reply(self, path: Path) -> None:
        content_type = "image/png" if path.suffix.lower() == ".png" else "application/octet-stream"
        body = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-store, max-age=0")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self) -> None:  # noqa: N802
        self._headers(204)

    def do_GET(self) -> None:  # noqa: N802
        request_path = urlparse(self.path).path
        if request_path == "/health":
            self._reply(200, {"ok": True})
            return
        match = re.fullmatch(
            r"/model-comparison/((?:\d{4}-\d{2}-\d{2}_(?:xgboost|cnn)|error_difference_cnn_vs_xgboost)\.png)",
            request_path,
        )
        if match:
            asset = MODEL_COMPARISON_DIR / match.group(1)
            if asset.is_file():
                self._asset_reply(asset)
                return
        self._reply(404, {"ok": False, "error": "not_found"})

    def do_POST(self) -> None:  # noqa: N802
        match = re.fullmatch(r"/canvas/([^/]+)", urlparse(self.path).path)
        if not match:
            self._reply(404, {"ok": False, "error": "not_found"})
            return
        try:
            key = unquote(match.group(1))
            path = _canvas_path(key)
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > MAX_REQUEST_BYTES:
                raise ValueError("Tamaño de petición no válido")
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            revision = int(payload["revision"])
            objects = payload["objects"]
            if revision < 0 or not isinstance(objects, list):
                raise ValueError("Estado de lienzo no válido")
            with _WRITE_LOCK:
                current = load_canvas_record(key)
                current_revision = int(current.get("revision", -1)) if current else -1
                if revision < current_revision:
                    self._reply(409, {"ok": False, "error": "stale_revision", "revision": current_revision})
                    return
                record = {"version": 1, "revision": revision, "objects": objects}
                _atomic_write(path, record)
            self._reply(200, {"ok": True, "revision": revision})
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
            self._reply(400, {"ok": False, "error": str(error)})
        except OSError as error:
            self._reply(500, {"ok": False, "error": str(error)})

    def log_message(self, _format: str, *_args: object) -> None:
        return


def ensure_content_store_server() -> str:
    """Arranca una única API local y devuelve su URL base."""
    global _SERVER
    if _SERVER is not None:
        return f"http://{HOST}:{PORT}"
    try:
        server = ThreadingHTTPServer((HOST, PORT), _ContentStoreHandler)
    except OSError:
        with urlopen(f"http://{HOST}:{PORT}/health", timeout=1) as response:
            if response.status != 200:
                raise RuntimeError("El puerto del almacén de contenido está ocupado")
        return f"http://{HOST}:{PORT}"
    thread = threading.Thread(target=server.serve_forever, name="urbanheat-content-store", daemon=True)
    thread.start()
    _SERVER = server
    return f"http://{HOST}:{PORT}"
