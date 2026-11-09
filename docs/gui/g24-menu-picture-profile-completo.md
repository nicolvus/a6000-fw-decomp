# G24 — Menú completo de Picture Profile (A6300/A7S) para la A6000: generador solo-datos (09-11-2026)

Continúa [G23](g23-pp-gamma-ruta-datos.md). Todo es **offline**: nada instalado ni probado en cámara.
Generador: `scripts/gui/build_pp_menu.py` (spec en `pp_menu_spec.py`, descriptores en `pp_descriptors.py`); tests `tests/test_g23_pp_menu.py`.

## 1. Qué construye

`build_pp_menu.py DEV_A6000 DEV_A6300 SALIDA` → `lib/cmn_view_processDataMgr.so` (26 descriptores), `lib/CautionConfig.so` (nodos de datos puros en un `PT_LOAD` RW:
8 carpetas, 9 páginas, 26 raíces, 274 nodos de opción), `lib/viewUnified2.so` (la carpeta «Picture Profile» como entrada en las 5 páginas del menú),
`share/app/string_<idioma>.uxc` (106 textos en ranuras libres; traducción de la A6300 cuando el inglés coincide, literal si no) y `MANIFEST.json`/`SHA256SUMS`.

Árbol (como la A6300): **Picture Profile** → página 1 [selector Off/PP1–PP9, Gamma, Black Level, *Black Gamma* (Range, Level), *Knee* (Mode, *Auto Set* (Max Point, Sensitivity), *Manual Set* (Point, Slope))] ·
página 2 [Color Mode, Saturation, Color Phase, *Color Depth* (R, G, B, C, M, Y), *Detail* (Level, Mode, *Manual Set* (V/H, B/W, Limit, Crispening, Hi-Light))].

## 2. Ajustes: clave y valores (qué es verificado y qué no)

Clave de escritura `0x1f8 + 4·i` (lectura +2). **VERIFICADO**: `i` sale de las clases `CmnViewProcessDataElementCustomPictureProfile*::setValue` del `cmn_view_processDataMgr.so` de la A7S (23 clases; la
clave aparece como inmediato): ColorModeType 0, Gamma 7, BlackGamma Range/Level 8/9, BlackLevel 10, Knee Mode 11, Auto Sens 12 / Max 13, Manual Point 14 / Slope 15, Detail Mode 16 / Level 17 / V/H 18 / B/W 19 / Limit 20 /
Crisp 21 / Hi-Light 22, Color Depth R…Y 23–28, Saturation 29, Phase 30, selector `0x274`. Los elementos de la A7S envían el número tal cual (`PrmNumber`), sin transformar.
La A6000 valida en `pvt_ChangePictureProfileParamApp2Obj` (`libObj 0x4b46b8`, un caso por `i`): los numéricos son con signo y se pasan **sin cambio** (`str r5,[r4]`) si están en rango;
los enumerados se traducen a `VALUEID`.

| Ajuste | `i` | Opciones (valor) | Evidencia |
|---|---|---|---|
| Selector | `0x274` | Off 9, PP1–PP9 = 0–8 | clave A7S; valores = A6300 (INFERENCIA que la A6000 acepte 0–9) |
| Gamma | 7 | Movie 4, Still 5, ITU709 3, Cine1–4 6–9 | G20 (VALUEID de la A6000) |
| BG Range / Level | 8 / 9 | Wide, Middle, Narrow = 0–2 (orden NO verificado) / −7…+7 | clave + validador |
| Black Level | 10 | −15…+15 | clave + validador |
| Knee Mode / Max Point / Sens. / Point / Slope | 11 / 13 / 12 / 14 / 15 | Auto 0, Manual 1 / 0–4 / High, Mid, Low = 0–2 / 0–12 / −5…+5 | clave + validador (el orden de los enumerados no está verificado) |
| Color Mode | 0 | Movie 5, Still 6, Cinema 7, Pro 3, ITU709 Matrix 4 | **VERIFICADO**: tabla `tbb` del caso 0 → `VALUEID` STD 0x1ad(0), TONE1(1), TONE2(2), PRO(3), ITU709(4), STD_MOV(5), STD_STL(6), CINEMA(7) |
| Saturation | 29 | **−8…+7** (la A6300 usa −32…+32) | el validador de la A6000 solo admite −8…+7 |
| Color Phase / Color Depth ×6 | 30 / 23–28 | −7…+7 | clave + validador |
| Detail Mode / Level / V/H / B/W / Limit / Crisp / Hi-Light | 16–22 | Auto, Manual / −7…+7 / −2…+2 / Type1–5 = 0–4 / 0–7 / 0–7 / 0–4 | clave + validador |

Fuera de alcance (y por qué): Copy/Reset (acciones `ActionExePictureprofileCopy/Reset`, no un parámetro), WB Shift (oculto también en la A6300), Gamma Disp. Assist (vista propia),
Color Mode Level (clave 1), ITU709(800%), S-Log2/3 y S-Gamut (la `libObj` de la A6000 no los tiene), Color Mode B&W (idem).

## 3. Cómo se asignan ProcessIds, textos y nodos

- **ProcessIds**: 26 inertes sin referencia en ninguna raíz de menú (`PIDS`); se excluye la familia contigua `0x55–0x5d` (parece de teclas personalizables). NO verificado que ningún otro consumidor use los elegidos.
- **Nodos**: objetos `{vtable, hijos, cuenta, props, 0×6}` con `props = {lista, nº}`; vtable `_ZTV18CmnViewSettingNode`+8; relocaciones `R_ARM_RELATIVE`. Raíz de ajuste `0xb=2, 0xc=0, 0xe=pid`; opción `0xb=0, 0xc=1, 0xf=0x10=índice`; carpeta `0xb=0, 0xc=3`; página `0xb=0`.
- **Textos**: ranuras libres en los 25 idiomas latinos (sin los de G09); los no latinos quedan sin textos nuevos (G10-C). La ayuda de cada nodo repite su etiqueta.

## 4. Verificación hecha

Tests offline (estructura, claves únicas, árbol 8/9/26/274, 26 descriptores) y carga conjunta de los tres `.so` con `libObj` en `qemu-arm`; con `gdb` se recorre en memoria el árbol entero desde la carpeta
y se comprueba cada descriptor (clave, lectura +2, nº de opciones, valores): 26/26 correctos.

## 5. Límites

Sin cámara; la UI real (¿cuántas entradas caben por página? ¿cómo se pinta una carpeta con carpetas dentro?) es NO_VERIFICADO. Las curvas de gamma siguen dependiendo de G18/3.56. Los enumerados con orden
inferido (Range, Knee Mode, Sens., Detail Mode, B/W) podrían estar permutados. No se combina todavía con Silent/3.56 (mismas páginas y `CautionConfig`). Colores/Detail no se atenúan según el modo (Auto/Manual).
