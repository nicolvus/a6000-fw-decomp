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

import json
from pathlib import Path

import liro_vm as L
import montura
from unicorn import UC_HOOK_MEM_WRITE

GPIO = 0xF2910000
CS, DATA_OUT = (5, 4), (2, 0xB)           # salidas del cuerpo (puerto, pin)
DATA_IN, LENS_IN = (0, 5), (2, 0xA)        # entradas que maneja el objetivo
UART = 0xF2001000
DESCRIPTORES = 0x4401CA4A  # tabla `{u16 id, u16 size, u16 extra}` de la montura (`[0x43fea2a0]`, VERIFICADO leyendo el runtime; `extra` = tamaño de la respuesta con ID)
IRQ_DATA_IN = 121 + DATA_IN[1]  # GPIO_S(5) = 0x7e (irqs.h del núcleo OSS: IRQ_GPIO_BASE 121 + bit; puerto 0 = GPIO_S)
Q_CA, Q_CA_POLL = 0x150309, 0x150306
RETARDO_CA_MS, RETARDO_SONDEO_MS = 50.0, 30.0   # INFERENCIA: orden de magnitud; el emisor real (CA) no está identificado


RETARDO_RESPUESTA_MS = 2.0   # INFERENCIA: el objetivo contesta unos ms tras el fin de la trama del cuerpo (av-cam espera ~940 ms por respuesta síncrona)


def trama(tipo: int, ident: int, datos: bytes = b"", param: int = 0) -> bytes:
    """Trama BL `F0 len16 tipo param ID datos cksum16 55` (VERIFICADO, analysis/s66/mount_functions.md §3.1; checksum = suma de `buf[1:len-3]`)."""
    n = len(datos) + 9  # longitud total: 5 de cabecera + ID + datos + 2 de checksum + pie
    cuerpo = n.to_bytes(2, "little") + bytes([tipo & 7, param, ident]) + datos
    return b"\xf0" + cuerpo + (sum(cuerpo) & 0xFFFF).to_bytes(2, "little") + b"\x55"


_J = json.loads((Path(__file__).with_name("objetivo_16-50.json")).read_text())
TRAMAS, REGIMEN = _J["tramas"], _J["regimen"]  # ID → datos de la respuesta / tramas tipo 1 de régimen (volcado real)


REGLAS = {  # ID → datos de la respuesta calculados de la trama `f` del cuerpo
    # UART_HZ: el analizador (`0x436e6620`) solo lee el bit 0 (aceptado); la RAM real fija 1500k (`[0x4401b1f0]` = 0xe1): MEDIDO igual con 1 y 3
    12: lambda f: b"\x01",
    # CS_POWER: el manejador (`0x436e4b64`) no mira el contenido (INFERIDO: eco de los 2 datos del cuerpo)
    11: lambda f: f[6:8],
    # STARTUP_INFO (11 B de datos): `0x436dfc30` copia bit a bit datos[1], datos[2]&0x3f a la estructura `0x43f9283d+2/+3`, que en la RAM real vale 0x01 / 0x00 (VERIFICADO);
    # datos[7] y datos[8] deben ser 0 (`0x436e4fce`: otro valor → error 0xc); el resto no lo lee ningún analizador localizado (INFERIDO a 0)
    9: lambda f: bytes([0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0]),
    # SYSTEM_HZ: el manejador (`0x436e4b98`) no mira el contenido (INFERIDO: eco)
    13: lambda f: f[6:7],
}


