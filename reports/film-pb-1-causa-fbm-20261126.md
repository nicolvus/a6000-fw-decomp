# FILM-PB-1 — Causa raíz cerrada: la tabla de sectores del backup FBM está vacía y nadie la crea

Fecha: 26-11-2026. Sustituye a §11 de [film-pb-1-cierre-estatico-20261126.md](film-pb-1-cierre-estatico-20261126.md),
que atribuía el fallo a que `FlashLib::Init` no se ejecutaba. **Eso era un error de escaneo** (§2.1).

## 0. Resumen

1. La cadena del síntoma está cerrada de punta a punta con direcciones: `Err RcsBackupTblData` →
   `0x10100001` → `mp4Ifo` `0xB0800001` → ninguna IFO cargada → guarda A del reproductor →
   **`0x1A` = «No se puede visualizar.»**
2. El productor exacto de `0x10100001` es **`0x2B3A28`**, dentro de `ReadFirstPackData` (`0x2B3948`),
   cuando `[0xA3699C + 0x14*idx + 4] == 0`. Esa entrada no tiene **handle de sector**, no "falta código".
3. Los handles los pone `FBM::Init` (`0x2B4820`) en `MprIf::Create`, y **solo si
   `CheckExistSector(sector) == 0x45` y `OpenSector32` devuelve handle**. `FBM::Init` **no crea** ningún
   sector: si no existe, deja `+4 = 0` y sigue.
4. En el volcado de RAM del 20-10 solo **4 de 30** entradas tienen handle (`0x30`, `0x62`, `0xA0`, `0xB2`);
   las de foto (`0x90/0x91/0x92`) y las de vídeo (idx 24…29) están a 0.
5. En los volcados de `nflasha4` el **historial completo** del anillo de la tabla de sectores nunca pasa de
   esos **5** `fileType`. Los de foto y vídeo no aparecen **nunca**, ni en el del 20-10 ni en los dos del 05-11.
6. Por eso la tarjeta, el formato, «Recuperar BD imág.» y el firmware oficial no cambian nada: **la tabla
   que falta está en NAND interna y nada la vuelve a crear**.
7. El camino de alta existe en el propio firmware: `BackupMgr::InitBackupData(OM, mediaID)` (`0x2B43F0`)
   → `WriteBaseData` (`0x2B4030`): `GetNewSectorManagerInfoTableIndexFromUserID` (`0x2B2E54`) +
   `FlashLib::CreateSector32` (`0x11FA5C`) + alta en `0xA3699C` (`0x2B40DA`) + `SetSectorManagerTable`
   (`0x2B45A8`). Se llega por consola con **`InitB [OM] [MediaID]`** (`0x2B5B5A`, cadenas `0x7E88D1`/`0x7E8946`).
8. Tras crearlos hay que **reiniciar MPR**: `0xA3699C` es una foto de `FBM::Init` en `MprIf::Create` y no se
   refresca sola.

## 1. La cadena, línea a línea del log real

Log: `[MSV][MS1]Err RcsBackupTblData`, `[DCF][MS1]Err RcsBackupTblData`, `[MP4IFO] ### mp4Ifo faild at
IF/mp4Ifo_General.cpp(1749) ErrCd: 0xB0800001`, `[XAVCIFO] ... xavcIfo_File.cpp(0874) ErrCd: 0xB0520001`,
`[MMGR][AVI] ## ERROR(MMGR):0x31000006 ## ... CreateAndLoad()`, `[AVI][PLAY] AviSeqPlay.cpp Error=[ER_BADARG]`.

| Paso | Dirección | Qué hace |
|---|---|---|
| 1 | `0x698EE6` (`mp4Ifo_General::FlashLoadForMsv`) | la llamada que falla es `0x698EDE bl 0x3AFA94` |
| 2 | `0x3AFA94` | `RcsBackupTblData`; imprime «Err RcsBackupTblData» en `0x3AFB28` |
| 3 | `0x35E0F4` | `bl 0x2B39B8` con `userID=[file+0x4088]`, `mediaID=[file+0x408c]` |
| 4 | `0x2B39EE` / `0x2B3A28` | lee `[entrada+4]`; si es 0 → `0x10100001` |
| 5 | `0x35E0FA..0x35E100` | solo tolera `0x10100003` (fin de tabla); `0x10100001` es error duro |
| 6 | `0x3502CA` → `0x350124` | `0x10100001` → `0x00100001` |
| 7 | `0x6F0D4C` (`mov r4,ip` en `0x6F0E96`) | el fallback imprime **`0xB0800001`**, código genérico de mp4Ifo |

El par de vídeo coherente con el fallo es `(0x23, 7)` → sector `0xBD` → idx 29, con `handle = 0` en el
volcado del 20-10. `(0x22, 8)` → `0xA0` (idx 23) tiene handle y no fallaría.

