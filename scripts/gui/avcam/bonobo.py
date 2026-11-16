"""Temporizador/capturador de eventos «BONOBO» (`0xf3c30000`) y generador de la V del sensor para la LIRO VM (E2E-10).

Mapa de registros (VERIFICADO leyendo `0x436ccd9c…0x436cd234`, `0x436cce28`, `0x43ad607e` de av-cam.bin 3.21; el significado de cada número de evento es INFERENCIA):
  +0x04 estado: bit c = el canal de captura c vio su evento       +0x08 ack: escribir 1 en los bits a borrar (`0x436cd1b8`)
  +0x0c/+0x10 habilitación: activar = `+0xc &= ~bit; +0x10 |= bit` (`0x436cd19c`), desactivar al revés (`0x436cd1c4`)
  +0x20+4c valor capturado del contador al ocurrir el evento (lo lee `0x436cd1ec` y es el argumento del callback)
  +0x40+4c número de evento que escucha el canal c (8 canales)     +0xb4…+0xdc parámetro de modo del canal (siempre 1)
  +0xe0 contador libre (lectura)  +0xe4/+0xe8 preescala (`0x17`)  +0xec habilitar contador
  +0xf4 estado de los 10 temporizadores de un disparo (bit i), +0xfc su ack (escribir 1 en los bits a borrar; `0x436cce58`), +0xf8 = 0x3ff y +0x100 = 0 al iniciar
  (NO_VERIFICADO su sentido: aquí se ignoran)  +0x110+8i activar (≠0 arma, 0 cancela) y +0x114+8i valor de comparación = lectura ABSOLUTA del contador
  (`0x436cd234`: escribe el valor y luego el activar; la expiración reescribe 0 vía `0x43ad602c`); el valor lo arma av-cam (p. ej. `0x437927a0`: marca de la V + retardo)
La interrupción de los 8 canales es la `0x53` (`0x436cce28` lee +4, escribe el ack en +8 y llama al callback de cada bit); la de los temporizadores, la `0x54` (`0x436cce58`).
av-cam registra el evento `0x1c` (callback `0x43795c2c`: pone el bit `0x1000` de `flg 0x1a`) y el `0x1d` (callback `0x43791a7c`: el `HS_Main` de
`[CAMERA_MAIN_SYNC]`, que avanza el secuenciador `[0x43ede338]`); la hipótesis aquí es que ambos son las V del sensor (el nombre de los eventos es NO_VERIFICADO).
"""
from __future__ import annotations

from unicorn import UC_HOOK_MEM_READ, UC_HOOK_MEM_WRITE

BASE = 0xF3C30000
INT_CANALES, INT_TEMPORIZADORES = 0x53, 0x54
EVENTOS_V = (0x1C, 0x1D)
# Registro de estado del reloj/temporizador (`0xf3402028`, lo lee `0x43b4c2fc` en cada V y guarda el bit 0 en `[[0x43e99208+4]+0xc]`): INFERENCIA, es la paridad de la V
# (VD_Pre `0x43793826…0x43793844` compara `[G+0x78c]&1` con ese bit y reajusta el retardo de 2 V; y `0x43792e60…0x43792e80` solo refresca la tabla `G` de
# destinos del secuenciador cuando el bit vale 1 o el retardo ≤ 1). NO_VERIFICADO: los bits 1/2.
REG_PARIDAD = 0xF3402028
# Contador de V (`0xf3402098`, 32 bits; `0x43b4c2fc` lo lee dos veces por estabilidad y `0x4378e1d0` lo guarda en `[0x43e9baa8]`/`+4`). VERIFICADO con el volcado real
# `ram-servicio-20261020`: `[0x43e9baa8]` = 0x2812 y la marca de tiempo `[0x43e9bab0]` = 342 270 108 µs = 10 257,7 V de 33 367 µs; la paridad guardada (`+0xc`) = 0 = contador & 1.
# Sin él, `0x4378f848` (cola de `0x43791454`) ve siempre 0 == último contador atendido (`[0x43e992dc]`, 0x2811 en la cámara) y nunca actualiza el módulo 3 (`G+0x1290`).
REG_CONTADOR_V = 0xF3402098
# `vd` = periodo del VD (µs) que av-cam fija para el modo activo: `[[0x43e9920c]+0x24]` (la lee `EC_VD_Post` en `0x43791f76`/`0x43791f8a`; 33 367 µs medidos con las 14 órdenes
# de EE_START = 1001/30 ms, 29,97 Hz). INFERENCIA: la V del sensor es ese vd (EC_VD_Post compara un retardo de 18 000 µs con vd, y la V a 59,94 Hz lo contradiría);
# hasta que av-cam lo fije se usa el mismo valor.
OBJ_VD = 0x43E9920C
PERIODO_V_MS = 33.367
# Otros eventos de captura que av-cam registra en el primer VD (`0x43791aac` evento 0x1e → callback `0x437918ac`, que encola `0x4379155c` con el
# estado del módulo 1; `0x43791ac4` evento 0x17 → `0x4378f2cc`; VERIFICADO leyendo y MEDIDO con `0x436ccee4`). NO_VERIFICADO: qué señal de hardware son y
# su latencia tras la V; se toma media V (el callback 0x1e compara dos contadores de trama que la V reinicia y que a +26 ms ya se han movido: con < ~26 ms corre
# `0x4379155c` hasta su escritura `0x437916dc`; con 0 ms o ≥ 30 ms no).
EVENTOS_POST_V = ((0x1E, PERIODO_V_MS / 2), (0x17, PERIODO_V_MS / 2))
# NO_VERIFICADO: reloj de entrada del contador (preescala +0xe8 = 0x17); con 24 MHz/24 el contador cuenta µs
CONTADOR_HZ = 1_000_000


