"""G56 — circuito genérico de «ajustes propios del CFW»: una entrada de menú guarda un byte en un id de Backup libre y un parche de `av-cam` lo lee.

Cadena (g56 §1): nodo de menú (CautionConfig) → ProcessId nuevo (pid_space, 0xE9…) → descriptor «solo respaldo» (plantilla nativa 0x55) → la UI escribe el
índice de la opción (1 B) en el id de Backup → persiste con el resto de la NVRAM → `av-cam` lo lee con `Backup_read(id, &byte)` (`0x435613b0`, el mismo que
usa en el arranque para restaurar EFCS, `0x43818380`).
Añadir un ajuste = una fila en `AJUSTES` (+ un parche que llame a `leer_asm`). Solo ficheros del `.dat` (`viewUnified2.so`, `CautionConfig.so`, `string_*.uxc`, `av-cam`).
`python3 scripts/cfw_ajustes.py DEV_A6000 DEV_A6300 SALIDA` escribe esos tres tipos de fichero (sin construir `.dat`).
"""
from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/gui"))
BACKUP_READ = 0x435613B0          # av-cam 3.21: Backup_read(r0 = id, r1 = búfer) vía tabla de servicios (+0x298)
PID_PRIMERO = 0xE9                # primer ProcessId nuevo (pid_space)
# Ids 1 B sin ningún literal en libs/bin/av-cam del 3.21 (volcados de 4 fechas, valor 0, mismo tamaño): hueco 0x1070208…0x1070219 (g56 §2)
ID_LIBRES = tuple(range(0x1070210, 0x107021A))


@dataclass(frozen=True)
class Ajuste:
    id: str
    label: str
    backup: int                   # id de Backup de 1 B
    opciones: tuple               # ((texto, valor), …); la UI escribe el índice de la opción (0…n-1); `valor` es lo que el parche de av-cam entiende (aquí segundos)
    pid: int = 0


AJUSTES = (
    Ajuste("bulb_timer", "Bulb Timer", ID_LIBRES[0],
           (("Off", 0), ("5 s", 5), ("10 s", 10), ("30 s", 30), ("1 min", 60), ("2 min", 120), ("5 min", 300), ("10 min", 600), ("15 min", 900)), PID_PRIMERO),
)
POR_ID = {a.id: a for a in AJUSTES}


def leer_asm(a: Ajuste, tabla: str = "tab") -> str:
    """Thumb para keystone: deja en r0 el valor (u16) de la opción guardada de `a` (0 si el byte no es una opción). Destruye r0-r3 y lr (el llamante debe haber guardado lr);
    la tabla de valores va tras `b.w fin_<tabla>` y el código termina en la etiqueta `fin_<tabla>`."""
    n = len(a.opciones)
    return f"""
        sub sp, #8
        movs r0, #0
        strb r0, [sp]
        movw r0, #{a.backup & 0xFFFF:#x}
        movt r0, #{a.backup >> 16:#x}
        mov r1, sp
        bl {BACKUP_READ:#x}
        ldrb r0, [sp]
        add sp, #8
        cmp r0, #{n}
        bhs.w fin_{tabla}
        adr.w r1, {tabla}
        ldrh.w r0, [r1, r0, lsl #1]
        b.w fin_{tabla}
        .align 2
    {tabla}:
        {"".join(f".short {v}{chr(10)}        " for _, v in a.opciones)}
    fin_{tabla}:
    """


def ensamblar(src: str, va: int) -> bytes:
    from keystone import KS_ARCH_ARM, KS_MODE_THUMB, Ks
    enc, _ = Ks(KS_ARCH_ARM, KS_MODE_THUMB).asm(src, va)
    return bytes(enc)


def configurar_menu(ajustes=AJUSTES):
    """Vuelca la tabla en la spec de `build_pp_menu` (en el sitio): árbol = el nodo del primer ajuste (se inserta directo en las páginas del menú) y un pid nuevo por ajuste."""
    import pp_menu_spec as M
    M.SETTINGS.clear()
    for a in ajustes:
        M.SETTINGS[a.id] = M.S(a.id, a.label, 0, tuple((t, i) for i, (t, _) in enumerate(a.opciones)), "g56", backup=a.backup)
    M.PIDS[:] = [a.pid or PID_PRIMERO + i for i, a in enumerate(ajustes)]
    M.TREE = ajustes[0].id            # nodo directo (build_nodes devuelve el nodo del ajuste); con varios, una carpeta como la de PP
    return M


def construir(dev_a, dev_b, dest, ajustes=AJUSTES):
    """Genera `lib/viewUnified2.so`, `lib/CautionConfig.so` y `share/app/string_*.uxc` con la entrada de menú (sin `.dat`)."""
    import build_pp_menu
    assert len(ajustes) == 1, "una entrada directa; para varias, agrúpalas en una carpeta (pp_menu_spec.TREE)"
    configurar_menu(ajustes)
    build_pp_menu.main(dev_a, dev_b, dest)


if __name__ == "__main__":
    construir(*sys.argv[1:4])
