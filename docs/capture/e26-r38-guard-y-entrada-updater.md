# E26-R38 — Guard de versión del actualizador, escritura de `dat4`/`comp` y entrada mínima `\updater\mode`

Fecha: 31-10-2026. Continúa [R37](e26-r37-cierre-estatico-recuperacion.md). **Solo análisis offline** del volcado de NAND del 20-10 (`dev_nflasha1.bin` → `initrd.img` cramfs → `sauu`, scripts; `dev_nflasha2.bin`), del cuerpo del actualizador del paquete 3.21 (`updater.img_unpacked`: `libupdaterbody.so`, `config.xml`) y de Loader3. Sin cámara ni USB. Pedido del usuario: «investiga más a fondo». Objetivo: cerrar la suposición que R37 dejó abierta (cómo compara el actualizador la versión instalada) y bajar la escritura física mínima al byte.

Etiquetas: **BINARIO** (llvm-objdump/Capstone, bytes releídos) · **DATOS** · **SCRIPT** · **INFERENCIA**. Pruebas: [`tests/test_e26_r38_guard_updater.py`](../../tests/test_e26_r38_guard_updater.py) (5). Herramienta: [`scripts/e26_recovery/updater_mode_entry.py`](../../scripts/e26_recovery/updater_mode_entry.py).

## 1. Resumen

| Tema | Resultado |
|---|---|
| Guard en modo actualizador | Lo aplica `sauu` (`nflasha1`) en `UpdaterHandler::isVersionOK`, comparando contra `<nflasha2>\updater\dat4`. Con solo `mode` (USER): exige versión **mayor**, o igual si falta `comp`. `-m` (MINOR, `mode3`) acepta igual; `-s` (VERSKIP, `mode6`) acepta **cualquiera** |
| Quién escribe `dat4`/`comp` | El cuerpo del paquete: `StartUpdate` borra `comp`; `CompleteUpdate` escribe `dat4 = versión del FDAT`, borra `mode1…6`, crea `comp` y borra `mode`. Ningún paquete 3.2x trae `updater_sum`/`loader_sum`: nunca reescriben `nflasha1` ni crean `uincomp` |
| Estado tras el 3.25 | `dat4 = 25 03` y `comp` presente (INFERENCIA: la instalación terminó, como informó el usuario) → hace falta **≥ 3.26** en modo USER. Confirma la suposición de R37 |
| Lectura de `\updater\mode` por Loader3 | Solo la entrada corta `MODE       ` en el primer clúster de `\updater`, con `attr & 0x18 == 0`. No lee datos: vale un archivo de 0 B |
| Escritura mínima | En el volcado del 20-10, `\updater` conserva una entrada `mode` **borrada** (0xE5, 0 B). Recuperarla = **1 byte** (`0xE5 → 0x4D` en el desplazamiento `0x108A0`, sector 132 de `nflasha2`). `fsck.vfat -n` limpio |
| Persistencia | Sin LFN, el nombre queda `MODE` y el `rm -rf /setting/updater/mode*` de `execute_ufp.sh` no lo borra: se puede reintentar sin volver a escribir la NAND. `CompleteUpdate` lo borra al acabar bien. Corrige R37 §2 («en esa misma sesión») |
| Datos prácticos | El actualizador se apaga a los **30 min** (`ud_timeout_poweroff.elf`: `sleep(1800)`). `pmca firmware -f` funciona con la cámara ya en actualizador (sin `switchMode`) |

## 2. Guard de versión en `sauu` (BINARIO)

`sauu` (`nflasha1`, sha256 `799a94d6…`, no stripped). `UpdaterHandler::UpdaterHandler(arg)` (`0xd180`): `"-m"` → `[this+0x14] = 1`; `"-s"` → `[this+0x15] = 1`. `execute_ufp.sh` pasa `-m` en MINOR (`mode3`), `-s` en VERSKIP (`mode6`) y nada en USER (solo `mode`).

`UpdaterHandler::isVersionOK` (`0xd3d0`), con `actual` = (`[+4]`,`[+8]`) y `nueva` = (`[+0x18]`,`[+0x1c]`):

