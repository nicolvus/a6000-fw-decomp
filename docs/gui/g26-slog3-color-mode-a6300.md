# G26 — S-Log3 y Color Mode ampliado copiados de la A6300 (09-11-2026)

Continúa [G25](g25-gamma-slog2-itu709-800.md). **Offline**: nada instalado ni probado en cámara. Herramientas: REA (sesión `analysis/rea-independent/bin/session_daemon.py` sobre el `av-cam.bin` de la A6300, 15 min en frío), capstone, Unicorn, `llvm-objdump`/`llvm-mc`.
Nuevos scripts: `scripts/gui/libobj_dis.py` (Thumb-2 con capstone; la `libObj` sin símbolos sale como ARM en `llvm-objdump`), `scripts/gui/valueid_table.py` (tabla de nombres VALUEID de una `libObj`).

## 1. Qué hace la A6300 (VERIFICADO con bytes)

| Dato | A6300 fw2.01 |
|---|---|
| `libObj` App2Obj, caso 7 (Gamma) | `tbb` de 13 casos en `0x4253ec`: 0–9 como A6000, **10 → 0x481, 11 → 0x480, 12 → 0x585 (S-Log3)** |
| `libObj` App2Obj, caso 0 (Color Mode) | `tbb` de 12 casos en `0x425378`: 0–7 como A6000, **8 → 0x505 (S-Gamut), 9 → 0x504 (B&W), 10 → 0x583 (S-Gamut3), 11 → 0x584 (S-Gamut3.Cine)** |
| Ids VALUEID | tabla de nombres en `0xfc8aac` (índice = id + 1): `PP_COLOR_BW` 0x504, `…SGAMUT` 0x505, `…SGAMUT3` 0x583, `…SGAMUT3_CINE` 0x584, `PP_GAMMA_SLOG3` 0x585 (la A6000 no tiene estos nombres) |
| `av-cam.bin` (base `0x43541000`, igual que la A6000) | tabla de curvas en `0x441bc70c` (`+8·gamma+4` = curva de vídeo, mismo formato 0x101a que la A7S); **gamma 0x1f = S-Log3** (`+0x1014 = 0x1f`); además trae 0x1b/0x1c/0x1d idénticas a las de la A7S |
| Selectores gamma→curva | tabla de pares en `0x43db1e2b`: índice 12 = `(0x1f,0x1f)`; el campo de la config pasa de `cfg+0x153` (A6000) a `cfg+0x171` |
| Menú Color Mode | Movie, Still, Cinema, Pro, ITU709 Matrix, Black & White, S-Gamut, S-Gamut3.Cine, S-Gamut3 (textos 0xe06f, 0xf699, 0xfa10, 0xfa15) |

## 2. Hecho — Gamma S-Log3 completo en datos (sin tocar código del núcleo)

- `patch_libobj_pp.patch_gamma` pasa a **13 valores** y cubre tres sitios con una única tabla de halfwords (índice = valor de app = selector del núcleo): App2Obj caso 7, la inversa Obj2App (trampolín, 28 B) y `CamMsgConv` byte `0x1a` del mensaje `0x4066` (`0x9b36de…0x9b3743`; sustituye una cadena de 12 comparaciones).
- `pp_curves_patch.py`: la curva `0x1f` de la A6300 se instala como **gamma `0x17`** (`+0x1012 = 4`, `+0x1014 = 0x17`) en una 8.ª ranura del hueco `0x43faf28c` (cabe: 8·0x1020 < 0x9c54) y el selector 12 pasa a `(0x17,0x17)`. Motivo: todas las gammas con caso propio en el código de la A6000 (`0x14–0x16`, `0x18–0x1b`) ya están en uso; `0x17` cae en la rama por defecto de los `tbb` (Movie/Still hacen lo mismo).
- Menú: Gamma tiene 10 opciones (… ITU709(800%) 10, S-Log2 11, **S-Log3 12**) con `--gamma-slog`.
- **Verificado**: Unicorn (`tests/test_g25_gamma_libobj.py`, ahora 4 tests: 0–12 aceptados, 13 rechazado, inversa exacta, CamMsgConv índice/ error) y emulación de la selección de gamma de la A6000 (`analysis/gui/g18/emu_gamma.py`): selector 12 → `0x17` (vídeo y foto); curva idéntica a la A6300 salvo 2 campos (`tests/test_g25_gamma_curves.py`). `analysis/gui/g26/{pp_ram.sh,pp_curvas.bin,manifest.json}` regenerados (26 escrituras, 8 curvas).
- **NO verificado**: el efecto en imagen (sin cámara), qué hacen los casos de las tablas de la A6000 para `0x17` (varias tablas lo tratan distinto de `0x14–0x16`), los límites de ISO de S-Log3 (la A6300 trae `PP_MIN_ISO_SLOG3_*`; aquí no hay equivalente) ni que el respaldo NVRAM admita el valor 12.