## 2. Correcciones a lo publicado el 26-11

### 2.1 `FlashLib::Init` **sí** tiene llamante

`0x7126E2` hace `blx` al stub PLT `0x11DFE8`, seis bytes antes de `bl BackupMgr::Init`. Cadena completa:
IMDB → `InfraMprCtrl_Init` → `MprCtrl::Init` → `MprIf::Create` (`0x71CC20`) → `0x712530` →
`FlashLib::Init` → `BackupMgr::Init`. El «no tiene llamante» era un fallo del escáner: los `blx` a PLT no
se enmascaraban a palabra (mismo defecto en `elftool.py calls()`; corregido, hay 1 llamante en a6000,
a6300 y a7s).

Y se ve en el log de arranque, que trae la geometría real:

```
[DFB]mb_useDfaCache = 1
lblkinfo.lblk_size    = 262144
lblkinfo.num_of_lblks = 1932
lblkinfo.ltu_size     = 4096
[DFB] partition start sector = 100864
```

No hay `[DFB]not initialized yet` ni `[NBL] GetEepData() bkupErr…`, así que `m_enableFlag` (`0xA36C78`)
está a 1 y `CheckExistSector` no devuelve -1 por esa causa. **La hipótesis «el flash no se inicializa»
queda descartada por el propio log.**

### 2.2 `MprIf::ExecMprUtility(1)` no es la vía de arranque

La utilidad 1 (`init`) solo la piden dos escenarios (`MPR_SCN_FLASH_BACKUP_INIT` `0x6DE`,
`MPR_SCN_EXEC_FACTORY_MODE` `0x79E`, vía `libtestcmd_scn.so`) y el comando de consola
`MPR FUNCRECOVERY ExecMprUtility init`. Ni `init`, ni `im.elf`, ni `libObj` la llaman.

## 3. Por qué la tabla está vacía: `FBM::Init` no crea sectores

`FBM::Init` (`0x2B4820`) recorre la lista estática `0x9D2380` (30 `fileType`) y por cada uno:

```
002b48c8: ldrh r0,[r8,r5,lsl #2]      ; fileType
002b4880: blx  FlashLib::CheckExistSector
002b4888: cmp  r0,#0x45
002b488a: bne  0x2b4918                ; <-- deja +4 = 0 y NO crea nada
002b4896: blx  FlashLib::OpenSector32  ; r1 = 0 (FBS_MOVEFLAG)
002b48d0: bl   SetSectorManagerTable   ; alta real
```

Dos detalles que cierran puertas:

- El `FBS_MOVEFLAG` que recibe `OpenSector_Body` (`0x2B6688`) se **ignora**: en `0x2B66A4` hace
  `movs r1,#0` y pasa 0 a `0x2B10BA`. Parchear el flag en el llamante no serviría de nada.
- El único test de "sector vacío" en `libmpr` es `0x2B061E` (primer `u32 == 0xFFFFFFFF`). No hay magic
  por sector: `0x004A004A` y `draCNV4'` no son constantes de ningún binario de usuario.

### 3.1 Medido en la NAND

`nflasha4` = 10 MiB: sector de **1024 B**, 128 sectores por bloque, 80 bloques. El primer KiB es un anillo
de copias de la tabla de sectores, con cabecera `00 00 00 00 4A 00 4A 00` y registros de 8 B
`{u32 fileType, 4 B}`. Contando todas las copias de los tres volcados:

| Volcado | Copias con tabla | `fileType` que aparecen en **todo** el anillo |
|---|---|---|
| `nand-20261020` | 765 bloques no vacíos | `0x81`, `0xA0`, `0x62`, `0xB2`, `0x30` — **nunca más de 5** |
| `nand-20261105` | 229 sectores con datos | los mismos 5; la copia del offset 0 está **vacía** |
| `nand-20261105-total` | 381 sectores (superset del anterior) | los mismos 5 |

Los `fileType` de foto (`0x90/0x91/0x92`) y de vídeo no aparecen **en ninguna copia, en ningún volcado**.
No es corrupción: es una tabla que **nunca se llenó** para esos tipos.

Y el firmware oficial no la escribe: el DAT 3.21 trae `nflasha3/5/7/15/16`, no la 4.

## 4. Consecuencia en el reproductor (reproducida en el arnés)

Con el despachador real de FeaCore y `FeaIf::PlayMovie` (`0x44EE9C`) reales, sin UI:

- Estado real `[core+0x1F0] == 2` ⇒ contesta **`0x0A`** en `0x437BE8` sin mirar guardas.
- Con estado 5 salta **la guarda A** (`0x447A1E`): `0x447810` devuelve error, log
  `" Pb Disable!! ref) dsm get"` y **`0x1A` en `0x437C0A`**. La guarda B (`0x447F26`) no se ejecuta nunca.
