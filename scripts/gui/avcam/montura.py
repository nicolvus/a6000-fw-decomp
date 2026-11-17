"""Canal UART de la montura en la LIRO VM (E2E-12, g75 T34): PL011 del canal 1 (`0xf2001000`) y el DMAC (`0xf0102000`) que lo alimenta.

VERIFICADO leyendo av-cam 3.21 y MEDIDO en la VM:
- Interrupción de la UART del canal 1 = `0x97` (stub `0x43b5e666`: `movs r0,#1; b 0x439918ac`). El manejador lee MIS (`+0x40`), borra con ICR (`+0x44`=0xff2)
  y despacha los callbacks por bit: TX bit 5, RX bit 4, RT bit 6, errores bits 7/8..10/11.
- Envío (`0x43a1c5f4`): DMAC canal 1 `src=buffer`, `dst=0xf2001000`, control `0x9609900c` (12 palabras de 32 bit, anchura de origen 4 B) y luego DMACR (`+0x48`) bit 1
  (TXDMAE, `0x43991cfc`). Recepción (`0x43a1c29e`): DMAC canal 0 `src=0xf2001000`, `dst=buffer`, 0x200 transferencias, RXDMAE (bit 0); lo que no llena
  una ráfaga lo recoge la interrupción RT por PIO (`0x43a1c260`, hasta 16 B por `0x43991cc0`).
- DMAC = PL080: controlador `0xf0102000 + 0x1000·(canal>>3)`, canal `c` en `+0x100+0x20·(c&7)`: SRC +0, DST +4, LLI +8, CONTROL +0xc (bits 11:0 = transferencias,
  20:18 anchura origen, 23:21 anchura destino), CONFIG +0x10 (bit 0 = habilitado; el hardware lo baja al terminar: `0x4398f8b0` sondea ese bit). Estado: +0x04 TC, +0x0c error,
  +0x08/+0x10 borrado.
INFERENCIA / NO_VERIFICADO: la FIFO de 16 B y el umbral de RX (IFLS) del PL011 estándar; la UART entrega a RX-DMA solo múltiplos de la ráfaga (`RAFAGA`); el DMAC
no genera interrupción propia (el driver sondea CONFIG).
"""
from __future__ import annotations

import collections
from collections.abc import Callable

from unicorn import UC_HOOK_MEM_READ, UC_HOOK_MEM_WRITE

UART, IRQ_UART, IRQ_DMAC = 0xF2001000, 0x97, 0xAD
DMAC = 0xF0102000
FIFO, RAFAGA = 16, 8  # profundidad del PL011 y bytes que pide a RX-DMA (INFERENCIA: umbral 1/2)
RXIS, TXIS, RTIS = 1 << 4, 1 << 5, 1 << 6


