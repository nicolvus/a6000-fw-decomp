"""E26-R22 — mapa completo del BootROM (0xffff0000–0xffff1a80): funciones, llamadores, MMIO y cadenas.

Descenso recursivo (Capstone) desde los vectores y los destinos BL/literales con bit 0. Solo lectura.
Uso: python3 r22_bootrom_map.py [salida.json]
"""

import json
import re
import struct
import sys
from collections import defaultdict
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

ROM = (
    Path(__file__).resolve().parents[1]
    / "camera-dumps/updater-20261020-175427/bootrom.bin"
)
B = 0xFFFF0000
END = 0x1A80  # el resto de los 0x6000 B es 0x00
ARM_END = 0x114  # vectores y arranque en modo ARM; después, Thumb
ENDERS = {"pop", "bx", "b", "b.w", "bxj"}


def load():
    return ROM.read_bytes()


def literal_addr(i):
    """Dirección absoluta del literal de `ldr rX,[pc,#imm]` (Thumb) o None."""
    if i.mnemonic.startswith("ldr") and "[pc" in i.op_str:
        m = re.search(r"#(-?0x[0-9a-f]+|-?\d+)\]", i.op_str)
        imm = int(m.group(1), 0) if m else 0
        return ((i.address + 4) & ~3) + imm
    return None


def descend(d: bytes, entries):
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    md.detail = True
    code, data, calls, owner = {}, set(), defaultdict(set), {}
    todo = [(e, e) for e in entries]
    seen = set()
    while todo:
        pc, fn = todo.pop()
        while B + ARM_END <= pc < B + END and pc not in seen:
            ins = list(md.disasm(d[pc - B : pc - B + 4], pc, 1))
            if not ins:
                break
            i = ins[0]
            seen.add(pc)
            code[pc], owner[pc] = i, fn
            la = literal_addr(i)
            if la is not None:
                data.update(range(la, la + 4))
            mn = i.mnemonic.split(".")[0]
            tgt = (
                int(i.op_str[1:], 0)
                if i.op_str.startswith("#")
                and (mn in ("b", "bl", "blx", "cbz", "cbnz") or mn.startswith("b"))
                else None
            )
            if i.mnemonic in ("cbz", "cbnz"):
                tgt = int(i.op_str.split("#")[1], 0)
            if i.mnemonic == "bl" and tgt:
                calls[fn].add(tgt)
                todo.append((tgt, tgt))
            elif (
                tgt
                and (mn == "b" or mn.startswith("b") or i.mnemonic in ("cbz", "cbnz"))
                and i.mnemonic not in ("bx", "blx", "bic", "bics")
            ):
                todo.append((tgt, fn))
            if (
                i.mnemonic in ("b", "b.w")
                or (mn == "pop" and "pc" in i.op_str)
                or i.mnemonic == "bx"
            ):
                break
            pc += i.size
    return code, data, calls, owner


def seed_entries(d: bytes):
    """Destinos con bit 0 en literales, `bl` lineales y arranque Thumb (0x114)."""
    out = {B + ARM_END}
    for o in range(0, END - 3, 4):
        w = struct.unpack_from("<I", d, o)[0]
        if B + ARM_END <= w - 1 < B + END and w & 1:
            out.add(w - 1)
    return sorted(out)


def build():
    d = load()
    entries = seed_entries(d)
    code, data, calls, owner = descend(d, entries)
    # segunda pasada: añadir destinos BL halladas
    for _ in range(3):
        found = {t for ts in calls.values() for t in ts} | set(entries)
        code, data, calls, owner = descend(d, sorted(found))
    funcs = sorted({owner[a] for a in code})
    return d, code, data, calls, owner, funcs


