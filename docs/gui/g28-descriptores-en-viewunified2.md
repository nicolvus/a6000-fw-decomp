# G28 — Los descriptores van en `viewUnified2.so`, no en `cmn_view_processDataMgr.so`

Continúa [G27](g27-pp-auditoria-color-mode-y-plan.md). Causa raíz de «se elige y vuelve» (Silent On y todo Picture Profile) en los CFW 3.57–3.61.

## 1. Evidencia (cámara con el 3.61, 09-11-2026; telnet + `/proc/144/mem` + SWD)

| Hecho | Cómo se vio |
|---|---|
| `cmn_view_processDataMgr.so` no está mapada en ningún proceso, ni durante el uso del menú | `grep` de todos los `/proc/*/maps`; vigilancia de `/proc/144/maps` cada 0,3 s mientras se probaba Silent y PP |
| La UI es `im.elf` (pid 144) y carga solo `viewUnified2/6/8` | `/proc/144/maps` |
| Ningún fichero de `/usr` referencia `cmn_view_processDataMgr` (ni `NEEDED` ni por nombre) | `readelf -d` + búsqueda de bytes en todo `/usr` |
| `viewUnified2.so` lleva una copia estática del gestor (bytes idénticos de `getElement`, `setProcessId`, `setValueToModel`, `setValueToBackup`, `Normal::getValue`) | búsqueda de prefijos de 16 B de cada función en `viewUnified2` (`0x1b4568`, `0x25d914`, `0x25e5e0`…) |
| Su `D[pid]` está en VA `0x4457d4`; en memoria `D[0x12]` = descriptor ORIGINAL de AfTrackingSpeed (`desc[6]` = 0, sin modelo) y `D[0x46]` = EFCS | lectura de `/proc/144/mem` (`base 0x16600000`) |
| Los md5 de los cuatro `.so` instalados coinciden con el 3.61 | `md5sum` en la cámara |
| `+0x210/+0x238/+0x138/+0x153` de `av-cam` no cambian al intentarlo | SWD (`rd4.log`) |

Consecuencia: con un descriptor sin modelo, `Normal::setValue` no envía nada y `getValue` falla (Off al arrancar); la UI vuelve a mostrar el valor anterior. EFCS funcionaba en los CFW 3.54–3.56 porque usaba su descriptor nativo.

## 2. Segundo defecto (mismo origen)

La clase del elemento sale de la tabla `pid → caso de factoría` (`viewUnified2` VA `0x3a5e1c`, idéntica a la de la `.so`). 16 de los 33 `PIDS` de PP eran `Custom*Button` (`0xC4–0xC8`, `0xDD–0xDF`, `0x52–0x54`, `0x62–0x66`), cuyo `setValue`/`getValue` ignoran el descriptor. El simulador G22 llamaba siempre a `Normal` y no lo vio.

## 3. Corrección (CFW 3.62)

- `pp_descriptors.patch(..., tabla_d=TABLA_D_VU2)` y `silent_descriptor.patch(..., TABLA_D_VU2, DESC_EFCS_VU2)` actúan sobre `viewUnified2.so` (tras `add_menu_entry`).
- `pp_descriptors.clase_normal` fuerza la clase `Normal` en `elem[pid]` para Silent y todos los `PIDS` (el segmento de código se edita en el fichero).
- `cmn_view_processDataMgr.so` deja de enviarse.
- Pruebas: `tests/test_g28_vu2_descriptores.py` (la cadena modelo/eventos/claves/valores de cada pid es idéntica a la ya validada en la `.so`; relocaciones `R_ARM_RELATIVE` presentes; clases).

## 4. Límites

NO probado en cámara. Se asume que la copia de `viewUnified2` ejecuta el mismo código que la `.so` (bytes idénticos de las funciones comprobadas). Los pids reasignados a `Normal` perdían su función `Custom*` (teclas personalizables): se asumió, como en G23, que ningún menú visible los usa. Aparte: por SWD la cueva `0x83fb7400` leía ceros con los ganchos presentes (posible caché de `/dev/mem`), sin resolver.

## 5. Auditoría tras la prueba del 3.62 (10-11-2026): por qué entrar a Picture Profile ahora bloquea la cámara

Qué cambió entre 3.61 (entraba, nada cambiaba) y 3.62 (bloquea): solo `viewUnified2.so`, 55 palabras en la parte original: 35 punteros de `D[pid]`, 16 casos de la tabla pid→clase, `e_phoff/e_phnum` y `DT_REL/DT_RELSZ` (más 2 segmentos nuevos). Con el 3.61 la UI usaba los descriptores originales de los pids prestados; con el 3.62 usa los míos, y al pintar cada fila llama a `getValue` → modelo → respaldo.

