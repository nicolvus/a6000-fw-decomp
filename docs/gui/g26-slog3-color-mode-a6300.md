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

## 4. Reset y resto (investigado, sin cerrar)

- Reset es un nodo de tipo acción (`0xb=2`, `0xc=4`) con pid `0x12a` (A6300) / `0x11e` (A7S) y una opción de valor `0x16` / `0x14`; su descriptor en la A7S no tiene modelo de datos (palabra 6 = 0, igual que Copy), así que **no se resuelve por el mecanismo `@M00B`**. En la `libObj` de la A6000 la acción es `pvt_ActionExePictureProfileReset` (`0x4c0a78`, llamada desde `0x4c0f08` y `0x4d000a`; recorre los 31 parámetros con el validador y emite un mensaje `0x75ae`); falta saber qué evento de UI la dispara.
- **Color Mode Level** (`PARAMID_PP_COLOR_MODE_LEVEL`, byte 9) y **Gamma Disp. Assist** (vista propia): sin trabajar.
- La A6300 extraída no trae `cmn_view_processDataMgr.so` (sus descriptores están fuera de lo extraído).