## 3. Hecho — Color Mode ampliado en `libObj` + menú (opt-in `--color-gamut`)

`patch_libobj_pp.patch_color`: App2Obj caso 0, Obj2App caso 0 y `CamMsgConv` byte 8 pasan a una tabla de 12 VALUEID (`COLOR`) con los ids de la A6300. Menú con 9 opciones en el orden de la A6300 (`pp_menu_spec.COLOR_MODE_COMPLETO`; app 9 = B&W, 8 = S-Gamut, 10 = S-Gamut3, 11 = S-Gamut3.Cine).
Tests en `tests/test_g26_color_libobj.py` (Unicorn: 0–7 igual que antes, 8–11 nuevos, 12 rechazado, inversa exacta, `CamMsgConv` registra el índice, Gamma intacta).
**Límite principal**: el tipo llega al núcleo como palabra en `cfg+0x138` (mensaje `0x4066` byte 8) pero las matrices de color de S-Gamut/B&W no están en el núcleo de la A6000; el consumidor (programación de registros YC desde un bloque de parámetros, p. ej. `0x438acc50` → `0x438ac3be`) no se ha portado. Sin eso, elegir esas opciones **no cambia la imagen** (o puede dar valores indefinidos): por eso es opt-in.

## 4. Copy y Reset (hecho en `libObj`, ids por analogía)

- En la A7S, `Copy::setValue` hace `requestModelExecute("@M00B", 0x41, {0x274: PP})`; las demás claves PP usan el id `0x40` (= `pvt_ActionSetPictureProfile`). En la A6000 el despachador de comandos (`libObj 0x4cfb9c`) solo llega a `0x40` en esa zona: `0x41–0x44` caen en el error `0x4d02b8`, **pero** la `libObj` ya trae `ActionExePictureprofileCopy` (`0x4b424c`) y `…Reset` (`0x4c0f4c` → `0x4c0e14`, que copia los 31 valores por defecto del PP indicado, `≤ 9`). Son las acciones 0x38/0x39 de la tabla de acciones (`tbh` en `0x4d02f0`, idéntica en la A7S).
- `patch_libobj_pp.patch_actions` (requiere `patch_gamma`) redirige la comparación `0x4cfcda` a un tramo de 40 B en el hueco que deja `CamMsgConv` (`0x9b370e`): `0x40` como antes, **`0x41` → Copy, `0x42` → Reset**. `0x42` es una INFERENCIA (la A6300/A7S no tienen clase propia para Reset: su descriptor no trae modelo, pid `0x12a`/`0x11e`). Test Unicorn (`tests/test_g26_actions_libobj.py`): 0x40 sigue a `SetPictureProfile`, 0x41/0x42 llegan a Copy/Reset con r0 = mensaje y r1 = parámetro, 0x43/0x44 siguen dando error.
- Menú: nuevo ajuste `reset` (pid `0x5b`, evento `0x42`, clave `0x274`, opciones PP1–PP9 = PP a restablecer); `build_pp_menu.py … --copy-reset` aplica `patch_gamma + patch_actions`. NO verificado: que la capa de modelo (`createRequestModelExecuteEvent`) entregue `0x41/0x42` tal cual al despachador, ni el comportamiento real del reset.

## 5. Color Mode Level, Gamma Disp. Assist y lo que queda

- **Color Mode Level**: no es un ajuste de usuario (ninguna raíz de la A6300 lo expone; «Color Level» de la A6300 es la saturación, ya cubierta con `--saturacion-a6300`). Es el byte 9 del `0x4066` que escribe `ColorModeType::setValue` junto con el tipo; sin menú.
- **Gamma Disp. Assist** (`SLogDispAssistRoot`, pid `0x151`, opciones Off/Auto/S-Log2/S-Log3 con ids `0x3f0–0x3f3`): no hay ningún `PARAMID/MSGID` de ese nombre en ninguna `libObj` (A6000 ni A6300); es una conversión de pantalla (S-Log→ITU709(800%)) del lado de la visualización, no resoluble solo con datos.
- La A6300 extraída no trae `cmn_view_processDataMgr.so` (sus descriptores están fuera de lo extraído).

## 6. Matrices de color del núcleo (investigado con REA, sin resolver)

