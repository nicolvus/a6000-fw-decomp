# FILM-PB-1 / sub-consola-fbm — la consola de FBM y el intento real de crear el sector 0x90 (27-11-2026)

## Resumen (≤20 líneas)

1. La tabla de consola del módulo **FBM** está en `.data` **0x7E7FAC–0x7E8108**: **29 registros de 12 B** `{char *name; int (*fn)(long argc,char **argv); char *desc}` + terminador `{0,0,0}`. El handler del módulo es **0x2B50D8** (literal 0x2B4E60 = 0x2B50D9) y se registra en 0x2B4D7E → `0x684940("FBM", 0x2B50D9, "FBM: ")`.
2. **No existe `CreateSector`, ni `Format`, ni `Repair`.** El que crea es **`InitB [Operation Mode] [MediaID]` (0x2B5B34; `bl 0x2B43F0` en 0x2B5B5A)** → `BackupMgr::InitBackupData` 0x2B43F0 → `WriteBaseData` 0x2B4030 → `0x2B2E54` (índice) + `FlashLib::CreateSector32` (0x2B40C8) + **alta en 0xA3699C en 0x2B40DA** (`+0`=id, `+4`=handle, `+8`=1, `+0xC`=OM).
3. Sintaxis exacta: ambos argumentos **decimales** (`0x5FFE6E` = parser base 10; el hex es `0x5FFE1A`). **OM** = `OperationMode` 0…10 (`INITIAL, VF, -VR, +VR, HD-AVC, M2PSAVC, M2PS, DCF, DCFONLY, DCFDIFF, MP4`, tabla 0x7E6654); `OM∈{7,8}` ⇒ rama «still» (0xA36970/0xA36C18), resto ⇒ «movie» (0xA36974/0xA36C0C) — 0x2B1DCC.
4. Qué sector sale de cada `InitB` lo decide la tabla estática **0x9D23FC** `{userID, mediaID, sector, OM}` (paso 0x18): **0x90 = (OM 4, media 7)**, 0x91 = (6,7), 0x92 = (7,7), 0xbd = (10,7), 0xb2 = (10, media 3 = MS1, la tarjeta). `mediaID` 7 = **USB**, 3 = **MS1** (tabla 0x7E6364) ⇒ `MediaID=7` **no** es la tarjeta.
5. **Prueba real (perfil nuevo `fbm`, QEMU)**: `lookup("FBM")` en el registro del monitor (base+0xA51EE4) devuelve **base+0x2B50D9**. `InitB 0 7`, `4 7`, `6 7`, `7 7`, `10 7` y `10 3` **se ejecutan** (devuelven 1) y **la tabla queda 0/30 antes y después**: ningún handle ≠ 0, ni en foto (0x90/0x91/0x92) ni en vídeo (idx 24…29).
6. **Código del fallo: `CreateSector32(sector, flag=0)` → `0x7` = `FBS_INVALID_PROCESS`** (medido con el traductor del propio firmware, `FlashLib::GetErrorString` 0x2B6114 sobre la tabla 0x7E9488; `handle=0`, `id=sector`). Llamado por símbolo (misma función que usa el comando) da lo mismo ⇒ **no es culpa de la consola**.
7. Por eso la consola **no puede** crear nada aquí: en el arnés el almacén DFB/FBS no es utilizable (`/dev/nflasha4` sólo se emula con `NFLASH4=1` + imagen real, `sonyshim.c:110-141`, y `pb_run` no pasa imagen). Hace falta: nflasha4 escribible y válido, el par `(OM, mediaID)` de 0x9D23FC, y (en cámara) reiniciar MPR porque 0xA3699C es un *snapshot* de `FBM::Init`.
8. `SetSMI` **no crea**: escribe 4 palabras en 0xA3699C (0x2B20AC–0x2B20B8, `idx<=0x1D`) sin tocar el flash y **sin validar el handle** ⇒ un `handle!=0` así es falso. `DeleteAll`/`CRFB` sólo borran/reparan.
9. Canal: la consola es el **monitor EX-PC de libmpr** dentro del proceso MPR, con I/O por un **anillo de 0x400 B en un área de MemInfo** (0x683C64–0x683CB4, objeto 0xA51AC4, selector 0x5F7A14(1,…) sobre 0xA4FD88) — **ni tty ni socket**. La salida de FBM va por `osal_snd_msg` (0x2B1D5C), así que `View` **no se lee por la consola serie**.

## 1. Tabla completa de comandos (VA del ELF, `libmpr.so` 3.21)

