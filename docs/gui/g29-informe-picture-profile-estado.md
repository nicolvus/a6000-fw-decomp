# G29 — Informe de estado de Picture Profile (PP) en la A6000 (10-11-2026)

Resumen de todo el trabajo de PP hasta el CFW 3.65: qué se hizo, qué está medido en cámara y qué sigue abierto.
Cámara: ILCE-6000 (fw base 3.21 + CFW). Pruebas en vivo por telnet (`192.168.1.18`); el 3.65 se instaló por USB el 10-11-2026.

## 1. Qué hay construido

| Pieza | Estado | Dónde |
|---|---|---|
| Menú PP de 34 ajustes (Gamma de 10 opciones, Color Mode con B&W / S-Gamut / S-Gamut3(.Cine), Color Mode Level, Copy, Reset) | hecho, **instalado en 3.65** | `scripts/gui/build_pp_menu.py`, `pp_menu_spec.py` ([G24](g24-menu-picture-profile-completo.md), [G27](g27-pp-auditoria-color-mode-y-plan.md)) |
| Espacio de ProcessIds ampliado 233 → 273 en la copia del gestor de `viewUnified2.so`; 34 descriptores propios (pids `0xE9…0x10A`) | hecho, instalado (3.63+) | `scripts/gui/pid_space.py` ([G28](g28-descriptores-en-viewunified2.md)) |
| Curvas de gamma (S-Log2, S-Log3, ITU709 800 %, Cine) y código de S-Gamut3 escritos en la RAM del núcleo al arrancar | hecho (3.62+) | `scripts/gui/pp_curves_patch.py` → `pp_ram.sh` + `pp_curvas.bin` |
| `pp_ram.sh` idempotente con vigilancia del hueco `0x43FAF28C…0x43FB8EE0` | hecho (3.64+), **el vigilante no queda vivo en cámara** | `pp_curves_patch.camera_files`, `tests/test_g29_pp_ram_vigilancia.py` |
| Silent Shooting de tres estados; **Silent manda sobre EFCS** (3.65) | hecho, sin probar en cámara | `scripts/g22/patch_tristate.py` (`electronic = [cfg+0x238]`) |
| Gris de EFCS con Silent On | **no hecho** (factor de inhibición del pid `0x46` sin localizar) | `docs/PENDIENTES.md` |

3.65: sha256 `ae492237c6c70983c517af7e5a9ee52bd98356f6da9f6a961650f552f431bec4`, auditoría 29/29 (`analysis/gui/audit-3.65.json`).
`base-357.tar` se regeneró con el nuevo `patch_tristate`; sin ello el BIONZ del paquete llevaba el parche viejo.

## 2. Cronología de fallos y hallazgos

1. **3.62**: abrir PP colgaba la cámara (3 veces); Custom Key y Function Menu Set. rotos. Causa A: los ajustes de PP usaban pids ya ocupados (230 de 233). Causa B (hipótesis): la cueva `0x43FB7400` (datos y código de los ganchos de Color Mode) leída a cero ~140–197 s tras el arranque con los ganchos presentes.
2. **3.63**: pids nuevos (ampliación de tablas). Verificado estáticamente que las únicas referencias a las tablas `ELEM`/`D` de `viewUnified2.so` son las tres parcheadas.
3. **3.64**: `pp_ram.sh` ya no se niega a escribir si los ganchos existen; vigila el hueco entero cada segundo y repara/vuelca.
4. **Prueba del 3.65 en cámara**:
   - La cueva `0x43FB7400` quedó **intacta hasta 391 s** (md5 de 256 B = el esperado). El cuelgue de PP **ya no ocurre**. Qué de los cambios 3.62→3.65 lo evitó no está determinado; la hipótesis de la cueva ni se confirma ni se descarta.
   - `pp_ram.log` solo trae `inicio` y `OK`; no hay `pp_hueco_*.bin`; `ps` no muestra el vigilante (lanzado con `( … ) &` en `s_start_android.sh:51`; probablemente muere con el subshell).
   - En PP **los valores vuelven al por defecto** al salir de cada fila. Color Mode B&W no cambia la imagen. Saturation «parece funcionar» (percepción del usuario, no medida).
