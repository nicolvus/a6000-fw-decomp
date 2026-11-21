"""Modelo OPT-IN del servicio de reloj que atiende `0xc2019f` y emite el «Master» de `[CLK_CTRL]` (E2E-15/E2E-3, g75 T66). ANDAMIO DE PRUEBA, no fidelidad.

Activación: `AVCAM_RELOJ=1` (por omisión apagado). Parámetro: `AVCAM_RELOJ_TRAMAS` (adelanto del `targetVfc`, 4).
DATO REAL (VERIFICADO en bytes, g75 T13/T65): `ClkCtrl` (`tsk0x4`) manda `{1, 0xc001bd, 2}` a `0xc2019f`; acepta en `0xc001bd` la etiqueta `0x80c001bd` solo con el byte `[0x43e4a5a4]`==2
y toma `targetVfc` (palabra 0, contador absoluto de tramas de 24 bit), `delay_req` (palabra 1), palabra 2 (`+0x14`).
NO_VERIFICADO (fabricado aquí): quién emite el Master (no está en ningún binario del paquete), que el rol 2 lo ponga el registro, el disparador (módulo 0 en 0x102), el adelanto de tramas,
`delay_req`=1 y palabra 2=0. En el volcado real en reposo el rol vale 0 y `targetVfc` 0xffffffff: en reposo no hay Master."""
from __future__ import annotations

import os
import struct

COLA_SERVICIO, COLA_CLK, ROL, VFC = 0xC2019F, 0xC001BD, 0x43E4A5A4, 0x43E991CC
ETIQUETA_MASTER = 0x80C001BD


MODULO0 = 0x43E9BD58  # u16 estado del módulo 0 del secuenciador (`id<<8 | estado`)
ESPERA_SYNC = 0x102  # estado en que el módulo 0 queda parado sin Master (MEDIDO, g75 T61/T65: `[0x43ede338]`=2, mod0 = 0x102)


class Reloj:
    """Tras el registro de ClkCtrl y mientras el módulo 0 está en ESPERA_SYNC, manda un Master cada N tramas con `targetVfc` = VFC + N (el siguiente llega justo al cumplirse el anterior).
NO_VERIFICADO: disparador y cadencia fabricados. MEDIDO: un Master único, más temprano o de `targetVfc` viejo no sirve: `0x4378e114` calcula X = targetVfc − VFC
solo cuando el secuenciador pide el cambio (≈13 s) y un objetivo pasado deja X negativo para siempre."""
    prox = None

    def __init__(self, vm, tramas: int) -> None:
        self.vm, self.tramas, self.visto, self.registrado, self.ultimo = vm, tramas, 0, False, None
        vm.fuentes.append(self)

    def avanza(self, vm) -> None:  # noqa: ANN001
        import liro_vm as L
        ext = vm.salida_ext
        for _t, _tarea, _api, q, datos, _cab in ext[self.visto:]:
            d = bytes.fromhex(datos)
            if q == COLA_SERVICIO and len(d) >= 12 and struct.unpack_from("<2I", d)[0] == 1 and struct.unpack_from("<I", d, 4)[0] == COLA_CLK:
                self.registrado = True
        self.visto = len(ext)
        vfc = vm.rd(VFC)
        if not (self.registrado and vm.rd(MODULO0, 2) == ESPERA_SYNC and (self.ultimo is None or vfc - self.ultimo >= self.tramas)):
            return
        self.ultimo = vfc
        vm.wr(ROL, 2, 1)
        objetivo = (vfc + self.tramas) & 0xFFFFFF
        m = vm.malloc(0x40 + 12 + 0x20) + 12
        vm.uc.mem_write(m - 12, struct.pack("<3I", 0, 1, ETIQUETA_MASTER))
        vm.uc.mem_write(m, struct.pack("<3I", objetivo, 1, 0))
        vm.msz[m] = 12
        L.entrega(vm, COLA_CLK, m)
        vm.log.append(f"{vm.t:9.1f} reloj (NO_VERIFICADO): Master targetVfc={objetivo:#x} (VFC {vfc})")


def instala(vm) -> Reloj | None:  # noqa: ANN001
    if os.environ.get("AVCAM_RELOJ", "0") in ("", "0"):
        return None
    r = Reloj(vm, int(os.environ.get("AVCAM_RELOJ_TRAMAS", "4")))
    vm.reloj = r
    return r
