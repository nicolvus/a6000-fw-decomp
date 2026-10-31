"""E26-R33 — `serial_entry` (`0xffff0fa0`) por emulación con las rutinas auxiliares sustituidas.

Mismo patrón que `r20_bootrom_selector.py`: se carga `bootrom.bin` en 0xffff0000 (Thumb) y se
sustituyen `get_flag0` (`0xffff0bd4`, lee `[0xc0010004]`), `get_flag1` (`0xffff0bda`, lee
`[0xc0010004+4]`) y `serial_receiver` (`0xffff0876`) por valores de retorno controlados. Cubre
las combinaciones de banderas de R23 §2; no emula la forma de onda (eso ya lo hace R21).
"""

import sys
from pathlib import Path

from unicorn import UC_ARCH_ARM, UC_HOOK_CODE, UC_MODE_THUMB, Uc
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0, UC_ARM_REG_SP

ROM = (
    Path(__file__).resolve().parents[2]
    / "analysis/camera-dumps/updater-20261020-175427/bootrom.bin"
)
BASE = 0xFFFF0000
ENTRY = 0xFFFF0FA0

FUNCS = {
    "trace": 0xFFFF0CB6,
    "get_flag0": 0xFFFF0BD4,
    "get_flag1": 0xFFFF0BDA,
    "rx_packet": 0xFFFF0876,
}
STOP = {
    "error_led": 0xFFFF0D62,
    "jump_ram": 0xFFFF0144,
}
MAX_STEPS = 400  # corta el bucle SIN_RECEPCION tras unas pocas vueltas


def run(get_flag0, get_flag1_seq, rx_packet_seq):
    """`get_flag1_seq`/`rx_packet_seq`: valores sucesivos por cada llamada (una lista basta
    para los escenarios que no reentran); el último valor se repite si se agota la lista."""
    rom = ROM.read_bytes()
    mu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    mu.mem_map(BASE, 0x8000)
    mu.mem_write(BASE, rom)
    mu.mem_map(0xC0000000, 0x100000)
    sp, ret_addr = 0xC00F0000, 0xFFFF2000
    mu.reg_write(UC_ARM_REG_SP, sp)
    mu.reg_write(UC_ARM_REG_LR, ret_addr | 1)
    por_dir = {a: n for n, a in {**FUNCS, **STOP}.items()}
    secuencia, fin, pasos = [], [], [0]
    g1_it, rx_it = iter(get_flag1_seq), iter(rx_packet_seq)
    g1_ultimo, rx_ultimo = [get_flag1_seq[-1]], [rx_packet_seq[-1]]

    def siguiente(it, ultimo):
        try:
            v = next(it)
            ultimo[0] = v
            return v
        except StopIteration:
            return ultimo[0]

    def codigo(uc, addr, _size, _):
        n = por_dir.get(addr)
        pasos[0] += 1
        if pasos[0] > MAX_STEPS:
            secuencia.append("...bucle_sin_cerrar")
            fin.append("bucle")
            uc.emu_stop()
            return
        if n is None:
            return
        if n in STOP:
            secuencia.append(n)
            fin.append(n)
            uc.emu_stop()
            return
        if n == "trace":
            secuencia.append("trace")
        elif n == "get_flag0":
            uc.reg_write(UC_ARM_REG_R0, get_flag0)
            secuencia.append(f"get_flag0->{get_flag0:#x}")
        elif n == "get_flag1":
            v = siguiente(g1_it, g1_ultimo)
            uc.reg_write(UC_ARM_REG_R0, v)
            secuencia.append(f"get_flag1->{v:#x}")
        elif n == "rx_packet":
            v = siguiente(rx_it, rx_ultimo)
            uc.reg_write(UC_ARM_REG_R0, v)
            secuencia.append(f"rx_packet->{v:#x}")
        uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR) | 1)

    mu.hook_add(UC_HOOK_CODE, codigo)
    mu.emu_start(ENTRY | 1, ret_addr, count=1_000_000)
    return secuencia, (fin[0] if fin else "retorno")


ESCENARIOS = {
    # get_flag1() 1.ª lectura == 1 -> salta la recepcion, va directo a jump_ram
    # (rx_packet no se llama nunca; el valor de rx_packet_seq es indiferente).
    "flag1==1 (1.a lectura)": {
        "get_flag0": 0,
        "get_flag1_seq": [1],
        "rx_packet_seq": [0],
    },
    # 1.a lectura != 1, 2.a lectura != 0 (ni 0 ni 1) -> error_blink(0x1001) directo,
    # sin consultar get_flag0 ni llamar a rx_packet.
    "flag1 ni 0 ni 1 (2.a lectura)": {
        "get_flag0": 1,  # no se consulta; se fija a 1 para comprobar que no influye
        "get_flag1_seq": [2, 2],
        "rx_packet_seq": [0],
    },
    # 1.a y 2.a lectura == 0, get_flag0() != 0 -> error_blink(0x1001).
    "flag1==0 dos veces, flag0!=0": {
        "get_flag0": 1,
        "get_flag1_seq": [0, 0],
        "rx_packet_seq": [0],
    },
    # flag1==0 dos veces, flag0==0 -> RECEPCION; rx_packet devuelve un error que no es
    # 0x3001 -> error_blink con ese mismo codigo (no se reescribe a 0x1001).
    "flag1==0, flag0==0, rx error distinto de 0x3001": {
        "get_flag0": 0,
        "get_flag1_seq": [0, 0],
        "rx_packet_seq": [0x3005],
    },
    # igual pero el error es 0x3001 (fallo de sincronismo) -> se reescribe a 0x1001.
    "flag1==0, flag0==0, rx 0x3001 (fallo de sincronismo)": {
        "get_flag0": 0,
        "get_flag1_seq": [0, 0],
        "rx_packet_seq": [0x3001],
    },
    # rx_packet acepta (0) -> SIN_RECEPCION; 3.a lectura de get_flag1 != 0 -> jump_ram
    # (motivo de arranque fijado por el paquete recien aceptado).
    "flag1==0, flag0==0, rx aceptado, 3.a lectura flag1!=0": {
        "get_flag0": 0,
        "get_flag1_seq": [0, 0, 1],
        "rx_packet_seq": [0],
    },
    # rx_packet acepta, 3.a lectura de flag1 == 0 -> reintenta: vuelve a RECEPCION
    # (llama a rx_packet otra vez). Con una 2.a vuelta que tambien acepta y una
    # 4.a lectura de flag1 != 0, cierra en jump_ram.
    "flag1==0, dos paquetes aceptados, cierra en jump_ram": {
        "get_flag0": 0,
        "get_flag1_seq": [0, 0, 0, 1],
        "rx_packet_seq": [0, 0],
    },
    # mismo caso pero sin que flag1 llegue a fijarse nunca -> bucle sin cerrar
    # (limite artificial del emulador, no del BootROM real).
    "flag1 nunca se fija, bucle": {
        "get_flag0": 0,
        "get_flag1_seq": [0, 0, 0, 0, 0, 0, 0, 0],
        "rx_packet_seq": [0] * 20,
    },
}

if __name__ == "__main__":
    for nombre, kw in ESCENARIOS.items():
        sec, fin = run(**kw)
        llamadas = [x for x in sec if not x.startswith("trace(")]
        print(f"{nombre:48} -> {fin:10} {' '.join(llamadas)}", file=sys.stdout)
