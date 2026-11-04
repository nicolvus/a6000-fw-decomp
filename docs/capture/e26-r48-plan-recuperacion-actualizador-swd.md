# E26-R48 — Plan de recuperación: arrancar el actualizador de fábrica por SWD sin escribir en la NAND

Fecha: 03-11-2026. **Plan sin ejecutar.** No se ha escrito nada en la cámara. Cada fase física requiere autorización expresa del usuario.

Base:
- [R47](e26-r47-primer-contacto-swd-lectura-ram.md) §15: el −302 lo produce P2 al cargar `\sabin\idt_cam.bin` de `nflasha3` en el segundo arranque.
- [R37](e26-r37-cierre-estatico-recuperacion.md), [R38](e26-r38-guard-y-entrada-updater.md), [R39](e26-r39-estatico-profundo.md): BootMode 3, guard del actualizador y MuMin.
- [R46](e26-r46-procedimiento-fisico-swd.md) F8: opciones de escritura.

Etiquetas: **LEÍDO** (código en RAM volcado o binario), **VERIFICADO** (hash o comprobación hecha hoy), **INFERENCIA**, **NO PROBADO**.

## 1. Decisión propuesta

| Opción | Qué escribe el operador | Valoración |
|---|---|---|
| A (R46 F8). Crear `\updater\mode` en `nflasha2` | 1 sector por MuMin desde el BIONZ | **Inviable con Loader3.** Su capa de bloques ignora las escrituras (§2.1). Usar las funciones internas de MuMin sin el contexto del controlador puede dañar las tablas de toda la NAND |
| B (R46 F8). Reescribir `nflasha3` por SWD | ~11 MB por MuMin | Misma objeción que A, y además a unos 11 KB/s por SWD |
| **C (nueva). Forzar en el arranque 2 que `chk updater` vea `\updater\mode`** | **Nada en la NAND.** Solo el registro `r0` de la CPU en una parada | Loader3 elige BootMode 3 y carga el actualizador de fábrica de `nflasha1` (intacto). La escritura la hace el actualizador oficial de Sony con el paquete 3.26 (`nflasha3` y Darwin oficiales) |

Se propone **C**. A y B quedan descartadas mientras no haya un camino de escritura que no dependa de llamar a MuMin a mano.

## 2. Evidencia

### 2.1 Loader3 no escribe en bloques (LEÍDO)

`muminblk_request` (`c01fd5a4`) lee la dirección de la petición en `[r8]` (`c01fd620`).
- **Lectura** (`[r8] = 0`): llama a `muminblk_transfer` (`c01fe958`).
- **Escritura** (`[r8] ≠ 0`): salta a `c01fd66a` con `r6 = 0` y devuelve éxito **sin transferir nada**. La cadena del registro es `"write"` (`c01fd874`) en lugar de `"read"` (`c01fd87c`).

En RAM hay funciones de escritura del núcleo MuMin (`mumin_ext_write_scts`, `__mumin_write_ltus`, `mumin_pbm_s_write_pages_in_pblk`…), pero Loader3 no las usa para escribir bloques.

### 2.2 Cómo se elige el actualizador (LEÍDO)

| Dirección | Qué hace |
|---|---|
| `c01f159a` | `chk updater`: monta la partición 2 y llama a `c01f44c6("\updater\mode")` |
| `c01f15c0` | `cmp r0, #0` / `bge`: si `r0 ≥ 0` (el fichero existe), devuelve 1 |
| `c01f1e10`–`c01f1e18` | Selección de modo: si `chk updater` devuelve 1, `movs r0, #3` en `c01f1e16` |
| `c01f1312` → `c01f1378` | Despacho del modo 3 a la carga del actualizador (`c01f068a`, dispositivo 1: `\boot\vmlinux.bin` e `initrd.img`). No lee `nflasha3` (R37 §2) |

`chk updater` se llama desde 8 sitios (`c01f11a8`, `c01f1df8`, `c01f1e10`, `c01f2122`, `c01f75cc`, `c01f7748`, `c01f8e24`, `c01f8e76`). Poner `r0 = 0` en `c01f15c0` en cada llamada equivale a que el fichero exista, que es el escenario estudiado en R37 y R38.

