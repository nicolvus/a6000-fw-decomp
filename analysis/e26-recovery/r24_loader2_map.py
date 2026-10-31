"""E26-R24 — mapa completo de Loader2 (`bootloader.bin`, runtime 0xc0030000..0xc0036c00).

Descenso recursivo sobre el desensamblado existente (`r13_loader3.py`, reapuntado a la base de
Loader2). Para cada función descubierta deriva un nombre a partir de:
  1. la cadena de registro (`LDR:`/`LDR_E:`/`BOS:`/`BOS_E:`/`INS_E:`/`LD3_W:`/`ERROR:`) que
     pasa como formato a la rutina de log (`log`, `0xc0030980`), si la llama directamente;
  2. constantes MMIO (`0xf2…`) o de eSRAM (`0xc0…`) que lee/escribe, si no hay cadena;
  3. su papel en el grafo de llamadas (hoja muy reutilizada = utilidad) en otro caso.
Solo lectura; no toca hardware. Uso: python3 r24_loader2_map.py [salida.json]
"""

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import r13_loader3 as L

L.BASE, L.OFF, L.END = 0xC0030000, 0x600, 0xC0030000 + 0x6C00

LOG_FN = 0xC0030980  # confirmado: log(nivel, fmt, ...) — vsnprintf + consola (R13 §*)
TAGS = re.compile(r"^([A-Z][A-Za-z0-9_]*:)")


def adr_target(addr: int, op: str) -> int:
    imm = int(op.split("#")[1], 16)
    return ((addr + 4) & ~3) + imm


def build():
    g, starts = L.build_graph()
    callers = defaultdict(set)
    for f, ts in g.items():
        for t in ts:
            callers[t].add(f)
    return g, starts, callers


def func_body(starts: list[int], f: int) -> list[tuple[int, str, str, int | None]]:
    i = starts.index(f)
    end = starts[i + 1] if i + 1 < len(starts) else L.END
    return L.disasm(f, end)


MANUAL = {  # confirmados por lectura directa (modo ARM o firmas de bytes), ver informe R24 §2
    0xC0030000: (
        "entry_arm",
        "ARM: pila, invalidación de caché (0x210/0x240), VIC (0x2a4), 0x110c/0x8b8/0x1094, salto a 0xc0036280 y 0x30054",
    ),
    0xC0030210: (
        "cache_invalidate",
        "ARM: invalida caché de datos por conjunto/vía (mcr p15,0,r2,c7,c6,2)",
    ),
    0xC0030240: (
        "cache_invalidate_i",
        "ARM: invalida caché de instrucciones (misma forma que 0x210)",
    ),
    0xC00302A4: (
        "vic_init",
        "ARM: enmascara IRQ (0xf8000000) y habilita el controlador de interrupciones",
    ),
    0xC003005C: (
        "ctx_restore_jump",
        "ARM: ldm con pc — restaura r1/r3/sp/pc desde una tabla y conmuta a Thumb (arranque del planificador)",
    ),
    0xC0036280: (
        "mmu_cache_setup",
        "ARM: desactiva bits de SCTLR (c1,c0,0) tras el arranque — apagado de caché/MMU previo al salto",
    ),
    0xC0030980: (
        "log",
        "log(nivel,fmt,...): vsnprintf (0xc0034870 memset + motor de formato) + consola; confirma R13",
    ),
    0xC0034870: (
        "memset",
        "memset: igual forma que BootROM 0xffff1926 (bloques de 0x20, relleno por tamaño decreciente)",
    ),
    0xC0034A76: (
        "fatal",
        "fatal(código): niega el código, llama a la rutina LED (0xc0030c7c) y no retorna (b self)",
    ),
    0xC0030C7C: (
        "led_error_blink",
        "patrón del LED de error: −n -> n/1000, (n%1000)/100, n%100; `log` ERROR: Blinking LED / Loader boot failed (R13)",
    ),
    0xC0032980: (
        "tcb_get",
        "lector de un campo de la tarea actual (tabla en 0xc00c8190) — forma idéntica en 0xc0032980..0xc00329bc (8 campos)",
    ),
    0xC0030DE8: (
        "load_rom_info",
        "INS_E:ROM size/info/Load ROM — lee la cabecera de la imagen y la carga (bl 0xc00306ce)",
    ),
    0xC0030054: (
        "mode_switch",
        "ARM: blx 0x3005c (conmuta a Thumb) y blx 0x301c4 (entrada Thumb)",
    ),
    0xC00301C4: (
        "thumb_entry",
        "Thumb: init global (0x3581a), entorno de tareas (0x30198), loader2_main (0x302d8); si retorna: fatal(0)",
    ),
    0xC0030198: (
        "task_env_init",
        "crea entorno/pila de tarea (0x34ad2/0x34f6c) y registra dos manejadores (0x363e0/0x3640c)",
    ),
    0xC00302D8: (
        "loader2_main",
        "secuencia de arranque completa (R24 §3): Init UDIF_P/D, InfSec_S, BOSS, Load InfSec_N/LBkup, Init DebugLv, Load LDR3, Exit UDIF_D/P, Jump LDR3",
    ),
    0xC00310B2: (
        "timer_read_us",
        "lee 0xf240310c (mismo temporizador que BootROM) >>1 para el «(%luus)» del log de salto a LDR3",
    ),
    0xC00310BC: (
        "timer_wait",
        "espera activa sobre 0xf2403000+0x10c (misma familia de temporizador que BootROM, R22)",
    ),
    0xC0030A18: (
        "mem_dump",
        "vuelca bytes en hex (formato '\\n%X: '/'%02X ') vía log — soporte de MEM_DUMP",
    ),
}


