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

Comando de consola ya existente: **`InitB [OM] [MediaID]`** (handler `0x2B5B34`, `bl 0x2B43F0` en
`0x2B5B5A`), los dos argumentos en **decimal**.

### 6.1 La orden exacta: `FBM InitB 6 3`

La tabla de pares `0x9D23FC` (37 filas × 0x18) está en `.data` de `libmpr.so` y se lee del propio ELF:
`{+0 userID, +4 mediaID, +8 sector, +0xC OM, +0x10 función, +0x14 dato}`. Volcado reproducible en
`reports/evidence/film-pb-1-causa-fbm-20261126/tabla_pares_om.txt`.

| userID | OM | mediaID | sector | handle en el volcado |
|---|---|---|---|---|
| `0x10` (HD-AVC) | 4 | **3** | `0x30` | **4** ✓ |
| `0x04` / `0x21` (M2PS) | **6** | **3** | **`0x31`** | **0** ✗ |
| `0x20` (DCF) | 7 | **3** | `0x62` | **3** ✓ |
| `0x23` (MP4) | 10 | **3** | `0xB2` | **5** ✓ |
| `0x22` | 9 | 8 | `0xA0` | 1 ✓ |

Que la tarjeta es **mediaID 3 (MS1)** no es una suposición: es el único media con tres pares ya
registrados, y es el que sostiene lo que sí funciona (fotos y su DCF `(0x20,3)`). **El único par del
media 3 sin handle es el del sector `0x31`**, compartido por `userID 0x04` y `0x21`, con **OM 6 (M2PS)**.
Por eso fallan MSV, DCF y XAVC/MP4 a la vez: los tres leen la misma tabla de contenidos de `0x31`.

⇒ Una sola orden: **`FBM InitB 6 3`**. En el arnés el handler se ejecuta (`0x2B5B34` → `0x2B43F0`) y la
tabla no se rellena porque el shim no emula `/dev/nflasha4` (`CreateSector32` devuelve `0x7` =
`FBS_INVALID_PROCESS`); con `NFLASH4=1` y una imagen real la prueba es válida (en curso).

Después de crearlo: **reiniciar MPR** (la tabla `0xA3699C` es un snapshot de `FBM::Init`) — aunque
`fbm-crear` documenta que el alta ya queda en la SMT viva y `FBM::Init` la reabre al arrancar.

### 6.2 La consola sola no basta: hay que registrar antes el escritor

`BackupMgr::InitBackupData(6, 3)` aborta con **`0x10800010`** porque `0x2B3000` (`0x2B301A cbz r2`) salta
las filas de `0x9D23FC` con `fn == 0`, y **las 37 lo están**. El único escritor de ese campo es
`BackupMgr::EntryWriteBaseDataFunction` (`0x2B1DEC`), que la consola expone como **`EWBDFD`** y como el
test de fábrica **`LTC`**.

Secuencia medida en el arnés con la imagen real de `nflasha4` (`NFLASH4=1`):

| línea | efecto | flash |
|---|---|---|
| `FBM EWBDFD 4 3 0` | `0x2B3000(6,3)`: `0x10800010` → `0` | 0 B |
| `FBM InitB 6 3` | idx 10 = `0x31 / h3 / +8 = 1 / om6`; `BkRead(0x04,3)` = `0x10100003` (tolerado) | **1 300 B** |
| reinicio | `FBM::Init` la registra sola desde el flash | 0 B |

`LTC 1` también funciona (`BkRead` = `0`) pero **no debe usarse en la cámara**: sus escritores
`0x2B5724`/`0x2B5658` son de fábrica y escriben en la página de datos base un texto de prueba
(`"MS "/"HDD "+"packData"`). El escritor real de `(4,3)` es `0x5CA354`, registrado en `0x5C9B06` por
`m2psIfo_Backup`, y hoy no lo registra nadie; el dummy `0x2B5184` de `EWBDFD` no estorba porque el camino
de grabación decide por `fileType` (`0x2B2F48`) y no por `fn`.

### 6.3 Qué se arregla y qué no

- **Clip nuevo: sí.** Con handle en idx 10 al arrancar, la grabación registra el clip en la BD
  (`m2psIfo_Backup` → `OpenRecFile` `0x5E7B8C`, `CloseRecFile` `0x5E7E50`) y ese clip tiene IFO.
- **Clips viejos: no quedan registrados.** El sector se crea vacío y nadie rellena registros antiguos;
  su lectura degrada a `0x10100003`, que los llamantes toleran, pero el contenido no está.
- **La grabación llevaba fallando en silencio**: `CloseRecFile` (`0x5E7E50`) descarta el `r0` del backup y
  `0x61D950` ni mira el retorno del gestor de medios. Por eso grababa clips sin registrarlos.
