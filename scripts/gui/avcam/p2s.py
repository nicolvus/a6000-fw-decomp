"""Fin de transferencia del P2S del imager en la LIRO VM (E2E-12c, g75 T48).

VERIFICADO leyendo av-cam 3.21 (Capstone):
- Canal `c` del P2S = registros de la tabla `0x4401f2b0` (12 B: control `0xfc088300`/`0xfc089300`, disparo `0xfc088800`/`0xfc089800`, estado `0xfc088900`/`0xfc089900` para c=1/2).
  `0x436d5cdc` programa el canal (`0x436d5e58` pone el bit 0 del control = habilitar), espera el flag 0x10 de `0x18` (`twai_flg`, 1 ms; «P2S Error: Last trans is not end -50»
  si no llega), registra el objeto (`0x436d594c`) y dispara con `0x436d5f60`: escribe 1, 0, 1 en `disparo+8`.
- Quien lo pone es el manejador del canal (`0x436d59dc` c=1, `0x436d5a18` c=2): `0x436d5fdc` activa el bit 0 de `[estado+4]` y `0x43ad8d7c` hace `set_flg(0x18, [obj+8])`.
  Lo registra `0x436d66dc` en la ranura 0/1 de la tabla `0x43e7ebf0`; la despacha el ISR de la interrupción `0x88` (`0x436cf278`), que lee el índice pendiente en `0xfc01ff00`
  (valor > 13 = error), llama a `ranura[índice]` y termina escribiendo 1 en `0xfc01ff00` (EOI).
INFERENCIA / NO_VERIFICADO: que el disparo `+8` sea lo que arranca la transferencia (VERIFICADO solo que lo escribe el driver justo tras registrar), la duración de la transferencia (aquí `RETARDO_MS`), la máscara de habilitación `0xfc01f010` (no se consulta) y que hay una transferencia por pulso 1,0,1.
"""
from __future__ import annotations

from unicorn import UC_HOOK_MEM_READ, UC_HOOK_MEM_WRITE

CANALES = {0xFC088808: 0, 0xFC089808: 1}  # registro de disparo → ranura del despachador (tabla `0x43e7ebf0`)
IRQ, INDICE = 0x88, 0xFC01FF00
RETARDO_MS = 0.0


class P2s:
    prox = None

    def __init__(self, vm) -> None:
        self.vm, self.pend, self.fin, self.hist = vm, [], [], {}
        for pg in {a & ~0xFFF for a in (*CANALES, INDICE)}:
            if pg not in vm.mmio:
                vm.uc.mem_map(pg, 0x1000)
                vm.mmio[pg] = [0, 0, 0]
        vm.fuentes.append(self)
        for ctrl in CANALES:
            vm.uc.hook_add(UC_HOOK_MEM_WRITE, self._arranque, None, ctrl, ctrl + 3)
        vm.uc.hook_add(UC_HOOK_MEM_READ, self._indice, None, INDICE, INDICE + 3)
        vm.uc.hook_add(UC_HOOK_MEM_WRITE, self._eoi, None, INDICE, INDICE + 3)
        vm.lineas[IRQ] = lambda: bool(self.pend)

    def _arranque(self, uc, acc, addr, size, val, _) -> None:
        h = self.hist.setdefault(addr & ~3, [])
        h.append(val & 1)
        if h[-3:] == [1, 0, 1]:  # el pulso 1,0,1 de `0x436d5f60`: el fin llega tras su última escritura
            self.fin.append((self.vm.t + RETARDO_MS, addr & ~3))
            self.prox = min(t for t, _a in self.fin)
            if RETARDO_MS == 0:
                uc.emu_stop()  # el manejador del fin interrumpe a la tarea antes de que av-cam desregistre el objeto (`0x436d58f4`)
        del h[:-3]

    def avanza(self, vm) -> None:
        hechos = [f for f in self.fin if f[0] <= vm.t]
        self.fin = [f for f in self.fin if f[0] > vm.t]
        for _t, ctrl in hechos:
            if CANALES[ctrl] not in self.pend:
                self.pend.append(CANALES[ctrl])
        self.prox = min((t for t, _a in self.fin), default=None)

    def _indice(self, uc, acc, addr, size, val, _) -> None:
        self.vm.wr(INDICE, self.pend[0] if self.pend else 0xFF)

    def _eoi(self, uc, acc, addr, size, val, _) -> None:
        if self.pend:
            self.pend.pop(0)


def instala(vm) -> P2s:
    p = P2s(vm)
    vm.p2s = p  # type: ignore[attr-defined]
    return p