class Dmac:
    """PL080 con dos controladores de 8 canales; solo los periféricos de la montura (UART canal 1) son extremos de transferencia por petición."""

    def __init__(self, vm, uart: Pl011) -> None:
        self.vm, self.uart = vm, uart
        uart.dmac = self
        for ctrl in (DMAC, DMAC + 0x1000):
            if ctrl not in vm.mmio:
                vm.uc.mem_map(ctrl, 0x1000)
                vm.mmio[ctrl] = [0, 0, 0]
            vm.uc.hook_add(UC_HOOK_MEM_WRITE, self._escribe, ctrl, ctrl + 0x100, ctrl + 0x2FF)
            vm.uc.hook_add(UC_HOOK_MEM_WRITE, self._borra, ctrl, ctrl + 0x08, ctrl + 0x13)
            for c in range(8):  # interrupción de cada canal: 0xad + canal (stubs `0x43b5e1a8…` → `0x4398ee98(canal)`, que lee IntStatus bit canal)
                irq = IRQ_DMAC + 8 * (ctrl != DMAC) + c
                vm.lineas[irq] = lambda ctrl=ctrl, c=c: bool(vm.rd(ctrl) >> c & 1)

    def _ch(self, ctrl: int, off: int) -> int:
        return ctrl + 0x100 + 0x20 * ((off - 0x100) // 0x20)

    def _escribe(self, uc, acc, addr, size, val, ctrl) -> None:
        if (addr - ctrl - 0x100) % 0x20 == 0x10 and val & 1:  # CONFIG con el bit de habilitación
            self.uart.sucio = True  # el gancho corre antes del store: la transferencia se procesa en `avanza`, con la memoria ya escrita

    def _borra(self, uc, acc, addr, size, val, ctrl) -> None:
        """IntTCClear (+0x08) e IntErrClr (+0x10): bajan los bits de estado (el valor escrito en el propio registro es irrelevante)."""
        for r in ((0x00, 0x04) if addr - ctrl < 0x10 else (0x00, 0x0C)):
            self.vm.wr(ctrl + r, self.vm.rd(ctrl + r) & ~val)

    def _regs(self, ctrl: int, c: int) -> tuple[int, int, int, int]:
        b = ctrl + 0x100 + 0x20 * c
        return self.vm.rd(b), self.vm.rd(b + 4), self.vm.rd(b + 0xC), self.vm.rd(b + 0x10)

    def mueve(self) -> None:
        """Avanza los canales habilitados cuyo extremo (UART) ya pide datos."""
        vm, u = self.vm, self.uart
        for ctrl in (DMAC, DMAC + 0x1000):
            for c in range(8):
                src, dst, ctl, cfg = self._regs(ctrl, c)
                if not cfg & 1:
                    continue
                n, sw = ctl & 0xFFF, 1 << (ctl >> 18 & 7)
                b = ctrl + 0x100 + 0x20 * c
                if dst == UART and u.dmacr & 2 and u.cr & 0x100:  # memoria → UART (TXDMAE y TXE)
                    u.transmite(bytes(vm.uc.mem_read(src, n * sw)))
                    vm.wr(b + 0xC, ctl & ~0xFFF)
                    self._fin(ctrl, c, b)
                elif src == UART and u.dmacr & 1 and u.cr & 0x200:  # UART → memoria (RXDMAE y RXE)
                    while n and len(u.fifo) >= min(RAFAGA, FIFO):  # el DMAC empaqueta: n cuenta transferencias de origen (1 B) y el destino avanza 1 B
                        vm.uc.mem_write(dst, bytes([u.fifo.popleft()]))
                        dst, n = dst + 1, n - 1
                    vm.wr(b + 4, dst)
                    vm.wr(b + 0xC, (ctl & ~0xFFF) | n)
                    u.sincroniza()
                    if not n:
                        self._fin(ctrl, c, b)

    def _fin(self, ctrl: int, c: int, b: int) -> None:
        self.vm.wr(b + 0x10, self.vm.rd(b + 0x10) & ~1)
        ctl = self.vm.rd(b + 0xC)
        self.vm.wr(ctrl + 0x04, self.vm.rd(ctrl + 0x04) | 1 << c)
        if ctl >> 31:  # bit I del control: interrupción de fin de transferencia
            self.vm.wr(ctrl, self.vm.rd(ctrl) | 1 << c)


class Pl011:
    def __init__(self, vm) -> None:
        self.vm = vm
        self.dmac: Dmac | None = None
        self.fifo: collections.deque[int] = collections.deque()
        self.tx = bytearray()
        self.al_transmitir: Callable[[bytes], None] | None = None
        self.ris = 0
        self.sucio = True
        vm.fuentes.append(self)
        if UART not in vm.mmio:
            vm.uc.mem_map(UART, 0x1000)
            vm.mmio[UART] = [0, 0, 0]
        uc = vm.uc
        uc.hook_add(UC_HOOK_MEM_READ, self._lee_dr, None, UART, UART + 3)
        uc.hook_add(UC_HOOK_MEM_WRITE, self._escribe_dr, None, UART, UART + 3)
        for off in (0x30, 0x38, 0x44, 0x48):
            uc.hook_add(UC_HOOK_MEM_WRITE, self._escribe, off, UART + off, UART + off + 3)
        vm.lineas[IRQ_UART] = lambda: bool(self.mis)
        self.sincroniza()

    # registros que lee el driver (los de control se leen tal cual de la memoria)
    @property
    def cr(self) -> int:
        return self.vm.rd(UART + 0x30)

    @property
    def dmacr(self) -> int:
        return self.vm.rd(UART + 0x48)

    @property
    def imsc(self) -> int:
        return self.vm.rd(UART + 0x38)

    @property
    def mis(self) -> int:
        return self.ris & self.imsc

    def sincroniza(self) -> None:
        """FR (RXFE bit 4, RXFF bit 6, TXFE bit 7), RIS (RX por umbral, RT con datos pendientes) y MIS en la memoria: sin ganchos de lectura (ver `liro_vm.PAGINAS_PROPIAS`)."""
        n = len(self.fifo)
        self.ris = (self.ris & ~RXIS) | (RXIS if n >= RAFAGA else 0)  # RT es un evento (fin de ráfaga con datos pendientes): solo lo sube `recibe`
        self.vm.wr(UART + 0x18, 0x80 | (0x10 if not n else 0) | (0x40 if n >= FIFO else 0))
        self.vm.wr(UART + 0x3C, self.ris)
        self.vm.wr(UART + 0x40, self.mis)

    prox = None

    def avanza(self, vm) -> None:
        while self.sucio:
            self.sucio = False
            if self.dmac:
                self.dmac.mueve()
            self.sincroniza()

    def _lee_dr(self, uc, acc, addr, size, val, _) -> None:
        self.vm.wr(UART, self.fifo.popleft() if self.fifo else 0)  # el valor leído es el de la memoria: el dato se deja antes de la instrucción siguiente
        self.sincroniza()

    def _escribe_dr(self, uc, acc, addr, size, val, _) -> None:
        self.transmite(bytes([val & 0xFF]))

    def _escribe(self, uc, acc, addr, size, val, off) -> None:
        if off == 0x44:  # ICR
            self.ris &= ~val
        self.sucio = True  # idem: CR/IMSC/DMACR se leen tras el store

    def transmite(self, datos: bytes) -> None:
        self.tx += datos
        self.ris |= TXIS
        self.sucio = True
        if self.al_transmitir:
            self.al_transmitir(datos)

    def recibe(self, datos: bytes) -> None:
        """El objetivo envía `datos` por la línea RX: la FIFO se llena y RX-DMA toma lo que pueda."""
        self.fifo.extend(datos)
        self.ris |= RTIS  # INFERENCIA: la línea queda en reposo tras la ráfaga y vence el tiempo de espera del PL011 (32 bits)
        self.sucio = True


def instala(vm) -> Pl011:
    u = Pl011(vm)
    Dmac(vm, u)
    vm.uart_montura = u  # type: ignore[attr-defined]
    return u
