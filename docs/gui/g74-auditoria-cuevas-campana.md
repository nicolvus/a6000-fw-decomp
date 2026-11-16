# G74 — Auditoría de todas las cuevas y celdas de datos de la campaña con el volcado vivo (15-11-2026)

Aplica el método de [g72](g72-zona-cero-av-cam.md) (fichero vs volcado de RAM real `ram-servicio-20261020`, referencias `movw/movt`/literales, `bss` de la cabecera LIRO) a todos los parches. Sin CFW construido, sin cámara. Test: `tests/test_g74_cuevas_seguras.py` (14 casos; el de cada cueva exige ceros en fichero **y** vivo, 0 referencias, fuera del `bss` `0x43CFE37F…0x43F430D9`).

## 1. av-cam
| Cueva (parche) | Rango | Veredicto | Evidencia |
|---|---|---|---|
| g55 Bulb Timer (antigua) | `0x43541900…0x43541B00` | **INSEGURA, corregida** | Vivo: 69 B no nulos desde `0x43541900` (tabla de 16 B de paso); GOT `0x44020f00` apunta a `0x43541900` y `0x43adeee4` a `0x43541a64` (ya lo anotaba `test_e25_25_caves`). La «celda» `0x43541920` cae dentro. |
| g65 contador (antigua) | `0x44018250…0x44018294` | **INSEGURA, corregida** | Ceros en fichero; vivo con datos (15 B en el rango, 100+ B en la página); está en la zona respaldada tras el `bss` (`0x43f430d9…0x4409ce00`). |
| g55 (nueva) | `0x43541600…0x43541680` | SEGURA | Dentro del hueco verificado `0x4354141c…0x435418d8` (cero fichero/vivo, 0 refs). 88 B de código. |
| g65 (nueva) | `0x43541700…0x43541744` (cueva 16 B + contador `0x43541740`) | SEGURA | Idem. |
| g57 `fb_paso` cueva + celda | `0x43541500…0x435415C0`, celda `0x435417F0` | SEGURA | Cero fichero/vivo, 0 refs. Se acotó `CAVE_END` (170 B) para no solapar g55/g65; la celda se comprueba aparte. |
| g69 Color Chrome | `0x43FB7C00…0x43FB7E00` | SEGURA | Hueco G18 (g72 §2); re-medido. |
| g63 Flicker Scan + g38 sublínea (cueva de `patch_silent_r5`) | `0x43FB7E00…0x43FB7EC0` | SEGURA | Idem (192 B). |
| g73 A / B | `0x43BE3B28…0x43BE4330`, `0x43C1FF24…0x43C20C8C` | SEGURA (confirmadas) | Ceros fichero/vivo, 0 refs. |

`0x43541000…0x435413cf` NO es relleno: el cargador reescribe 769 B (relocaciones de la cabecera; `0x435410d8…0x435412df`, `0x43541318…0x435413cf`). El hueco `0x435413d0…0x435418d9` (1289 B) es cero en ambos y sin referencias; las cuevas g55/g57/g65 quedan más allá de `0x4354141c`. Límite: un solo volcado (no se ve si algo escribe en el hueco en otros estados; cuevas en el hueco G18 y este comparten esa limitación).

## 2. libObj.so
| Elemento | Veredicto | Evidencia |
|---|---|---|
| Función muerta `0x2648d8` (g61 `+0…+0x500`, g68 `+0x600…+0x800`; función `0x2648d8…0x266e0c`) | SEGURA (estático) | Barrido de palabras de 32 bits (paso 2, con y sin bit Thumb) en todo el fichero: solo 2 palabras `0x266a00` (en `.ARM.extab`, +0x2128 de la función, fuera de ambas cuevas); `.rel.dyn`/`.rel.plt` sin entradas dentro; `.dynsym` sin símbolo que la cubra; `.init_array` sin entradas; `.ARM.exidx` solo su propia entrada (`0x809728ab`, compacta inline, sin LSDA/aterrizajes). 1.er `LOAD` `R E`. |
| Contador `0x10e2c00` | SEGURA (estático) | 2.º `LOAD`: `0xfd25a4 + memsz 0x11062c` = fin `0x10e2bd0`; el contador está en la cola de la última página (`…0x10e3000`), que el cargador mapea RW anónima y nadie reclama; ningún símbolo ni palabra del fichero referencia `0x10e2bd0…0x10e3000`. Heap/`brk` no pueden usarla (es de la propia biblioteca). |
| `patch_libobj_ppeco` (g30) | n/a | Segmento `PT_LOAD` nuevo en el hueco de VA `0xFCB000`; no reutiliza memoria existente. |

Límites: no hay volcado `/proc/PID/maps` de libObj en `analysis/camera-dumps/` (solo `shell.txt`), así que «página mapeada como texto normal» y «cola de página RW» salen de las cabeceras ELF, no de la cámara. Pendiente LIBOBJ-MAP.

## 3. Resto
- g39/g43 (`iso_list_patch.py`), `CautionConfig.so`: solo cambian literales de pool; sin cuevas. g70 es diseño, sin código (usará un segmento nuevo con relocalizaciones, patrón G58).
- Cuevas del hueco G18 de pp_* (`pp_bwhl`, `pp_color`, `pp_tone`, `pp_curves`): cubiertas por g72 (hueco idéntico fichero/vivo, 0 refs); no re-medidas una a una.

## 4. Cambios
`scripts/g55/bulb_timer_patch.py` (`0x43541600`), `scripts/g65/jpeg_hook_patch.py` (`0x43541700`/`0x43541740`), `scripts/g57/focus_bracket_patch.py` (`CAVE_END = 0x435415C0`, comprueba la celda aparte). Tests de bytes/Unicorn de g65 y `test_cfw_ajustes` siguen en verde. **Cualquier .dat/CFW previo con g55 o g65 escribía en memoria viva: no instalar.**