### 2.3 El actualizador no necesita el fichero (VERIFICADO)

Se extrajo `UdtrMain.sh` del `initrd.img` de `nflasha1` del volcado del 20-10:
- `dev_nflasha1.bin`: SHA-256 `ea74eb04…`.
- `UdtrMain.sh`: SHA-256 `b90a7c2d…`.

`getCurrentMode` revisa `mode3`, `mode2`, `mode6` y `mode1`. Si no hay ninguno, devuelve **`MODE_USER` por defecto**, sin exigir `mode`. Por tanto basta con que Loader3 elija el modo 3.

### 2.4 Persistencia y reintento (LEÍDO en R5 §3, sin verificar hoy)

- `StartUpdate` del cuerpo del paquete crea `updater/mode` en el modo USER y borra `comp`.
- Si la sesión USB se corta después, el siguiente arranque vuelve solo al actualizador.
- `CompleteUpdate` borra `mode` (`unlink`, que lanza una excepción si falla). Como `StartUpdate` lo creó, existe.

### 2.5 Paquete y guard (VERIFICADO hoy)

| Elemento | Valor |
|---|---|
| `.dat` | `analysis/darwin-patch/fdat/recuperacion-326/firmware_packed.dat`, SHA-256 `c730f8e2…` = `manifest-recuperacion-326.json` |
| `.fdat` | `e652ddb5…` = manifiesto |
| Contenido | 3.24 oficial con la versión cambiada a 3.26 (R37 §3); `firmware.tar` y `updater.img` oficiales, sin recomprimir `nflasha3` |
| Guard | `dat4 = 25 03` exige versión mayor que 3.25 en modo USER (R38). El 3.26 cumple modelo, región y versión |

## 3. Procedimiento

### P0. Preparación (sin cámara)

1. Instalar `pyusb` y comprobar `references/pmca/pmca-console.py` en el PC. Es la herramienta que usó T024 (`firmware -f`).
2. Confirmar que se puede conectar el USB de la cámara con la placa abierta y la sonda SWD puesta.
3. Batería **cargada del todo**. `sauu` no comprueba la batería (R39 §6).
4. Revisar el script [`r48_updater_swd.cfg`](../../analysis/e26-recovery/r48_updater_swd.cfg) (OpenOCD; se lanza con `LOGF=<registro> openocd -f …`). Hace lo siguiente:
   1. espera el corte del arranque 1;
   2. para la CPU al inicio del arranque 2 (método ya usado en R47 §15);
   3. pone un punto de parada en la entrada de Loader3 y luego `{c01f15c0, c01f1e16, c01f1378}`;
   4. en cada parada en `c01f15c0`, pone `r0 = 0` con `set_reg` y comprueba el valor leyéndolo de nuevo;
   5. al llegar a `c01f1378`, quita los puntos de parada, reanuda y termina sin cortar ninguna transacción.

   **Paradas del script:** no hay corte en 5 s, más de 8 comprobaciones, `r0` no cambia, falla `step`, o no llega a `c01f1378` en 10 s.

### P1. Arrancar el actualizador (requiere autorización: modificar `r0` en ejecución)

1. Lanzar el script con la cámara apagada.
2. Encender la cámara.
3. **Criterio:** el registro muestra «BootMode 3 elegido» y la entrada a `c01f1378`.
4. Si se para antes: apagar y no repetir sin revisar el registro.

### P2. Comprobar el actualizador (solo lectura)

1. Conectar el USB.
2. `lsusb` debe mostrar el dispositivo Sony en modo actualizador.
3. `pmca-console info`: versión 3.25, modelo `0x41030035`.
4. **Paradas:** no aparece el dispositivo en 2 min, o el modelo no coincide.

### P3. Instalar el 3.26 (requiere autorización: instalación de firmware)

1. `pmca-console firmware -f analysis/darwin-patch/fdat/recuperacion-326/firmware_packed.dat`, antes de los 30 min del apagado automático (`ud_timeout_poweroff`).
2. No tocar la cámara ni la sonda hasta que termine.
3. **Criterio:** `pmca` termina sin error (`CMD_COMPLETE`).