- La causa inmediata es `[core+0xDC0] = 0`, el handle de media, que solo pone `EnterMoviePb`
  (`0x437A28`, orden **`0x40000017`**), y esa orden exige estado 2 **y media ya enumerada**.

El identificador correcto para instrumentar no es `MprIfMcmd::mp_owner` (cae fuera de `libmpr`) sino
`mp_mprIf` (`libmpr+0xAD3D90`) → `[0] = FeaIf`, `[FeaIf+4] = FeaCore`.

## 5. Lo que NO arregla el problema (ya probado)

| Acción | Resultado |
|---|---|
| Formatear la tarjeta en la cámara | nada: la tabla que falta está en NAND interna |
| «Recuperar BD imág.» | nada: la reconstrucción se apoya en las mismas tablas |
| Firmware oficial 3.21 / paquete A2 | nada: el DAT no reescribe `nflasha4` |
| CFW 3.93 `pp` | nada: no toca `libmpr` y sus 506 B de `libObj` son Picture Profile |
| Paquete con `av-cam` de fábrica (3.94) | nada: los parches de `av-cam` tienen 0 B en códec/muxer/decoder |
| Guardas anuladas (paquete C) | cambia el síntoma, no la causa: sin IFO no hay duración ni miniatura |

## 6. El arreglo: recrear los sectores FBM

```
BackupMgr::InitBackupData(OM, mediaID)        0x2B43F0
 ├ 0x2B4030  WriteBaseData
 │  ├ 0x2B2E54  GetNewSectorManagerInfoTableIndexFromUserID
 │  ├ 0x11FA5C  FlashLib::CreateSector32
 │  └ 0x2B40DA  alta en 0xA3699C (sector, handle, valid=1, +0xC)
 └ 0x2B45A8  SetSectorManagerTable  (rellena +0x10 con el segundo byte del pack)
```

Llamantes: consola FBM **`InitB`** (`0x2B5B5A`), y los de uso normal `mp4 0x37FC06/0x37FD4C`,
`MSV 0x38FEC4`, `DCF 0x61D94C` — es decir, la cámara crea estos sectores **cuando graba o guarda**, y en
esta unidad ese camino nunca ha llegado a completarse para foto ni para vídeo.

Comando de consola ya existente: **`InitB [OM] [MediaID]`**, cadenas `0x7E88D1`/`0x7E8946`.
Después: **reiniciar MPR** (la tabla `0xA3699C` es un snapshot de `FBM::Init`).

## 7. Cómo verificarlo sin cámara y cómo comprobarlo en cámara

- **Arnés**: `InitB` sobre el MPR real y lectura de `base+0xA3699C`; el sector debe quedar con `+4 != 0`
  (prueba en curso, `fbm-consola`).
- **Cámara** (requiere autorización, es escritura en NAND): consola MPR → `InitB 0 7` → apagar y encender
  → reproducir. Antes, volcado de `nflasha4` para tener rollback.
- **Discriminante barato**: leer `base+0xA3699C` de `im.elf` por `/proc/<pid>/maps` + SWD; si el idx 29
  sigue a 0 tras `InitB`, `CreateSector32` está fallando y el problema es de hueco/estado del flash.

## 8. Riesgos

- `CreateSector32` usa el asignador FBS, no escritura cruda: es la vía prevista por el firmware, pero no se
  ha probado en esta unidad.
- Crear los sectores **no rellena** el contenido: los vídeos ya grabados tendrán que entrar por el camino
  normal (enumerar y reconstruir). Las fotos no dependen de esta tabla, así que no hay riesgo de perderlas.
- Escribir `nflasha4` a mano (`dd`) se salta el asignador: **no hacerlo** salvo con rollback y como último
  recurso.

## 9. Evidencia

| Fichero | Contenido |
|---|---|
| [sub-mp4ifo-1749](film-pb-1-sub-mp4ifo-1749-20261126.md) | la cadena 1749 → `0x2B3A28` y la ausencia de rama alternativa |
| [sub-tabla-readers](film-pb-1-sub-tabla-readers-20261126.md) | geometría de `0xA3699C` y los 4/30 con handle en RAM |
| [sub-nflasha4](film-pb-1-sub-nflasha4-20261126.md) | geometría 1024/128/80, comparación de los tres volcados, D3 superset de D2 |
| [sub-executility](film-pb-1-sub-executility-20261126.md) | corrección del llamante de `FlashLib::Init` y de `ExecMprUtility` |
| [sub-arnes-orden](film-pb-1-sub-arnes-orden-20261126.md) | guarda A disparada con el despachador real |
| `reports/evidence/film-pb-1-log-real-20261126/anillo-mpr-20261020.txt` | el anillo de arranque con la geometría DFB |
