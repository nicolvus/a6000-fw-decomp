# S62 — PMCA: inyección de código, service shell y la propiedad `modelName` (ILCE-6001)

Fecha: 20-10-2026. Alcance: lectura estática de **Sony-PMCA-RE v0.17** (checkout en
`references/pmca/`) y verificación contra el firmware **ILCE-6000 3.21**
(`firmware.fdat`, SHA-256 `603b42ec9d2dd66b91e38c15a6a23e860fb8af46a072050903506672036f0f90`).
No se ejecutó firmware, no se usó cámara, no se flasheó ni se escribió NVRAM.
El procedimiento de cambio de modelo se documenta como **reportado por el usuario**;
su efecto («shell mode») queda **NO VERIFICADO**.

## 1. Dos canales distintos (no confundirlos)

| Canal | Qué hace | Dónde corre | Evidencia |
|---|---|---|---|
| `updatershell` | Inyecta un binario propio en un contenedor firmware y lo ejecuta el **updater** (partición secundaria) | RAM del updater; el firmware de la cámara no se toca | `references/pmca/updatershell/`, `pmca/usb/sony.py` |
| `serviceshell` | No inyecta binario: autentica por HASP y usa comandos de **adjust-control / terminal / ficheros / memoria** sobre el sistema en marcha | SO de la cámara (modo senser) | `pmca/platform/backend/senser.py`, `pmca/usb/sony.py` |
| `install` | Instala un APK (market server local) | Android de la cámara | `pmca/installer`, `pmca/marketserver` |

`bk` es un subcomando de la **platform shell** y funciona en los dos primeros canales porque
`CameraShell` se construye sobre el backend disponible
(`pmca/platform/__init__.py:38-48`).

## 2. `updatershell`: cómo se inyecta código

1. **Payload.** `updatershell/` compila `libupdaterbody_gen{1,2,3}.so` (gen3 = CXD90014) que
   exporta `GetBody`/`ReleaseBody`; `UpdaterBodyImpl::Execute()` monta `/dev/nflasha2` en
   `/setting` y llama `usbshell_loop()` (`references/pmca/updatershell/updaterbody.cpp:14-36`).
2. **Empaquetado.** `pack.py` crea un **cramfs** con `/bodylib/libupdaterbody.so` y lo envuelve
   con `fdat.writeFdat(model=<código>, region, version='9.99', fs=...)`; después cifra con la
   clave de la plataforma y separa un **header de 0x30 B por modelo** (`.hdr`) de un cuerpo
   común (`.dat`) (`references/pmca/updatershell/pack.py:24-94`).
3. **Por qué el split funciona.** En gen3 el cifrado es DoubleAES y los **primeros 512 B solo
   llevan la primera capa**; el header fdat (CRC en `+0x08`, modelo en `+0x24`, región en
   `+0x28`) cae en esa zona, así que cambiar de modelo solo requiere sustituir 0x30 B
   (`references/fwtool/fwtool/sony/fdat.py:157-188`, `updatershell/pack.py:79-94`).
4. **Entrega.** `SonyUpdaterCamera` habla el protocolo del updater por USB
   (`SONY_CMD_Updater = 0`): INIT `0x1`, CHK_GUARD `0x10`, QUERY_VERSION `0x20`,
   SWITCH_MODE `0x30`, WRITE_FIRM `0x40`, COMPLETE `0x100`, con buffers de 512 B
   (`pmca/usb/sony.py:417-582`). `switchMode()` reinicia la cámara en la partición de
   actualización; `writeFirmware()` envía el fdat completo (header + cuerpo).
5. **Ejecución.** El updater descifra, valida magic `UDTRFIRM`, CRC, modelo, región y versión,
   monta el cramfs y carga la librería. El **guard no es una firma**: es CRC + modelo + región
   + versión; por eso un fdat propio pasa si el modelo coincide.
6. **Capacidades.** Shell USB por *feature* `0x23`: `TEST`, `SHEL` (`sh -i`), `PULL`/`PUSH`
   (ficheros), `RMEM` (memoria), `BLDR`, `BKRD`/`BKWR`/`BKSY`/`BKST`/`BKDA`/`BKDW`/`BKPR`
   (backup), `AMNT`/`AUMT` (datos Android), `EXIT`
   (`references/pmca/updatershell/usbshell.cpp`).

**Compatibilidad.** CXD90045 y CXD90057 **no** son compatibles: su firmware está firmado
(`references/pmca/README.md:45-49`). CXD90014 (A6000/A6300) solo está cifrado, así que el
payload propio se acepta. El A6000 está en la lista: `updatershell/fdat/CXD90014/ILCE-6000.hdr`
y `references/fwtool/devices.yml:400-403` (`arch: CXD90014`, `model: 0x41030035`, `apps: 2.4`).