### P4. Verificación y cierre

1. Apagar, retirar la batería 10 s y encender sin OpenOCD.
2. **Criterio:** no hay patrón de LED de error y la cámara arranca. `pmca-console info` = 3.26.
3. Opcional, solo lectura: repetir el muestreo de PC de R47 §15 para confirmar que el arranque 2 pasa de `CFG`.
4. Retirar la sonda (R46 F9), documentar el resultado y actualizar PENDIENTES y la página 14 del wiki.

## 4. Riesgos

| Riesgo | Mitigación |
|---|---|
| El forzado deja a Loader3 en un estado no previsto (por ejemplo, la llamada en una ruta de energía) | Equivale a que el fichero exista (R37/R38). El script se para ante cualquier anomalía. No escribe en la NAND: si falla, la cámara vuelve al estado actual |
| El actualizador escribe en la NAND y se corta la alimentación | Batería llena. No mover la placa. Si se corta tras `StartUpdate`, el siguiente arranque vuelve al actualizador (§2.4) |
| El paquete 3.26 es un empaquetado propio, aunque con contenido oficial | Verificado dos veces en R37 y con el hash de hoy. El fallo del 3.25 se debió a recomprimir `nflasha3`, y el 3.26 no lo hace. **NO PROBADO en la cámara** |
| Los puntos de parada o la sonda interfieren con Linux | El script los quita y deja la sonda en reposo antes de que arranque el núcleo |

## 5. No verificado

- Que el modo 3 arranque de verdad con este Loader3 y esta alimentación (nunca ejecutado).
- La enumeración USB con la placa abierta.
- `StartUpdate`/`CompleteUpdate` en la versión exacta del cuerpo del paquete 3.26. Se toman de R5, no revisados hoy.
- Que `set_reg` de OpenOCD 0.12 funcione con este núcleo.

## 6. Resultado de P0 (03-11-2026, sin cámara)

| Comprobación | Resultado |
|---|---|
| Entorno de `pmca` | `~/.local/share/pmca-venv`, el mismo de T024. Python 3.14.7, `pyusb` 1.3.1 y libusb1 ya instalados: **no hizo falta instalar nada** |
| Código de `pmca` | `~/.local/share/Sony-PMCA-RE`, commit `a82f5ba`, `pmca-console.py --help` y `firmware -h` funcionan. Solo se diferencia de `references/pmca` en el tiempo de espera del cambio de modo (60 frente a 10 vueltas), que no se usa con la cámara ya en actualizador |
| Ruta de instalación | `firmwareUpdateCommandInternal`: con un `SonyUpdaterDevice` hace `init`, `checkGuard`, `getFirmwareVersion`, `writeFirmware` y `complete`, sin `switchMode` (leído en el código instalado) |
| Paquete 3.26 | `firmware.readDat` de `pmca` lo lee (offset 140, carga útil 212 987 904 B). Los hashes coinciden con el manifiesto (§2.5) |
| Permisos USB | No hay regla udev para Sony (`054c`). P2 y P3 se ejecutarán con `sudo` y el Python del venv. No se ha cambiado la configuración del sistema |
| Parte física de P0 | **Confirmada por el usuario (03-11-2026):** el USB se puede conectar con la placa abierta y la sonda puesta, y la batería está cargada |

## 7. Primer intento de P1 y secuencia real de arranques (03-11-2026)

**P1 (autorizado por el usuario).** El script vio el primer arranque, pero no el corte en 5 s, y se detuvo con «sin corte en 5 s, no se toca nada». **No se modificó ningún registro.** Después, `DBGPCSR` sin parar la CPU dio `0xc01f4f9d`: el bucle de espera del LED de error, igual que antes.

**Muestreo pasivo con la batería cargada** (sin halt ni puntos de parada; la secuencia la hizo el usuario):

| Momento | Resultado (MEDIDO) |
|---|---|
| Meter la batería con el interruptor en OFF | Arranca Loader2 y luego Loader3. El enlace se corta a los 868 ms y no vuelve en 10 s: la cámara se queda apagada |
| Encender con el interruptor | Un solo arranque desde el BootROM (`0xffff1439`), Loader2 y Loader3, sin corte. Desde los 2,7 s está en `0xc01f4f9d` (bucle del LED) |

