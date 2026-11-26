# FILM-PB-1 / sub-consola-sector31 — la vía de consola que registra el sector 0x31 (26-11-2026)

## Resumen (≤20 líneas)

1. **Sí hay vía de consola, sin parchear firmware: `FBM LTC 1` (mejor) o `FBM EWBDFD 4 3 0`, y después `FBM InitB 6 3`.**
2. Medido en el arnés con `NFLASH4=1` sobre copia del volcado (runs C y G): tras `EWBDFD 4 3 0` (o `LTC 1`), `0x2B3000(6,3)` pasa de **`0x10800010`→`0`**; tras `InitB 6 3` el idx 10 de `0xA3699C` queda **`0x31 / h3 / +8=1 / om6`** ⇒ criterio OK.
3. Criterio real cumplido: `BkRead(0x04,3)` = **`0`** con `LTC 1` (run G) y **`0x10100003`** con `EWBDFD` (run C), antes `0x10100001`; entrada `sec=0x31 h=3 est=4 om=3`.
4. **Persiste**: `WBI` (borra y reconstruye `0xA3699C` con `CheckExistSector`) deja el idx 10 en `h1/+8=1` (runs C y G) y un **reinicio real** con la imagen modificada lo registra ya en el arranque, con `BkRead` = `0x10100003` (run D, imagen de `EWBDFD`; run H, imagen de `LTC 1`).
5. **Escribe en nflasha4**: 1 300 B en tres zonas — `0x9D400` (tabla de sectores, 394 B), `0xBD780` (página de asignación/copia, 394 B) y `0x380000` (página de datos base, 512 B) — reconstruible con `patch_desde_log.py`.
6. **Ninguno de los comandos pedidos sirve por sí solo**: `ChgSec 6 3` y `ChgSec 4 3` no crean (0 B, tabla igual, `0x10100001`), `CRFB`/`INRFB`/`DRWBI` no tocan la tabla (0 B), y `WBI` sólo reconstruye lo que ya existe en el flash (run A).
7. La causa es una sola línea: `0x2B3000` **salta las entradas de `0x9D23FC` con `fn==0`** (`0x2B301A: cbz r2`) y las 37 están a 0; el **único escritor de `fn`** es `BackupMgr::EntryWriteBaseDataFunction` `0x2B1DEC`, que la consola expone como **`EWBDFD`** (y como `LTC 1`, que es el test de fábrica para (4,3)/(0x21,3)/(4,4)/(0x21,4)).
8. `ChgSec` **no puede crear nunca**: exige handle ya registrado (`0x2B41EE: cbz r3` → `0x10100006`) y sólo después llama a `WriteBaseData` (run E: 0 B creados).
9. Sin página de datos base (`0x380000`) el sector **sí existe** (`BkRead` = `0x10100003`) pero `+8` queda a 0 (run F): la página de datos es lo que fija el estado 1.
10. **No hace falta plan B (parche)**: la secuencia mínima de consola es `LTC 1` (o `EWBDFD 4 3 0`) + `InitB 6 3`; `LTC 1` usa los escritores de prueba de fábrica y da `BkRead` = `0`.

## 1. Tabla de comandos del monitor FBM (`0x7E7FAC–0x7E8108`, 29 registros de 12 B)

Volcado propio (`evidencia/tabla_cmds.py` → `evidencia/tabla-comandos-fbm-detalle.txt`) sobre
`analysis/camera-extract/usr/lib/libmpr.so` (sha256 `9a74a3bb…4c30`; base ELF = VA). Despacho: `0x2B50D8`
→ `0x6822F8(tabla, argc, argv)`; `argc` cuenta la línea entera con el nombre del módulo (el comando ve
`argc-1`). Parsers: **`0x5FFE1A` = HEX**, **`0x5FFE6E` = DEC**.

