# G09 — Dónde vive el ajuste «Silent Shooting / Shutter Type» del A6300 y qué falta en la A6000 (estático, 07-11-2026)

**Base**: A6300 fw2.01 y A6000 fw3.21 extraídos (`nflasha15_unpacked_unpacked`). **Método**: lectura de bytes/símbolos
(`scripts/gui/setting_nodes.py`, `uxc_strings.py`), REA (`viewUnified2.so` A6300, `CautionConfig.so` A6000). Sin tocar la cámara.
**Objetivo del usuario**: replicar en la A6000 el selector de obturador silencioso del A6300 **sin** perder «EFCS off» (hoy el
electrónico reutiliza el selector EFCS, byte `+0x210`, [E25-24](../capture/e25-24-selector-efcs-electronico.md)).

## 1. Qué trae el menú del A6300 (VERIFICADO)

| Entrada de menú | Etiqueta / ayuda (`string_english`) | Opciones |
|---|---|---|
| **Silent Shooting** | `0xf840` «Silent Shooting» (`0xf846`) / `0xf847` «Suppress operation sounds… to the minimum» | Off `0xf2a1`, On `0xf849` |
| **Shutter Type** | `0xf901` / `0xf93a` «Sets the shutter type when shooting still images» | Auto `0xf912`, Mechanical Shut. `0xf907`/`0xf90d`, Electronic Shut. `0xf927`/`0xf935` |
| e-Front Curtain Shut. (ya en la A6000) | `0xf04e` / `0xe930` | On `0xe95a`, Off `0xe95b` |

Ninguno de estos ids `0xf840–0xf949` existe en `string_english.uxc` de la A6000 (4 360 textos frente a 5 415): habría que **añadirlos** (el editor
`uxc_strings.py` ya reindexa) o reutilizar los existentes de la A6000 (`0xf290` «Silent Shutter Mode», `0xf2a1`).

## 2. Las cuatro capas del ajuste

| Capa | Dónde | A6300 | A6000 |
|---|---|---|---|
| **1. Nodo de ajuste** (etiquetas, opciones, ProcessId) | `lib/CautionConfig.so`, símbolos `cmnViewSettingNode*` / `cmnViewSettingPropertyList*` (`.rodata`) | `SilentShutter` raíz: ProcessId `0x2b`; `CustomStillShutterType` raíz: ProcessId `0x13f`, opciones Auto=0 / Mechanical=1 / Electronic=2 | **Sin nodo real de Silent** (§3). EFCS: ProcessId `0x46` (A6300: `0x4e`), On=0 / Off=1 |
| **2. Elemento de proceso y página de menú** | `viewUnified2/4/7.so`: clases `CmnViewProcessDataElementCustom{SilentShutter,StillShutterType,FrontCurtainShutter}`, `ACT_SilentShutter*` | existen | `CustomFrontCurtainShutter` sí; los de Silent/StillShutterType **no** (150 elementos frente a 248) |
| **3. Camera-user (`libObj.so`)** | secuencias `N7CamUser28SequenceSetSilentShutterMode`, `…SetFrontEShutterMode`; A6300 añade `SequenceSetShutterType`, `pvt_ActionSetShutterType`, `pvt_ChangeShutterTypeParamApp2Obj/Obj2App`, `pvt_ActionNotifyShutterTypeEvt` | las tres | **Silent y FrontEShutter sí** (mensajes `0x768e`→selector LIRO `0x40e3`; `0x75fa`→`0x4099`, [investigación](../capture/shutter-investigation.md)); ShutterType **no** |
| **4. Núcleo (`av-cam.bin`, LiroSeq/CAIF)** | validación `CheckSetShutterType` (`shutterType`, `0x438c8b52`, [S169](../capture/s169-drive-api-a6300.md)); paquete CAIF `pkt[+0x12] \|= 0x20` si `*(cap+0x804)==2` ([S401](../capture/s401-a7s-silent-control-path.md)); `libScalarDaemon`: `setSilentShutterMode`, `s_silentShutterMode` | completo | sin handler de `0x40e3` ni campos `SilentShutterMode`/`shutterType`; sí `0x4099` (EFCS) |

Formato de la capa 1 (`setting_nodes.py`): tripletas `{prop, flag, valor}`; `0`=etiqueta, `6`=ayuda, `0xe`=ProcessId (solo raíz), `0xf/0x10`=valor interno de la opción.

## 3. Corrección: el nodo «SilentShutter» de la A6000 es de SteadyShot

[E007](../silent-shutter-trace.md) y [silent-shutter-status](../capture/silent-shutter-status.md) tomaron `cmnViewSettingNodeRootSilentShutter` de la A6000 por
un nodo de obturador silencioso. Sus propiedades dicen otra cosa (VERIFICADO en bytes, `test_gui_uxc_strings.py`): raíz con etiqueta `0xf199` «SteadyShot», ayuda `0xe589`
«Sets SteadyShot…», On `0xe27c` «Turns on SteadyShot.», Off `0xe27d`, ProcessId `0x26`. Es un resto con nombre engañoso (INFERENCIA: reutilización del símbolo); **no** es un menú
de Silent oculto. En el A6300 el mismo símbolo sí es el de Silent Shooting (etiqueta `0xf840`, ProcessId `0x2b`).

