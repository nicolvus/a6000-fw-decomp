# FILM-PB-1 / sub-backup-store — Dónde vive el pack `RcsTbl`, quién registra los readers y por qué puede quedar sin registrar en frío

26-11-2026 · Binario: `firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libmpr.so`
(fw 3.21, 10 321 204 B, SHA-256 `9a74a3bb42836559888509b6113d281b85ae53b03eb9cdf4a965eafb545e4c30`).
**Direcciones = VA del ELF (base 0).** Desensamblado: `python3 /tmp/tools/elftool.py <so> dis <va> <len>` (capstone Thumb-2, con nombres de PLT resueltos).
Evidencia: [reports/evidence/film-pb-1-sub-backup-store-20261126/](evidence/film-pb-1-sub-backup-store-20261126/) (índice fichero a fichero en su `INDEX.md`).
Todo sale de bytes del binario. No se ha ejecutado firmware, ni tocado cámara ni tarjeta.

Continúa [la auditoría de RcsBackupTblData](film-pb-1-sub-rcsbackup-20261126.md) y usa el fallo cerrado `0x10100001`
en `0x2B39EE` que aporta el subagente *tabla-readers*. Aquí no se repite el barrido de la tabla: se responde **por qué** puede
quedar vacía y **cómo comprobarlo en la cámara**.

---

## 0. Resumen (20 líneas)