# dirección -> (nombre, función). Etiquetas de certeza en el informe R22.
NAMES = {
    0x0114: ("delay_ms_arm", "ARM: espera en ms (lazo de 0xdac0 iteraciones por ms)"),
    0x0104: (
        "fmt_ext_dispatch",
        "Thumb: extensión de printf; 'd'→0x1608, 'x'→0x167c, otro→0",
    ),
    0x013C: ("jump_main_image", "bx 0xc0030000 (Loader2 cargado)"),
    0x0144: (
        "jump_serial_image",
        "bx [0xc000500c+0xc] (destino fijado por la ruta serie)",
    ),
    0x0150: (
        "block_read",
        "lee N bloques vía 0x1352, vuelca estado al anillo de lectura, mapea códigos 0x3005/0x3006",
    ),
    0x0244: (
        "nand_ctrl_timing",
        "escribe tiempos del controlador de bloque (0x20100..0x20190)",
    ),
    0x028C: (
        "storage_init",
        "0x12d8 + marca [0xc0005024]=1 y puntero de anillo (0xc0010000)",
    ),
    0x02C6: ("load_boot_main", "block_read(0,3,0xd,6)→0xc0030000; error 0x1004/0x1005"),
    0x0332: ("load_header", "block_read(0,0,3,6)→0xc0000600; error 0x1006/0x1007"),
    0x039C: (
        "find_key_entry",
        "busca la 1.ª palabra ≠0xFFFFFFFF en la tabla 0xc0001200 (0x180 palabras) y copia 8 B",
    ),
    0x03DE: (
        "load_key_target",
        "block_read con campos de la tabla de clave → 0xc0000000; error 0x1008/0x1009",
    ),
    0x044E: (
        "check_loaded",
        "comprueba que 0xc0000000 (0x180 palabras) no es todo 0xFFFFFFFF",
    ),
    0x0486: (
        "load_payload",
        "copia 4 parámetros de la cabecera a 0xc0005000 y block_read; error 0x100a/0x100b",
    ),
    0x0514: (
        "ring_push",
        "añade una palabra al anillo 0xc000b000..0xc0010000 (puntero en 0xc0010000)",
    ),
    0x0554: ("serial_profile_select", "GPIO(4) bit21 → perfil en 0xc0010218 (R21)"),
    0x05DA: (
        "sample_confirm",
        "espera `filtro` ticks y reexamina MODEREG bit1 (error 0x3004 si cambia)",
    ),
    0x0634: (
        "serial_recv_bytes",
        "recibe N bytes 8O1 (paridad impar) por MODEREG bit1; acumula CRC; errores 0x100c/0x100d",
    ),
    0x0876: (
        "serial_receiver",
        "sincronismo 60 flancos + cabecera/longitud/carga (R8/R21)",
    ),
    0x0BD4: ("get_flag0", "devuelve [0xc0010004]"),
    0x0BDA: ("get_flag1", "devuelve [0xc0010004+4]"),
    0x0C00: ("crc32_byte", "CRC-32 reflejado 0xEDB88320, un byte"),
    0x0C18: ("crc32_update", "CRC-32 (buf,len,acc) — sin llamadores (código muerto)"),
    0x0C52: ("crc32", "CRC-32 completo con inversión final"),
    0x0C98: ("console_puts", "cadena → registro de consola [0xc0005030] + LF"),
    0x0CB6: (
        "trace",
        "(etapa,paso): anillo 0xc0006000..0xc000b000 y línea «%02d:%02d» a la consola",
    ),
    0x0D14: (
        "ctx_reset",
        "pone a cero 0xc0005030/40/50/60, 0xc0010238 y reinicia el anillo de traza",
    ),
    0x0D4C: ("led_gpio_init", "habilita las GPIO del LED (0xf2910000/0xf2912000)"),
    0x0D62: (
        "error_blink",
        "código → (c>>12)−1 largos + (c&0xfff) cortos, medio periodo 0x1e8480 ticks; no retorna",
    ),
    0x0E0A: (
        "error_blink_ms",
        "mismo patrón con delay_ms (500/250 ms, pausa 2000 ms); usado si falla el temporizador",
    ),
    0x0ED0: ("timer1_restart", "reinicia temporizador 1 (0xf2403100)"),
    0x0EE8: ("timer0_restart", "reinicia temporizador 0 (0xf2403000)"),
    0x0EFC: (
        "timer_init",
        "programa ambos temporizadores (0x1030) y comprueba que cuentan (0xe10 vueltas, si no 0x100e)",
    ),
    0x0F36: ("wait_t0", "espera a que temporizador 0 alcance r0"),
    0x0F52: ("wait_t1", "espera a que temporizador 1 alcance r0 (0 = ok)"),
    0x0F72: ("t0_expired", "-1 si temporizador 0 > r0"),
    0x0F82: ("t1_expired", "-1 si temporizador 1 > r0"),
    0x0FA0: (
        "serial_entry",
        "ruta serie: espera clave/bandera, llama serial_receiver y salta a la imagen",
    ),
    0x1062: (
        "main",
        "selector MODEREG bit0: 0 = Loader2 por almacenamiento; 1 = ruta de servicio",
    ),
    0x12D8: (
        "storage_ctrl_init",
        "reinicia/configura el controlador de bloque 0x20000",
    ),
    0x1352: (
        "read_sectors",
        "lector de sectores 0x600 B (FIFO 0x10000010), reintentos (R20)",
    ),
    0x1532: ("ctrl_reset", "pone/quita el reset del controlador (0x200f0 bit4)"),
    0x1584: ("snprintf", "snprintf(buf,n,fmt,…)"),
    0x15B8: ("pad_left", "relleno previo del campo (espacios/ceros)"),
    0x15E4: ("pad_right", "relleno posterior del campo"),
    0x1608: ("fmt_decimal", "conversión %d/%u"),
    0x167C: ("fmt_hex", "conversión %x/%X/%p"),
    0x16D8: ("vformat", "intérprete de formato (flags, anchura, conversiones)"),
    0x1814: ("memset_word", "memset con replicación del byte"),
    0x1824: ("emit_field", "emite un campo numérico con relleno"),
    0x18D8: ("fmt_getc", "siguiente carácter del formato"),
    0x18E2: ("vsnprintf", "inicializa el contexto y llama a vformat"),
    0x1908: ("putc_unbounded", "escribe un carácter y avanza"),
    0x1912: ("putc_bounded", "escribe un carácter si cabe"),
    0x1922: ("memclr", "memset(…,0)"),
    0x1926: ("memset", "memset general (alineación + 0x1998 en bloques)"),
    0x1968: ("divmod10", "ARM: r0=n → cociente en r0, resto en r1"),
    0x19E2: ("isdigit", "1 si '0'..'9'"),
}
SPECIAL = {  # regiones que no son funciones Thumb descubiertas
    (0x0000, 0x0020): "tabla de vectores ARM (reset → 0x58; resto → 0x20)",
    (
        0x0020,
        0x0058,
    ): "manejador de excepción/estacionamiento: log (5,núcleo) y error 0x1002",
    (
        0x0058,
        0x00E8,
    ): "reset ARM: id de núcleo, pila (0xc002f400+0x400·núcleo), marca; núcleo 0 → main, resto espera [0xc0005000+0x1c+n] y salta a [0xc000500c+4n]",
    (0x00E8, 0x0114): "pool de literales del arranque (+ 0x104 fmt_ext_dispatch)",
    (
        0x1288,
        0x12B8,
    ): "cadena de versión «Musashi Loader1 Ver.01.00 Dec  2 2011 10:45:17»",
    (0x12C8, 0x12D8): "cadena «KEY f:%x r:%x»",
    (0x0E7C, 0x0EC8): "cadenas «ERROR: Blinking LED…» / «ERROR: Loader boot failed...»",
    (0x1A48, 0x1A80): "dígitos hexadecimales (mayúsculas y minúsculas) para fmt_hex",
    (
        0x19F0,
        0x1A48,
    ): "tablas de muestreo serie (perfil bit21=0 en 0x19f0, bit21=1 en 0x1a1c)",
}


def table():
    *_, calls, _, funcs = build()
    callers = defaultdict(set)
    for f, ts in calls.items():
        for t in ts:
            callers[t].add(f)
    rows = []
    for a in sorted(NAMES):
        full = B + a
        n, role = NAMES[a]
        cs = sorted(callers.get(full, ()))
        rows.append((full, n, role, [hex(c)[-4:] for c in cs]))
    return rows, funcs


def main(out: Path | None):
    rows, funcs = table()
    known = {B + a for a in NAMES}
    sin_nombre = [hex(f) for f in funcs if f not in known and f not in (B + 0x116,)]
    res = {
        "funciones_con_nombre": len(rows),
        "funciones_descubiertas_sin_nombre": sin_nombre,
    }
    json.dump(res, out.open("w") if out else sys.stdout, indent=1)


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else None)
