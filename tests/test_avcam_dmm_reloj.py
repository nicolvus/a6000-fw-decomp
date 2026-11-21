"""G75 T66 (E2E-15): órdenes 4 (Free) y 6 (Close) de dmm.ko y modelo opt-in del servicio de reloj."""
from __future__ import annotations

import os
import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/gui/avcam"))
L = pytest.importorskip("liro_vm")


class FalsaVm:
    """Memoria plana mínima: solo lo que usa servicio_kernel para DMM."""
    def __init__(self) -> None:
        self.mem, self.dmm_n, self.dmm_bases, self.log, self.t, self.n = bytearray(0x400), 0, [], [], 0.0, 0

    def rd(self, a: int, n: int = 4) -> int:
        return int.from_bytes(self.mem[a:a + n], "little")

    def wr(self, a: int, v: int, n: int = 4) -> None:
        self.mem[a:a + n] = (v & ((1 << 8 * n) - 1)).to_bytes(n, "little")

    def malloc(self, n: int) -> int:
        return 0x300


class Tarea:
    name = "t"


@pytest.mark.parametrize("orden", [4, 6])
def test_free_y_close_repiten_el_componente_en_mas_6(orden: int) -> None:
    """VERIFICADO en bytes (av-cam `0x43903088…0x439030b2` Free, `0x439034ea…0x439034fa` Close): éxito = `[+0]`==0x8000|orden, `[+2]`==0 y `[+6]`==0x55 (el comp de `[+0x14]`)."""
    vm = FalsaVm()
    B = 0x40
    vm.wr(B, orden, 2)
    vm.wr(B + 2, 7, 2)  # asa de la unidad (la respuesta la pone a 0 = sin error)
    vm.wr(B + 0x14, 0x55, 2)
    assert L.servicio_kernel(vm, 0x61003C, B, Tarea())
    assert (vm.rd(B, 2), vm.rd(B + 2, 2), vm.rd(B + 6, 2)) == (0x8000 | orden, 0, 0x55)


def test_reloj_apagado_por_omision(monkeypatch: pytest.MonkeyPatch) -> None:
    import reloj
    monkeypatch.delenv("AVCAM_RELOJ", raising=False)
    assert reloj.instala(object()) is None


E68 = ROOT / "analysis/gui/g22/harness/live/e2e68/avcam.jsonl"


@pytest.mark.skipif(not E68.exists(), reason="falta la sesión e2e68 (no versionada)")
def test_reloj_opt_in_lleva_a_av_cam_al_estado_8_y_contesta_0x3000() -> None:
    """Réplica ≈15 s con `AVCAM_RELOJ=1`: el modelo (andamio, NO_VERIFICADO) pone el Master y av-cam contesta 0x3000 (sin él: estado 2)."""
    import subprocess
    env = {**os.environ, "AVCAM_RELOJ": "1"}
    out = subprocess.run([sys.executable, str(ROOT / "scripts/gui/avcam/master_diag.py"), str(E68), "reloj", "13800", "22000"], env=env, capture_output=True, text=True, timeout=900, check=True).stdout
    assert "[0x43ede338] 0x8" in out and "'0x3000'" in out