| # | comando | handler | argc comando | argumentos (parser) | destino y qué escribe |
|---|---|---|---|---|---|
| 00 | `Destroy` | 0x2B5EA0 | 2…5 | tipo 1…4; mediaID/OM/userID **HEX** | `0x2B3794`/`0x2B361C`/`0x2B34D8`: destruye backups (borra sectores del flash) |
| 01 | `Close` | 0x2B5E6C | 2 | `[index]` **DEC** | `0x2B2A6C`: `FlashLib::CloseSector(handle)` y **pone a 0 `+4`(handle), `+8`, `+0xC`** de la entrada |
| 02 | `Delete` | 0x2B5E38 | 2 | `[index]` **DEC** | `0x2B2A2C`: `FlashLib::DeleteSector(id)` en el flash; **no** limpia la SMT |
| 03 | `DeleteAll` | 0x2B5E20 | 1 | — | `0x2B29CC` (`DeleteAllSectors`): cierra/borra los 30 sectores |
| 04 | `ReadAllPD` | 0x2B5D30 | 2 | `[Sec name]` **HEX** | `0x2B3AB8`: vuelca todos los packs del sector (lectura) |
| 05 | `ReadPD` | 0x2B5C6C | 3 | `[UserID] [MediaID]` **HEX** | `0x2B39B8` (`BkRead`) + `0x2B2138`/`0x2B4584`/`0x2B3948`: lee y vuelca el primer pack |
| 06 | `WritePack` | 0x2B5B74 | 5 | `[USER_ID] [MEDIA_ID] [DATA_ID]` **HEX** + `[len]` **DEC** | `0x2B3B94`/`0x2B3C64`/`0x2B3D24`: escribe un pack de prueba (búfer 128 KiB) |
| 07 | **`InitB`** | **0x2B5B34** | 3 | `[Operation Mode] [MediaID]` **DEC** | **`0x2B43F0` (`InitBackupData`) → `0x2B4030` (`WriteBaseData`): crea y da de alta** (ver §3) |
| 08 | **`ChgSec`** | **0x2B5AF4** | 3 | `ChangeSector[userID(HEX),mediaID(HEX)]` — **userID y mediaID, HEX** | **`0x2B41B4` (`ChangeSector`): mueve un sector ya registrado; exige `handle!=0`** |
| 09 | `SetOM` | 0x2B5A60 | 3 | `[OM] …` **DEC** | `0x2B1EE8`: fija el *operation mode* en curso (global) |
| 10 | `SetSMI` | 0x2B59DC | 6 | `[index] [SectorName] [handle] [status] [OM]` (nombre **HEX**, resto **DEC**) | **`0x2B208C`: escritura directa** de `+0/+4/+8/+0xC` en `0xA3699C` (`idx<=0x1D`), sin flash ni validación; luego `View` |
| 11 | `View` | 0x2B59CA | 1 | — | `0x2B3260`: vuelca los 30 sectores (por `osal_snd_msg`, no por la serie) |
| 12 | `ASV` | 0x2B59B8 | 1 | — | `FlashLib::ConPutStatus()`: estado de todos los sectores |
| 13 | `GASI` | 0x2B5AA8 | 1 | — | `0x2B2520`: información de todos los sectores |
| 14 | `WDS` | 0x2B5E08 | 1 | — | `0x2B2AC8` (`WaitDeleteSector`) |
| 15 | `Flush` | 0x2B5DF0 | 1 | — | `0x2B2AF0`: vacía búferes (escritura diferida al flash) |
| 16 | `SSS` | 0x2B5DB0 | 3 | `[SectorNo] [Status]` **HEX** | `FlashLib::DbgSetSectorStatus(sector,status)`: **fuerza el estado FBS de un sector** |
| 17 | `GSS` | 0x2B5D64 | 2/3 | `GSS` ó `[UserID] [MediaID]` **HEX** | `0x2B30C4` → `0x2B3094`: estado del sector (`GSS ret = [%x]`) |
| 18 | `ARB` | 0x2B5AC0 | 1 | — | `FlashLib::AllDeleteRingBuffer()`: vacía el anillo del FBS |
| 19 | `Quit` | 0x2B598C | 1 | — | `FlashLib::Quit()`: cierra FlashLib |
| 20 | `GetAlignSize` | 0x2B5924 | 2 | `[Original Data Size]` **DEC** | `0x2B20D4`: sólo calcula |
| 21 | **`INRFB`** | **0x2B5904** | 1 | — | **`FlashLib::IsNeedRepairFlashBackup` `0x2B8950`: sólo consulta** (`0x2B1304`; 1/0/0x49) |
| 22 | **`CRFB`** | **0x2B58EC** | 1 | — | **`FlashLib::CheckAndRepairFlashBackup` `0x2B89C0`: repara el FBS** (`0x2B1074`) si `m_enableFlag`; no toca `0xA3699C` |
| 23 | `DFT` | 0x2B58D4 | 1 | — | `0x2B23A0`: vuelca la tabla de funciones de usuario (`0x9D23FC`) |
| 24 | `DRWBI` | 0x2B58BC | 1 | — | `0x2B49EC`: **sólo imprime** `m_rwBufferInfo[2]` (`0xA36C20`) y su handle |
| 25 | `LTC` | 0x2B57F0 | 2 | `[module number]` **DEC** | tests locales LTC_01…LTC_12; **`LTC 1` = `0x2B5598`** da de alta `fn=0x2B5724`/`0x2B5658` con `arg=0xA36C4C`/`0xA36C50` para (4,3) (0x21,3) (4,4) (0x21,4) |
| 26 | **`EWBDFD`** | **0x2B5198** | 4 | `[UserID] [MediaID] [FunctionDataAdrs]` **HEX** | **`0x2B1DEC`: escribe `fn=0x2B5185` (dummy) y `arg=<adrs>` en la entrada de `0x9D23FC` de ese (user,media)** |
| 27 | `CWBDF` | 0x2B5128 | 3 | `[UserID] [MediaID]` **HEX** | `0x2B1E34`: pone `fn`/`arg` a 0 en esa entrada |
| 28 | **`WBI`** | **0x2B4AAC** | 1 | — | `FlashLib::WarmBootInit()` + **`FBM::WarmBootInit` `0x2B4624`: borra `0xA3699C` y la reconstruye** con `CheckExistSector`; **devuelve 0** |