## 4. Cómo replicarlo en la A6000 sin perder «EFCS off» (propuesta, sin implementar)

Principio: **un selector nuevo e independiente del EFCS** (el A6300 también los separa: EFCS `0x4e` y Silent `0x2b` / Shutter Type `0x13f`).

1. **Capa 1**: clonar en `CautionConfig.so` de la A6000 los `PropertyList` del A6300 (Root + opciones) con ProcessId libre y textos propios (`uxc_strings.py`).
   Las listas son datos de `.rodata`; hace falta además el objeto nodo (`B`, 0x28 B) y el constructor estático (`_INIT_*`) que lo registra: parche de código o cueva, **no solo datos**.
2. **Capa 2**: elemento de proceso y fila en la tabla de la página (formato `CmnViewMenuItemStruct`, [G04](g04-menus-y-recursos.md)), con el mapeo ProcessId→mensaje.
3. **Capa 3**: la A6000 ya tiene `SequenceSetSilentShutterMode` (`0x768e`→`0x40e3`); basta con que el elemento la invoque (sin tocar el camino EFCS `0x75fa`/`0x4099`).
4. **Capa 4** (la difícil, ya conocida): dar a `0x40e3` un manejador en `av-cam` que active la ruta electrónica **sin** reescribir `+0x210`; usar un campo propio (análogo a `cap+0x804==2` del A6300). Comprometido con lo ya hecho desde el 3.30 (`pkt[0x0e]`) y con el parche EFCS v3 de Darwin, que no se tocan.

Alternativa mínima (sin menú nuevo): tercer estado en el selector EFCS — ya valorada y **no segura** en E25-24.

## 5. Hallazgos adicionales (misma fecha)

- **Capa de mensajes (`libObj.so`, VERIFICADO por cadenas)**: la A6000 ya trae `PARAMID_SILENT_SHUTTER_MODE{,_ACT,_SET}` y `PARAMID_FRONT_ESHUTTER_MODE{,_ACT,_SET}`; el A6300 añade solo
  `PARAMID_SHUTTER_TYPE{,_ACT,_SET}` y `ObjCamera::MSGID_SET_SHUTTER_TYPE_CMD`. Es decir, el camino Silent de capa 3 existe en la A6000; ShutterType sería el único añadido de `libObj`.
- **Las dos compilaciones no son intercambiables**: la A6000 tiene bibliotecas separadas (`cmnFnWrapper`, `wrapper*.so`, `cmn_view_processDataMgr`, `cmn_menuTableUtil`…) que el A6300 funde en `viewUnified*.so`
  (sin esos `.so`, y con `libInfra*` nuevas). Por eso las capas 1–2 del A6300 no se pueden trasplantar tal cual: hay que reescribirlas al esquema de la A6000, usando el A6300 solo como modelo de datos (propiedades, textos, ids).
- **Descartado**: el barrido de «listas de ProcessId» por todas las bibliotecas (`/tmp`, no versionado) da ruido (valores pequeños se repiten en tablas ajenas, p. ej. pares `{id, nombre de MSG_PARAM_ID}` de `libScalarDaemon`); **no** se usa como evidencia de dónde se registra un ProcessId.
- `CameraOnDemandSaver.so`, `arbiter.so` y `CmnViewIroiroConDataMgr.so` contienen listas con el ProcessId EFCS (`0x46`) en la A6000: candidatas a registros de persistencia/exclusión que un ajuste nuevo debería tocar. **NO_VERIFICADO** su función.

## 5b. Dónde se coloca el ajuste en el menú (VERIFICADO sobre relocaciones, 07-11-2026)

Las páginas de menú son **arrays de punteros a nodos raíz** (`cmnViewSettingNodeRoot*`, importados de `CautionConfig.so`) en `.data.rel.ro` de `viewUnified2.so`, con una relocación
`R_ARM_ABS32` por entrada (`readelf -r -W`). El orden del array es el orden del menú. La entrada del EFCS aparece en **5 páginas** en ambas cámaras:

| | A6000 fw3.21 (vaddr ELF) | A6300 fw2.01 (vaddr ELF) |
|---|---|---|
| Entradas EFCS | `0x4a2f3c`, `0x4a338c`, `0x4a366c`, `0x4a36cc`, `0x4a377c` | `0x75778c+4`, `0x757fe0+4`, `0x758728+4`, `0x759a98+4`, `0x75a0a0+4` |
| Vecinos | `AfWShutter`/`AelWShutter` → **EFCS** → `SuperiorAutoSettings`/`AutoImageExtract`/`TouchShutter` | `AfWShutter`/`AelWShutter` → **SilentShutter** → **EFCS** → `AutoImageExtract` |