- **«Recuperar BD imág.» no podía ayudar**: `BeginRepair` reescribe `AVF_INFO/AVIN0001.INP` pero no llama
  a `0x2B43F0` ni a `CreateSector32`; su re-registro choca en `0x5C9F7E` / `0x2B3D24` (`0x10100001`).

### 6.4 ¿Basta crear el sector para que el cargador del IFO devuelva 0? Sí, y con matiz

Medido en el arnés con la imagen real de `nflasha4`: tras `FBM EWBDFD 4 3 0` + `FBM InitB 6 3`
(idx 10 = `0x31 / h3 / +8=1 / om6`), `BkRead(0x04,3)` devuelve **`0x10100003`**. Ese código lo tolera
`0x35E0FA..0x35E100` y el resto de la cadena, por código, es:

`0x35E118 vtbl[0xB8]` (`0x3B16B0`) escribe `8` y deja `[r7+0xd6] = 0` → `0x35E954` → `r5 = 0x00500003`
(«tabla vacía») → **`RcsBackupTblData` = `0x00500003`** → `0x3AFA94` lo interpreta como **Need Salvage**,
pone `[msv+0x44] = 1` (`0x3AFB18`) y **devuelve 0** → `0x698EC8`: `0x6F0D4C(0)` → **0**, sin el 1749.

Antes de crear el sector los mismos puntos daban `0x00100001` y `0xB0800001`. Es decir: **crear el sector
hace que el cargador deje de fallar**, pero lo que queda es una tabla vacía marcada para *salvage* — el
propio firmware sabe que la BD está vacía y es él quien debe reconstruirla. Eso encaja con que un clip
**nuevo** sí quede registrado y los viejos no.

No se pudo medir `0x3AFA94` / `0x698EC8` ejecutándose de verdad: el arnés no arranca el gestor de vídeo
(sin `MsvMcmd`), y las llamadas inyectadas se quedan en la macro de traza `0x34E468` →
`osal_valloc_msg_wait`. El valor de arriba es la cadena leída instrucción a instrucción.

### 6.5 Auditoría independiente del paquete 3.97

Rehecha desde cero (desempaquetado propio, `debugfs`, Unicorn): `.dat` `69447a27…5cd9`, `libmpr`
`831142ae…e378e`, gancho `0x7126E6 = 28 f2 8b fc`, `0x7126EA` intacto, 132 021 relocaciones sin un solo
`r_offset` en el gancho o la cueva, cabecera y las 25 secciones byte a byte, y el `.dat` vuelve a pasar el
auditor con `--base-dat` (`todo_ok`, 22/22). Dos observaciones no bloqueantes: la cueva vive en `.rodata`
(flags de sección `A`) pero se ejecuta porque el primer `PT_LOAD` es `R E` y cubre esa VA —está medido en
QEMU—, y su `push {r4,r5,lr}` deja `SP ≡ 4 (mod 8)` en las llamadas, fuera de AAPCS, sin que ninguno de los
tres destinos use `ldrd/strd/vldr/vstr` en sus primeros `0x300` B.

### 6.6 El camino de escritura, medido con el sector y con `fn`

En el invitado, sobre copias de la imagen (`nf4` + `NFLASH4=1`):

| llamada | antes (imagen prístina) | sólo sector `0x31` | sector + `fn` |
|---|---|---|---|
| `ChangeSector(4,3)` `0x2B41B4` | `0x10100006` | `0x10800010` | **0** |
| `WritePackBegin` `0x2B3D24` | `0x10100001` | 0 | **0** |
| `WritePackAdd` `0x2B3C64` | — | 0 | **0** |
| `WritePackEnd` `0x2B3B94` | — | `0x10800020` (`FBS_UNCERTAIN_WRITE_POINT`) | **0** |
| bytes escritos en `nflasha4` | 0 | 0 | **4 770** |

Es decir: **hacen falta las dos cosas**, el sector y el `fn` de la fila `0x9D23FC[13]` (`u04 / m3 /
ft031 / om6`) — exactamente lo que hacen `FBM EWBDFD 4 3 0` + `FBM InitB 6 3` y lo que hace el parche C.
Con las dos, un clip nuevo queda registrado en la BD.

### 6.7 El `fn` no persiste; el sector sí

`0x9D23FC` es `.data`: el `fn` que registra `EWBDFD` vive **sólo en RAM** de esa sesión. El sector `0x31`,
en cambio, queda en `nflasha4`. Consecuencia práctica, medida en el invitado: tras reiniciar, la
**lectura** sigue arreglada (`BkRead` = `0x10100003`), pero la **escritura** de un clip nuevo vuelve a
`ChangeSector = 0x10800010` / `WritePackEnd = 0x10800020`. Por eso:

- consola: aplicar → **sin apagar** → grabar el clip nuevo → reproducirlo (si se reinicia antes de grabar,
  repetir `FBM EWBDFD 4 3 0`; el `InitB` ya no hace falta);
- CFW 3.97: su cueva registra el `fn` en **cada** arranque, así que no depende de la sesión.

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