Comprobaciones de la tabla: nombres, handlers y `desc` salen del volcado directo; el reparto nombre↔handler y
las cadenas de ayuda coinciden con el informe previo
[`film-pb-1-sub-consola-fbm-20261127.md`](film-pb-1-sub-consola-fbm-20261127.md) §1 (aquí se añade el parser
de cada argumento y el destino resuelto por `bl`/PLT).

## 2. Las cuatro rutas pedidas, medidas en orden (run A, `runA-orden/consola.log`)

Estado de partida (arnés, imagen = volcado del 20-10): `0xA3699C` con **1/30** handles (idx 23 `0xa0`),
idx 10 = `0x31 h0/s0/om0`, `0x9D23FC` con `fn=0/arg=0` en las 37 entradas, flash idéntico al volcado (0 B).

| paso | retorno del handler | `0xA3699C` (handles) | diff de `/nflasha4.img` | `0x2B3000(6,3)` |
|---|---|---|---|---|
| `ChgSec 6 3` | 1 | 1/30 · idx10 `h0` | **0 B** | `0x10800010` |
| `ChgSec 4 3` | 1 | 1/30 · idx10 `h0` | **0 B** | `0x10800010` |
| `CRFB` | 1 | 1/30 · idx10 `h0` | **0 B** | `0x10800010` (y `0x9D23FC` sigue `fn=0`) |
| `INRFB` | 1 | 1/30 · idx10 `h0` | **0 B** | — (`IsNeedRepairFlashBackup()` = **0**) |
| `DRWBI` | 1 | 1/30 · idx10 `h0` | **0 B** | — |
| `WBI` | **0** | 1/30 (sólo reabre `0xa0`, `h1`) | **0 B** | `0x10800010` |
| `BkRead(0x04,3)` | — | — | — | **`0x10100001`** |