Es decir, en el A6300 «Silent Shooting» es **una entrada insertada justo antes de EFCS en las mismas cinco páginas** (y `Shutter Type` va en otras: `0x757248`, `0x7585a8`, `0x7599e0`, `0x75a65c`, junto a `StillMemory`/`SelfPortrait…`).
Además `viewUnified7` lista `SilentShutter` antes de `StillSteadyShot` en ambas cámaras (A6000 `0x5f7b8`, A6300 `0x75638`).

**Consecuencias de diseño** (INFERENCIA; sin verificar el consumidor de los arrays): (a) añadir la entrada exige alargar cinco arrays — hay que localizar el contador/consumidor — o **sustituir** el puntero de una entrada poco usada
cambiando solo el símbolo de su relocación (sin tocar tamaños); (b) el nodo nuevo ha de ser un símbolo definido en `CautionConfig.so` (el stub `SilentShutter` de la A6000, con sus nodos On/Off ya construidos, es la base más barata: cambiar su `PropertyList`
—etiquetas, ProcessId— son datos de `.rodata`, y añadir los textos a `string_*.uxc`).

## 5c. Consumidor de las páginas: `_INIT_70` de `viewUnified2.so` (A6000, VERIFICADO con REA)

Cada página es un nodo local construido con `CmnViewSettingNode::CmnViewSettingNode(nodo, hijos**, cuenta, propiedades)`; `hijos` es el array de punteros de §5b y `cuenta` una **constante en el código** (`_INIT_70`, Ghidra `0x11b674+`; hay 394 construcciones en esa función).
Páginas que contienen el EFCS (direcciones Ghidra = ELF + `0x10000`):

| Nodo de página | Array de hijos | Cuenta | Índice del EFCS | Propiedades | Tras el array |
|---|---|---|---|---|---|
| `0x4d4c88` | `0x4b2f38` [`AelWShutter`, **EFCS**, `SuperiorAutoSettings`, `CustomFaceRecognition`, `CustomLensComp`] | 5 | 1 | `0x4d2034` | 2 palabras nulas y luego otros datos |
| `0x4d4da4` | `0x4b337c` [`StillDigitalZoom`, `StillClearImageZoom`, `ReleaseWOLens`, `AelWShutter`, **EFCS**, `TouchShutter`] | 6 | 4 | `0x4d24a4` | 2 palabras nulas |
| `0x4d4738` | `0x4b3664` [`AfWShutter`, `AelWShutter`, **EFCS**, `SuperiorAutoSettings`] | 4 | 2 | `0x4d6bd8` | contiguo con otro array |
| `0x4d2c0c` | `0x4b36c8` [`AelWShutter`, **EFCS**, `AutoImageExtract`, `CustomExpCompSet`, `CustomBracketOrder`] | 5 | 1 | `0x4d5960` | contiguo |
| `0x4d3494` | `0x4b3778` [`AelWShutter`, **EFCS**, `AutoImageExtract`, `CustomExpCompSet`, `ExposureCompSaveReset`, `CustomBracketOrder`] | 6 | 1 | `0x4d2668` | contiguo |

(Comprobado: cada EFCS cae dentro de `[array, array + 4·cuenta)` en las 5 páginas.) Añadir una entrada exige **tres** cosas: (1) mover o ensanchar el array, (2) una relocación dinámica nueva (`R_ARM_ABS32` contra el símbolo del nodo; el `.rel.dyn` no tiene hueco evidente), (3) subir la constante `cuenta` en `_INIT_70`.
Solo las páginas 1 y 2 tienen palabras nulas de relleno tras el array, pero un puntero nulo hijo no es válido y aun así faltaría la relocación.
**Ruta sin crecimiento** (la más barata): *sustituir* el símbolo de una relocación existente en cada página (`r_info`), p. ej. `AelWShutter` → nodo Silent, a costa de esa entrada de menú; no cambia tamaños ni cuentas. La variante «insertar» queda como trabajo de parcheo ELF (NO_VERIFICADO que sea viable sin reconstruir el `.rel.dyn`).
No he comprobado que las cuentas del A6300 sean las de la A6000 + 1 (NO_VERIFICADO; el A6300 solo se leyó por relocaciones).

## 5d. Decisión del usuario: **insertar** una entrada nueva (no sustituir) — viabilidad (07-11-2026, estático)

Motivo (usuario): su CFW actual ya reutiliza la opción EFCS (On/Off) como «Silent» / «Mechanical con EFCS On»; la entrada nueva debe convivir con ella sin sustituir nada.

**Restricciones medidas en `viewUnified2.so` (A6000 fw3.21), VERIFICADO:**