1. El pack `RcsTbl` **no vive en la tarjeta**: vive en un *sector FBS* (Flash Backup Sector) del **NAND interno**, accesible sólo por `FlashLib` sobre `/dev/nflasha4` (bloque) / `/dev/cnflasha4` (carácter). Ni NVRAM-partición con ficheros, ni `/setting`, ni partición montada.
2. La tabla `0xA3699C` está en **`.bss`** (`.bss` = `0x9DF808`+`0xFC2FC`): al cargar la librería está **a ceros**. Ningún reader existe de fábrica; todos se registran en tiempo de ejecución.
3. Geometría: **30 entradas × 0x14 B**, indexadas por el **fileType** de `0x9D2380` (30 words: `0x10,0x11,0x12,0x20,0x21,0x28,0x29,0x2c,0x2d,0x30,0x31,0x38,0x39,0x40,0x60,0x61,0x68,0x6c,0x62,0x63,0x90,0x91,0x92,0xa0,0xb1,0xb2,0xb3,0xb8,0xbc,0xbd` + centinela `-1`).
4. Campos: `+0x00` fileType/SName (u32, se usa también como `ldrh`), `+0x04` **handle del sector FBS**, `+0x08` estado (`1`=abierto), `+0x0C` y `+0x10` los dos primeros bytes del pack leído (`0x2B45FE`/`0x2B4600`).
5. El "reader" **no es una función**, es un **handle de sector** de `FlashLib`. El test `[entry+4]==0` de `0x2B39EC` significa "ese sector nunca se abrió", no "falta una rutina".
6. **Único escritor** del campo reader: `SetSectorManagerTable` (`0x2B45A8`), y tiene **exactamente 2 llamantes**: `0x2B46D0` y `0x2B48D0`.
7. Esos dos llamantes son **el mismo bucle copiado** en `BackupMgr::WarmBootInit` (`0x2B4624`) y `BackupMgr::Init` (`0x2B4820`).
8. `SetSectorManagerInfo` (`0x2B208C`, el otro posible "registro") es **sólo el comando de consola** `SetSMI`: 1 llamante, `0x2B5A3A`, que parsea argv con `"%s %s %s %s %s %s"`. No interviene en el arranque.
9. La rama que deja el hueco a cero está en `0x2B4718`: escribe `+0x00`=fileType, `+0x08`=0, `+0x0C`=0 y `+0x04`=**handle (posiblemente 0)**. Es el `else` del test de existencia.
10. Test de existencia por cada uno de los 30 fileTypes: `FlashLib::CheckExistSector` (`0x2B8B48`) debe devolver **`0x45`** (`cmp r0,#0x45` en `0x2B4688`/`0x2B4888`).
11. `0x45` = "existe": `DFB::CheckExistFile` devuelve `0x45` en el camino bueno (`0x2A672E`, `movs r4,#0x45`) y **`0x4F` si el DFB "not initialized yet"** (`0x2A66AE`, log `0x7DE124`).
12. Si `FlashLib::m_enableFlag` (`0xA36C78`) es **0**, `CheckExistSector` devuelve **`-1`** para todo (`0x2B8B6E`) y no se abre nada.
13. `m_enableFlag` **sólo se escribe en un sitio**: `0x2B6B64`, dentro de `FlashLib::Init(MPR::SystemType)` (`0x2B696C`).
14. `FlashLib::Init` obtiene la geometría con `0x2B0FFC(SystemType,&m_blockNum,&m_sectorNum,&m_sectorSize)` y la capa DFB la saca del NAND: abre `/dev/nflasha4` o `/dev/cnflasha4` y calcula el offset con **`/sys/block/nflasha0/nflasha0p4/start`** (`0x7DD572`; errores en `0x7DD597`/`0x7DD5CD`).
15. Por tanto el registro depende de: **modelo** (`SystemType` → geometría), **driver/partición NAND** (`nflasha4`, `nflasha0p4`) y **orden de arranque**. **No** depende de `/setting` (libmpr no contiene esa cadena), **ni de `nflasha2`**, ni de ningún fichero.
16. Hay rearme: `BackupMgr::Init` deja su callback en `FlashLib` (`SetBackupMgrCallback`, `0x2B4946`, apunta a `BackupMgr::Event` `0x2B47E0`); `Event(0)` rehace el bucle (`0x2B4810` → `0x2B4624`). Si ese aviso no llega, la tabla queda a cero **toda la sesión**.
17. El CFW instalado **no toca este código**: los 5 `.so` del paquete son `CautionConfig.so`, `libObj.so`, `viewUnified2/4/7.so`; `libmpr.so` no existe en el paquete y `MPR_SCN_FLASH_BACKUP_INIT.so` es de fábrica.
18. Lo que sí cambia el CFW es **global**: quita `0700_part_image/dev/nflasha5` (WBI) → arranque **en frío** (`BootMode 1`), y el actualizador reescribe particiones (`us_mkfs.sh`, `part_image.sum`).
19. Si el DFB no consigue su área (`nflasha0p4`) o `DvdFlashBackupLib::Init` sale con geometría 0, **los 30 fileTypes fallan a la vez** → cualquier `(userId,backupId)` devuelve `0x10100001` → MSV, DCF y XAVC caen juntos **aunque la tarjeta esté recién formateada**.
20. Segundo borrado masivo posible, del mismo módulo: `FlashBackupCheckAndDestroy` (`0x61DB54`) borra AVCHD/M2PS/MP4/DCF (`0x61DB94…0x61DC54`) cuando el sector devuelve `0x10100002`. Con la tabla vacía el índice AV, el journal de MSV y el DCF se pierden en el mismo arranque.

---

## 1. Geometría de `0xA3699C` (lo mínimo para leer el fallo)

`0xA3699C` cae en `.bss` (`.data` acaba en `0x9DF808`), es decir **ceros al `dlopen`**. Dump y región:
[03-table-A3699C-dump.txt](evidence/film-pb-1-sub-backup-store-20261126/03-table-A3699C-dump.txt),
[05-sector-mgr-region-2b2000-2b4c00.txt](evidence/film-pb-1-sub-backup-store-20261126/05-sector-mgr-region-2b2000-2b4c00.txt).

La tabla se llama en el propio binario *Sector Manager Info Table* (`0x7E72CF`: `[ SName (ID) ]|[ Handle ]|[status ]|[ OM ][Index]`),
y los 30 fileTypes y sus nombres están en `.data` `0x9D2154…` con literales en `0x7E3F9D`
(`FLH AVCHD`, `FLH DCF`, `FLASH MP4`, `FSYS`, `AVI1 (CSVC1)`…) — ver
[19-sector-names.txt](evidence/film-pb-1-sub-backup-store-20261126/19-sector-names.txt).
El índice se obtiene con `GetSectorManagerInfoTableIndexFromUserID` (`0x2B2F48`), que compara `entry[+0]`
contra el fileType de `(userId, mediaId)` y devuelve `0x10800010` si no encuentra (`0x2B2FBA`) —
**también cabecera `0x10`**, así que ese código imprime el mismo `Err RcsBackupTblData`.

