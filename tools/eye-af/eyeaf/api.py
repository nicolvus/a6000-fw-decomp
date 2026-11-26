"""Cliente mínimo del Camera Remote API de Sony (A6000, app Smart Remote Control).

Solo stdlib. Cada llamada es un POST JSON a ``/sony/camera``; el servidor de la
cámara (``orb-server``) contesta ``{"result": [...]}`` o ``{"error": [código, mensaje]}``,
a veces con HTTP 500 y el error igualmente en el cuerpo.
"""
from __future__ import annotations

import json
import time
import urllib.error
import urllib.request


def _answers(host: str, port: int, timeout: float) -> bool:
    try:
        CameraRemoteAPI(host, port, min(timeout, 3.0)).versions()
        return True
    except (CameraError, OSError):
        return False


class CameraError(RuntimeError):
    """Error devuelto por la cámara o fallo de transporte."""

    def __init__(self, message: str, code: int | None = None) -> None:
        super().__init__(message)
        self.code = code


PORTS = (8080, 10000)  # 8080 = Camera Remote API clásica; 10000 = orb-server (Smart Remote Control)


class CameraRemoteAPI:
    def __init__(self, host: str, port: int | None = 8080, timeout: float = 10.0) -> None:
        if port is None:  # autodetección: la cámara escucha en 8080 o en 10000 según el modelo
            port = next((p for p in PORTS if _answers(host, p, timeout)), PORTS[0])
        self.base = f"http://{host}:{port}"
        self.timeout = timeout
        self._id = 0
        self._versions: dict[str, str] = {}

    # -- transporte ---------------------------------------------------------
    def call(self, method: str, params: list | None = None, version: str | None = None) -> list:
        self._id += 1
        body = {
            "method": method,
            "params": params if params is not None else [],
            "id": self._id,
            "version": version or self._versions.get(method, "1.0"),
        }
        req = urllib.request.Request(
            f"{self.base}/sony/camera",
            data=json.dumps(body).encode(),
            headers={"Content-Type": "application/json; charset=UTF-8"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as r:
                raw = r.read()
        except urllib.error.HTTPError as e:  # la cámara devuelve 500 con el error dentro
            raw = e.read()
            if not raw:
                raise CameraError(f"{method}: HTTP {e.code}") from e
        except (TimeoutError, urllib.error.URLError) as e:
            raise CameraError(f"{method}: sin respuesta ({e})") from e

        try:
            data = json.loads(raw)
        except json.JSONDecodeError as e:
            raise CameraError(f"{method}: respuesta no JSON ({raw[:120]!r})") from e
        if "error" in data:
            code, msg = (data["error"] + [None, None])[:2]
            raise CameraError(f"{method}: {msg}", code)
        return data.get("result", [])

    # -- descubrimiento -----------------------------------------------------
    def versions(self) -> list[str]:
        return list(self.call("getVersions")[0])

    def method_types(self) -> dict[str, list[dict]]:
        """``getMethodTypes`` -> {método: [{returnType, params, version}, ...]}."""
        out: dict[str, list[dict]] = {}
        for row in self.call("getMethodTypes", [""]):
            name, ret, params, version = row[0], row[1], row[2], row[3]
            out.setdefault(name, []).append({"return": ret, "params": params, "version": version})
            self._versions.setdefault(name, version)
        return out

    def available_api_list(self) -> list[str]:
        return list(self.call("getAvailableApiList")[0])

    # -- live view ----------------------------------------------------------
    def start_liveview(self) -> str:
        res = self.call("startLiveview")
        url = res[0]
        if isinstance(url, list):  # algunas versiones devuelven ["1.0", url]
            url = url[-1]
        if not str(url).startswith("http"):
            raise CameraError(f"startLiveview: URL inesperada {url!r}")
        return url

    def stop_liveview(self) -> None:
        self.call("stopLiveview")

    # -- enfoque ------------------------------------------------------------
    def set_touch_af(self, x: float, y: float, version: str | None = None) -> list:
        """Mueve el punto de AF y enfoca ahí. ``x``/``y`` en porcentaje del encuadre (0..100)."""
        return self.call("setTouchAFPosition", [x, y], version)

    def get_touch_af(self) -> list:
        return self.call("getTouchAFPosition")

    def cancel_touch_af(self) -> list:
        return self.call("cancelTouchAFPosition")

    def set_focus_mode(self, mode: str) -> None:
        self.call("setFocusMode", [mode])

    def act_take_picture(self) -> list:
        return self.call("actTakePicture")

    # -- eventos ------------------------------------------------------------
    def get_event(self, long_poll: bool = False) -> dict:
        res = self.call("getEvent", [long_poll])
        names = res[0] if res else []
        return dict(zip(names, res[1:]))


def parse_af_result(result: list) -> bool | None:
    """Extrae ``AFResult`` de ``[int, {"AFResult": bool, "AFType": "Touch"}]``."""
    for item in result:
        if isinstance(item, dict) and "AFResult" in item:
            return bool(item["AFResult"])
    return None


def wait_for_method(api: CameraRemoteAPI, method: str, timeout: float, period: float = 0.5) -> bool:
    """Espera a que la cámara publique ``method`` en su lista de APIs disponibles."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            if method in api.available_api_list():
                return True
        except CameraError:
            pass
        time.sleep(period)
    return False