Base **0x7E7FAC**; registro de 12 B `{name, fn|1, desc}`; termina en 0x7E8108. Despacho: `0x2B50D8`
(`subs r1,argc,#1` / `adds r2,argv,#4`) → `0x6847EC` → **`0x6822F8(tabla, argc, argv)`**: `argv[0]=="?"`
(0x8CDFA2) → ayuda (0x682280); `argv[0]=="??"` (0x862811) → lista todo; si no, `0x682230` hace `strcmp`
contra `name` y `blx` a `fn` con `(argc, argv)`. Si no casa: imprime **"???" (0x85B781)** y devuelve 0.

| # | nombre | handler | argc mínimo | sintaxis exacta (cadena que imprime) | qué hace |
|---|---|---|---|---|---|
| 00 | `Destroy` | 0x2B5EA0 | 2 | `Destroy <1|2|3|4> …` — `type 1 Destroy(void)`, `type 2 … [mediaID(HEX)]`, `type 3 … [mediaID(HEX)] [operationMode(HEX)]`, `type 4 … [userID(HEX)] [mediaID(HEX)]` (0x7E8B70/0x7E8A7A/0x7E8AAD/0x7E8B06) | `BackupMgr::Destroy` variantes → 0x2B3794 |
| 01 | `Close` | 0x2B5E6C | 2 | `Close [index]` | cierra el sector `idx` de 0xA3699C → 0x2B2A6C |
| 02 | `Delete` | 0x2B5E38 | 2 | `Delete [index]` | borra el sector `idx` → 0x2B2A2C |
| 03 | `DeleteAll` | 0x2B5E20 | 1 | *(sin argumentos)* | cierra/borra los 30 → 0x2B29CC (`DeleteAllSectors`); la variante forzada es 0x2B2974 |
| 04 | `ReadAllPD` | 0x2B5D30 | 2 | `ReadAllPD [Sec name]` (hex) | vuelca todos los packs del sector → 0x2B3AB8 |
| 05 | `ReadPD` | 0x2B5C6C | 3 | `ReadPD [UserID(Hex)] [MediaID(Hex)]` | lee el primer pack y lo vuelca (`[SeekPoint][UserID][DataID] [Length] [Data]`) → 0x2B39B8 |
| 06 | `WritePack` | 0x2B5B74 | 5 | `WritePack [USER_ID] [MEDIA_ID] [DATA_ID] [Data length]` | escribe un pack de prueba (0x20000 B) |
| 07 | **`InitB`** | **0x2B5B34** | 3 | **`InitB [Operation Mode] [MediaID]`** (0x7E8946) | **crea los sectores de ese (OM, mediaID)** → 0x2B43F0 (ver §3) |
| 08 | `ChgSec` | 0x2B5AF4 | 3 | `ChangeSector[userID(HEX),mediaID(HEX)]` (0x7E891F) | cambia de sector → 0x2B41B4 |
| 09 | `SetOM` | 0x2B5A60 | 3 | imprime **por error** `InitB [Operation Mode]` (0x7E88D1) | fija el *operation mode* en curso → 0x2B1EE8 |
| 10 | **`SetSMI`** | **0x2B59DC** | 6 | **`SetSMI [index] [SectorName(Hex)] [handle] [status] [OM]`** (0x7E8899) | **escritura directa** en 0xA3699C → 0x2B208C |
| 11 | **`View`** | **0x2B59CA** | 1 | *(sin argumentos)* | vuelca los 30 sectores + lista de usuarios → **0x2B3260** |
| 12 | `ASV` | 0x2B59B8 | 1 | — | `FlashLib::ConPutStatus` (0x2B610C) |
| 13 | `GASI` | 0x2B5AA8 | 1 | — | todas las entradas de sector → 0x2B2520 |
| 14 | `WDS` | 0x2B5E08 | 1 | — | espera a que acabe un borrado → 0x2B2AC8 |
| 15 | `Flush` | 0x2B5DF0 | 1 | — | vacía el búfer → 0x2B2AF0 |
| 16 | `SSS` | 0x2B5DB0 | 3 | `SSS [SectorNo] [Status]` (hex) | `FlashLib::DbgSetSectorStatus` |
| 17 | `GSS` | 0x2B5D64 | 2 | `GSS` ó `GSS [UserID(Hex)] [MediaID(Hex)]` (0x7E8A1C) | estado del sector → 0x2B30C4 (`GSS ret = [%x]`) |
| 18 | `ARB` | 0x2B5AC0 | 1 | — | `FlashLib::AllDeleteRingBuffer` |
| 19 | `Quit` | 0x2B598C | 1 | — | `FlashLib::Quit` (0x11F0DC) |
| 20 | `GetAlignSize` | 0x2B5924 | 2 | `GetAlignSize [Original Data Size]` | `FlashLib::GetAlignSize` → 0x2B20D4 |
| 21 | `INRFB` | 0x2B5904 | 1 | — | `IsNeedRepairFlashBackup` (0x11F4C8) |
| 22 | **`CRFB`** | **0x2B58EC** | 1 | — | **`FlashLib::CheckAndRepairFlashBackup` 0x2B89C0** (repara la tabla de respaldo, no los sectores) |
| 23 | `DFT` | 0x2B58D4 | 1 | — | `m_userFuncTable` (0x7E6A9A) → 0x2B23A0 |
| 24 | `DRWBI` | 0x2B58BC | 1 | — | info de los búferes de lectura/escritura → 0x2B49EC |
| 25 | `LTC` | 0x2B57F0 | 2 | `fbm ltc [module number] [parameter1]....` (0x7E87C4) | tests locales (LTC_01…LTC_12) |
| 26 | `EWBDFD` | 0x2B5198 | 4 | `EWBDFD [UserID(HEX)][MediaID(HEX)][FunctionDataAdrs(HEX)]` | pone la función de escritura a un dummy |
| 27 | `CWBDF` | 0x2B5128 | 3 | `CWBDF [UserID(HEX)][MediaID(HEX)]` | limpia esa función |
| 28 | `WBI` | 0x2B4AAC | 1 | — | `FlashLib::WarmBootInit` + `FBM::WarmBootInit` 0x2B4624 |