1. Modo accesorio → acepta. `[this+0x15]` (VERSKIP) → acepta.
2. `nueva.mayor < actual.mayor` → rechaza; `>` → acepta. Igual con el menor.
3. Versiones iguales: `[this+0x14]` (MINOR) → acepta; si no, acepta solo si `IsCurrentFirmwareValid` da falso.

`CurrentFirmware::getVersion` (`0xf6e4`) lee `VersionFile` (`updater/dat4` en `libupdatercommon.so`, montado sobre `nflasha2`): `mayor = v >> 8`, `menor = v & 0xff`. `CurrentFirmware::IsValid` (`0xf0b8`) es la existencia de `CompleteFlagFile` = `updater/comp`.

**DATOS:** en `dev_nflasha2.bin` (20-10, fw 3.21) `\updater\dat4` = `21 03` (u16 LE `0x0321`) y `\updater\comp` existe (0 B, oculto). Así se explica que la medición de [custom-fw-recovery](custom-fw-recovery-and-install.md) rechazara 3.21 sobre 3.21.

## 3. Quién escribe `dat4` y `comp` (BINARIO)

`sauu` nunca llama a `WriteValue`: no escribe la versión. La escribe el cuerpo que trae el paquete (`libupdaterbody.so`, `FlagFirmwareInformationHandler`):

- `StartUpdate` (`0x14e88`): crea `mode` + `modeN` según la acción; si existe `comp`, lo **borra**.
- `CompleteUpdate` (`0x1516c`): si no es accesorio, `setVersion(info.mayor << 8 | info.menor)` (`0x152a8`, vtable `+0x1c`); después borra `mode1/2/3/5/6`, **crea `comp`** y **borra `mode`** (`0x1551c`–`0x155ce`).
- `uincomp` solo lo crean `UpdaterKeyTag::PreExecute` / `UpdaterChksumKeyTag::PostExecute`, es decir, un paquete con imagen de actualizador. `config.xml` prevé `updater_sum` y `loader_sum`, pero el `firmware.tar` 3.21 (y por tanto el 3.23/3.25, que solo difieren en Darwin, `nflasha3` y `part_image.sum`, R36) no los incluye. `nflasha1` y los loaders nunca se reescribieron, y `uincomp` no existe.

**Consecuencia:** con el 3.25 instalado hasta el final, `dat4 = 25 03` y `comp` existe. En modo USER, `sauu` rechaza 3.25 e inferiores y acepta el **3.26** de R37. Si la instalación se hubiera cortado antes de `CompleteUpdate`, `comp` faltaría y `dat4` seguiría en 3.23: el 3.26 también pasaría. **El 3.26 sirve en los dos casos.**

## 4. Cómo busca Loader3 `\updater\mode` (BINARIO)

`c01f159a` («`BOM:chk updater`»): `fat_mount(2)` y `c01f44c6("\updater\mode")`; si el resultado es `>= 0`, modo 3.

- `c01f4434` separa la ruta (un solo nivel de directorio).
- La raíz se recorre entera comparando 11 bytes. `UPDATER` debe tener `attr & 0x18` (directorio).
- `c01f407e` lee **solo el primer clúster** del subdirectorio.
- `c01f3f34` recorre las entradas **hasta la primera con nombre[0] = 0**, compara `MODE       ` y exige `attr & 0x18 == 0`.
- Guarda el clúster y el tamaño, pero **no lee datos**.
- Si no lo encuentra, devuelve −302 (`0xfffffece + 4`), que `chk updater` trata como «no existe».

Requisitos de la entrada: nombre corto `MODE` en el primer clúster de `\updater`, antes de la marca de fin, sin bits de directorio ni de volumen. El tamaño y el clúster pueden ser 0. El LFN es irrelevante.

## 5. Escritura mínima (DATOS + SCRIPT)

`\updater` del volcado del 20-10 (clúster 5, desplazamiento `0x10800`, FAT12, 32 sectores/clúster):