**Defecto A (causa probable del bloqueo).** `pp_descriptors.patch` copiaba cada descriptor con relocación solo en las palabras 1 y 6. El descriptor original de un pid prestado tiene más punteros (respaldo NVRAM `w8`, vista de destino `w10`, cola `w13–18`); sin relocación apuntan a la dirección de enlace (p. ej. `0x4b9ee4`), no a la de carga. `Normal::getValue` = `getDisableValue` → `getValueFromModel` → `getValueFromBackup` (verificado en el desensamblado): cuando el valor leído del núcleo no coincide con ninguna opción, o la clave no existe (p. ej. `sel`, `0x276`), cae al respaldo y desreferencia ese puntero → SEGV. `silent_descriptor.py` ya copiaba relocaciones de forma genérica (por eso Silent sí funciona). **Corregido** en `pp_descriptors.patch`: relocaciones genéricas y `w8/w9/w10 = 0` (ver B); test `test_descriptores_conservan_relocaciones_y_sin_respaldo_ajeno`.

**Defecto B (de diseño, G23).** Los pids «inertes» NO lo son. De los 233 pids, 230 los referencia algún nodo raíz de `CautionConfig`; solo 3 no (`0xf` con modelo `@M00B`, `0x9d` con respaldo `0x1070b5d`, `0xb3`). `viewUnified2` importa `cmnViewSettingNodeRootCustomFunction` (Custom Key) y `…FnFunction` (Function Menu Set.), cuyos hijos son `CustomFunctionCbutton/AEL/AF-MF/…` (`0xC4–0xC8`, `0x52–0x54`, `0x62–0x68`, `0xDC–0xDF`) y `FnFunctionCustomFunction1–12` (`0x55–0x60`), con sus respaldos NVRAM de asignación de teclas. El 3.62 les cambió descriptor y clase: **los menús Custom Key y Function Menu Set. quedan rotos** y escribir en ellos manda órdenes de PP. (El 3.61 y anteriores no, porque la UI no usaba los descriptores nuevos.)

**Consecuencia.** El 3.62 no es instalable como versión de uso. Para PP hacen falta 34 ProcessIds que de verdad no se usen: o se amplía el espacio de pids (`getElement`/`setProcessId` comparan con `0xe8`; tablas `elem` y `D` a una copia mayor en un segmento nuevo, con `cmp` ampliados y literales reapuntados, y comprobar que nada más indexa por pid), o se prestan pids de funciones ausentes en la A6000 (hay que decidir cuáles con el árbol real de nodos, que se construye en el código de arranque de `CautionConfig`, no en datos).

## 6. CFW 3.63: espacio de pids ampliado (10-11-2026)

Corrige §5: los ajustes de Picture Profile ya no usan pids prestados.
- `scripts/gui/pid_space.py`: las tres comprobaciones `pid ≤ 0xE8` de la copia del gestor (`getElement` `0x1b4568`, `initProcessDataElement` `0x25d8f2`, `setProcessId` `0x25d91c`) pasan por tramos nuevos que comparan con `PID_MAX = 0x110` (`cmp.w`, porque el `cmp` de 2 B no pasa de 255; condicional con `bls` corto + `b.w` por la distancia al segmento nuevo); las tablas `ELEM` (VA `0x3a5e1c`) y `D` (VA `0x4457d4`) se copian a un segmento nuevo RWX con 273 entradas y sus tres literales PC-relativos se reapuntan. Los pids `0xE9…0x10A` (34) llevan un descriptor `Normal` propio (modelo `@M00B`, escritura `0x40`, lectura `0x49`, sin respaldo/vista/inhibiciones) y clase `Normal`. Ningún pid original cambia salvo el `0x12` de Silent (descriptor propio, como en el 3.59).
- `pp_descriptors.patch` (usado antes) copia ahora las relocaciones de todos los punteros y pone a 0 respaldo y vista de destino (defecto A de §5); queda solo para las pruebas.
- Pruebas: `tests/test_g28_pid_space.py` ejecuta con unicorn el código real de los tres sitios sobre la imagen parcheada (pids antiguos intactos, nuevos resueltos con puntero al modelo reubicado, `PID_MAX+1` rechazado, caso de factoría de `Normal` para los nuevos) y comprueba que ningún pid de PP lo usa un nodo original. Sobre el `viewUnified2.so` final del CFW se emularon además los 34 descriptores (nombre `@M00B`, evento, claves, opciones y valores) y el de Silent: todos correctos.
- Construcción: `build_cfw_completo.py` 3:33 min (antes 26 min): `tpzl.rebuild` comprime página a página en todos los núcleos, `tpzl.decompressed/_apply` descomprimen en paralelo y `encode_lz` calcula el prefijo común con XOR de enteros (misma salida, 5× más rápido). Auditoría [`audit-3.63.json`](../../analysis/gui/audit-3.63.json) 29/29; `.dat` sha256 `bbc48325b0ade7b9c38ff897113bb6c34fcb7e2f6c76081f42d7d48b300c976e`.
- Límites: NO instalado ni probado en cámara. Sin comprobar que nada más en la UI indexe por pid con tablas de 233 entradas (el barrido de comparaciones `#0xe8` solo halló los tres sitios); sin resolver el borrado de la cueva `0x43FB7400`, la prioridad Silent > EFCS ni el gris de EFCS con Silent On.