| offset | contenido | escritor |
|---|---|---|
| `+0x00` | fileType / nombre de sector | `0x2B45F2`, `0x2B4724` |
| `+0x04` | **handle FBS (reader)** | `0x2B45FC`, `0x2B4730` |
| `+0x08` | estado (1 = abierto) | `0x2B45F6`, `0x2B472A` |
| `+0x0C` | byte 0 del pack leído | `0x2B45FE`, `0x2B472C` |
| `+0x10` | byte 1 del pack leído | `0x2B4600` |

---

## 2. Quién rellena: dos bucles idénticos y un `else` que deja `reader = 0`

`SetSectorManagerTable(userId, handle, index)` — `0x2B45A8`
([08-table-registration-2b4400.txt](evidence/film-pb-1-sub-backup-store-20261126/08-table-registration-2b4400.txt)):

```
002b45e0  bl 0x2B3948              ; lee 0x80 B del sector (ReadNextPackData)
002b45e6  cbnz r0, 0x2B4602       ; si falla, NO registra
002b45f2  str  r5,[r1,r6]         ; +0x00 = fileType
002b45f6  str  r1,[r3,#8]         ; +0x08 = 1
002b45fc  str  r4,[r3,#4]         ; +0x04 = handle  <-- el "reader"
002b45fe  str  r1,[r3,#0xc]  ; 002b4600 str r2,[r3,#0x10]
```

Llamantes (`e.calls(0x2B45A8)` = `0x2B46D0`, `0x2B48D0`), ambos dentro del **mismo bucle de 30 vueltas**:

```
002b487c  ldr.w r0,[r8,r5,lsl#2]        ; r8 = 0x9D2380 (fileType)
002b4880  blx  FlashLib::CheckExistSector
002b4888  cmp  r0,#0x45
002b488a  bne  0x2B4918                 ; <-- si NO es 0x45 -> rama que pone reader=0
...
002b4918  str.w r1,[sb,r2]              ; +0x00 = fileType
002b492a  str  r2,[r3,#8]               ; +0x08 = 0
002b492c  str  r2,[r3,#0xc]             ; +0x0c = 0
002b4930  str  r2,[r3,#4]               ; +0x04 = handle (0 si falló OpenSector32)
```

- `BackupMgr::Init()` `0x2B4820`: `FlashLib::InvalidateSync` → bucle → `FlashLib::SetBackupMgrCallback(&BackupMgr::Event)` → `ValidateSync`.
- `BackupMgr::WarmBootInit()` `0x2B4624`: bucle idéntico, **alcanzado desde `BackupMgr::Event(0)`** (`0x2B4804`:`cbz r4` → `0x2B4810`:`b.w 0x2B4624`).
- `BackupMgr::Init` tiene **un solo llamante**: `0x7126E6`, dentro de una cadena secuencial de `bl` de inicialización (0x514C6C, 0x4CA630, …, 0x2B4820, 0x4A8864, …). No hay condición alrededor: se ejecuta siempre que se cargue `libmpr`.

`SetSectorManagerInfo` (`0x2B208C`) escribe los mismos campos pero desde **argv de consola**; su único llamante `0x2B5A3A`
está en el handler de `SetSMI [index] [SectorName(Hex)] [handle] ...` (`0x7E8899`). **No es el registro de arranque.**

---

## 3. La condición real: `CheckExistSector == 0x45` ⟸ DFB inicializado **y** sector existente

`FlashLib::CheckExistSector` (`0x2B8B48`):