class Bonobo:
    def __init__(self, vm) -> None:  # noqa: ANN001
        self.vm = vm
        if BASE not in vm.mmio:
            vm.uc.mem_map(BASE, 0x1000)
            vm.mmio[BASE] = [0, 0, 0]
        vm.uc.hook_add(UC_HOOK_MEM_READ, self._lee, None, BASE + 0xE0, BASE + 0xE3)
        vm.uc.hook_add(UC_HOOK_MEM_WRITE, self._escribe, None, BASE + 0x08, BASE + 0x0B)
        vm.uc.hook_add(UC_HOOK_MEM_WRITE, self._escribe, None, BASE + 0xFC, BASE + 0xFF)
        vm.uc.hook_add(UC_HOOK_MEM_WRITE, self._arma, None, BASE + 0x110, BASE + 0x15F)
        vm.lineas[INT_CANALES] = lambda: bool(self.rd(0x04))
        vm.lineas[INT_TEMPORIZADORES] = lambda: bool(self.rd(0xF4))
        vm.fuentes.append(self)
        self.venc: dict[int, float] = {}  # temporizador i → tiempo virtual (ms) en que vence

    def rd(self, off: int) -> int:
        return self.vm.rd(BASE + off)

    def wr(self, off: int, v: int) -> None:
        self.vm.wr(BASE + off, v & 0xFFFFFFFF)

    def contador(self) -> int:
        return int(self.vm.t * CONTADOR_HZ / 1000) & 0xFFFFFFFF

    def _lee(self, uc, acc, addr, size, val, _) -> None:  # noqa: ANN001
        self.wr(0xE0, self.contador())

    def _escribe(self, uc, acc, addr, size, val, _) -> None:  # noqa: ANN001
        off = addr - BASE
        est = 0x04 if off == 0x08 else 0xF4
        self.wr(est, self.rd(est) & ~(val & 0xFFFFFFFF))

    def _arma(self, uc, acc, addr, size, val, _) -> None:  # noqa: ANN001
        off = addr - BASE - 0x110
        if off % 8:
            return
        i = off // 8
        if not val & 0xFFFFFFFF:
            self.venc.pop(i, None)
            return
        resta = (self.rd(0x114 + 8 * i) - self.contador()) & 0xFFFFFFFF
        self.venc[i] = self.vm.t + (resta / CONTADOR_HZ * 1000 if resta < 1 << 31 else 0.0)  # un valor ya pasado vence al instante

    @property
    def prox(self) -> float | None:
        return min(self.venc.values(), default=None)

    def avanza(self, vm) -> None:  # noqa: ANN001
        for i, t in list(self.venc.items()):
            if t <= vm.t:
                del self.venc[i]
                self.wr(0xF4, self.rd(0xF4) | 1 << i)

    def evento(self, n: int) -> None:
        """Ocurre el evento n: los canales habilitados que lo escuchan capturan el contador y levantan su bit de estado."""
        hab = self.rd(0x10)
        for c in range(8):
            if hab >> c & 1 and self.rd(0x40 + 4 * c) == n:
                self.wr(0x20 + 4 * c, self.contador())
                self.wr(0x04, self.rd(0x04) | 1 << c)


