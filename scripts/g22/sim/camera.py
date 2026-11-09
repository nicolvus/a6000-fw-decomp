"""Cadena completa emulada: elemento `Normal` (cmn_view_processDataMgr) → `libObj` (escritura/lectura) → paquete LIRO → `av-cam`."""

from __future__ import annotations

from pathlib import Path

from .avcam import AvCam
from .cmnview import CmnView
from .libobj import LibObj

SELECTOR = {0x5B: 0x40E3, 0x54: 0x4099}  # evento del modelo @M00F → selector LIRO


class Camera:
    def __init__(
        self,
        libobj: Path,
        cmnview: Path,
        avcam: Path,
        pid: int = 0x12,
        init_elems: tuple[int, int] = (0, 0),
    ) -> None:
        self.av, self.obj = AvCam(avcam), LibObj(libobj, init_elems)
        self.requests: list[tuple[str, int, dict[int, int]]] = []
        self.packets: list[bytes] = []
        self.cmn = CmnView(cmnview, pid, self._req, self._info)

    def _req(self, name: str, ev: int, params: dict[int, int]) -> None:
        self.requests.append((name, ev, params))
        sent = self.obj.write(ev, params)
        if sent:
            pkt = self.obj.to_liro(SELECTOR[ev], sent)
            self.packets.append(pkt)
            self.av.deliver(pkt)

    def _info(self, name: str, mid: int):
        return self.obj.read(mid) if name == "@M00F" and mid == 0x6C else None