Interpretación (todo estático, §1): `ChgSec` llama a `ChangeSector` `0x2B41B4`, que (a) resuelve el handle con
`0x2B3094` y (b) llama a `WriteBaseData(om,media)` sólo si ese handle ya existe (`0x2B41EE: cbz r3` →
`0x10100006`). `CRFB`/`INRFB` trabajan en la capa FBS (`0x2B1074`/`0x2B1304`), `DRWBI` es un `printf` y `WBI`
reconstruye, no crea: los cuatro son coherentes con 0 B de escritura y tabla intacta.

## 3. La cadena que crea y registra, y el único cerrojo: `fn==0` en `0x9D23FC`

`WriteBaseData` `0x2B4030` es el **único** sitio que da de alta en `0xA3699C` (`0x2B40CE–0x2B40EA`):

```
0x2B40C8  blx FlashLib::CreateSector32( sector = [0xA3699C + idx*0x14 + 0], flag=0, &handle, &id )
0x2B40CC  cbnz r0 -> error 0x10800010
0x2B40DA  [0xA3699C+idx*0x14+0]  = id        (0x31)
0x2B40E2  [.. +4] = handle        [.. +8] = 1        [.. +0xC] = operationMode
```

y su primera puerta es `0x2B3000` (`GetSectorHandleFromOperatioModeAndMediaID`, **un solo llamante: `0x2B406A`**),
que recorre `0x9D23FC` (paso 0x18) y **descarta toda entrada con `fn==0`**:

```
0x2B3018  ldr r2,[r3,#4]     ; fn
0x2B301A  cbz r2, 0x2B302A   ; fn==0 -> siguiente entrada
0x2B301C  ldr r2,[r3]        ; OM   | 0x2B3022 ldr r2,[r3,#-8] ; mediaID
```

Con las 37 entradas a 0, `InitB 6 3` y `ChgSec` mueren en `0x10800010` **antes** de crear. El escritor de esos
dos campos es `BackupMgr::EntryWriteBaseDataFunction` `0x2B1DEC` (`[entry+0x10]=fn`, `[entry+0x14]=arg`, sólo
para el `(userID,mediaID)` que case) y su inverso `0x2B1E34`; **la consola los expone como `EWBDFD` y `CWBDF`**
(§1). La entrada que hace falta es la **[13] `u04/m3/ft031/om6`**, es decir **`EWBDFD 4 3 <adrs>`**.

`0x2B1DEC` tiene 11 llamantes; entre ellos `0x38096E`, `0x380990`, `0x3AC5AE`, `0x3B0466`, `0x520230` (módulos
reales que registran su función) y **`LTC_01` `0x2B5598`**, que registra las funciones de prueba
`0x2B5724`/`0x2B5658` con `p_arg` `0xA36C4C`/`0xA36C50` **para (4,3), (0x21,3), (4,4) y (0x21,4)** —
exactamente los pares "M2PS + MS/HDD" de los sectores `0x31`/`0x21`/`0x2c`/`0x2d`.

## 4. Medición de la ruta (run C, `runC-ewbdfd-wbi/consola.log`)

| línea | retorno | tabla `0xA3699C` | flash |
|---|---|---|---|
| `EWBDFD 4 3 0` | 1 | 1/30 · `0x9D23FC[13]` = `u04/m3/ft031/om6/**fn=0xAE5B0185**/arg0` (= base+0x2B5185) | 0 B |
| `0x2B3000(6,3)` | — | — | — → **ret=0, handle=0** (antes `0x10800010`) |
| `InitB 6 3` | 1 | **2/30 · idx10 = `0x31 h3 s1 om6` → CRITERIO OK** | **1 300 B** |
| `0x2B3000(6,3)` | — | — | ret=0, **handle=3** |
| `BkRead(0x04,3)` | — | — | **`0x10100003`** (entrada `sec=0x31 h=3 est=4 om=3`) |
| `WBI` | 0 | **2/30 · idx10 = `0x31 h1 s1 om6` → CRITERIO OK** (reconstruida desde el flash) | 0 B más |

