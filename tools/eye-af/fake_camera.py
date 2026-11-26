"""Cámara falsa: servidor HTTP con el mismo contrato que la app Smart Remote Control.

Permite probar el cliente, el parser de Live View y el bucle completo sin cámara.
Sólo para pruebas y desarrollo (``python tools/eye-af/fake_camera.py --image foto.jpg``).
"""
from __future__ import annotations

import argparse
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Self

METHODS = {
    "getVersions": "1.0",
    "getMethodTypes": "1.0",
    "getAvailableApiList": "1.0",
    "startLiveview": "1.0",
    "stopLiveview": "1.0",
    "setTouchAFPosition": "1.0",
    "getTouchAFPosition": "1.0",
    "cancelTouchAFPosition": "1.0",
    "setFocusMode": "1.0",
    "getEvent": "1.0",
    "actTakePicture": "1.0",
}


class FakeCamera:
    def __init__(self, jpegs: list[bytes], port: int = 0, fps: float = 15.0,
                 available: list[str] | None = None) -> None:
        self.jpegs = jpegs
        self.fps = fps
        self.af_calls: list[tuple[float, float]] = []
        self.cancels = 0
        self.focus_modes: list[str] = []
        self.available = available if available is not None else [
            "startLiveview", "stopLiveview", "setTouchAFPosition", "getTouchAFPosition",
            "cancelTouchAFPosition", "setFocusMode", "getEvent", "actTakePicture",
        ]
        self.liveview_started = 0
        handler = self._handler()
        self.httpd = ThreadingHTTPServer(("127.0.0.1", port), handler)
        self.port = self.httpd.server_address[1]
        self._thread: threading.Thread | None = None

    @property
    def url(self) -> str:
        return f"http://127.0.0.1:{self.port}"

    def __enter__(self) -> Self:
        self._thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self._thread.start()
        return self

    def __exit__(self, *exc) -> None:
        self.httpd.shutdown()
        self.httpd.server_close()

    # -- contrato -----------------------------------------------------------
    def dispatch(self, method: str, params: list) -> list:
        if method == "getVersions":
            return [["1.0"]]
        if method == "getMethodTypes":
            return [[n, ["string"], [], v] for n, v in METHODS.items()]
        if method == "getAvailableApiList":
            return [self.available]
        if method == "startLiveview":
            self.liveview_started += 1
            return [f"{self.url}/liveviewstream"]
        if method == "stopLiveview":
            return []
        if method == "setTouchAFPosition":
            if len(params) < 2:
                raise ValueError("params")
            self.af_calls.append((float(params[0]), float(params[1])))
            return [0, {"AFResult": True, "AFType": "Touch"}]
        if method == "getTouchAFPosition":
            x, y = self.af_calls[-1] if self.af_calls else (0.0, 0.0)
            return [[x, y]]
        if method == "cancelTouchAFPosition":
            self.cancels += 1
            return []
        if method == "setFocusMode":
            self.focus_modes.append(str(params[0]))
            return []
        if method == "getEvent":
            return [["cameraStatus", "liveviewStatus", "touchAFPosition"],
                    "IDLE", 1 if self.liveview_started else 0,
                    list(self.af_calls[-1]) if self.af_calls else []]
        if method == "actTakePicture":
            return [[f"{self.url}/photo.jpg"]]
        raise KeyError(method)

    def _handler(self):
        cam = self

        class Handler(BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.1"

            def log_message(self, *a):  # silencio
                pass

            def do_POST(self):
                n = int(self.headers.get("Content-Length", 0))
                body = json.loads(self.rfile.read(n) or b"{}")
                method = body.get("method", "")
                try:
                    result = cam.dispatch(method, body.get("params") or [])
                    payload = {"result": result, "id": body.get("id", 1)}
                    code = 200
                except KeyError:
                    payload = {"error": [12, "No Such Method"], "id": body.get("id", 1)}
                    code = 500
                data = json.dumps(payload).encode()
                self.send_response(code)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            def do_GET(self):
                if not self.path.startswith("/liveviewstream"):
                    self.send_error(404)
                    return
                self.send_response(200)
                self.send_header("Content-Type", "multipart/x-mixed-replace; boundary=--boundary")
                self.send_header("Transfer-Encoding", "chunked")
                self.end_headers()
                interval = 1.0 / cam.fps
                try:
                    while True:
                        for jpg in cam.jpegs:
                            part = (b"--boundary\r\nContent-Type: image/jpeg\r\nContent-Length: "
                                    + str(len(jpg)).encode() + b"\r\n\r\n" + jpg + b"\r\n")
                            self.wfile.write(b"%X\r\n" % len(part) + part + b"\r\n")
                            self.wfile.flush()
                            threading.Event().wait(interval)
                except (BrokenPipeError, ConnectionResetError):
                    return

        return Handler


def main() -> int:
    ap = argparse.ArgumentParser(description="Cámara falsa para probar Eye AF sin hardware")
    ap.add_argument("--image", required=True, help="JPEG que se repite como Live View")
    ap.add_argument("--port", type=int, default=8080)
    ap.add_argument("--fps", type=float, default=15.0)
    a = ap.parse_args()
    with open(a.image, "rb") as f:
        jpg = f.read()
    with FakeCamera([jpg], port=a.port, fps=a.fps):
        print(f"cámara falsa en http://127.0.0.1:{a.port}  (Ctrl-C para salir)")
        try:
            threading.Event().wait()
        except KeyboardInterrupt:
            pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