def derive_name(f: int, body, callers) -> tuple[str, str]:
    if f in MANUAL:
        return MANUAL[f]
    # 1) cadena de log pasada a LOG_FN (adr justo antes de un bl a 0xc0030980)
    for k, (a, m, o, lit) in enumerate(body):
        if m == "bl" and lit is None and o == f"#{LOG_FN:#x}":
            for a2, m2, o2, _ in reversed(body[max(0, k - 4) : k]):
                if m2 == "adr":
                    s = L.cstr(adr_target(a2, o2))
                    if s:
                        tag = TAGS.match(s)
                        note = s.split("\n")[0][:70] or repr(s[:40])
                        return (
                            f"log_{tag.group(1)[:-1].lower()}" if tag else "log_msg",
                            note,
                        )
    # 2) MMIO/eSRAM literal decisivo
    mmio = [
        lit
        for *_, lit in body
        if lit is not None
        and (
            0x40000000 <= lit < 0x60000000
            or 0xC0000000 <= lit < 0xC0100000
            or 0xF0000000 <= lit < 0xF0100000
        )
    ]
    if mmio:
        return ("mmio_access", "toca " + ", ".join(sorted({hex(x) for x in mmio})[:4]))
    # 3) utilidad muy reutilizada (sin cadena ni MMIO): nombrar por tamaño/forma
    # 4) hereda de un único destino bl/b.w directo si esa función ya está nombrada (envoltorio fino)
    bl_only = [
        o2 for a2, m2, o2, lit in body if m2 in ("bl", "b.w") and o2.startswith("#0x")
    ]
    if len(body) <= 6 and len(bl_only) == 1:
        t = int(bl_only[0][1:], 0)
        if t in MANUAL:
            return (
                f"envoltorio:{MANUAL[t][0]}",
                f"delega todo en {t:#x} ({MANUAL[t][0]})",
            )
    n = len(callers.get(f, ()))
    if n >= 8:
        return ("util_compartida", f"sin cadena de log; reutilizada por {n} funciones")
    return ("auxiliar", f"sin cadena de log ni MMIO directo; {n} llamador(es)")


def table():
    g, starts, callers = build()
    rows = []
    for f in starts:
        body = func_body(starts, f)
        size = (body[-1][0] + 2 - f) if body else 0
        name, note = derive_name(f, body, callers)
        rows.append(
            {
                "addr": hex(f),
                "name": name,
                "note": note,
                "size": size,
                "callers": len(callers.get(f, ())),
                "callees": len(g.get(f, ())),
            }
        )
    return rows


def main(out: Path | None):
    rows = table()
    cat = Counter(r["name"].split("_")[0] for r in rows)
    res = {"total_funciones": len(rows), "por_categoria": dict(cat), "funciones": rows}
    json.dump(res, out.open("w") if out else sys.stdout, indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else None)