`0x10100003` es el código que el llamante tolera (el `0x10100001` de «entrada sin handle» desaparece).
Las escrituras en `/dev/nflasha4` (1300 B, 3 zonas):

| zona | bytes | qué es |
|---|---|---|
| `0x9D400` | 394 | página de tabla de sectores: cabecera `00000000 4a004a00 81000000 010103ff`, entradas de 8 B `a0 0000 0001 01 ff`, `31 0000 0005 07 ff` (seq y cks al final) |
| `0xBD780` | 394 | página de asignación/copia (contiene `… 00 10 00 00 d4 00 15 22 …`, la referencia a la página `0x9D400`); sin ella el arranque **no** ve el sector (run F del informe previo: run5) |
| `0x380000` | 512 | página de **datos base** del sector: cabecera `80000000 02000603 8403f0fa …` y cuerpo a cero (la escribe `WriteBaseData`) |

## 4-bis. La misma ruta con el test de fábrica (`LTC 1`, run G `runG-ltc1/consola.log`)

| línea | retorno | tabla `0xA3699C` / `0x9D23FC` | flash |
|---|---|---|---|
| `LTC 1` | 1 | `0x9D23FC`: `[04] u04/m2 fn=0x2B5725 arg=0xA36C50`, `[05] u21/m2 fn=0x2B5659 arg=0xA36C50`, **`[13] u04/m3 (0x31) fn=0x2B5725 arg=0xA36C4C`**, `[14] u21/m3 fn=0x2B5659 arg=0xA36C4C` | 0 B |
| `0x2B3000(6,3)` | — | — | ret=0, handle=0 |
| `InitB 6 3` | 1 | **2/30 · idx10 = `0x31 h3 s1 om6` → CRITERIO OK** | **1 300 B** |
| `BkRead(0x04,3)` | — | — | **`0000000000` (= 0)** — mejor que con el dummy |
| `WBI` | 0 | **2/30 · idx10 = `0x31 h1 s1 om6` → CRITERIO OK** | 0 B más |

Las dos rutas escriben **las mismas páginas de metadatos** (`0x9D400` y `0xBD780`, byte a byte iguales) y
difieren sólo en 104 B de la página de datos `0x380000`: el escritor de `LTC 1` vuelca su carga de prueba
(`"userid::M2PS+HDMapplication--mediaid::MS" + "packData"`, en ASCII en la imagen) y el dummy de `EWBDFD` no
escribe nada (cuerpo a cero) ⇒ por eso `LTC 1` deja `BkRead` = `0` y `EWBDFD` `0x10100003`.

## 5. Persistencia (runs C, D, G y H)

- **Dentro del proceso** (`WBI`, la misma rutina que `FBM::Init`: borra la tabla y la reconstruye con
  `FlashLib::CheckExistSector == 0x45` + `OpenSector32`): idx 10 = `h1/+8=1` → **sobrevive**.
- **Reinicio real**: imagen reconstruida en el host desde el volcado de tramos del log
  (`patch_desde_log.py` → `/tmp/nflasha4-tras-ewbdfd.bin`, sha256 `6d2ab43a…ca51`, 1 300 B distintos; y
  `/tmp/nflasha4-tras-ltc1.bin`, sha256 `4ae884d5…20d8`) y nueva pasada QEMU
  (`runD-reinicio/consola.log`, `runH-reinicio-ltc1/consola.log`):
  · imagen de `EWBDFD` (run D): `tras-arranque 2/30 · idx10 = 0x31 h1 s1 om6 → CRITERIO OK` y
    `BkRead(0x04,3) = 0x10100003`;
  · imagen de `LTC 1` (run H): `tras-arranque 2/30 · idx10 = 0x31 h1 s1 om6 → CRITERIO OK` y
    `BkRead(0x04,3) = 0000000000` (= 0);
  ambas **sin escribir nada** (diff 0 B). Es decir: `FBM::Init` ya registra el sector en el arranque sin
  ninguna orden de consola.