**Corrección de R47 §15 (INFERENCIA):** el «arranque 1 que acaba en `XPOWER_OFF`» parece ser el arranque que provoca meter la batería, no una fase de cada encendido. En los intentos 4 y 5 no se registró cuándo se metió la batería. El arranque que da el −302 es el del interruptor, y es uno solo. El script `r48_updater_swd.cfg` supone dos arranques seguidos y **no sirve tal cual**.

**Estado:** P1 queda sin ejecutar, y no se continúa en esta sesión. No se escribió nada en la cámara.

## 8. P2 y P3: actualizador alcanzado e instalación del 3.26 interrumpida al 45 % (03-11-2026)

**Entrada al actualizador.** La puso el usuario por su cuenta; el método no se registró en esta sesión y no es la vía C de §1. **P1 no llegó a ejecutarse** (§7).

**P2, verificación de solo lectura (MEDIDO).**

| Comprobación | Resultado |
|---|---|
| `lsusb` | `054c:03e2 Sony Corp.`, uno de los identificadores de actualizador que reconoce `pmca` (`SONY_ID_PRODUCT_UPDATER = [0x033a, 0x03e2]`) |
| `pmca` | «Sony DSC is a camera in updater mode» (`SonyMscUpdaterDevice`) |
| `init` y `checkGuard` del `.dat` 3.26 | Correctos: el guard acepta el paquete |
| `getFirmwareVersion` | Actual **3.25**, nueva **3.26** |
| Paquete | SHA-256 `c730f8e2…`, igual que el manifiesto |

**P3, instalación (autorizada por el usuario: «instálale la buena»).** Se ejecutó `pmca-console.py firmware -f …/recuperacion-326/firmware_packed.dat` desde el venv de §6. No hizo falta `sudo`: el nodo USB tenía permisos `rw` para todos.

| Fase | Resultado (MEDIDO) |
|---|---|
| `Initializing firmware update`, `Updating from version 3.25 to version 3.26` | Correctos |
| `Writing firmware` | El progreso llegó al **45 %**, unos 96 MB de 213 MB |
| Respuesta de la cámara | **`Response error: 0x1063`** a un `CMD_WRITE_FIRM` (`_sendWriteCommands`). `pmca` terminó con `EXIT=1` sin `CMD_COMPLETE` |
| Justo después | La cámara seguía en USB como `054c:03e2` (actualizador) |

**Código de error (LEÍDO en `sauu`, SHA-256 `799a94d6…`).** `ErrorConverter::Convert` (`0xe9b0`) devuelve el código de LED de `LEDErrorConverter::Convert` con `| 0x1000`. Por tanto `0x1063` corresponde al código de LED **`0x63`**. **No se ha determinado** qué fallo representa `0x63`.

**Estado de la cámara tras el fallo (sin verificar):**
- La escritura del cuerpo del paquete había empezado. **Es posible que alguna partición de destino haya quedado escrita a medias.** No se sabe cuáles se escribieron antes del corte.
- `nflasha1` (actualizador de fábrica) no está entre las imágenes del paquete (R38: ningún paquete 3.2x trae `updater_sum`/`loader_sum`). INFERENCIA: sigue intacta.
- Si `StartUpdate` llegó a crear `updater/mode` (R5 §3), el siguiente arranque debería volver al actualizador. No comprobado.
- No se volvió a medir el estado de la cámara después del fallo.

**Causa del fallo: desconocida.** Las hipótesis, todas sin probar, son un error al escribir en la NAND, un problema del paquete en esa zona o un fallo de la sesión USB.

**Decisión.** No se reintenta la instalación a ciegas. Recomendación: retirar la sonda y el USB con cuidado y llevar la cámara a un servicio técnico con este informe, R47 §15 y R36. El diagnóstico concreto es `nflasha3` dañada por el 3.25 y la instalación oficial interrumpida al 45 % con `0x1063`.

Registro de la instalación (fuera del repo): `p3.log`, que no contiene datos de la cámara.