Sesiones REA abiertas y reutilizables: `analysis/rea-independent/run/a6k.sock` (A6000) y `run/a6300b.sock` (A6300). Hallazgos:
- El desempaquetador del `0x4066` (A6000 `0x43802a28`) guarda el byte 8 (tipo de Color Mode) como **palabra** en `cfg+0x138` (el byte 9, nivel, en `+0x13c`). La A6300 usa otro diseño del `cfg` (el selector de gamma está en `+0x171`, no `+0x153`) y su desempaquetador no coincide con el patrón de la A6000.
- Los lectores de `cfg+0x133…0x144` copian esos bytes a un bloque de parámetros (`0x438acc20…`, offsets `0x740–0x751`) que `FUN_438ab3e8` (decompilado en la sesión `a6k`) vuelca a un bloque de registros YC: en él hay una rejilla de ganancias con diagonal `0x200` (corrección de color por sectores, es decir Color Depth), **no** la matriz del modo de color. La selección por gamma del mismo bloque (`param_2[0] == 0x1b`) usa tablas de ajuste por ISO, no datos por modo.
- No hay matrices 3×3 `s16` reconocibles en el `av-cam` de la A6000 (barrido por filas con suma constante: 4 coincidencias, todas ajenas) ni cadenas `SGAMUT`/`ColorMode` en ninguno de los dos `av-cam`; el cálculo del modo de color no es una tabla simple indexada por tipo.
- Conclusión: portar B&W/S-Gamut/S-Gamut3(.Cine) exige localizar y portar el consumidor del tipo en la A6300 (código + tablas de ajuste), trabajo que se apoya en tener ambas sesiones REA y, para validarlo, una captura en cámara.

### 6.1 Segunda pasada (sesiones `a6k` / `a6300b` reutilizadas)

- Mensaje PP de la A6300 en el núcleo (desempaquetador `0x43882e82…`): el mensaje es más largo (gamma en el byte `0x64`, no `0x1a`) y se vuelca a una estructura de ajustes (`+0x47d…+0x4bc`; gamma `+0x495`, tipo y nivel previsiblemente `+0x484`/`+0x485`), que otra función (`0x4393e700…`) copia al `cfg` de trabajo (gamma en `cfg+0x171`). Es decir, el diseño del `cfg` de la A6300 **no es el de la A6000** y no se puede portar campo a campo.
- En la A6000 los únicos lectores de `cfg+0x138` (tipo) que se han podido decompilar (`0x4382bf58`, `0x438345b0`, `0x4383bfd4`) son accesores genéricos (informe/traza de parámetros) y la copia al bloque de parámetros YC; no hay un `switch` del tipo con matrices. Hipótesis más probable: el tipo selecciona **datos de ajuste (tuning) cargados fuera del `av-cam`**, con 8 conjuntos en la A6000; las modos nuevos de la A6300 necesitan conjuntos nuevos, que no se pueden fabricar sin esos datos de la A6300 y un lugar donde instalarlos.
- Por eso el Color Mode ampliado queda «listo» en menú + `libObj` (opt-in `--color-gamut`), pero el efecto en imagen de B&W/S-Gamut/S-Gamut3(.Cine) no está resuelto. Idea no implementada: aproximar B&W con una opción que escriba a la vez Color Mode = Movie, Saturation = −8 y Color Depth R…Y = −7 (el modelo admite varias claves por opción), a costa de pisar esos ajustes.

### 6.2 Tercera pasada (sesión `a7sb` nueva)

- La `libObj` de la **A7S** también trae B&W y S-Gamut (app 8 = `0x504` BW, 9 = `0x505` SGAMUT; la A6300 los tiene en orden inverso). El parche de `libObj` y el menú usan ahora el orden de la A7S (más cercano al núcleo de la A6000); S-Gamut3 y S-Gamut3.Cine (10, 11) solo existen en la A6300.
- Ruta del tipo en la A6000: mensaje `0x4066` byte 8 → palabra en el contexto de trabajo (+0x138) → copia de la instantánea de ajustes (`0x438b83a0`, llamada desde `0x43afa0ce`: contexto por fotograma de >0x5000 B) → generador de registros YC `FUN_438ab3e8`, que traslada bytes `0x133…0x144` a un bloque de parámetros. En ningún punto aparece un `switch`/tabla indexada por el tipo; los bytes se tratan como parámetros genéricos por eje de color. El efecto de B&W/S-Gamut depende por tanto de datos de ajuste/código fuera de lo identificado (posiblemente otra imagen de `nflasha5`, formato `WBI1`), no de una tabla del `av-cam`.
- Alternativa con efecto real y ya disponible: B&W ≈ Color Level −32 (ajuste «Saturation» con `--saturacion-a6300`, sin verificar que el núcleo acepte ±32).