- Contraste útil (run F, imagen **sin** la página de datos `0x380000`): el sector **existe** (idx10 `h1`,
  `BkRead` = `0x10100003`) pero `+8` queda a **0** → el estado 1 lo aporta la página de datos base.
- Artefacto de método: llamar `FBM::Init` `0x2B4820` **directamente** (sin `FlashLib::WarmBootInit`) deja la
  tabla a 0/30; la reconstrucción válida es la de `WBI` (run C) o la del arranque (run D).

## 6. Por qué `ChgSec` no sirve y qué pasa si se usa (run E, `runE-ewbdfd-chgsec/consola.log`)

`EWBDFD 4 3 0` deja `0x2B3000(6,3)` en 0, pero `ChgSec 4 3` **no crea**: `ChangeSector` `0x2B41B4` empieza por
`0x2B3094(4,3,&handle)` y, si el handle de la SMT es 0, se va a `0x10100006` («Source backup handle not
found», `0x2B41EE`/`0x2B41F4`) sin llegar a `WriteBaseData`. Medido: 0 B de flash, tabla 1/30 y
`BkRead(0x04,3)` = **`0x10100001`**. `ChgSec` es *relocación*, no creación.

## 7. Conclusión operativa

- **Vía de consola (sin parche)**: `FBM LTC 1` (o `FBM EWBDFD 4 3 0`) y luego `FBM InitB 6 3`. Da `idx10 = 0x31 / handle!=0 / +8=1`, `BkRead(0x04,3)` = `0x10100003` y **persiste** al
  reiniciar MPR porque queda en `nflasha4` (tabla + asignación + datos base).
- **No hace falta plan B.** Si se quisiera el parche mínimo, sería el equivalente a esas 2 escrituras:
  `fn` = una dirección Thumb válida en `0x9D241C+0x10` (`0x9D23FC + 4*0x18 + 0x10`) y `arg` = 0 — es decir
  `str r2,[0x9D242C]` — y luego dejar que `WriteBaseData` haga el alta de 4 palabras (`+0=0x31`, `+4=handle`,
  `+8=1`, `+0xC=OM`); no se propone porque la consola ya lo consigue.
- **Límite**: `EWBDFD` deja `fn = DummyEntryWriteBaseDataFunction` (`0x2B5185`, sólo log + `return 0`); es la
  función que la capa FBM usa para escribir «base data» de ese `(user,media)`: con ella la lectura devuelve
  `0x10100003` porque no escribe el pack. `LTC 1` instala en su lugar los escritores de prueba
  `0x2B5724`/`0x2B5658` (que sí escriben la carga en el pack) ⇒ `BkRead` = `0`. Si en la cámara se quiere la
  función real de producción, el alta debe hacerla el módulo que la registra (11 llamantes de `0x2B1DEC`).
  **No medido en cámara.**

## 8. Reproducción

```sh
sh reports/evidence/fbm-sector31-consola-20261126/comando.sh      # compila y lanza A, C, E, F y D
grep -a NF6 reports/evidence/fbm-sector31-consola-20261126/runC-ewbdfd-wbi/consola.log
python3 reports/evidence/fbm-sector31-consola-20261126/patch_desde_log.py \
    reports/evidence/fbm-sector31-consola-20261126/runC-ewbdfd-wbi/consola.log /tmp/nflasha4-tras-ewbdfd.bin
.venv/bin/python reports/evidence/fbm-sector31-consola-20261126/evidencia/tabla_cmds.py   # tabla de §1
```