```
002b8b4c  ldr r3,=0xA36C78 (m_enableFlag)
002b8b52  cbz r3, 0x2B8B6E   ; -> 0xFFFFFFFF
002b8b62  bl  0x2B1068       ; -> DFB::CheckExistFile(fileType, idCheckFlag)
```

`DFB::CheckExistFile` (`0x2A6690`) — [26-DFB-CheckExistFile-2a6690.txt](evidence/film-pb-1-sub-backup-store-20261126/26-DFB-CheckExistFile-2a6690.txt):

```
002a66a2  ldrb r3,[0x9E484C]           ; "initialized"
002a66a6  cbnz r3, 0x2A66B8
002a66aa  log "[DFB]not initialized yet:CheckExistFile()"   (0x7DE124)
002a66ae  movs r0,#0x4F                                     ; <-- NO inicializado
...
002a66da  log "[DFB]CheckExistFile--exist[%x]"
002a672e  movs r4,#0x45                                     ; <-- existe
```

Conclusión mecánica: **`0x4F` (o `-1`) ≠ `0x45` ⇒ no se abre nada ⇒ las 30 entradas quedan con `+0x04 = 0`
⇒ cualquier `ReadFirstPackData` corta en `0x2B39EE` con `0x10100001`.** Es un fallo **todo-o-nada**: no hay
camino por el que MSV, DCF y XAVC se registren por separado; comparten el mismo bucle.

`m_enableFlag` se escribe **sólo** en `0x2B6B64` (dentro de `FlashLib::Init`); los otros 34 xrefs del símbolo son lecturas
([22-enableflag-xrefs.txt](evidence/film-pb-1-sub-backup-store-20261126/22-enableflag-xrefs.txt)).

---

## 4. De qué depende el registro (respuesta a la pregunta 3)

`FlashLib::Init(MPR::SystemType)` — `0x2B696C`
([23-FlashLib-Init-2b696c.txt](evidence/film-pb-1-sub-backup-store-20261126/23-FlashLib-Init-2b696c.txt)):

```
002b6982  ldr r0,=0x003C00BF ; bl 0x2B1468 -> flag
002b698c  tst r3,#1 ; bne -> m_enableFlag = 0    /  si bit0==0 -> m_enableFlag = 1  (0x2B6B64)
002b69bc  bl 0x2B0FFC(SystemType, &m_blockNum, &m_sectorNum, &m_sectorSize)
002b69c6  cmp r0,#0x49 ; beq (ya inicializado, se tolera)
```

y la capa DFB abre dispositivo real:

| dependencia | evidencia |
|---|---|
| Dispositivo NAND: `/dev/nflasha4` (bloque) y `/dev/cnflasha4` (carácter) | strings en `.data` `0x9D20F4` / `0x9D212D`, xref `0x2A3FD8`/`0x2A3FD0` |
| **Offset de la partición**: `/sys/block/nflasha0/nflasha0p4/start` | `0x7DD572`, errores `0x7DD597` (`open`) y `0x7DD5CD` (`fstat`) |
| Driver NAND (`DFA::OpenDriver`, ioctl `SDM_IOC_GETPBLKID`/`MMS_IOC_PERASE`) | `0x7DD46B`, `0x7DD9A4`, `0x7DDC58` |
| **Modelo**: `MPR::SystemType` → geometría `blockNum/sectorNum/sectorSize` | firma `_ZN8FlashLib4InitEN3MPR10SystemTypeE`; log `DvdFlashBackupLib::Init result:blockNum[%d],sectorNum[%d],sectorSize[%d]` (`0x7E3CCE`) |
| **Orden de arranque**: rearme por callback | `0x2B4944` `ldr r0,=0x2B47E1` ; `0x2B4946` `SetBackupMgrCallback` |

Negativos verificados ([27-dependencias-negativas.txt](evidence/film-pb-1-sub-backup-store-20261126/27-dependencias-negativas.txt)): **`/setting` no aparece** en `libmpr.so` (barrido de la `.rodata`/`.data`: cero coincidencias),
**`nflasha2` tampoco**, y en toda la cadena (`0x2B39B8`→`0x2B2F48`→`0x2B3948`→`FlashLib`→DFB) **no hay `open`/`fopen`
de ningún fichero**: sólo `open` de `/dev/(c)nflasha4` y `open`/`fstat` de `/sys/block/nflasha0/nflasha0p4/start`.