**Verificación en el fdat 3.21 real** (`firmware/extracted/fw321/firmware.fdat`, 212 155 392 B):
magic `UDTRFIRM`, `model = 0x41030035`, versión `3.21`, `firmwareOffset = 0x23200`,
`firmwareSize = 212 011 520`, 2 file systems. El cuerpo es un `firmware.tar` con las
particiones (`0110_backup/...`, `nflasha3`, `nflasha5`, `nflasha15`, `nflasha16`).

## 3. `serviceshell` (senser): segundo canal, sin binario inyectado

- **Entrada**: peticiones *vendor* `StartSenser (1, 0x37ff, 0xd7aa)` y `StopSenser
  (1, 0xc800, 0x2855)`; autenticación HASP con `ReadHASP (0, 0x1f)` y listas de claves
  SHA-1/SHA-256 (`pmca/usb/sony.py:890-936`, `pmca/usb/crypto.py`).
- **Comandos**: `ProductInfo 0x10`, `AdjustControl 0x40`, `FileControl 0xff01`,
  `MemoryDump 0xff03` (`pmca/usb/sony.py:939-1011`).
- **Backup**: `0x603/1` leer, `0x603/2` escribir, `0x603/3` guardar, `0x603/4-6` datos
  preset, `0x603/15` id1 (protección) (`pmca/usb/sony.py:964-1057`).
- **Terminal**: `0x601/0x1f` con modo 2 y `ProductInfo (0, 0xf1)`; `setTerminalEnable`
  conmuta la consola serie (`pmca/usb/sony.py:1031-1036`; `platform/backend/senser.py`).
- **Ficheros/memoria**: `readFile`/`writeFile`/`deleteFile` y `readMemory`/`writeMemory`
  (dump con base + tamaño).
- **Diferencia clave**: aquí se ejecuta código con la terminal (`shell`) del sistema en
  marcha; el backup se escribe por adjust-control, no por la API de backup del updater.

## 4. `bk w 0x003e0005`: qué es y dónde escribe

- `bk` agrupa `r`, `w`, `patch`, `s`, `lock`, `unlock`; solo se registra si el backend
  implementa `BackupPlatformBackend` (`pmca/platform/__init__.py:38-48`).
- `w` parsea `ID` y bytes hex y llama `writeBackup(id, data)`; según backend:
  - **updater**: `BKWR` con `{id, size, data[0xfff4]}` → en cámara
    `BaseBackupProperty(id).write(data)` (`pmca/platform/backend/usb/__init__.py:101-104`,
    `updatershell/usbshell.cpp:155-167`);
  - **senser**: `AdjustControl (0x603, 2)` con `id` + datos (`pmca/usb/sony.py:1041-1042`).
- **El ID no es una dirección**: BK4 lo descompone como `subsystem << 16 | index`
  (`pmca/backup/__init__.py:109-114`). `0x003e0005` = subsistema `0x3e` (62), índice `5`.
- Esa propiedad es **`modelName`, 16 B** (`pmca/platform/backup.py:169`). El offset real
  dentro del blob lo da la tabla de propiedades (en el preset analizado: `0x461a8`); el ID
  es estable entre unidades.
- **Persistencia**: `bk s` (`BKSY` / `Backup_sync_all`, `0x603/3`); el almacén es
  `Backup.bin` en `/dev/nflasha2` (el payload del updater lo monta en `/setting`),
  checksum del blob en `+0x20` recalculado por la cámara al sincronizar
  (`pmca/backup/__init__.py:84-90`). `bk patch` reescribe el blob entero
  (`BKDA` → editar → checksum → `BKDW`) y es la ruta prevista para propiedades de solo
  lectura (`pmca/platform/backup.py:120-159`).

### Verificación del preset de fábrica (test `tests/test_s62_backup_modelname.py`)

En `0110_backup/SYSMUSASHI-DSLR/DM_UUD3/CX77500_ALLLANG.bin` (852 647 B, SHA-256
`ff67f1ab81fbebcfe12000ba396dac546997c7fbf5042e8b3c2a55a7a202cd4b`):

| ID | Propiedad | attr | Tamaño | Valor |
|---|---|---|---|---|
| `0x003e0005` | `modelName` | `0x01` | 16 | `ILCE-6000` + 7 NUL |
| `0x00e70000` | `modelCode` | `0x02` | 5 | `00 00 06 99 05` |
| `0x00e70003` | `serialNumber` | `0x02` | 4 | `17 89 56 97` (placeholder) |
| `0x01660024` | `androidPlatformVersion` | `0x00` | 8 | `2.4` |

`modelName` aparece **una sola vez** en el blob; `ILCE-6001` no aparece en ningún fichero
del firmware. Aviso: attr `0x01` significa «solo lectura» según el parser de PMCA; si `BKWR`
devuelve `-2` («Protection enabled»), las alternativas son `bk unlock` antes de `bk w`, o
`bk patch`. El procedimiento reportado no incluye `unlock`.

