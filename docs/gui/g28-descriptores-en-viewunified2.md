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