Volcado reproducible en `evidence/film-pb-1-sub-consola-fbm-20261127/evidencia/tabla-comandos-fbm.txt`.

## 2. Cómo se llega a esa consola desde fuera

- **Quién la lee: el proceso del MPR (`im.elf`)**, que es el único que mapea `libmpr.so`: la tabla del
  monitor y el despachador son código/`.bss` de libmpr (registro en **0xA51EE4**, 12 B `{name, handler,
  título}`, alta con **0x684940**, máx 0x80, error `"Over Flow Monitor Command Buffer"` 0x90F17F).
  Medido en el arnés: base libmpr `0xAE2B8000`, registro `0xAED09EE4`, `lookup("FBM")` → `0xAE56D0D9`
  = base+0x2B50D9 (`run3/consola.log`).
- **Cómo se da de alta FBM**: `FBM::Init` 0x2B4820 → **0x2B4D7E** `0x684940("FBM" 0x7E8114,
  0x2B50D9, "FBM: " 0x7E8118)`. El mismo registro aloja el módulo **"MPR"** (0x90232A) con handler
  `MprIfMcmd::ExecSubCmd` (reloc ABS32 en 0x728340, símbolo 1656) y título
  `"Media Player Recorder Monitor Command"` (0x928120) — es la consola donde se teclea
  `MPR debug ApiTrace on`.
- **Formato de línea**: `<MODULO> <comando> [args…]`, separados por espacios; `argc` cuenta la línea
  **entera incluido el módulo** y `argv[0]` es el módulo (por eso el handler hace `argc-1`/`argv+1` y el
  comando ve `argc = 1 + nº args`). `?` y `??` son ayuda/listado. Nombre desconocido → `"???"`.