| Hecho | Medida | Consecuencia |
|---|---|---|
| `.rel.dyn` | `0x2e7a4`, 733 952 B, seguido de `.rel.plt` sin hueco; `DT_RELCOUNT` = 43 132 | no se pueden añadir relocaciones en sitio |
| Cabeceras de programa | 5 (`EXIDX`, 2×`LOAD`, `DYNAMIC`, `GNU_STACK`), tabla pegada a la primera sección | para añadir un `LOAD` hay que mover la tabla de cabeceras |
| `PT_GNU_RELRO` | **no existe** | `.data.rel.ro` es escribible tras la carga: un parche en tiempo de ejecución (código) sería posible |
| Huecos de código | ninguna racha de ceros ≥ 32 B en `.text` | no hay cueva ejecutable en el ELF actual |
| Símbolo del nodo | `cmnViewSettingNodeRootSilentShutter` **no** está en `.dynsym` de `viewUnified2` | usar `R_ARM_ABS32` contra un símbolo ya importado (p. ej. `…RootAelWShutter`) con **addendum** = distancia fija a la raíz Silent dentro de `CautionConfig.so` (mismo `.so`, mismo diseño de `.bss`), sin tocar `.dynsym` |
| Llamada del constructor | `ldr r1,[pc,#lit]; add r1,pc` (array) y `movs r2,#N` (cuenta) antes de `blx #0xe81c8` (PLT de `CmnViewSettingNode::CmnViewSettingNode`) | por página basta cambiar **una palabra de literal** (dirección del array) y **un inmediato** (cuenta) |

Sitios localizados (ELF): página 1: `ldr` `0x166182`, literal `0x166ce8`, `add` `0x16618c`, `movs r2,#5` en `0x166180`; página 2: literal `0x166f70`, `movs r2,#6` en `0x166918`; página 3: literal `0x166fe8`, `movs r2,#4` en `0x166a80`.
**Páginas 4 y 5 no encontradas** con el mismo patrón (otra codificación; pendiente).

**Mecanismo propuesto (no implementado):** añadir un segmento `PT_LOAD` al final del `.so` con (1) copias de los 5 arrays con una entrada más, (2) una copia ampliada de `.rel.dyn` con las relocaciones de todas las entradas de los arrays nuevos (`DT_REL`/`DT_RELSZ` apuntan a ella; las relocaciones de los arrays antiguos pasan a ser inofensivas) y (3) el `movs r2,#N+1` y el literal reapuntados en `_INIT_70`. Orden elegido: la entrada nueva **antes** del EFCS (como en el A6300). El EFCS conserva su entrada, id `0x46` y camino `0x4099`.
Riesgos: la tabla de cabeceras movida y el `LOAD` nuevo no se han probado con el cargador de la cámara (glibc 2.11.2); no hay `qemu-user` instalado (requiere `sudo pacman -S qemu-user`, que necesita contraseña) para un cargado de prueba fuera de la cámara; el ext2 de `/usr` está casi lleno (el `.so` crece ~0,1–0,3 MB; ~7 MB libres, [G04 §6](g04-menus-y-recursos.md)).

## 5e. Prototipo del parche de inserción y prueba de carga con `qemu-user` (07-11-2026, VERIFICADO fuera de la cámara)

**Herramientas**: `scripts/gui/add_menu_entry.py` (genera el `viewUnified2.so` parcheado), `scripts/gui/qemu_sysroot.py` (sysroot con el glibc 2.11.2 y las bibliotecas de la cámara para `qemu-arm`),
prueba `test_parche_de_paginas_inserta_y_reubica`. `qemu-user` y `gdb` instalados en el equipo de trabajo (Arch).

**Sitios corregidos** (ELF; `array → literal / add / movs r2,#N`): p1 `0x4a2f38` (`0x166ce8`/`0x16618c`/`0x166180`, N=5); p2 `0x4a337c` (`0x166f70`/`0x166924`/`0x166918`, 6);
p3 `0x4a3664` (`0x166e20`/`0x166534`/`0x166528`, 4; **corrige** un array erróneo `0x4a3654` de la primera pasada, que era la página de «Cleaning Mode/Calibration»);
p4 `0x4a36c8` (`0x16b16c`/`0x16a84a`/`0x16a842`, 5); p5 `0x4a3778` (`0x169200`/`0x168df8`/`0x168dec`, 6). El parche comprueba por aserción que cada literal resuelve al array y que el `movs` es `0x2200|N`.
Los arrays de p1–p3 también los usan otros nodos con cuentas menores (subconjuntos): no se tocan, siguen con el array antiguo.

**Parche**: segmento `PT_LOAD` RW nuevo en `0x4d0000` (0xb353c B: `.rel.dyn` copiado + 31 relocaciones, los cinco arrays con una entrada más y la tabla de cabeceras movida, 6 entradas); `DT_REL` y `DT_RELSZ` reapuntados; la entrada nueva va **antes del EFCS**
(`R_ARM_ABS32` contra `cmnViewSettingNodeRootAelWShutter` + addendum `0xeb0` = distancia a `cmnViewSettingNodeRootSilentShutter` en `CautionConfig.so`). El fichero crece 0,76 MB (4 953 524 → 5 715 260 B).

**Prueba de carga** (`qemu-arm -L sysroot`, ld.so de la cámara, `LD_PRELOAD="/usr/lib/libObj.so viewUnified2.parcheado.so"`):
1. El cargador acepta el `.so` (6 cabeceras, `phdr` en el segmento nuevo) y llega a «calling init» del parcheado en el mismo punto que el original (el guest muere después con SIGSEGV en `libObj`/`osal`: no hay hardware, **igual con el original**).
2. Con `gdb` (`target remote`) tras la señal, memoria real de las cinco páginas: cada nodo apunta a su array nuevo con **cuenta + 1** (6, 7, 5, 6, 7) y cada array queda `[…, AelWShutter, <Silent 0x42faab2c = base CautionConfig + 0x1c9b2c>, <EFCS 0x42fab490 = base + 0x1ca490>, …]`:
   la entrada nueva se resuelve al nodo `SilentShutter` y el EFCS conserva su entrada.