5. **Medición en vivo del bloque `cfg` del núcleo** (`0x43EDF684`, `/dev/mem`, `chroot /android hd`) tras elegir B&W (= Movie + saturación −8): `cfg+0x138` = 0 (tipo Movie), `cfg+0x13c` = 8 (nivel), `cfg+0x14e` = `0xF8` (−8, antes 0). La cadena menú → `libObj` → LIRO `0x4066` → `cfg` **funciona**.
6. **El núcleo sí reenvía los campos PP** (corrección de una afirmación previa errónea): la función que empieza antes de `0x437aa790` arma el mensaje de colorimetría con `+0x23` = (`cfg+0x138`==0 ? 8 : `cfg+0x13c`), `+0x24` = `cfg+0x14e` + `cfg+0x3d9`, `+0x25` = `cfg+0x14f`, `+0x2a…+0x2f` = Color Depth `cfg+0x148…0x14d` + `cfg+0x3f0…0x3f5`, `+0x30` = gamma `cfg+0x153`. Otros lectores de `+0x14e`/`+0x14f`: `0x4382944e`, `0x438a3900`, `0x438acd28`, `0x438902ba`, `0x43b0fb58`. No hay nada que portar de la A7S para saturación, fase ni Color Depth.

## 3. Estado de cada síntoma

| Síntoma | Estado | Evidencia |
|---|---|---|
| Cuelgue al abrir PP | resuelto en 3.65 (no reaparece en la sesión probada) | PP abre; cueva intacta |
| Escritura menú → núcleo | funciona | `cfg+0x14e` pasó de 0 a `0xF8` |
| B&W sin efecto visible | **sin explicar** | hipótesis: −8 es poco en la escala del ISP (PP real: −31…+31) o la suma con `cfg+0x3d9` satura; sin medir |
| Valor vuelve al por defecto en el menú | **sin explicar** | lectura `0x49` (`libObj 0x4a77bc`, getter virtual `0x4a5adc`) devuelve estado cacheado; no se ha trazado quién lo actualiza |
| Vigilante de `pp_ram.sh` muerto | causa probable, sin arreglar | `ps` sin proceso; `s_start_android.sh:51` |

## 4. Límites de lo afirmado

- Todo lo de cámara procede de una sola sesión (uptime hasta ~1300 s) y de percepciones del usuario sobre la imagen; no hay capturas.
- No se probó en cámara que Silent mande sobre EFCS ni que Custom Key / Function Menu Set. funcionen.
- Sin comprobar: Reset (id `0x42`), consumidores de los índices de matriz `0x10/0x11/0x19`, y otras tablas de 233 entradas fuera de `viewUnified2.so`.

## 5. Siguientes pasos

1. Arreglar el vigilante (`nohup`/`setsid`) y reconstruir (3.66).
2. Lectura del valor en el menú: trazar `0x4a5adc`/notificación `0x8577`; alternativa, descriptor con respaldo NVRAM.
3. Con cámara: saturación mínima y B&W mirando el byte `+0x24` del mensaje; probar Silent > EFCS; abrir PP tras >5 min y leer `pp_ram.log`.
4. Localizar el factor de inhibición del nodo EFCS (pid `0x46`) para el gris con Silent On.

## 6. Actualización 11-11-2026 (CFW 3.66–3.73)

Este informe cubría hasta el 3.65; lo posterior, con los cambios que invalidan §3 y §5:

| Versión | Cambio | Estado |
|---|---|---|
| 3.67 | S-Log3 con valor de app 2; selector de perfil lee `getModelInfo 0x4a` clave `0x275`; eco `0x4a5836` | selector PP1–PP9 **funciona** (usuario); S-Log2/3 sin diferencia visible |
| 3.68 | `CamMsgConv` corregida (0x480→10, 0x481→11); EFCS en gris con Silent On (`isGrayedOut`) | sin probar en cámara |
| 3.69–3.72 | trazas `CFW_TRACE=1` en `libObj` (relativas al PC desde `8afedebe`) | diagnóstico |
| 3.71 | **parche PP del núcleo en `nflasha3`** (`build_base_pp.py`, G31); desaparecen `pp_ram.sh` y su vigilante | instalado, 100 % Done |
| 3.73 | repintado instantáneo (el eco marca los ids `0x49`/`0x4a`) y menú **plano** de 6 filas por página | instalado; sin prueba funcional registrada |

Correcciones a §3/§5: «vigilante muerto» y «arreglar el vigilante» quedan **superados** (ya no hay vigilante); «valor vuelve al por defecto» tiene causa medida con el 3.72 (`[obj+8] = −1`, sin notificación; la lectura periódica lo corregía) y arreglo en el 3.73; la estructura de carpetas anidadas de la A6300 **no funciona** en la A6000 (la UI no abre carpetas anidadas y solo muestra 6 filas). Pendientes vivos: [PENDIENTES § G30-C](../PENDIENTES.md).

