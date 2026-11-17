"""Objetivo de kit E PZ 16-50mm F3.5-5.6 OSS en la LIRO VM (E2E-12, g75 T33): lado del objetivo del handshake de la montura.

VERIFICADO (volcado real `ram-servicio-20261020` + código de av-cam.bin): los pines salen de los descriptores GPIO `0x43f52b1c…0x43f52b64` (puerto, pin);
`gpio_get` lee `0xf2910000 + 0x100·puerto + 0x10`, `gpio_write` escribe +0x44 (alto) / +0x48 (bajo). El handshake `[HS]` (`0x436e48fc`, paso `[0x43e81250]`):
  CS (5,4) ← 1 → el objetivo sube DATA_IN (0,5) → el cuerpo sube DATA_OUT (2,0xb) → el objetivo sube LENS_IN (2,0xa) → CS ← 0 → DATA_IN baja → COMPLETE.
INFERENCIA: el objetivo responde al instante (av-cam espera hasta 5000 ms); los niveles siguen a las líneas del cuerpo.
`CA_REQ`: la montura (`0x436e4294`/`0x436e42f0`, colas síncronas `0x150309`/`0x150306`) arranca con una petición de «CA» (otro procesador/Darwin) que
NO está en ningún binario Linux: INFERENCIA, se inyecta la petición con el bit 0 del byte +7 a 1 (en la RAM real `[0x43e81240+0x3b]`=1) y luego el sondeo.
UART de la montura: PL011 en `0xf2001000` (canal 1, VERIFICADO por los accesos del controlador); aquí solo se da el estado de FIFO vacía (FR=0x90). Las tramas
del objetivo (ATTACH_INFO, STARTUP_INFO…) NO están emuladas todavía (g75 T33, siguiente paso).
"""
from __future__ import annotations

import liro_vm as L
import montura
from unicorn import UC_HOOK_MEM_WRITE

GPIO = 0xF2910000
CS, DATA_OUT = (5, 4), (2, 0xB)           # salidas del cuerpo (puerto, pin)
DATA_IN, LENS_IN = (0, 5), (2, 0xA)        # entradas que maneja el objetivo
UART = 0xF2001000
Q_CA, Q_CA_POLL = 0x150309, 0x150306
RETARDO_CA_MS, RETARDO_SONDEO_MS = 50.0, 30.0   # INFERENCIA: orden de magnitud; el emisor real (CA) no está identificado


class Objetivo:
    def __init__(self, vm) -> None:
        self.vm = vm
        self.t_ca: float | None = None
        self.hecho = 0   # 0 nada, 1 petición enviada, 2 sondeo enviado
        if GPIO not in vm.mmio:  # una página cubre los puertos 0-0xf del GPIO (0x100 cada uno)
            vm.uc.mem_map(GPIO, 0x1000)
            vm.mmio[GPIO] = [0, 0, 0]
        for p in (CS[0], DATA_OUT[0]):
            for off in (0x44, 0x48):
                vm.uc.hook_add(UC_HOOK_MEM_WRITE, self._gpio, None, GPIO + 0x100 * p + off, GPIO + 0x100 * p + off)
        self.uart = montura.instala(vm)
        self.uart.al_transmitir = self._tx
        self.tx_buf = bytearray()
        self.tramas: list[bytes] = []  # tramas BL completas enviadas por el cuerpo
        vm.fuentes.append(self)

    def _linea(self, ent: tuple[int, int], alto: bool) -> None:
        a = GPIO + 0x100 * ent[0] + 0x10
        v = self.vm.rd(a)
        self.vm.wr(a, (v | 1 << ent[1]) if alto else (v & ~(1 << ent[1])))

    def _gpio(self, uc, acc, addr, size, val, _) -> None:
        alto = addr & 0xFF == 0x44
        puerto = (addr - GPIO) >> 8
        if (puerto, 4) == CS and val & 1 << CS[1]:
            self._linea(DATA_IN, alto)
        elif (puerto, 0xB) == DATA_OUT and val & 1 << DATA_OUT[1]:
            self._linea(LENS_IN, alto)

    def _tx(self, datos: bytes) -> None:
        self.tx_buf += datos
        while (i := self.tx_buf.find(0xF0)) >= 0:
            del self.tx_buf[:i]
            n = self.tx_buf[1] if len(self.tx_buf) > 1 else 0
            if n < 8 or len(self.tx_buf) < n:
                break
            f = bytes(self.tx_buf[:n])
            del self.tx_buf[:n]
            if f[-1] == 0x55 and sum(f[1:-3]) & 0xFFFF == int.from_bytes(f[-3:-1], "little"):
                self.tramas.append(f)
                self.vm.log.append(f"{self.vm.t:9.1f} [LENS] RX trama del cuerpo: {f.hex()}")

    # --- fuente de tiempo: la petición de CA y su sondeo
    @property
    def prox(self) -> float | None:
        if self.hecho >= 2:
            return None
        return None if self.t_ca is None else self.t_ca + (RETARDO_SONDEO_MS if self.hecho else 0)

    def avanza(self, vm) -> None:
        if self.t_ca is None:
            if Q_CA in vm.qcb and Q_CA_POLL in vm.qcb and getattr(vm, "sensor_v", None) and vm.sensor_v.v_prox is not None:
                self.t_ca = vm.t + RETARDO_CA_MS
            return
        if self.hecho == 0 and vm.t >= self.t_ca:
            self._envia(Q_CA, 1)
            self.hecho = 1
        elif self.hecho == 1 and vm.t >= self.t_ca + RETARDO_SONDEO_MS:
            self._envia(Q_CA_POLL, 0)
            self.hecho = 2

    def _envia(self, q: int, bit: int) -> None:
        vm = self.vm
        m = vm.malloc(0x100) + 12
        p, d, o = vm.malloc(0x100), vm.malloc(0x100), vm.malloc(0x100)
        vm.wr(m, p)
        vm.wr(p + 0xC, d)   # petición: byte +7 bit 0 (0x436e4294)
        vm.wr(p + 0x28, o)  # respuesta: byte +5 (0x436e42f0)
        vm.uc.mem_write(d, bytes([0, 0, 0, 0, 0, 0, 0, bit]))
        vm.msz[m] = 0x40
        L.entrega(vm, q, m, True)


def instala(vm) -> Objetivo:
    o = Objetivo(vm)
    vm.objetivo = o  # type: ignore[attr-defined]
    return o