**Límites**: es la carga y el reubicado de datos; no se ha ejecutado la interfaz ni el menú (necesita la cámara). El nodo insertado es todavía el stub con etiquetas de SteadyShot (§3): falta cambiar su `PropertyList` en `CautionConfig.so`,
añadir textos a `string_*.uxc` y el cableado a `libObj`/`av-cam`. Persistencia: el `.so` parcheado exige reempaquetar `nflasha15` (riesgo de §G8) o probarlo por la vía B (montaje temporal por telnet). `/usr` queda con ~6 MB libres.

## 7. Paquete de prueba «Silent Shooting al estilo A6300» — listo para probar (07-11-2026)

**Requisito del usuario**: que la entrada nueva funcione **como el CFW ya hecho** (activar el silencioso, nada más), con la presentación del A6300 y sin sustituir el menú EFCS.

**Cómo funciona (mismo backend que el CFW)**: el nodo nuevo escribe el **mismo ajuste que el menú EFCS** (ProcessId `0x46` → `PARAMID_FRONT_ESHUTTER_MODE` → selector LIRO `0x4099` → `+0x210`;
[E25-24b](../capture/e25-24b-implementacion-selector.md): valor 0 = EFCS, 1 = electrónico). «Silent Shooting: **Off** = valor 0, **On** = valor 1». No añade Shutter Type, ni toca `av-cam`/Darwin. Las dos entradas (EFCS y Silent) son vistas del mismo valor y quedan sincronizadas.
(INFERENCIA: que el elemento de proceso del ProcessId `0x46` acepte un segundo nodo es lo que la prueba debe confirmar.)

**Construcción** (`scripts/gui/build_silent_menu_test.py DEV_A6000 DEV_A6300 analysis/gui/silent-menu-test`; carpeta ignorada por git, 13 MB, 27 ficheros, `SHA256SUMS` y `MANIFEST.json` con md5 de originales y parcheados):

| Fichero | Cambio |
|---|---|
| `lib/viewUnified2.so` | 5 páginas con la entrada nueva antes del EFCS (§5d/§5e) |
| `lib/CautionConfig.so` | las 3 listas de propiedades del nodo `SilentShutter` (3+4+4 entradas, tamaños fijos): raíz = etiqueta `0xf840` «Silent Shooting», ayuda `0xf847`, ProcessId `0x46`; «On» = valor 1, ayuda `0xf849`; «Off» = valor 0, ayuda `0xf2a1` |
| `share/app/string_<idioma>.uxc` | ids `0xf840/0xf847/0xf849` añadidos en 25 idiomas de esquema latino (traducción de la A6300 en 6; en el resto el texto en inglés). Los 35 idiomas de tabla de 32 bits (ruso, japonés, árabe…) **no** se parsearon: sin textos nuevos |

**Verificado fuera de la cámara**: los dos `.so` parcheados cargan juntos con el cargador de la cámara (`qemu-user`, glibc 2.11.2); en memoria el nodo `SilentShutter` queda con 3 propiedades de raíz, 2 hijos y las listas editadas; test `test_paquete_silent_menu_semantica_efcs`.

**Prueba en cámara** (`scripts/gui/camera_ui_test.py PAQUETE {probe|deploy|revert} [--execute]`; sin `--execute` solo imprime). Telnet + FTP temporal, montajes `bind` en RAM (un reinicio los borra; **nada se flashea**):
1. `probe --execute`: mounts, md5 de `/usr` frente al 3.21 (aborta si difiere), proceso de la UI (`im.elf`, su padre), espacio en `/android` (tmpfs; `/tmp` es vfat de 5 MB y no cabe) y soporte de `mount --bind`.
2. Sin volcado NVRAM previo (el usuario indicó que ya hay suficientes copias; esta prueba no escribe NAND ni NVRAM, solo montajes en RAM y el ajuste EFCS que el menú ya escribe).
3. `deploy --execute`: sube a `/android/silentmenu`, verifica md5 y monta cada fichero sobre su original.
4. **Recargar la UI**: `libObj` carga `CautionConfig`/`viewUnified2` al arrancar `im.elf`; el montaje solo surte efecto al reiniciar ese proceso. **NO VERIFICADO** cómo se lanza/respawnea `im.elf` (ningún script del rootfs lo menciona): lo dirá `probe` (padre del proceso). Si no hay supervisor, matar `im.elf` puede dejar la cámara sin pantalla hasta reiniciar, y reiniciar borra el montaje: en ese caso hace falta un gancho de arranque (vía A, flasheo) y no se sigue por esta vía.
5. Criterios: la entrada «Silent Shooting» aparece antes de «e-Front Curtain Shut.» en las 5 páginas; elegir On/Off no cuelga la UI; el menú EFCS refleja el cambio (On ⇄ Off del EFCS) y el disparo se comporta como con el CFW (EFCS off = electrónico).
6. `revert --execute` (o reiniciar): desmonta y borra.

