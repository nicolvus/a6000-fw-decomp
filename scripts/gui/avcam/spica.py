"""Fin de trabajo del acelerador «Spica» (DFE/ISP) en la LIRO VM (E2E-15, g75 T67).

VERIFICADO leyendo av-cam 3.21 (Capstone; instancia 0 = `[hdl+0x68]`=`0xf3810000`, instancia 1 = `0xf3910000`, `hdl` = `0x43f22c80`/`0x43f22d30`):
- `SpicaApiExpandParam` (`0x43950b68`) y `SpicaApiExecute` (`0x43950bc8`) meten una entrada en una cola de 2 ranuras (`0x439533bc`: ranuras en `+8/+0xc` y `+0x10/+0x14`;
  si las dos están ocupadas devuelve 4 = el `SPC_ERR:0x04` de `Sequence_Movie`). Solo se vacían en el manejador de fin (`0x43950e54`, vía `0x43b53374`); nada más las libera.
- Arranque: `Execute` escribe 1 en `base+0x20` (`0x43b53244`). Estado en `base+0x10` y ack escribiendo lo leído en `base+0x14` (`0x43952a34`); máscara `base+0x18` (`0x11010`, `0x439526f4`).
  Bit `0x10` = fin de Execute (saca de la cola `hdl+0x20` y llama a su callback), `0x1000` = fin de Expand (cola `hdl+4`), `0x10000` = error (`0x43952a4a`).
- Interrupciones: tabla `0x43fd5cb0` {1, 0x51, 0, `0x43b52f5b`} y {1, 0x52, 0, `0x43b52f6f`}: instancia 0 → `0x51`, instancia 1 → `0x52`.
- Los canales DMA del bloque (`base+0x1200/0x1280/0x1300`) usan el ayudante `0x4390b8d8` cuyo «ocupado» es el bit 0 del control.
NO_VERIFICADO (fabricado): la latencia del trabajo (`LATENCIA_MS`), que Expand y Execute terminen juntos (`0x1010`) y que el hardware borre el bit 0 de los controles DMA al acabar."""
from __future__ import annotations

import os

from unicorn import UC_HOOK_MEM_READ, UC_HOOK_MEM_WRITE

INSTANCIAS = ((0xF3810000, 0x51), (0xF3910000, 0x52))  # (base MMIO, interrupción)
ESTADO, ACK, MASCARA, ARRANQUE = 0x10, 0x14, 0x18, 0x20
FIN = 0x10 | 0x1000  # Execute + Expand
DMA = (0x1200, 0x1280, 0x1300)
LATENCIA_MS = float(os.environ.get("AVCAM_SPICA_LATENCIA_MS", "1"))


class Spica:
    prox = None

    def __init__(self, vm) -> None:
        self.vm, self.estado, self.fin = vm, {}, {}
        vm.fuentes.append(self)
        for base, irq in INSTANCIAS:
            for pg in (base, base + 0x1000):
                if pg not in vm.mmio:
                    vm.uc.mem_map(pg, 0x1000)
                    vm.mmio[pg] = [0, 0, 0]
            self.estado[base] = 0
            vm.uc.hook_add(UC_HOOK_MEM_WRITE, self._escribe, base, base + ARRANQUE, base + ARRANQUE + 3)
            vm.uc.hook_add(UC_HOOK_MEM_WRITE, self._escribe, base, base + ACK, base + ACK + 3)
            vm.uc.hook_add(UC_HOOK_MEM_READ, self._lee, base, base + ESTADO, base + ESTADO + 3)
            vm.lineas[irq] = lambda b=base: bool(self.estado[b] & vm.rd(b + MASCARA))

    def _lee(self, uc, acc, addr, size, val, base) -> None:
        self.vm.wr(base + ESTADO, self.estado[base])

    def _escribe(self, uc, acc, addr, size, val, base) -> None:
        if addr == base + ACK:
            self.estado[base] &= ~val & 0xFFFFFFFF  # escribir 1 borra (el manejador devuelve lo que leyó)
        elif val & 1 and base not in self.fin:
            self.fin[base] = self.vm.t + LATENCIA_MS
            self.prox = min(self.fin.values())

    def avanza(self, vm) -> None:
        for base, t in list(self.fin.items()):
            if t <= vm.t:
                del self.fin[base]
                self.estado[base] |= FIN
                for d in DMA:  # el hardware libera los canales al acabar
                    vm.wr(base + d, vm.rd(base + d) & ~1)
        self.prox = min(self.fin.values(), default=None)


def instala(vm) -> Spica | None:
    if os.environ.get("AVCAM_SPICA", "1") == "0":
        return None
    s = Spica(vm)
    vm.spica = s
    return s