# Temporizadores de un disparo `0xf2403000 + canal·0x100` (literal de `0x43991200`). VERIFICADO leyendo av-cam: `+0` control (bits 0–2 modo, 4–5, 16 de `0x43991118`;
# bit 8 interrupción `0x439911d4`; bit 12 marcha `0x43991180`/`0x439911a8`), `+4` estado (el manejador escribe bit 0 = ack, `0x43991200`), `+8` cuenta. Interrupción por canal
# según los stubs de `def_inh` (`movs r0,#canal; b.w 0x43990f28`): canales 0xa–0xf → 0xa3–0xa8. Lo usa p. ej. `tsk0x5a` (`0x43a13418`, módulo 9): cuenta 0x24b8 en el canal 0xb.
# NO_VERIFICADO: reloj de la cuenta (se toma 1 MHz, como el BONOBO) y si el modo es periódico (se dispara una vez por arranque).
TMR_BASE = 0xF2403000
TMR_IRQ = {c: 0x99 + c for c in range(0xA, 0x10)}


class Temporizadores:
    def __init__(self, vm) -> None:  # noqa: ANN001
        self.vm = vm
        for c, irq in TMR_IRQ.items():
            pg = (TMR_BASE + 0x100 * c) & ~0xFFF
            if pg not in vm.mmio:
                vm.uc.mem_map(pg, 0x1000)
                vm.mmio[pg] = [0, 0, 0]
            a = TMR_BASE + 0x100 * c
            vm.uc.hook_add(UC_HOOK_MEM_WRITE, self._control, c, a, a + 3)
            vm.uc.hook_add(UC_HOOK_MEM_WRITE, self._ack, c, a + 4, a + 7)
            vm.lineas[irq] = lambda c=c: c in self.alto and bool(vm.rd(TMR_BASE + 0x100 * c) & 0x100)
        self.venc: dict[int, float] = {}
        self.alto: set[int] = set()
        vm.fuentes.append(self)

    def _control(self, uc, acc, addr, size, val, c) -> None:  # noqa: ANN001
        if val & 0x1000 and not self.vm.rd(addr) & 0x1000:
            self.venc[c] = self.vm.t + self.vm.rd(addr + 8) / CONTADOR_HZ * 1000
        elif not val & 0x1000:
            self.venc.pop(c, None)

    def _ack(self, uc, acc, addr, size, val, c) -> None:  # noqa: ANN001
        if val & 1:
            self.alto.discard(c)

    @property
    def prox(self) -> float | None:
        return min(self.venc.values(), default=None)

    def avanza(self, vm) -> None:  # noqa: ANN001
        for c, t in list(self.venc.items()):
            if t <= vm.t:
                del self.venc[c]
                self.alto.add(c)


class SensorV:
    """V del sensor: cada periodo ocurren los eventos de `EVENTOS_V` en el BONOBO."""

    def __init__(self, bonobo: Bonobo, periodo_ms: float = PERIODO_V_MS) -> None:
        self.bonobo, self.periodo = bonobo, periodo_ms
        self.v_prox: float | None = None  # `inicia` al acabar el arranque: la VM lo da por terminado al quedar en reposo
        self.n = 0
        self.pend: list[tuple[float, int]] = []  # (tiempo virtual ms, evento) de los EVENTOS_POST_V pendientes

    @property
    def prox(self) -> float | None:
        return min([self.v_prox, *(t for t, _ in self.pend)] if self.v_prox is not None else [t for t, _ in self.pend], default=None)

    def inicia(self, t: float) -> None:
        self.v_prox = t + self.periodo

    def periodo_ms(self, vm) -> float:  # noqa: ANN001
        o = vm.rd(OBJ_VD)
        vd = vm.rd(o + 0x24) if o else 0
        return vd / 1000 if 1000 < vd < 200_000 else self.periodo

    def _paridad(self, vm) -> None:  # noqa: ANN001
        pg = REG_PARIDAD & ~0xFFF
        if pg not in vm.mmio:
            vm.uc.mem_map(pg, 0x1000)
            vm.mmio[pg] = [0, 0, 0]
        n = (vm.rd(REG_CONTADOR_V) + 1) & 0xFFFFFFFF
        vm.wr(REG_CONTADOR_V, n)
        vm.wr(REG_PARIDAD, (vm.rd(REG_PARIDAD) & ~1) | (n & 1))

    def avanza(self, vm) -> None:  # noqa: ANN001
        if self.v_prox is not None and self.v_prox <= vm.t:
            self.pend += [(self.v_prox + dt, e) for e, dt in EVENTOS_POST_V]
            self.v_prox += self.periodo_ms(vm)
            self.n += 1
            self._paridad(vm)
            for e in EVENTOS_V:
                self.bonobo.evento(e)
        for t, e in [x for x in self.pend if x[0] <= vm.t]:
            self.pend.remove((t, e))
            self.bonobo.evento(e)


def instala(vm, periodo_ms: float = PERIODO_V_MS) -> SensorV:  # noqa: ANN001
    v = SensorV(Bonobo(vm), periodo_ms)
    vm.fuentes.append(v)
    Temporizadores(vm)
    vm.sensor_v = v  # type: ignore[attr-defined]
    return v