## 7b. Resultado de la prueba en cámara (07-11-2026) — la vía temporal NO sirve

Ejecutado con autorización del usuario (cámara por red y SWD disponibles; sin SWD usado):
- `probe`: OK. `/usr` es `ext2 ro`; md5 de `viewUnified2.so`, `CautionConfig.so` y todos los `string_*.uxc` **iguales** al 3.21 de referencia; `mount --bind` funciona; `/tmp` vfat 5 MB, `/android` tmpfs con 8–14 MB libres (insuficiente), SD = FUSE servido por `im.elf` (no vale de origen). Staging en `/android/data/silentmenu` (vfat interno).
- `deploy`: FTP temporal (hizo falta abrir `ufw` para 192.168.1.29, ya cerrado) → md5 verificado → `bind` de los 3 ficheros (`viewUnified2`, `CautionConfig`, `string_spanish`, el idioma activo).
- **`im.elf`** (pid 148, `ppid=1`, cwd `/usr/share/app`, args `debug s g r u l i a lazy-global`) **ignora SIGTERM** y no tiene supervisor: PID 1 es un bucle `ash`. Con `kill -9` murió; el relanzado manual (mismo entorno y argumentos; `nohup` no existe en el busybox) arrancó (pid 3195, «GLES Vecgen disabled», «DMP_2D_Initialize : 0») y a los pocos segundos **la cámara se reinició sola** (el usuario lo confirmó): reiniciar `im.elf` en caliente dispara el reinicio, y el reinicio **borra los montajes**.
- Conclusión: el cambio solo puede aplicarse **de forma persistente** (firmware con `nflasha15` modificado, vía A de §G8) o con un gancho que monte los ficheros **antes** de que arranque `im.elf` (no existe en el rootfs conocido; el que lanza `im.elf` es anterior al shell de PID 1). La cámara no queda modificada: ni NAND ni NVRAM escritas; solo ~8 MB en `/android/data/silentmenu` (borrar con `revert`).
- Para la próxima: `camera_ui_test.py deploy` + `restart-ui` quedan como herramientas históricas; no repetir `restart-ui` (provoca reinicio).

## 8. Cómo reconstruir `nflasha15` en el paquete (investigado y construido offline, 07-11-2026)

**Formato** (VERIFICADO): `dev/nflasha15` del `firmware.tar` es un **TPZL** (LZPT) de un ext2 de 155 516 928 B (blocks de 1 KiB, raíz = `/usr`): 2 373 bloques de 64 KiB, cada uno = 16 registros LZ77 de 4 096 B, alineados a 512 B.
La cámara lo expone como `/dev/dnflasha15` (capa de descompresión; `/usr` = `ext2 ro`) y el actualizador lo escribe como blob de ~84 MB en la partición de 104 857 600 B (`mount.conf`). Integridad: solo CRC-32 + tamaño en `part_image.sum` (línea `dev/nflasha15`) y la comprobación del FDAT (modelo/región/versión); sin firma.

**Cadena construida** (misma técnica que `nflasha3` en `scripts/e25_27`, reutilizada):
1. `scripts/gui/build_nflasha15.py ORIGINAL PAQUETE SALIDA`: descomprime el TPZL, sustituye los ficheros del paquete en el ext2 con `debugfs` (`rm` + `write`, modo/uid/gid conservados), exige `e2fsck -fn` limpio, y recompone **solo los bloques que cambian** (`tpzl.patch_decompressed`: registros originales para las páginas intactas, LZ77 de Sony para las nuevas, relleno a 512 B, reglas del LDEC).
2. `scripts/gui/build_package_nflasha15.py NFLASHA15 SALIDA [--base-tar] [--version]`: sustituye `dev/nflasha15` y su línea de `part_image.sum` en el tar base, empaqueta con `fwtool` y comprueba el desempaquetado byte a byte (tar, sumas, firma ext2, resto de miembros idéntico).

**Resultado** (base = CFW 3.38, `analysis/e25-27/artifacts-338/firmware.integrated.tar`, EFCS off = electrónico):
- `nflasha15` nuevo: 84 699 136 B (+656 KB; límite de partición 104 857 600), CRC-32 `bc6d4807`, **135 de 2 373 bloques recompuestos** (el resto, byte a byte de Sony); `fsck` limpio.
- Verificaciones: descompresión = ext2 parcheado; **decodificador independiente** (`fwtool.lz77`) coincide en los 136 bloques distintos y 24 de muestra; los 27 ficheros del paquete extraídos del ext2 del `.dat` coinciden con `silent-menu-test` (27/27); `libObj.so` (no tocado) idéntico al original.
- Paquetes (carpeta `analysis/gui/silent-menu-pkg/`, ignorada por git, 1,3 GB, con `SHA256SUMS`):
  - `pkg-3.39/package-3.39/firmware_packed.dat` — **con el menú**: `d0be79039bcb6126…`, línea `0,bc6d4807,050c6800,000001a4,00000000,000003e8,root,root,-1,-1,dev/nflasha15,`.
  - `pkg-3.40-revert/package-3.40/firmware_packed.dat` — **vuelta atrás**: `/usr` original de Sony (CRC `df198ecd`, `050264e1`) sobre el mismo CFW 3.38, versión 3.40 porque el actualizador solo acepta versiones mayores: `5ac4a9b24e74d91e…`.
  - Mismo modelo `0x41030035`, región 0, `updater.img` oficial; estado **CONSTRUIDO OFFLINE — INSTALACIÓN NO AUTORIZADA**.