## 7. La cueva `0x43FB7400` se pone a cero (10-11-2026): causa probable del bloqueo al abrir Picture Profile

Evidencia (SWD `analysis/camera-dumps/20261109-swd-360/` + `uptime` de la transcripción; todo con `pp_ram.log` = «OK»):

| Hora local | Firmware · uptime | Cueva `0x83fb7400` | Ganchos `0x837a4db2/4b62/44fa`, `cmp #10` |
|---|---|---|---|
| 22:34 | 3.61 · ~100–137 s | `0f 10 11 12 …` (escrita) | presentes |
| 22:55 | 3.61 · ~1100 s | ceros | presentes |
| 23:51 | 3.62 · 197 s | ceros | presentes |
| 00:01 | 3.62 · arranque reciente | escrita | presentes |

El hueco se escribe bien al arrancar y se borra después (entre ~140 s y 197 s en las dos pruebas con ceros), pero los ganchos de código siguen apuntando a ella. Una cueva a cero ejecuta `movs r0,r0` en deslizamiento hasta el primer dato no nulo (`0x43FB8EE0`) y el gancho del `switch` de ids (`0x437a4db2`, antes un `bhi.w`) salta a ella en cada evaluación del tipo de Color Mode. Las tres caídas observadas al abrir Picture Profile en el 3.62 (reinicio, reinicio, apagado con LED) son compatibles con eso: las dos primeras con uptime > 150 s, la tercera con el borrado a mitad de la vigilancia (`mon.log`: últimas lecturas con la cueva escrita, luego error de lectura SWD). **No demostrado**: falta ver el borrado en vivo y quién lo hace (los datos del 3.56–3.58 mostraron las 8 curvas intactas a 60/600/3600 s, así que el hueco no se borra entero; el comprobador antiguo solo miraba curvas, nunca la cueva).

Por qué quedó sin verse: `pp_ram.sh` (a) solo repetía el control de las curvas y (b) si se relanza con los ganchos ya escritos se negaba a escribir («no es el original»), de modo que una cueva a cero no se reparaba nunca.

Corrección (CFW 3.64, `pp_curves_patch.camera_files`): cada sitio puede estar original (se escribe), ya parcheado (se omite) u otro (se aborta); la tarea en segundo plano lee el hueco completo (curvas + cueva) **cada segundo**, y si su md5 cambia registra el uptime y los ganchos alterados, vuelca el hueco ya alterado a `/android/data/pp_hueco_N.bin` (3 como máximo) y reescribe curvas y cueva. CFW 3.64 construido en 3:51 min, `.dat` sha256 `a671db1c3f31c32c1a258df2154c55d049f9184ff803e24af396e9eb700fe03d`, auditoría [`audit-3.64.json`](../../analysis/gui/audit-3.64.json) 29/29 `todo_ok`. Pruebas: `tests/test_g29_pp_ram_vigilancia.py` (memoria falsa en fichero: idempotencia, cueva a cero con ganchos presentes, vigilancia que detecta+repara+vuelca, núcleo distinto no escribe).

Límites: la ventana entre el borrado y la reparación (≤ 1 s) sigue expuesta; el comportamiento real del borrado (cuándo, qué tamaño, quién) solo se sabrá con `pp_ram.log` y `pp_hueco_N.bin` de una cámara con el 3.64; no probado en cámara; sin sonda SWD ni Wi-Fi conectados en esta sesión.