Consecuencia: **el registro depende de modelo + driver/partición NAND + secuencia de arranque**, no de ficheros de ajustes.

### 4.1 El rearme que casi nadie mira

`BackupMgr::Init` termina dejando su callback en `FlashLib` (`SetBackupMgrCallback`, `0x2B4946`) apuntando a
`BackupMgr::Event` (`0x2B47E0`). `Event(eventId)` con `eventId==0` rehace **el bucle completo**:
`0x2B47FA` (`movw r2,#0x8030`, semáforo) y `0x2B4810` `b.w 0x2B4624`.

Esto significa dos cosas:
1. `BackupMgr::Init` corre **muy pronto** (cadena de init de `libmpr`, `0x7126E6`), probablemente **antes** de que el DFB
   tenga su geometría. En ese primer paso el bucle puede no registrar nada: es *normal* y se corrige cuando llega el aviso.
2. Si el aviso no llega (DFB que nunca termina de inicializar, `DvdFlashBackupLib::Init` fallido, `nflasha0p4` ilegible),
   la tabla se queda **con los 30 handles a 0 durante toda la sesión** — sin ningún error visible salvo el `Err RcsBackupTblData`
   de cada consumidor (MSV, DCF, XAVC).

---

## 5. ¿Pudo romperlo el CFW? (pregunta 4)

**El código no.** Los 5 `.so` del paquete 3.93 son `lib/CautionConfig.so`, `lib/libObj.so`, `lib/viewUnified2.so`,
`lib/viewUnified4.so`, `lib/viewUnified7.so`; `libmpr.so` **no existe en el paquete**
([paquete-diferencias.txt](evidence/film-pb-1-20261127/paquete-diferencias.txt)) y el escenario que dispara la
inicialización del backup, `scenario/MPR_SCN_FLASH_BACKUP_INIT.so`, es de fábrica: 6 093 B que sólo hacen
`MprCtrl::GetMprIfInstance()` y `MprIf::ExecMprUtility(1, NULL)` (`0x6DA`/`0x6DE`)
([24-scenario-flash-backup-init.txt](evidence/film-pb-1-sub-backup-store-20261126/24-scenario-flash-backup-init.txt)).

**El entorno sí puede.** El CFW es el único cambio global del proyecto: retira `0700_part_image/dev/nflasha5`
(WBI de Sony) y el actualizador reescribe el mapa de particiones (`us_mkfs.sh`/`part_image.sum`). Encaja con esta cadena por
dos vías independientes:

- **Vía A (tabla vacía).** Si tras el arranque en frío la partición que el DFB espera como `nflasha0p4` no es la misma
  (renumerada, recortada o con `start` distinto), `open`/`fstat` de `.../nflasha0p4/start` falla → `FlashLib::Init`
  no habilita (`m_enableFlag=0`) o el DFB queda "not initialized" (`0x4F`) → **30 handles a 0** → `0x10100001` en todo.
- **Vía B (borrado masivo).** `FlashBackupCheckAndDestroy` (`0x61DB54`) prueba los cuatro medios y, cuando el sector
  devuelve `0x10100002`, escribe `... AVCHD / M2PS / MP4 / DCF BackupClear!!` y **destruye** cada sector
  (`0x61DB94…0x61DC54`, [25-FlashBackupCheckAndDestroy.txt](evidence/film-pb-1-sub-backup-store-20261126/25-FlashBackupCheckAndDestroy.txt)).
  Un solo pase deja sin índice AV, sin journal de MSV y sin DCF al mismo tiempo.
- **Vía C (reparación).** `IsNeedRepairFlashBackup` (`0x2B8950`) devuelve **1 cuando `m_enableFlag==0`** (`0x2B89A8`),
  es decir "sin FlashLib esto hay que repararlo"; su llamante (`0x2B5904`) escribe `need repair FlashBackup` (`0x7E8811`)
  y encadena `CheckAndRepairFlashBackup` (`0x2B89C0`).