**Pendiente de comprobar en cámara / riesgos**:
1. Que el Linux de la cámara acepte los 135 bloques recompuestos (el decodificador software lo hace; el de la cámara usa el LDEC — R51 §6.6: un bloque de `nflasha3` recompuesto con registros almacenados que crecía colgó el LZP; aquí `hardware_violations` es vacío y las páginas nuevas usan LZ77, pero **no hay prueba hardware**).
2. Que `viewUnified2.so` parcheado (segmento añadido) y `CautionConfig.so` editado arranquen la UI (probado solo con `qemu-user`).
3. La versión instalada ahora es 3.37/3.38: instalar el 3.39 exige batería > 50 %, cable directo y `sha256sum -c SHA256SUMS`; la vuelta atrás es el 3.40. Si no arrancara: recuperación por SWD/actualizador como en R46–R49 (`nflasha1` no va en el paquete).
4. Los 35 idiomas de tabla de 32 bits no llevan textos nuevos; el español sí (en inglés).

## 8b. Auditoría del paquete de instalación 3.39 (07-11-2026) — **APTO** (offline)

Cambios respecto a la primera construcción de §8:
1. **Bloque TPZL 0 idéntico al de Sony** (R55: recomponer el bloque 0 de `nflasha3` colgó el LZP de Linux, causa sin aislar). En el ext2 los únicos bytes que cambiaban en los primeros 64 KiB eran **contadores** (superbloque: `s_free_blocks_count`, `s_wtime`; descriptores de grupo: libres de bloques/inodos). Se restauran los de Sony: `/usr` es de solo lectura y los contadores no se usan; `e2fsck -fn` solo informa «count wrong». Bloques recompuestos: 134 (antes 135). `nflasha15` CRC `6268e2ff`, 84 699 136 B.
2. **Parche de Darwin v3** (R82/R83, commit `20b33eed`, pedido del usuario): `build.efcs_tabla_diff` sobre el `darwin_core.bin` del 3.38 (solo `0x18d6e..0x18e0f`) y `darwin.sum` actualizado. Es **neutro** mientras la tabla NVRAM (`0x1850000+0x48`) esté a ceros (R82); no se escribe NVRAM.

`scripts/gui/audit_package_nflasha15.py` (descifrado propio E25-06, no fwtool) sobre `pkg-3.39/package-3.39/firmware_packed.dat` (`0d054b97…`): **23/23 comprobaciones OK** ([`analysis/gui/audit-3.39.json`](../../analysis/gui/audit-3.39.json)):
contenedor (DEND, descifrado = FDAT, CRC de cabecera, modelo `0x41030035`/región 0, updater oficial 3.21, versión 3.39 > 3.38); tar (solo cambian `darwin_core.bin`, `darwin.sum`, `dev/nflasha15`, `part_image.sum` frente al 3.38; **66/66** líneas de suma verifican);
`nflasha15` (cabe en 104 857 600 B, 0 violaciones LDEC, alineado a 512, contiguo, 2 373 bloques, máx. 129 sectores = Sony, **bloque 0 = Sony**, decodificador independiente `fwtool.lz77` coincide en los 134 bloques); ext2 montado en solo lectura y comparado con el de Sony: **solo cambian los 27 ficheros del paquete**, con sus hashes; Darwin v3 presente y solo en su rango.
Además: `pytest -k "r82 or e25_27_build"` 39/39; la vuelta atrás `pkg-3.40-revert` (`5ac4a9b2…`) es el 3.38 con `/usr` de Sony (sin cambios frente al 3.38 salvo versión; sumas 66/66).

**Riesgos que la auditoría no puede cerrar**: (a) que el LDEC de la cámara lea los 134 bloques recompuestos (bloques intermedios recompuestos sí se leyeron bien en `nflasha3`: 48, 57); (b) que la UI arranque con los `.so` parcheados (solo `qemu-user`); (c) versión instalada < 3.39 (no se pudo leer: cámara fuera de red). Recuperación: `pkg-3.40-revert` por el actualizador, o SWD + actualizador (R46–R49).

## 8c. Fallo del 3.39 en cámara y paquete corregido 3.40 (07/08-11-2026)

**Síntoma (usuario):** tras instalar el 3.39 (`Done`), pantalla negra, sin menú; por USB solo aparece un momento «Sony USB Charger» (`054c:0994`); sin Wi-Fi.

