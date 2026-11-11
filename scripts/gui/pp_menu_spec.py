"""G23 — especificación del menú Picture Profile para la A6000 (datos, sin lógica).

Claves de escritura = `0x1f8 + 4·i`, con `i` leído de las clases `CmnViewProcessDataElementCustomPictureProfile*::setValue` de la A7S (VERIFICADO, `…::setValue`
del `cmn_view_processDataMgr.so` fw3.20): ColorModeType 0, Gamma 7, BlackGamma Range/Level 8/9, BlackLevel 10, Knee Mode 11, Auto Sens/Max 12/13, Manual Point/Slope 14/15,
Detail Mode/Level 16/17, V/H 18, B/W 19, Limit 20, Crispening 21, Hi-Light 22, Color Depth R,G,B,C,M,Y 23–28, Saturation 29, Phase 30; selector de perfil = `0x274`.
Rangos y valores = lo que acepta el validador de la A6000 (`pvt_ChangePictureProfileParamApp2Obj`, libObj `0x4b46b8`): numéricos con signo y paso 1 (valor = número);
enumerados = índice de la tabla VALUEID del caso (Gamma y ColorMode con la identificación de curvas/modos de G20 y G23).
Evidencia por ajuste: «clave» (A7S) · «rango» (validador A6000) · «mapa» (INFERENCIA: orden de VALUEID o índice igual al de la A6300).
Fuera de alcance: Gamma Disp. Assist (vista propia). Color Mode Level (clave K(1)) entra en G27; B&W: menú + libObj con efecto (Movie + saturación −8, G27); S-Gamut = Movie (G27 §5); S-Gamut3(.Cine): menú + libObj + parche de núcleo `pp_curves_patch.py --color` (G27 §6).
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class S:
    id: str
    label: str
    clave: int
    opciones: tuple                       # ((texto, valor), …)
    evidencia: str
    evento: int = 0x40                    # evento de escritura de `@M00B` (0x40 = SET_PICTURE_PROFILE, 0x41 = copiar perfil)
    id_get: int = 0x49                    # id de lectura (`getModelInfo`): 0x49 = los 31 parámetros (claves c+1, c+2); 0x4a = perfil actual (clave 0x275)
    clave_get: int | None = None          # clave de lectura; por defecto clave + 2


def num(lo, hi):
    return tuple((("0" if v == 0 else f"{v:+d}") if lo < 0 else str(v), v) for v in range(lo, hi + 1))


K = lambda i: 0x1F8 + 4 * i
SETTINGS = {s.id: s for s in (
    S("sel", "Picture Profile", 0x274, (("Off", 9),) + tuple((f"PP{k + 1}", k) for k in range(9)), "clave+mapa", id_get=0x4A, clave_get=0x275),  # 0x49 no devuelve 0x276 (solo 31 claves hasta 0x272): se lee con 0x4a
    S("gamma", "Gamma", K(7), (("Movie", 4), ("Still", 5), ("ITU709", 3), ("Cine1", 6), ("Cine2", 7), ("Cine3", 8), ("Cine4", 9)), "clave+G20"),
    S("bg_range", "Black Gamma Range", K(8), (("Wide", 0), ("Middle", 1), ("Narrow", 2)), "clave+mapa"),
    S("bg_level", "Black Gamma Level", K(9), num(-7, 7), "clave+rango"),
    S("black_level", "Black Level", K(10), num(-15, 15), "clave+rango"),
    S("knee_mode", "Knee Mode", K(11), (("Auto", 0), ("Manual", 1)), "clave+mapa"),
    S("knee_max", "Knee Max Point", K(13), num(0, 4), "clave+rango"),
    S("knee_sens", "Knee Sensitivity", K(12), (("High", 0), ("Mid", 1), ("Low", 2)), "clave+mapa"),
    S("knee_point", "Knee Point", K(14), num(0, 12), "clave+rango"),
    S("knee_slope", "Knee Slope", K(15), num(-5, 5), "clave+rango"),
    S("color_mode", "Color Mode", K(0), (("Movie", 5), ("Still", 6), ("Cinema", 7), ("Pro", 3), ("ITU709 Matrix", 4)), "clave+VALUEID"),
    S("copy", "Copy", 0x274, tuple((f"PP{k + 1}", k) for k in range(9)), "INFERENCIA: evento 0x41 y clave 0x274 de `Copy::setValue` (A7S); el valor = PP destino", 0x41),
    S("saturation", "Saturation", K(29), num(-8, 7), "clave+rango(A6000: -8..+7, la A6300 -32..+32); -8 = blanco y negro en el núcleo (G27)"),
    S("phase", "Color Phase", K(30), num(-7, 7), "clave+rango"),
    *(S(f"cd_{c.lower()}", f"Color Depth {c}", K(23 + i), num(-7, 7), "clave+rango") for i, c in enumerate("RGBCMY")),
    S("det_mode", "Detail Mode", K(16), (("Auto", 0), ("Manual", 1)), "clave+mapa"),
    S("det_level", "Detail Level", K(17), num(-7, 7), "clave+rango"),
    S("det_vh", "V/H Balance", K(18), num(-2, 2), "clave+rango"),
    S("det_bw", "B/W Balance", K(19), tuple((f"Type{k}", k - 1) for k in range(1, 6)), "clave+mapa"),
    S("det_limit", "Detail Limit", K(20), num(0, 7), "clave+rango"),
    S("det_crisp", "Detail Crispening", K(21), num(0, 7), "clave+rango"),
    S("wb_filter", "WB Filter Type", 0x200, (("LB/CC", 0), ("R/B", 1)), "clave+VALUEID (caso 2 → WB_SHIFT_LB_CC 0x1b2 / WB_SHIFT_RGAIN_BGAIN 0x1b3); rótulos de la A6300 NO verificados"),
    *(S(f"wb_{k}", f"WB {t}", K(3 + i), num(-9, 9), "clave A7S `WbShift` + validador (caso 3–6: -9..+9)") for i, (k, t) in enumerate((("lb", "LB"), ("cc", "CC"), ("r", "R"), ("b", "B")))),
    S("det_hilight", "Hi-Light Detail", K(22), num(0, 4), "clave+rango"),
    S("reset", "Reset", 0x274, tuple((f"PP{k + 1}", k) for k in range(9)), "INFERENCIA (G26): evento 0x42 → `ActionExePictureprofileReset` (necesita patch_actions); el valor = PP a restablecer (el reset real acepta 0–9)", 0x42),
    S("color_level", "Color Mode Level", K(1), num(1, 8), "clave K(1)=0x1fc (A7S ColorModeLevel) + rango 1..8 del caso 1 del validador de la A6000 (byte 9 del 0x4066)"),
)}
# Gamma con el orden y las opciones de la A6300; 10/11/2 = app de ITU709(800%)/S-Log2/S-Log3 en la `libObj` parcheada (G25/G26)
GAMMA_COMPLETA = ((("Movie", 4), ("Still", 5)) + tuple((f"Cine{k}", 5 + k) for k in range(1, 5)) + (("ITU709", 3), ("ITU709(800%)", 10), ("S-Log2", 11), ("S-Log3", 2)))
# Color Mode con el orden y las opciones de la A6300 (G26): app 8 = B&W (0x504), 9 = S-Gamut (0x505) como la A7S, 10 = S-Gamut3 (0x583), 11 = S-Gamut3.Cine (0x584) en la `libObj` parcheada
COLOR_MODE_COMPLETO = (("Movie", 5), ("Still", 6), ("Cinema", 7), ("Pro", 3), ("ITU709 Matrix", 4), ("Black & White", 8), ("S-Gamut", 9), ("S-Gamut3.Cine", 11), ("S-Gamut3", 10))
# Menú PLANO (11-11-2026, medido en cámara): la interfaz de la A6000 muestra 6 filas por página (la 7.ª no aparece) y las carpetas anidadas no abren, así que cada ajuste
# es una fila de la carpeta «Picture Profile», en páginas de 6 con la etiqueta desambiguada. `F` solo queda para la raíz.
F = lambda label, *pages: ("folder", label, pages)
FILAS_POR_PAGINA = 6
ORDEN = ["sel", "copy", "reset", "gamma", "black_level", "bg_range", "bg_level", "knee_mode", "knee_max", "knee_sens", "knee_point", "knee_slope",
         "color_mode", "color_level", "saturation", "phase", *(f"cd_{c}" for c in "rgbcmy"), "wb_filter", "wb_lb", "wb_cc", "wb_r", "wb_b",
         "det_level", "det_mode", "det_vh", "det_bw", "det_limit", "det_crisp", "det_hilight"]
paginar = lambda orden: [orden[i:i + FILAS_POR_PAGINA] for i in range(0, len(orden), FILAS_POR_PAGINA)]
TREE = ("folder", "Picture Profile", paginar(ORDEN))   # las páginas son una lista: `sin_acciones` las repagina en el sitio
# G28: pids NUEVOS (fuera de los 233 originales, que casi todos usa algún nodo): el espacio se amplía en pid_space.py. PIDS_PRESTADOS es la lista del 3.57–3.62
# (G23: se creían «inertes», pero eran Custom Key / Function Menu Set.) y solo se conserva para las pruebas de los descriptores de la .so.
PIDS_PRESTADOS = [0x35, 0x9D, 0xB3, 0xC3, 0xC4, 0xC5, 0xC6, 0xC7, 0xC8, 0xDC, 0xDD, 0xDE, 0xDF, 0x52, 0x53, 0x54, 0x5E, 0x5F, 0x60, 0x62, 0x63, 0x64, 0x65, 0x66, 0x67, 0x68,
                  0x55, 0x56, 0x57, 0x58, 0x59, 0x5A, 0x5B, 0x26]
PIDS = list(range(0xE9, 0xE9 + len(PIDS_PRESTADOS)))
