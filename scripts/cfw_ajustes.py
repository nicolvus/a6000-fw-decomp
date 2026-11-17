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
CARPETA = "CFW"
PID_PRIMERO = 0xE9                # primer ProcessId nuevo (pid_space)
# Ids 1 B sin ningún literal en libs/bin/av-cam del 3.21 (volcados de 4 fechas, valor 0, mismo tamaño): hueco 0x1070208…0x1070219 (g56 §2)
ID_LIBRES = tuple(range(0x1070210, 0x107021A))
# G76: 0x1070208/9, del mismo hueco de g56; sin literal (palabra de 32 bits) en ningún fichero de /usr ni en av-cam 3.21; 1 B y valor 0 en todos los volcados
ID_LIBRES_2 = (0x1070208, 0x1070209)


@dataclass(frozen=True)
class Ajuste:
    id: str
    label: str
    backup: int                   # id de Backup de 1 B
    opciones: tuple               # ((texto, valor), …); la UI escribe el índice de la opción (0…n-1); `valor` es lo que el parche de av-cam entiende (aquí segundos)
    pid: int = 0


AJUSTES = (
    Ajuste("bulb_timer", "Bulb Timer", ID_LIBRES[0],
           # 7 opciones: tope de la lista de la clase Normal medido en cámara (G36); no medido para este nodo, por prudencia no se pasa de 7
           (("Off", 0), ("5 s", 5), ("30 s", 30), ("1 min", 60), ("2 min", 120), ("5 min", 300), ("15 min", 900)), PID_PRIMERO),
    # G71 LUT 3D: Off = de fábrica; LUT1…3 = tablas 5×9×9 del `.dat` (`scripts/lut/lut_patch.py`). Reutiliza el id del antiguo «CFW test» (inerte, sin consumidor)
    Ajuste("lut", "LUT", ID_LIBRES[1], (("Off", 0), ("LUT1", 1), ("LUT2", 2), ("LUT3", 3)), PID_PRIMERO + 1),
    # G57 Focus Bracket: nº de tomas (el valor es N) y paso (s16 del comando de lente 0x1D; unidades y sentido NO medidos, g57 §4)
    Ajuste("fb_n", "Focus Bracket", ID_LIBRES[2], (("Off", 0), ("3", 3), ("5", 5), ("10", 10), ("15", 15), ("20", 20), ("30", 30)), PID_PRIMERO + 2),
    Ajuste("fb_paso", "Focus Br. paso", ID_LIBRES[3], (("Fino", 4), ("Medio", 16), ("Grueso", 64)), PID_PRIMERO + 3),
    # G61 autodisparador continuo (`libObj`): espera entre tomas en segundos (Off = la de fábrica de cada modo) y nº de tomas (0 = sin tope)
    Ajuste("intervalo", "Intervalo", ID_LIBRES[4], (("Off", 0), ("2 s", 2), ("5 s", 5), ("10 s", 10), ("30 s", 30), ("60 s", 60), ("5 min", 300)), PID_PRIMERO + 4),
    Ajuste("n_disparos", "N. disparos", ID_LIBRES[5], (("10", 10), ("30", 30), ("60", 60), ("100", 100), ("300", 300), ("999", 999), ("Sin tope", 0)), PID_PRIMERO + 5),
    # G62 seguimiento AE en la serie del intervalómetro: Normal (AE por toma, de fábrica) o Bloqueado (AEL tras la 1.ª toma, se libera al acabar la serie)
    Ajuste("seguim_ae", "Seguim. AE", ID_LIBRES[6], (("Normal", 0), ("Bloqueado", 1)), PID_PRIMERO + 6),
    # G63 Flicker Scan (Silent): redondea la exposición al múltiplo más cercano del periodo del parpadeo (líneas de 17,135 µs: 100 Hz = 584, 120 Hz = 486)
    Ajuste("flicker_scan", "Flicker Scan", ID_LIBRES[7], (("Off", 0), ("50 Hz", 584), ("60 Hz", 486)), PID_PRIMERO + 7),
    # G68 DR Prioridad (libObj, al pulsar a medias): Débil = DRO Lv3 + sesgo −1 EV; Fuerte = DRO Lv5 + sesgo −2 EV (Off = de fábrica). El valor es el nivel (0/1/2)
    Ajuste("dr_prior", "DR Prioridad", ID_LIBRES[8], (("Off", 0), ("Débil", 1), ("Fuerte", 2)), PID_PRIMERO + 8),
    # G69 Color Chrome / Film (av-cam): suma desplazamientos a Saturación y Color Depth del mensaje de colorimetría. El valor es el desplazamiento (8·fila) en la tabla de la cueva
    Ajuste("color_chrome", "Color Chrome", ID_LIBRES[9],
           (("Off", 0), ("Débil", 8), ("Fuerte", 16), ("Clásico", 24), ("Vivo", 32), ("Suave", 40)), PID_PRIMERO + 9),
    # G76 S&Q (VFR): frecuencia de captura del vídeo a cámara lenta/rápida (libObj, como el modelo MOVIE_REC_O_U_CRANK de Sony). El valor es el índice de UI de Sony + 1
    # (0 = Off): 9 = 120/100 fps (índice 8, el que pide el formato HFR), 1 = 60/50, 2 = 30/25, 3 = 15/12, 4 = 8/6, 7 = 1 fps
    Ajuste("sq", "S&Q", ID_LIBRES_2[0], (("Off", 0), ("120/100", 9), ("60/50", 1), ("30/25", 2), ("15/12", 3), ("8/6", 4), ("1 fps", 7)), PID_PRIMERO + 10),
)
POR_ID = {a.id: a for a in AJUSTES}


def leer_asm(a: Ajuste, tabla: str = "tab", llamada: str = f"bl {BACKUP_READ:#x}") -> str:
    """Thumb para keystone: deja en r0 el valor (u16) de la opción guardada de `a` (0 si el byte no es una opción). Destruye r0-r3 y lr (el llamante debe haber guardado lr);
    la tabla de valores va tras `b.w fin_<tabla>` y el código termina en la etiqueta `fin_<tabla>`.
    `llamada`: instrucción que lee el Backup (por defecto la de `av-cam`; en `libObj` es `blx 0xdd5f4`, mismos argumentos r0 = id, r1 = búfer)."""
    n = len(a.opciones)
    return f"""
        sub sp, #8
        movs r0, #0
        strb r0, [sp]
        movw r0, #{a.backup & 0xFFFF:#x}
        movt r0, #{a.backup >> 16:#x}
        mov r1, sp
        {llamada}
        ldrb r0, [sp]
        add sp, #8
        cmp r0, #{n}
        blo ok_{tabla}
        movs r0, #0
        b.w fin_{tabla}
    ok_{tabla}:
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
    M.TREE = ("folder", CARPETA, M.paginar([a.id for a in ajustes]))   # carpeta «CFW» en Ajustes personalizados, como la de Picture Profile (g24/g36)
    return M


def construir(dev_a, dev_b, dest, ajustes=AJUSTES):
    """Genera `lib/viewUnified2.so`, `lib/CautionConfig.so` y `share/app/string_*.uxc` con la entrada de menú (sin `.dat`)."""
    import build_pp_menu
    configurar_menu(ajustes)
    build_pp_menu.main(dev_a, dev_b, dest)


if __name__ == "__main__":
    construir(*sys.argv[1:4])