**Diagnóstico por SWD (solo lectura, sin parar la CPU salvo un `halt` corto; MEDIDO)** — evidencias en
[`analysis/camera-dumps/20261107-swd-339-pantalla-negra/`](../../analysis/camera-dumps/20261107-swd-339-pantalla-negra/):
* CPU (`r_readonly_postfail_state.cfg`): modo SVC, `pc=0x40049e9c` (`mov pc, lr` de la rutina de reposo), pila en el `init_thread` → **el kernel Linux está vivo y en reposo**; el fallo es de espacio de usuario.
* Log del kernel por AP0 en `0x83400000` (método de R51): `E/stella(148): assert : src/ResourceManager.cpp(954)` repetido a los 8,29 s (pid 148 = `im.elf`) y después ~80 × `osd_pin send failed`. En los logs de arranques normales (R51) no aparece ninguna de las dos líneas.

**Causa (VERIFICADO offline):** los textos se copiaron a la A6000 con los **ids de la A6300** `0xf840/0xf847/0xf849`, pero el índice de `string_*.uxc` del A6000 tiene **5 958 ranuras** (ids `0xe000…0xf745`). Los registros estaban en el fichero, pero el índice no los alcanzaba (la A6300 tiene 7 120 ranuras). `uxc_strings.build` no lo comprobaba, así que el nodo apuntaba a ids que el `ResourceManager` no encuentra. El assert es de `libObj.so` (`ux::resmgr`). No se ha localizado la línea 954 exacta en el desensamblado; la relación es una INFERENCIA fuerte: es el único recurso nuevo y el resto del parche (`viewUnified2`/`CautionConfig`) no pasa por `ResourceManager`.

**Arreglo:**
* `uxc_strings.build` rechaza cualquier id sin ranura (regresión `test_build_rechaza_id_fuera_del_indice`).
* `build_silent_menu_test.py`: los textos de la A6300 se copian en **ranuras libres del A6000**: `0xf840→0xf3e8`, `0xf847→0xf515`, `0xf849→0xf56a`. Las tres están vacías en los 25 idiomas latinos, no hay registro con esos ids en los 8 no latinos y ningún fichero de `/usr` las referencia como `0x0204xxxx`. Cabecera y número de ranuras sin cambios.
* El test del paquete comprueba que todas las etiquetas y ayudas del nodo quedan dentro del índice. Los 25 `string_*.uxc` se recorren registro a registro: 0 registros inalcanzables (el 3.39 tenía `0xf840/0xf847/0xf849`).

**Paquetes (no versionados, `analysis/gui/silent-menu-fix/`):**
* `pkg-3.40/package-3.40/firmware_packed.dat` (`ac01db34…`): menú corregido + Darwin v3. `nflasha15` CRC `da2cdb80`, 84 691 456 B, 165 bloques recompuestos, bloque 0 = Sony. Auditoría [`audit-3.40.json`](../../analysis/gui/audit-3.40.json): **22/22 OK**, el mismo juego de comprobaciones que el 3.39.
* `pkg-3.41-revert/package-3.41/firmware_packed.dat` (`9cccdfdd…`): vuelta atrás, 3.38 con el `/usr` de Sony. Sustituye al `pkg-3.40-revert`, que ya no se podría instalar sobre un 3.40.

**Instalación:** con la UI caída la cámara no expone USB al PC, así que el actualizador solo se alcanza por SWD (R48/R49 §7.2). Secuencia: batería fuera → batería dentro con el interruptor en OFF → OpenOCD con `analysis/e26-recovery/r48_updater_swd.cfg` → encender → `pmca-console firmware -f …/package-3.40/firmware_packed.dat`.

**Riesgos que siguen abiertos:**
* En los 8 idiomas no latinos (esquema `0x0f`, sin parsear) los tres textos no existen: con la cámara en uno de ellos podría repetirse el assert.
* El LDEC con 165 bloques recompuestos y la UI con los `.so` parcheados (solo probados en `qemu-user`) siguen sin verificar en cámara.

## 6. Límites / siguiente

- **NO_VERIFICADO**: qué tabla de página incluye cada elemento (G4) y cómo se conecta ProcessId → elemento (vtables de `viewUnified2` del A6300 sin resolver: REA no enlaza la relocación del vptr, las funciones salen sin símbolo y la vtable hallada por RTTI es de una clase genérica de rango `0x15a/0x15c`; se dejó para G4/G7). El significado de las props `0xb/0xc/0x11/0x14`.
- Las 4 capas son estáticas; **ninguna** probada en cámara ni parcheada. La capa 4 es el bloqueo real del proyecto (sin handler `0x40e3`).
- Siguiente: (0) instalar `pkg-3.39` (requiere autorización; vuelta atrás `pkg-3.40-revert`); (a) localizar la tabla de la página «Shooting Settings» del A6300 que contiene Shutter Type/Silent Shooting (G4); (b) volcar ProcessId→elemento; (c) diseñar el manejador `0x40e3` con el selector independiente (carril obturador, requiere autorización para cualquier prueba).
