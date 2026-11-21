"""Fin de transferencia de los canales DMA del bloque RC (resize / corrección de distorsión) en la LIRO VM (E2E-15, g75 T67).

VERIFICADO leyendo av-cam 3.21 (Capstone) y por trazado de la réplica `e2e68`:
- Bloque `0xf3880000`. La clase de canal (`0x43b5078e…0x43b507e8`) usa `[obj+0x40]`=c: control `0xf3881000 + ((c+4)<<7)` (inicio = OR del bit 0, `0x43b507a2`), estado por nibble
  en `0xf3881000` (se borra escribiendo `0xf << 4c`, `0x43b507e6`) y máscara de interrupción en `0xf3881008` (el driver escribe `0xf000` = nibble 3, `0x43947638`).
- El ISR de cada canal (`0x43941cdc`) no lee MMIO: marca el canal hecho en software y, si el estado de la petición es 4, `0x43946e10` la pasa a 6 y llama a sus callbacks.
  Una petición (ranura de `[obj+0x44+4i]`, estado en `+0x164`: 1 reservada, 4 enviada `0x43b4ff41`) solo vuelve a quedar libre así; sin esa interrupción se agotan las 2 ranuras y `ResizeHSeqCt`
  falla con «[RC] request = NULL» (código 7, `0x439448b2`) y el pipeline de vídeo de `Sequence_Movie` no avanza.
- Interrupciones (manejadores `0x43941d6d…0x4394202d`; el primer argumento es un índice de ISR, no el id): cada manejador lleva cableado el driver de un id (`IRQ_ID`; los ids 7 y 10 no tienen interrupción). Cada driver tiene su objeto de canal `[drv+0xfc]` con `+0x3c` (canal de entrada), `+0x40` (canal de salida = nibble de la máscara; `0x43b50798`/`0x43b507ae`).
El cableado canal DMA → interrupción no está en ningún registro: aquí se reconstruye de las tablas de los drivers (driver cuyo canal de salida acaba; si hay varios, el de entrada arrancado en el mismo disparo): NO_VERIFICADO.
NO_VERIFICADO (fabricado): la latencia (`LATENCIA_MS`), que el bit 0 del control lo borre el hardware al acabar (el ayudante `0x4390b8d8` lo trata como «ocupado») y que el nibble de estado quede en `0xf`;
"""
from __future__ import annotations

import os
import struct

from unicorn import UC_HOOK_MEM_READ, UC_HOOK_MEM_WRITE

BASE = 0xF3881000
ESTADO, MASCARA = BASE, BASE + 8
CANALES = 11
LATENCIA_MS = float(os.environ.get("AVCAM_RC_LATENCIA_MS", "1"))


# id de función RC `[drv+0x6c]` → interrupción. VERIFICADO leyendo la tabla de literales de cada manejador (`0x43941d6c…0x4394202c`: el global que carga cada uno apunta al driver de ese id).
IRQ_ID = {0: 0x2E, 1: 0x2F, 2: 0x30, 3: 0x31, 4: 0x32, 5: 0x2A, 6: 0x2B, 8: 0x28, 9: 0x29, 11: 0x2C, 12: 0x2D}


