"""E26-R25 — mapa completo de Loader3 (`bootloader.bin`, runtime 0xc01f0000..0xc0205800, INFO 5).

Misma metodología que R24 (Loader2): descenso recursivo sobre `r13_loader3.py` y derivación de
nombre por (1) cadena de registro (`LD3:`/`LD3_E:`/`LD3_W:`/`BOS_E:`/`CFG_E:`/`FAT_E:`/`INS_E:`)
referenciada en cualquier punto del cuerpo, (2) constante MMIO/eSRAM decisiva, (3) envoltorio de
una única función ya nombrada, (4) utilidad muy reutilizada. Solo lectura; no toca hardware.
Uso: python3 r25_loader3_map.py [salida.json]
"""

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import r13_loader3 as L

L.BASE, L.OFF, L.END = 0xC01F0000, 0x22800, 0xC01F0000 + 43 * 0x800

LOG_FN = (
    0xC01F3670  # confirmado: log(nivel, fmt, ...) — misma forma que Loader2 0xc0030980
)
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


# Confirmados por lectura directa (modo ARM, bytes o informes R5/R13/R15/R16/R17), ver R25 §2-4.
MANUAL = {
    0xC01F0000: (
        "exc_vectors",
        "ARM: tabla de vectores; reset -> 0xc01f0028; el resto -> 0xc01f0020 -> blx led_error_blink",
    ),
    0xC01F0020: (
        "exc_handler",
        "ARM: carga un código y llama directamente a led_error_blink (0xc01f3b74)",
    ),
    0xC01F0028: (
        "entry_arm",
        "ARM: pila, bl 0xc020e090/0xc020e024, salto a 0xc01f0070",
    ),
    0xC01F0070: (
        "mode_switch",
        "ARM: blx 0xc01f0078 (conmuta a Thumb) y blx thumb_entry (0xc01f01e0)",
    ),
    0xC01F0078: (
        "ctx_restore_jump",
        "ARM: ldm con pc — restaura r1/r3/sp/pc desde tabla y conmuta a Thumb",
    ),
    0xC01F01E0: (
        "thumb_entry",
        "despacha a 0xc01f11ec según el modo de arranque (R13 §3)",
    ),
    0xC01F11EC: (
        "boot_dispatch",
        "cadena principal; cualquier retorno != 0 de init/modo/carga acaba en 0xc01f1262 -> led_error_blink (R13)",
    ),
    0xC01F3670: (
        "log",
        "log(nivel,fmt,...): vsnprintf + consola — misma forma que Loader2 0xc0030980",
    ),
    0xC01F3B74: (
        "led_error_blink",
        "patrón −n -> n/1000,(n%1000)/100,n%100, d=0x3d0900; gemela de Loader2 0xc0030c7c (R13)",
    ),
    0xC01F2C98: (
        "bos_load",
        "BOS_E:Load partition error/Partition signature error — tabla BOS en 0xc00e04ac (R13 P1)",
    ),
    0xC01F2F24: (
        "cfg_load_file",
        "CFG_E:Load file — carga un archivo de la lista RAMCFG (R13 P2)",
    ),
    0xC01F2B7C: (
        "bos_read",
        "lee la tabla de particiones BOS; firma esperada 0x36343238 (R13 P1)",
    ),
    0xC01F3D8A: (
        "fat_check_id",
        "FAT_E:FAT ID.../not supported — valida el byte de ID de la FAT (R13 P3)",
    ),
    0xC01F3E54: (
        "fat_check_pbr",
        "FAT_E:PBR... — valida el sector de arranque (marca 0xAA55, 512 B/sector) (R13 P4)",
    ),
    0xC01F3EB6: (
        "fat_mount",
        "monta la partición; literal usado con -4 -> -306 'Not initialized yet' (R13 P7)",
    ),
    0xC01F3FD0: ("fat_next_cluster", "FAT_E:End of cluster chain (R13 P6)"),
    0xC01F407E: (
        "fat_dirent_type",
        "FAT_E:Unknown Fat Type — tipo de FAT guardado fuera de {12,16} (R13 P5)",
    ),
    0xC01F4654: (
        "fat_load_file",
        "abre/lee un archivo de la FAT; <=0 -> fallo (CFG_E:Mount part / P2)",
    ),
    0xC01FDD8E: (
        "tpzl_block_read",
        "lector TPZL: residuo=offset&0x1ff (solo aviso si !=0), sectores=(residuo+tamaño+0x1ff)>>9 (R15/R16)",
    ),
    0xC01FE006: (
        "tpzl_toc_lookup",
        "valida índice de bloque < entradas y llama a tpzl_block_read (R15/R16)",
    ),
    0xC01F2282: (
        "ramcfg_skip_decide",
        "v=ramcfg_skip_flag(); v en {1,2} y !=6 -> consulta c01f5f18; !=0 -> 1 'omitir' (R15 §10)",
    ),
    0xC01F4F88: (
        "wait_timer",
        "espera sobre 0xf2403000+0xc (TMCS_FREERUN|TMCK_DIV2, 0x31/0x1031) — mismo SoC que BootROM/Loader2",
    ),
}


def derive_name(f: int, body, callers) -> tuple[str, str]:
    if f in MANUAL:
        return MANUAL[f]
    # 1) cadena de registro (LD3:/LD3_E:/LD3_W:/BOS_E:/CFG_E:/FAT_E:/INS_E:) en cualquier punto del cuerpo
    for a, m, o, lit in body:
        s = None
        if lit is not None:
            s = L.cstr(lit)
        elif m == "adr":
            s = L.cstr(adr_target(a, o))
        if s:
            tag = TAGS.match(s)
            if tag and tag.group(1)[:-1] in (
                "LD3",
                "LD3_E",
                "LD3_W",
                "BOS_E",
                "CFG_E",
                "FAT_E",
                "INS_E",
                "LBK_E",
                "ERROR",
            ):
                note = s.split("\n")[0][:70] or repr(s[:40])
                return (f"log_{tag.group(1)[:-1].lower()}", note)
    # 2) MMIO/eSRAM literal decisivo
    mmio = [
        lit
        for *_, lit in body
        if lit is not None
        and (
            0x40000000 <= lit < 0x60000000
            or 0xC0000000 <= lit < 0xC0210000
            or 0xF0000000 <= lit < 0xF0100000
        )
    ]
    if mmio:
        return ("mmio_access", "toca " + ", ".join(sorted({hex(x) for x in mmio})[:4]))
    # 3) envoltorio de una única función ya nombrada
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
    # 4) utilidad muy reutilizada
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
    cat = Counter(r["name"].split("_")[0].split(":")[0] for r in rows)
    res = {"total_funciones": len(rows), "por_categoria": dict(cat), "funciones": rows}
    json.dump(res, out.open("w") if out else sys.stdout, indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else None)