def respuestas(f: bytes, extra: int) -> list[bytes]:
    """Tramas con que contesta el objetivo a la trama `f` del cuerpo; `extra` = tamaño de la respuesta (ID incluido) del descriptor `{id,size,extra}`.
    Sin dato verificado ni regla, `extra-1` ceros (INFERIDO). Régimen (tipo 1): el cuerpo manda ID 3 y 4 cada VD y el objetivo contesta con ID 6 y 5
    (INFERIDO: tras la trama ID 4 y con su contador; los datos son tal cual de los anillos del volcado real).

    Manejadores de ID no cubiertos por REGLAS/TRAMAS (CS_RESET=16, CS_CREDIT=10, etc.):
    - `0x436e4c24` (VERIFICADO por Capstone): validador genérico de comando; recibe el ID en r0, rechaza 0xff, llama `0x43ad9d58` (lookup con r2=0x16) y, si se encuentra,
      construye un informe AM 0x125. No es específico de ID 16: es la ruta común de validación de comandos del cuerpo.
    - `0x436e505c` (VERIFICADO por Capstone): manejador concreto para ID 10 (CS_CREDIT, usa r2=0xa); si el lookup tiene resultado, copia 17 B (0x11) vía memcpy
      `0x439c5320`, procesa con `0x436e3894` y construye informe AM 0x125.
    El contenido real de las respuestas (IDs 10/16) proviene del hardware del objetivo vía la tabla de descriptores `{id,size,extra}` en runtime
    (`0x440240a8` → `0x43fea2a0`, inicializada en ejecución, no recuperable estáticamente). En el emulador, devolver `extra-1` ceros es funcional:
    av-cam las acepta y la montura llega a 5 (T35, 7/7 tests pasan). Sustituir solo si se captura del cámara real con autorización."""
    ident, param = f[5], f[4]
    if f[3] & 7 == 1:
        return [trama(1, i, bytes.fromhex(REGIMEN[str(i)]), param) for i in (6, 5)] if ident == 4 else []
    if ident in REGLAS:
        return [trama(2, ident, REGLAS[ident](f))]
    if (d := TRAMAS.get(str(ident))) is not None:
        return [trama(2, ident, bytes.fromhex(d))]
    return [trama(2, ident, bytes(extra - 1))] if extra else []


class Objetivo:
    def __init__(self, vm) -> None:
        self.vm = vm
        self.t_ca: float | None = None
        self.flanco = False
        self.pend: list[tuple[float, bytes]] = []   # (instante, trama) del objetivo por enviar
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
        vm.lineas[IRQ_DATA_IN] = self._irq_data_in
        vm.fuentes.append(self)

    def _linea(self, ent: tuple[int, int], alto: bool) -> None:
        a = GPIO + 0x100 * ent[0] + 0x10
        v = self.vm.rd(a)
        if ent == DATA_IN and alto and not v >> ent[1] & 1:
            self.flanco = True
        self.vm.wr(a, (v | 1 << ent[1]) if alto else (v & ~(1 << ent[1])))

    def _irq_data_in(self) -> bool:
        """Interrupción de flanco: se sirve una vez por flanco de subida."""
        f, self.flanco = self.flanco, False
        return f

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
                extra = self.vm.rd(DESCRIPTORES + 6 * f[5] + 4) & 0xFFFF
                for k, r in enumerate(respuestas(f, extra)):
                    self.pend.append((self.vm.t + RETARDO_RESPUESTA_MS + k * RETARDO_RESPUESTA_MS, r))
                self.vm.log.append(f"{self.vm.t:9.1f} [LENS] RX trama del cuerpo: {f.hex()}")

    # --- fuente de tiempo: la petición de CA y su sondeo
    @property
    def prox(self) -> float | None:
        t = [x[0] for x in self.pend]
        if self.hecho < 2 and self.t_ca is not None:
            t.append(self.t_ca + (RETARDO_SONDEO_MS if self.hecho else 0))
        return min(t, default=None)

    def avanza(self, vm) -> None:
        for x in [x for x in self.pend if vm.t >= x[0]]:
            self.pend.remove(x)
            self.uart.recibe(x[1])
            self.uart.avanza(vm)   # el DMAC de RX toma los datos antes de que la irq cierre la recepción
            vm.log.append(f"{vm.t:9.1f} [LENS] TX trama del objetivo: {x[1].hex()}")
            self._linea(DATA_IN, True)   # la subida de DATA_IN cierra la recepción en av-cam (irq 0x7e)
            self._linea(DATA_IN, False)
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