Ninguna de las tres es un parche de código: son **estado del NAND interno** tras un arranque distinto. Y explican que la
tarjeta recién formateada no cambie nada: la tarjeta nunca entra en esta cadena.

---

## 6. Qué mirar en la cámara para confirmarlo

Ordenado por coste. Cualquiera de los tres primeros cierra el caso.

| # | Comprobación | Comando / dónde | Qué confirma |
|---|---|---|---|
| 1 | ¿Existen los nodos del NAND interno? | `ls -l /dev/nflasha4 /dev/cnflasha4` | si faltan, el DFB no abre: `m_enableFlag=0` |
| 2 | ¿Se puede leer el offset que usa el DFB? | `cat /sys/block/nflasha0/nflasha0p4/start` y `cat /proc/partitions` | si `nflasha0p4` no existe o el `start` no cuadra con la tabla real, es la Vía A |
| 3 | Log del módulo en el arranque | `dmesg`/log de `libmpr`: `[DFB]not initialized yet:CheckExistFile()` (`0x7DE124`), `[DFB] open /sys/block/nflasha0/nflasha0p4/start error`, `DvdFlashBackupLib::Init result:blockNum[..],sectorNum[..],sectorSize[..]` | geometría `0,0,0` o "not initialized" ⇒ DFB caído, no tarjeta |
| 4 | Traza del bucle de registro | buscar `[FBM]Init()  [entryNo:%d]` (30 líneas) y `[FBM]--Init()-OpenSector32()[errorFBS:%d][hand..]` | 30 líneas con `errorFBS:0x4f`/`0xffffffff` ⇒ fallo de existencia, no de datos |
| 5 | ¿Se borró solo? | buscar `FlashBackupCheckAndDestroy : ... BackupClear!!` y `need repair FlashBackup` | confirma la Vía B/C (sectores destruidos por reparación) |
| 6 | Autotest del sistema | buscar `MPR::SELF_CHECK_FLASH_BACKUP_FAILURE` / `FLASH_BACKUP_FAILURE :` (`0x923C2B`, `0x92A67D`) | el propio firmware marca el subsistema de backup como fallo |
| 7 | Estado de los 30 sectores | consola MPR: dump de la *Sector Manager Info Table* (`0x7E72CF`: `[SName][Handle][status][OM][Index]`) | lectura directa de `0xA3699C`: todo `Handle` a 0 = tabla vacía |

Lectura esperada si se confirma: **`Handle = 0` en las 30 filas**, `entry[+0]` con el fileType correcto
(la rama `0x2B4718` sí escribió el nombre) y ningún error de tarjeta ni del sistema de ficheros.

---

## 7. NO_VERIFICADO

1. **Quién llama a `FlashLib::Init`**: no tiene llamante dentro de `libmpr` (ni `bl`, ni PLT, ni puntero literal, ni
   `R_ARM_RELATIVE`), y en todo `/usr` el único importador de símbolos `FlashLib*` es `libInfraFsys.so`, que usa unos
   `FlashLib_Open/Read/Write` **distintos** (C, de sistema de ficheros). El camino real es
   `MPR_SCN_FLASH_BACKUP_INIT.so → MprIf::ExecMprUtility(1) → 0x722BCC → 0x4500CC → …`: falta recorrer ese último salto.
2. **Significado exacto de `0x10100002`** (el que dispara `BackupClear`) dentro de la familia `0x1010xxxx` del gestor de sectores.
3. **Mapa de particiones esperado**: no se ha comparado el `nflasha0p4` que espera el DFB con el que deja el actualizador del CFW;
   sólo se ha verificado que el DFB lee exactamente esa ruta de sysfs.
4. Los tres mecanismos (A/B/C) son **compatibles con** el log del 20-10, pero el log no se ha podido cotejar línea a línea aquí:
   el discriminante es la presencia de `[DFB]not initialized yet` frente a `FlashBackupCheckAndDestroy`.