| Entrada | Contenido |
|---|---|
| 0–1 | `.` `..` |
| 2–3 | LFN `comp` + `COMP` (attr `0x02`, 0 B) |
| 4–5 | LFN `mode` **borrado** + `\xE5ODE` **borrado** (attr `0x20`, clúster 0, 0 B): rastro de una sesión de actualizador anterior |
| 6–7 | LFN `dat4` + `DAT4` (clúster 466, 2 B) |
| 8 | fin |

`updater_mode_entry.py` replica la búsqueda de Loader3 y aplica el menor cambio posible: recupera la entrada `MODE` borrada si existe (**1 byte**), o escribe una nueva de 32 B en el primer hueco. Sobre el volcado:

- **Cambio:** un byte en `0x108A0` (sector 132 de `nflasha2`), `0xE5 → 0x4D`.
- **Comprobaciones:** `fsck.vfat -n` sin errores (24 → 25 archivos, mismos clústeres); `mdir` lista `MODE`; la réplica de Loader3 pasa de «no existe» a «existe».

**Por qué sin LFN (INFERENCIA, semántica de Linux `vfat` con `shortname=mixed` y del glob de busybox):**
- Una entrada corta en mayúsculas sin LFN aparece como `MODE`.
- `test -f /setting/updater/mode` la encuentra, porque `vfat` compara sin distinguir mayúsculas.
- El glob `mode*` de `execute_ufp.sh` distingue mayúsculas y no la borra. Si la sesión USB falla o se agota la batería, el siguiente encendido vuelve al actualizador sin volver a escribir la NAND.
- `CompleteUpdate` la borra por API, sin distinguir mayúsculas, al terminar bien.
- Si la inferencia fallara, el resultado sería el de R37 (un solo intento), no algo peor.

**Límite:** el volcado es anterior a las sesiones 3.22/3.23/3.25. Cada una creó y borró `mode`, y `vfat` reutiliza los huecos borrados, así que lo esperable es el mismo par 4–5. Aun así, **hay que ejecutar la herramienta sobre una lectura actual de `nflasha2`** antes de escribir nada. La traducción del sector lógico 132 de `nflasha2` a página física de NAND pertenece a `E26-FISICO-BOOT`.

## 6. Procedimiento resultante (no autorizado ni probado)

1. Leer `nflasha2` actual y conservar una copia.
2. Ejecutar `updater_mode_entry.py actual.bin parcheado.bin` y escribir **solo** los bytes que indique (esperado: 1 byte en el sector 132).
3. Encender: Loader3 elige el modo 3 y arranca el actualizador de `nflasha1`.
4. Antes de 30 min, `pmca-console firmware -f recuperacion-326/firmware_packed.dat`. Con la cámara ya en actualizador, `firmwareUpdateCommandInternal` hace `checkGuard` y `writeFirmware` sin `switchMode` (`references/pmca/pmca/commands/usb.py:380-423`).
5. `CompleteUpdate` escribe `dat4 = 26 03`, crea `comp` y borra `MODE`, y el siguiente arranque es normal.

**Alternativas descartadas:**
- **VERSKIP** (`mode` + `mode6`) aceptaría cualquier versión, incluido el `.dat` oficial 3.21 sin tocar. Pero:
  - `endupdate.sh` formatea `/dev/nflasha24`, que en `partinf.conf` mide 0 B (resultado desconocido; INFERENCIA: error 48);
  - `us_crc32sum_appli.sh` restaura `dat2/3/4` y vuelve a crear `mode` + `mode6`.
  - Más efectos y más bytes que USER + 3.26.
- **MINOR** (`mode3`) solo añade aceptar la misma versión; no hace falta.

## 7. Límites

- Nada se ha probado en la cámara. El estado actual de `nflasha2` (`dat4`, huecos de `\updater`) se infiere del volcado del 20-10 y del código, no se ha leído.
- La persistencia de `MODE` depende de la semántica de `vfat`/busybox en el kernel del actualizador (§5). No se ha comprobado en ejecución.
- Escribir el sector exige la vía física de E26 (lector externo o BootROM serie con la clave de `nflasha0`, [R33](e26-r33-veracidad-clave-nflasha0.md)), que no está autorizada.