## 5. El procedimiento reportado (modelo → `ILCE-6001`)

Cambio (cámara aún identificada como `ILCE-6000`, por eso no hace falta `-m`):

```
pmca-console-v0.17-win updatershell
bk w 0x003e0005 49 4c 43 45 2d 36 30 30 31 00 00 00 00 00 00 00
bk s
```

Reversión (aquí **sí** hace falta `-m ILCE-6000`):

```
pmca-console-v0.17-win.exe updatershell -m ILCE-6000
bk w 0x003e0005 49 4c 43 45 2d 36 30 30 30 00 00 00 00 00 00 00
bk s
```

- Los 16 B son `ILCE-6001` + 7 NUL, exactamente el tamaño de la propiedad.
- `-m ILCE-6000` en la vuelta es coherente con el código: `updatershell` elige el fdat con
  `getCameraInfo().modelName` y `getFdat()` recorta sufijos no numéricos; con el nombre ya
  cambiado no encontraría payload para `ILCE-6001` y hay que forzar el modelo
  (`pmca/commands/usb.py:350-370`, `pmca/commands/usb.py:319-338`). Es una señal de que el
  nombre reportado es lo que el host usa para seleccionar firmware.
- **Efecto «shell mode»: NO VERIFICADO.** El nombre es dato, no código: el barrido del
  firmware 3.21 (`av-cam.bin`, `nflasha15`, `nflasha16`, `firmware.fdat`) no encuentra
  `ILCE-6001` en ninguna parte, y `ILCE-6000` solo aparece en los presets de backup. No puede
  ser un match literal de tabla. Sí se sabe que el nombre se consume en runtime:
  `MprCtrl::GetModelName(char*)` (17 B, `analysis/objstillpool-100b-layout.json:23`) y
  `CmnMRUtil::_temporaryConvModelID2ModelName` (ID→nombre, `reports/elf-atlas.json:46602`),
  lo que sugiere identidad funcional por código de modelo y nombre derivado/descriptivo.
  Si el efecto existe, depende de un consumidor que parsee el string o de otro ajuste.
- **Riesgo**: escribir NVRAM. El nombre no afecta al guard del updater (usa el código
  numérico `0x41030035`), pero sí a la identificación y a la selección de fdat del host; la
  reversión es el mismo procedimiento con `ILCE-6000`.

## 6. Relación con el resto del proyecto

- El almacén BK4 es el mismo de S55 (`Backup_read_4Byte` en `liro.ko`, pares GPIO leídos de
  `CX77500_*`); `modelName` convive con esos pares en la misma tabla. Es la capa de
  configuración/NVRAM, no código.
- CXD90014 aparece a la vez como familia de cifrado fdat y como descrambler en el RE del
  proyecto.
- Nada de esto altera S51: **A=NO, B=NO, C=NO**.

## 7. Evidencia y límites

| Afirmación | Estado | Evidencia |
|---|---|---|
| `bk w` = escritura de propiedad BK4 por `BKWR` o `0x603/2` | VERIFICADO (fuente) | `platform/__init__.py:111-119`, `backend/usb/__init__.py:101`, `usb/sony.py:1041` |
| `0x003e0005` = `modelName`, 16 B | VERIFICADO (fuente + preset) | `platform/backup.py:169`, test S62 |
| Preset A6000 con `ILCE-6000` en `0x3e0005` | VERIFICADO (bytes) | test S62, blob SHA-256 arriba |
| fdat A6000: modelo numérico `0x41030035`, versión 3.21, guard CRC | VERIFICADO (bytes + fuente) | test S62, `fwtool/sony/fdat.py:32-56,298-340` |
| `updatershell` ejecuta código en el updater y expone shell USB `0x23` | VERIFICADO (fuente; no ejecutado) | `updatershell/*.cpp`, `pmca/usb/sony.py:417-582` |
| `serviceshell` autentica y expone backup/terminal/ficheros | VERIFICADO (fuente; no ejecutado) | `pmca/usb/sony.py:890-1057` |
| `ILCE-6001` no existe en el firmware 3.21 | VERIFICADO (barrido) | este documento §5 |
| El cambio de nombre habilita «shell mode» | NO VERIFICADO | reporte del usuario; sin confirmación estática ni dinámica |
| Reversión requiere `-m ILCE-6000` por selección de fdat | INFERENCIA fuerte | `commands/usb.py:350-370` + coherencia con el procedimiento |

**Pendiente para cerrar el efecto**: leer con REA los lectores de `Backup_read` para
`0x3e0005` (¿`MprCtrl`, `MprIf`?) y comprobar si comparan/parsean el nombre; o una traza
pasiva autorizada (`bk r`, `info`, `serviceshell`). Fuera de las reglas actuales.