def drivers(vm) -> list[tuple[int, int, int, int]]:
    """(id, canal de entrada, canal de salida, canal del DMAC PL080 `[chobj+0x4c]`) de cada driver RC en la RAM de av-cam: objeto con `[+0xfc]` → canal DMA cuyo registro base `[+0x14]` es el bloque RC y id `[+0x6c]` < 11."""
    ram = bytes(vm.uc.mem_read(0x43F00000, 0x100000))
    w = struct.unpack(f"<{len(ram) // 4}I", ram)
    res = []
    for i in range(0x6C // 4, len(w) - 0x40):
        p = w[i + (0xFC - 0x6C) // 4] if i + 0x40 < len(w) else 0
        if 0x43F00000 <= p < 0x44000000 and (p - 0x43F00000) // 4 + 0x11 < len(w):
            j = (p - 0x43F00000) // 4
            if w[j + 5] & 0xFFFFF000 in (BASE, BASE & ~0xFFFFF) and w[i] in IRQ_ID and w[j + 0x10] < CANALES and w[j + 0xF] < CANALES:
                res.append((w[i], w[j + 0xF], w[j + 0x10], w[j + 0x13]))
    return res


class Rc:
    prox = None

    def __init__(self, vm) -> None:
        self.vm, self.fin, self.pend, self.estado, self.ini = vm, {}, set(), 0, {}
        vm.fuentes.append(self)
        if BASE not in vm.mmio:
            vm.uc.mem_map(BASE & ~0xFFF, 0x1000)
            vm.mmio[BASE & ~0xFFF] = [0, 0, 0]
        for c in range(CANALES):
            a = BASE + ((c + 4) << 7)
            if (a & ~0xFFF) != BASE:
                continue
            vm.uc.hook_add(UC_HOOK_MEM_WRITE, self._inicio, c, a, a + 3)
        for i, n in IRQ_ID.items():
            vm.lineas[n] = lambda i=i: i in self.pend and not self.pend.discard(i)  # pulso: se sirve una vez (el ISR no lee MMIO)
        vm.uc.hook_add(UC_HOOK_MEM_WRITE, self._ack, None, ESTADO, ESTADO + 3)
        vm.uc.hook_add(UC_HOOK_MEM_READ, self._lee, None, ESTADO, ESTADO + 3)

    def _inicio(self, uc, acc, addr, size, val, c) -> None:
        if val & 1 and c not in self.fin:
            self.fin[c] = self.vm.t + LATENCIA_MS
            self.ini[c] = self.vm.t
            self.prox = min(self.fin.values())

    def _lee(self, uc, acc, addr, size, val, _) -> None:
        self.vm.wr(ESTADO, self.estado)

    def _ack(self, uc, acc, addr, size, val, _) -> None:
        self.estado &= ~val & 0xFFFFFFFF  # escribir 1 borra el nibble

    def avanza(self, vm) -> None:
        for c, t in list(self.fin.items()):
            if t <= vm.t:
                del self.fin[c]
                a = BASE + ((c + 4) << 7)
                vm.wr(a, vm.rd(a) & ~1)
                nib = (vm.rd(MASCARA) >> (4 * c)) & 0xF
                if nib:
                    self.estado |= nib << (4 * c)
                    cand = [d for d in drivers(vm) if d[2] == c]
                    if len(cand) > 1:  # canal de salida compartido: el driver cuyo canal de entrada arrancó con él (mismo disparo)
                        cand = [d for d in cand if abs(self.ini.get(d[1], -9.0) - self.ini.get(c, 9.0)) <= 0.5] or cand
                    self.pend.update(d[0] for d in cand)
        self.prox = min(self.fin.values(), default=None)


    def fin_dmac(self, canal: int, dst: int) -> None:
        """Fin de una cadena del DMAC PL080 cuyo destino es el bloque RC (`0xf388xxxx`). Peticiones «directas» ([req+0x114]==1, p. ej. el driver vertical id 9): VERIFICADO en bytes que la ruta (`0x43b513b6`, `0x43b50688` → `0x4398f454`) no arranca los canales `0xf3881xxx`: solo carga por DMAC la secuencia
        (tablas y un `0xc` a `0xf3880044` por línea) y espera la IRQ del driver. NO_VERIFICADO: que el RC la levante al terminar la secuencia y la latencia (pulso inmediato)."""
        if os.environ.get("AVCAM_RC_DIRECTO", "1") == "0" or dst >> 16 != 0xF388:
            return
        self.pend.update(d[0] for d in drivers(self.vm) if d[3] == canal)


def instala(vm) -> Rc | None:
    if os.environ.get("AVCAM_RC", "1") == "0":
        return None
    r = Rc(vm)
    vm.rc = r
    return r