- **Canal: ni serie, ni socket, ni `/dev` de terminal.** El monitor de libmpr ("**** EX-PC Monitor
  Program ****" 0x90F1A0, prompt **"MON>"** 0x90EC49, arranque 0x684D2A–0x684D60) monta su E/S sobre un
  **anillo de 0x400 B en un área de memoria**: 0x683C64–0x683CB4 crea el objeto stream (**0xA51AC4**,
  ctor 0x684A48) con los punteros que devuelve el selector de MemInfo **0x5F7A14(1,…)** sobre el
  descriptor 0xA4FD88; 0x684ACC escribe un carácter y 0x684CBC lo lee. Las cadenas del propio monitor lo
  llaman *stream driver* (`/dev/stream` 0x860738, `"ERROR : Failed to open stream driver"` 0x90ECC7).
  Es el puente con la herramienta EX-PC, no la consola serie.
- **La salida de FBM no sale por ahí**: cada línea de FBM va por `osal_snd_msg` a una cola
  (**0x2B1D5C**, colas 0x8F013A/0x8F0313), así que `View` escribe en el log del MPR, no en la consola.
- **En el arnés no hay cliente EX-PC**: `scripts/gui/harness/e2e_drv.py … linea='…'` publica en
  `/linea` del **shim** (`E K=V`, variables de entorno), **no** llega al monitor. La vía usada aquí
  (§3) es llamar al **handler real 0x2B50D8** con la línea ya troceada: a partir de ahí corre el
  código de fábrica (registro → despacho → tabla → comando), sin fabricar argv dentro del comando.

## 3. Prueba real en el arnés (perfil nuevo `fbm`)

Shim propio `evidence/…/sonyshim-fbm.c` (copia del del arnés + hilo `PBINJECT`), instalado como
`OVERLAY2` en el perfil **`analysis/gui/g22/harness/live/fbm/`**; lanzador `pb_run_fbm.py`
(`run.build_initrd` + `qemu_cmd`, `-serial file:consola.log`). Cámara no usada: sólo QEMU.

Secuencia por el handler real, con volcado de `base+0xA3699C` (30 × 0x14 B) antes y después:

| línea | retorno del handler | tabla 0xA3699C |
|---|---|---|
| `View` | 1 | — |
| `InitB 0 7` (lo pedido: OM 0, media 7) | 1 | **0/30** (sin cambios) |
| `InitB 4 7` (par de 0x90) | 1 | **0/30** |
| `InitB 6 7`, `InitB 7 7`, `InitB 10 7` (0x91, 0x92, 0xbd) | 1, 1, 1 | **0/30** |
| `InitB 10 3` (par de 0xb2, MS1) | 1 | **0/30** |
| `View` otra vez | 1 | — |

Estado de la tabla en el arnés (`run3`): los 30 nombres **sí** están
(`00:010 01:011 02:012 03:020 04:021 05:028 06:029 07:02c 08:02d 09:030 10:031 11:038 12:039 13:040
14:060 15:061 16:068 17:06c 18:062 19:063 20:090 21:091 22:092 23:0a0 24:0b1 25:0b2 26:0b3 27:0b8
28:0bc 29:0bd`), y **todos los `handle`/`status` a 0** ⇒ en el arnés faltan **30/30** (en la cámara
faltaban 26/30). `OM`/`+0x10` quedan como estaban.

**Código del fallo**: llamando por símbolo a la **misma** función que usa el comando
(`FlashLib::CreateSector32` 0x2B7080, invocada desde 0x2B40C8):

```
CreateSector32(0x90, flag=0) -> ret=0x7 handle=0 id=0x90
CreateSector32(0x91, flag=0) -> ret=0x7 handle=0 id=0x91
CreateSector32(0x92, flag=0) -> ret=0x7 handle=0 id=0x92
CreateSector32(0xbd, flag=0) -> ret=0x7 handle=0 id=0xbd
GetErrorString(0x7) = "FBS_INVALID_PROCESS"      (tabla 0x7E9488, índice = código-1)
```

⇒ **0x07 = `FBS_INVALID_PROCESS`**, devuelto por la capa FBS/DFB, no por la consola: el comando llega,
llama y propaga; `InitB` devuelve **1 siempre** (0x2B5B5E) aunque la creación falle, así que la consola
**no informa** del error (sólo queda en el log de FBM).

## 4. Por qué no se crean y qué haría falta

- **No es falta de geometría ni estado de fábrica**: el nombre del sector ya está en la tabla
  (idx 20 = 0x90) y el par `(OM 4, media 7)` existe en 0x9D23FC, que es lo único que valida `InitB`
  (`GetUserIDFromOperationModeAndMediaID` 0x2B385C y `GetSectorHandleFromOperatioModeAndMediaID`
  0x2B3000; si no hay par, devuelven 0x10800010 y no se llega a crear).
- **El destino lo decide 0x9D23FC**, no el índice: `InitB` recorre las entradas de ese `(userID,
  mediaID)` y crea el `sector` que toque; el nombre que pasa a `CreateSector32` es el que ya ocupa la
  ranura (`ldr r0,[0xA3699C+0x14*idx]` en 0x2B40C2).
- **Falla en el almacén**: en el arnés el DFB no tiene dispositivo válido. `CreateSector_Body` exige
  `FlashLib` abierto (`byte 0xA36C78 != 0`, 0x2B6F90) y luego `0x2B1080 → 0x2A8750 (DFB CreateSector)`;
  éste sólo devuelve `0x1f/0x40/0x45/0x47/0x4b/0x4c/0x4f` (p.ej. `"not initialized yet:CreateSector()"`
  0x7DED34 → 0x4F), de modo que el **0x7 viene de una capa inferior** (accesores FBS 0x2B07xx/0x2B09xx
  y ABL). `/dev/nflasha4` **sólo** se emula con `NFLASH4=1` y una imagen de la partición
  (`scripts/gui/harness/shim/sonyshim.c:110-141`), y `run.build_initrd(nflash4=…)` no recibe ninguna en
  esta pasada (`pb_run_fbm.py`), así que el volumen no es escribible.
- **Para crearlo de verdad**: (1) un `nflasha4` válido y escribible (en el arnés, `NFLASH4=1` +
  imagen real de la partición; en la cámara, la tabla FBS con área libre); (2) el par `(OM, mediaID)`
  correcto — **0x90 ⇒ `InitB 4 7`**, no `InitB 0 7`; (3) tras crear, **reiniciar MPR**: 0xA3699C es un
  *snapshot* que rellena `FBM::Init` desde `MprIf::Create` (0x2B484E), y `InitB` sí escribe la tabla,
  pero un arranque nuevo vuelve a decidir con `CheckExistSector` (0x2B8B48, exigido `0x45`).
- **`SetSMI` no sirve como creación**: 0x2B208C sólo escribe `+0,+4,+8,+0xC` para `idx<=0x1D`
  (0x2B20A0–0x2B20B8) sin llamar a FlashLib ni validar el handle; un `handle!=0` así es falso y la
  primera lectura devolvería `0x10100001` (entrada sin sector abierto).

## 5. Correcciones y límites

1. **Corrige `reports/film-pb-1-sub-tabla-readers-20261126.md` §6.1**: la tabla no está en `.rodata`
   `0x7E8014..0x7E8060` ni empareja «`View` con 0x2B59CA por proximidad»: está en `.data`
   **0x7E7FAC–0x7E8108** (29 × 12 B, la reubica el *loader* por `.rel.dyn`) y el emparejamiento
   nombre↔handler de este informe es exacto. Además `0x2B208C` (`SetSectorManagerInfo`) **no** es «la API
   de consola de SetSMI»: es a la vez la API interna y el destino del comando.
2. **Corrige `reports/film-pb-1-sub-logs-20261127.md` §3-bis**: «consola del monitor de MPR» no es la
   consola serie; el monitor lee de un anillo en memoria (0x683C64–0x683CB4). La consola serie sólo
   recibe la salida que el propio invitado escribe en `/dev/console` (aquí, la del shim).
3. **`MediaID=7` no es la tarjeta**: la tabla de nombres de 0x2B21AC (0x7E6364) da 7 = `USB`; la tarjeta
   es **3 = MS1** (y 4 = MS2). En la tabla estática, 0xb2 (el que la cámara sí tenía, handle 5) es
   `(user 35, media 3, OM 10)`.
4. **Límite de la medición**: el `argc` correcto se dedujo del código (0x6822F8 pasa `argc` tal cual) y se
   comprobó por contraste: con `argc` sin el nombre del módulo (`run0`) `InitB` devuelve **0** (rama de
   ayuda) y con el bueno (`run3`) devuelve **1** y ejecuta. `flag=0` en `CreateSector32` es una elección
   (`FBS_MOVEFLAG`); no se ha probado otro valor. No se ha probado `NFLASH4=1` por no haber imagen de la
   partición a mano.

## 6. Reproducción

```sh
# compila el shim y lanza el perfil nuevo `fbm` (PBINJECT=25; corta al «[FBMC] FIN»)
sh reports/evidence/film-pb-1-sub-consola-fbm-20261127/comando.sh
# consola completa de la pasada buena y contraste
grep -a FBMC reports/evidence/film-pb-1-sub-consola-fbm-20261127/run3/consola.log
grep -a FBMC reports/evidence/film-pb-1-sub-consola-fbm-20261127/run0/consola.log   # argc erróneo: -> 0
# volcado estático de la tabla de comandos
python3 reports/evidence/film-pb-1-sub-consola-fbm-20261127/evidencia/dump_tabla.py
```

Evidencia: `reports/evidence/film-pb-1-sub-consola-fbm-20261127/` (`sonyshim-fbm.c`, `comando.sh`,
`pb_run_fbm.py`, `im_pb.sh`, `run0|run2|run3/consola.log`, `evidencia/tabla-comandos-fbm.txt`,
`evidencia/initb-cadena-y-tablas.txt`).
