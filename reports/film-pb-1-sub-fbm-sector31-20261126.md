# FILM-PB-1 · sub-encargo FBM: parche de `libmpr.so` que crea el sector `0x31` (probado en el arnés)

**Fecha:** 2026-11-26 · **Evidencia:** `reports/evidence/film-pb-1-sub-fbm-create-20261126/` ·
**Binario:** fw 3.21, `libmpr.so` sha256 `9a74a3bb…` ·
**Parche final (v3):** `build/cfw_fbm_sector31_v3/libmpr.so`, sha256 **`9be3731213a776dbc5934e7f37d9a7a4ef50480e35b09a4e8b1d0727e0b00640`**, 68 B distintos.
Cámara no usada; sólo QEMU. No se ha construido ningún `.dat` (§9).

## Resumen (20 líneas)

1. `FlashLib::CreateSector32` = **`0x2B7080`** (`_ZN8FlashLib14CreateSector32Em12FBS_MOVEFLAGPmS1_`, dynsym #666 → `0x2b7081`): thunk `push{r7,lr}/pop{r7,lr}/b.w 0x11E000` (PLT ARM). Firma real, medida: `(fileType, flag, &handleOut, &sectorOut)`; `flag` no se lee en todo `CreateSector_Body 0x2B6F80`. `WriteBaseData` la llama en `0x2B40C8` con `r1=0`, `r2=&[r7]`, `r3=&[r7,#4]`.
2. `BackupMgr::WriteBaseData 0x2B4030` (r0=OM, r1=mediaID) **no sirve como atajo**: aborta en `0x2B4072` si `GetSectorHandleFromOperatioModeAndMediaID 0x2B3000` falla, y `0x2B3000` exige `[0x9D23FC fila +0x10] != 0`; las 37 filas lo tienen a 0.
3. La alta a mano que sí vale es la de `0x2B40DA..0x2B40EA`: `[+0]=*r3` (sector), `[+4]=*r2` (handle), `[+8]=1`, `[+0xC]=OM`. `SetSectorManagerTable 0x2B45A8` **no** vale para un sector vacío (saca `+0xC/+0x10` de `ReadFirstPackData`).
4. Parche v3 (68 B, tamaño y cabeceras intactos): gancho `0x7126E6` `a2 f7 9b f0` (`bl 0x2B4820`) → **`28 f2 8b fc`** (`bl 0x93B000`); cueva de **0x40 B** en `0x93B000` (`00 00 …` → ver §3). `0x7126EA` **no se toca**.
5. La cueva: `FBM::Init` → cero los 2 slots de salida (como `0x2B4042..0x2B404A`) → `r4 = PC + 0xFBA64 = &0xA3699C[10]` (PC-relativo, **sin literales**) → si `[r4+4] != 0` sale (idempotente) → `CreateSector32(0x31,0,&h,&id)` → si `ret != 0` sale sin escribir → escribe `[+0]=*r3 · [+4]=*r2 · [+8]=1 · [+0xC]=6`.
6. **La v2 (con literal `0x00A36A64`) revienta**: `.rodata` no tiene relocaciones y la VA de enlace no se reubica; el arnés lo cazó con SIGSEGV en `0x93B010`, `addr=0xA36A68`, base real `0xAE3E5000` (§4). Por eso la v3 calcula la dirección desde el PC.
7. Auditoría (`auditoria-parche-v3.txt`): 132 021 relocaciones revisadas (ninguna en los 68 B), ningún `ldr/adr` pc-relativo hacia la cueva, ningún puntero a ella, 5 `PT_*` y 25 secciones idénticas, diff exacto.
8. Pre-vuelo en **Unicorn** (`emulacion-cueva-v3.txt`): con `ret=0, h=3, id=0x31` deja `idx10 = {0x31, 3, 1, om6}` y vuelve a `0x7126EA`; con `ret=0x7` no escribe nada; con `h=0x55` copia `0x55` (no hardcodea).
9. **Arnés, sin parche** (`run-r0`): `0xA3699C` = 30 sectores, **1** con handle (`idx 23 = 0xA0/h1/om9`), `CheckExistSector(0x31) = 0x48`, `BkRead/ReadFirstPackData(0x21,3) = 0x10100001` (y `(0x04,3)` igual).
10. **Arnés, con parche v3** (`run-r1v3`): `nh=2` (`0x31`, `0xA0`), `idx 10 sector=0x0031 handle=0x00000002 valido=1 om=6`, `CheckExistSector(0x31) = 0x45`, `ReadFirstPackData(0x21,3) = 0x10100003` y `(0x04,3) = 0x10100003`. **Criterio cumplido.**
11. Imagen `nflasha4` tras el parche: **394 B** distintos en `0x9D400..0x9D7FF` (sectores 1258-1259), página de control nueva con la entrada `31 00 00 00 00 05 07 ff`, seq `0x2C2`; sha256 `609afa73…`, **idéntico** al que obtuvo el otro agente por la ruta `InitB 6 3` + `CreateSector32` a mano.
12. **Segundo arranque con la imagen ya escrita**: con `libmpr` de fábrica (`run-r2`) `FBM::Init` **no** registra la entrada (`CheckExistSector(0x31)` vuelve a **0x48**, `nh=1`, `ReadFirstPackData = 0x10100001`): **el efecto no persiste solo**. Con el parche (`run-r2b`) vuelve a funcionar (`nh=2`, `0x10100003`), y el DFB escribe **otra** página de control de 1024 B en `0x3D800` (no toca `0x9D400`): no duplica la entrada, pero **sí rota página en cada arranque**.
13. Contenido del sector: **en el mismo arranque no hace falta** (sólo 394 B, la página de control) y `ReadFirstPackData` ya da `0x10100003`; para el reinicio **sí falta la página de datos base `0x380000`** que escribe `TermSectorData 0x2B4164` (lo que hace `WriteBaseData` y mi cueva no) — encaja con la medida del otro agente («sin la tercera el sector existe pero `+8=0`»). La reproducción real no se prueba aquí (§7).
14. Queda de cámara: (a) por qué `CheckExistSector` dice `0x48` con la página ya en la imagen —y si en la cámara pasa lo mismo, en cuyo caso el parche recrearía el sector en cada arranque—, (b) que la reproducción de vídeo deje de fallar.

## 1. `WriteBaseData` (0x2B4030), `CreateSector32` y lo que hace falta para crear

Desensamblado: `dis/dis-writebasedata-2b4030.txt`, `dis/dis-2b7080-create32.txt`,
`dis/dis-2b6f80-createsector-body.txt`, `dis/dis-2b3000.txt`, `dis/dis-2b2e54-getidx-from-userid.txt`,
`dis/dis-2b385c-getuseridfromoper.txt`, `dis/dis-2b45a8-setsmt.txt`.

`BackupMgr::WriteBaseData(r0 = operationMode, r1 = mediaID)` (0x2B4030):

| VA | qué hace |
|---|---|
| `0x2B403E..0x2B404A` | toma el mutex `0x9E6954` y **pone a cero `[r7]` y `[r7,#4]`** (los dos slots de salida) |
| `0x2B406A` | `0x2B3000(OM, mediaID, &handle)`; **aborta en `0x2B4072` si `ret != 0`** (código `0x10800010`, línea `0xF47`) |
| `0x2B4074/0x2B407C` | si `handle != 0` → `0x2B40EE` (`ChangeSectorRelocateReady`) y no crea |
| `0x2B4086` | `0x2B385C(OM, mediaID, &userID)` |
| `0x2B40A0` | `0x2B2E54(userID, mediaID, &idx)` (escribe **1 byte**) |
| `0x2B40B0..0x2B40C8` | `r0 = [0xA3699C+0x14*idx]` (fileType **leído de la tabla**), `r1 = 0` (flag), `r2 = &[r7]`, `r3 = &[r7,#4]`, **`blx 0x11FA5C`** (PLT de `CreateSector32`) |
| `0x2B40CC` | `cbnz r0, 0x2B4110` → si falla, no escribe la entrada |
| `0x2B40DA..0x2B40EA` | `[+0] = [r7,#4]` (**out r3 = sector**), `[+4] = [r7]` (**out r2 = handle**), `[+8] = 1`, `[+0xC] = r5` (OM) |
| `0x2B4124..0x2B4130` | `pthread_mutex_unlock(0x9E6954)` y `0x2B3F7C(OM, mediaID)` (callbacks de `0x9D23FC`) |

`FlashLib::CreateSector_Body 0x2B6F80`: si `[0xA36C78]==0` devuelve `-1`; `idCheckFlag/baseLen/maxLen`
salen de `m_fileTypeSizeInfo 0x9D2794` (para `0x31`: `1`, `0x9D800`, `0xDC800`); llama
`0x2B1080 → DvdFlashBackupLib::CreateSector 0x2A8750`; con `ret==0` devuelve `*sectorOut = GetID(...)`
y `*handleOut` = índice interno. **Tamaño**: no se pide por argumento, lo pone la tabla.

`SetSectorManagerTable 0x2B45A8` no sirve para un sector recién creado (usa `0x2B3948` para `+0xC/+0x10`).
`BackupMgr::InitBackupData 0x2B43F0 → WriteBaseData` tampoco (guarda `+0x10` de `0x9D23FC`).

## 2. `ReadFirstPackData` (0x2B39B8): de dónde sale `0x10100001`

```
2b39d8  r0 = userID (r5) · r1 = mediaID (r4) · bl 0x2B2F48(GetIdx)   -> idx en [r7,#0xf]
2b39e2  r1 = 0x14*idx ; r0 = 0xA3699C (literal de 0x2B39E8) ; r2 = [r0+r1+4] = handle
2b39ee  cbz r2, 0x2B3A28                       <-- sin handle: NO hay sector abierto
2b3a28  ldr.w sb,[pc,#0x28]  -> literal en 0x2B3A54 = 0x01010001  <-- el código que se devuelve
```
Con handle: `0x2B3A1E r3=[r7,#0x30]` y `0x2B3A20 bl 0x2B3948` (camino profundo) → devuelve
**`0x10100003`** (no está como literal en `libmpr`; `FlashLib::GetErrorString 0x2B6114` sólo nombra
los códigos 1..`0x55`, así que este sale «unknown»).

## 3. El parche v3, byte a byte

`parche_fbm31_v3.py` → `auditoria-parche-v3.txt`:

```
antes   0x7126E6  a2 f7 9b f0   bl 0x2B4820   (FBM::Init dentro de MprIf::Create 0x712530)
despues 0x7126E6  28 f2 8b fc   bl 0x93B000
        0x7126EA  96 f5 bb f8   bl 0x4A8864   <-- NO se toca

antes   0x93B000  00 x64
despues 0x93B000  10 b5              push {r4, lr}
        0x93B002  79 f5 0d f4        bl 0x2B4820            FBM::Init (el efecto original)
        0x93B006  82 b0              sub sp, #8
        0x93B008  00 20              movs r0, #0
        0x93B00A  00 90              str r0, [sp]           } cero los 2 slots de salida,
        0x93B00C  01 90              str r0, [sp, #4]       } como 0x2B4042..0x2B404A
        0x93B00E  7c 46              mov r4, pc             ; r4 = C+0x12  (C = base+0x93B000)
        0x93B010  4b f6 52 21        movw r1, #0xBA52
        0x93B014  c0 f2 0f 01        movt r1, #0x000F
        0x93B018  0c 44              add r4, r1             ; r4 = C+0xFBA64 = &0xA3699C[10]
        0x93B01A  60 68              ldr r0, [r4, #4]       ; handle actual
        0x93B01C  70 b9              cbnz r0, 0x93B03C      ; idempotente
        0x93B01E  31 20              movs r0, #0x31         ; fileType
        0x93B020  00 21              movs r1, #0
        0x93B022  6a 46              mov r2, sp             ; &handleOut
        0x93B024  01 ab              add r3, sp, #4         ; &sectorOut
        0x93B026  7c f5 2b f0        bl 0x2B7080            CreateSector32(0x31,0,&h,&id)
        0x93B02A  38 b9              cbnz r0, 0x93B03C      ; si falla NO se toca la tabla
        0x93B02C  00 99              ldr r1, [sp]           ; handle
        0x93B02E  01 9a              ldr r2, [sp, #4]       ; sector
        0x93B030  22 60              str r2, [r4]           ; [+0] = sector
        0x93B032  61 60              str r1, [r4, #4]       ; [+4] = handle
        0x93B034  01 21              movs r1, #1
        0x93B036  a1 60              str r1, [r4, #8]       ; [+8] = 1
        0x93B038  06 21              movs r1, #6
        0x93B03A  e1 60              str r1, [r4, #0xC]     ; [+0xC] = OM 6
        0x93B03C  02 b0              add sp, #8
        0x93B03E  10 bd              pop {r4, pc}           ; vuelve a 0x7126EA (lr del gancho)
```

Por qué PC-relativo: `0xFBA64 = (0xA3699C + 0x14*10) - 0x93B000` y `mov r4,pc` en `0x93B00E` lee
`C+0x12`, de ahí `0xBA52 = 0xFBA64 - 0x12`. No hay ningún literal con VA dentro de la cueva
(la v2 sí lo tenía y reventó, §4).

Comprobaciones que pasa la auditoría: sha256 del original; bytes de gancho y de `0x7126EA`;
los 28 instrucciones de la cueva decodifican exactamente lo previsto (capstone 5); gancho en `.text`
y cueva en `.rodata`, ambos en el `PT_LOAD` R+X (`off=0 vaddr=0 filesz=memsz=0x9BB1C8 flags=5`),
VA == offset; **132 021** entradas `.rel.dyn`+`.rel.plt` revisadas, ninguna con `r_offset` en los
68 B; ningún `ldr/ldr.w/adr` pc-relativo que lea `0x93B000..0x93B03F`; ningún u32 del fichero con
un puntero a ese rango (el único candidato, `0x495390 = 0x0093B014`, es una ventana de 4 B a caballo
de dos instrucciones y el auditor lo descarta por eso); diff exacto (68 B escritos, 64 con valor
nuevo, 4 ya eran `00`), tamaño `10 321 204` B, cabecera + 5 `PT_*` + 25 secciones idénticas.

## 4. La v2 y su SIGSEGV (por qué el literal absoluto no vale)

La v2 (`auditoria-parche-v2.txt`, ya descartada) llevaba `ldr r4,[pc,#0x28]` con el literal
`0x00A36A64` en `0x93B038`. Medido en el arnés (`run-v2-crash/consola.log`):

```
NF4: [shim] FBMTAB libmpr base=0xae3e5000 tabla=0xaee1b99c gancho=28 f2 8b fc cueva=10 b5 79 f5 0d f4 82 46
[shim] --- pila (sig 11 tid 222 THREAD_INFRA1) pc/lr:
[shim]   raw pc=aed20010 lr=ae9a0c95 addr=00a36a68 r0=00000000 r1=0000000b r2=00001d01
[shim]   aed20010 /usr/lib/libmpr.so+0x93b010     <- ldr r0,[r4,#4] de la cueva
[shim]   ae9a0c95 /usr/lib/libmpr.so+0x5bbc95
[shim]   aeaf76eb /usr/lib/libmpr.so+0x7126eb     <- vuelta del bl del gancho
```
`addr = 0xA36A68` = `0xA3699C+0xC8+4`: el literal quedó con la VA de enlace porque `.rodata` no
tiene relocaciones (`reloc: NINGUNA` en el rango). Con la base real `0xAE3E5000` la tabla está en
`0xAEE1B99C`, así que `0xA36A64` no está mapeada. La v3 lo arregla calculando la dirección con el PC.

## 5. Pre-vuelo en Unicorn (sin QEMU)

`emula_cueva.py build/cfw_fbm_sector31_v3/libmpr.so` → `emulacion-cueva-v3.txt`. Mapea el `.so`
parcheado con base `0xAE3E5000`, PC = `base+0x93B000`, LR = `(base+0x7126EA)|1`, intercepta
`FBM::Init` y `CreateSector32` (Cortex-A15/Thumb-2):

```
== CreateSector32 -> 0, handle 3, sector 0x31 ==
   llamadas : FBM::Init · CreateSector32(fileType=0x31, flag=0x0, p2=..., p3=...)
   PC final : 0x7126ea (vuelve a 0x7126EA)
   idx10    : sector=0x0031 handle=0x00000003 valido=1 om=6 b10=0x0
   otras entradas tocadas: NINGUNA
== CreateSector32 -> 0x7 ==   idx10: 0/0/0/0    (no escribe nada)
== CreateSector32 -> 0, handle 0x55 ==  idx10: handle=0x00000055
VEREDICTO: OK
```

## 6. Medición en el arnés

Arnés: `fbm_run.py` (copia propia de `run.py`/`live.py`), overlay `cam/usr/lib/sonyshim.so`
(+ `cam/usr/lib/libmpr.so` en las pasadas con parche), `/dev/nflasha4` emulado desde
`analysis/camera-dumps/nand-20261020/dev_nflasha4.bin`, `SHIMENV` = `CADENA` de
`scripts/gui/harness/estable.sh` + `WAIT=120 FBMTAB=1` **+ `NFLASH4=<sha256[:12]>`**.
El `NFLASH4` es imprescindible (`scripts/gui/harness/shim/sonyshim.c:111`): sin él no hay
`/dev/nflasha4` y `CreateSector32` devuelve `0x7`; por eso la 1ª iteración midió `nh=0`.
Tabla completa y códigos: `medidas.txt`.

| pasada | libmpr | `0xA3699C` | `CheckExistSector(0x31)` | `ReadFirstPackData` (0x21,3 / 0x04,3) | imagen `nflasha4` |
|---|---|---|---|---|---|
| `run-r0` | de fábrica | `llena=30`, **`nh=1`** (`idx23 0xA0/h1/om9`), idx10 a cero | `0x48` | `0x10100001` / `0x10100001` | 0 B |
| `run-r1v3` | **v3** | `llena=30`, **`nh=2`** (`0x31`,`0xA0`), `idx10 sector=0x0031 handle=2 valido=1 om=6` | **`0x45`** | **`0x10100003`** / **`0x10100003`** | **+394 B** en `0x9D400..0x9D7FF` |
| `run-r2` | de fábrica, imagen de `run-r1v3` | `llena=30`, **`nh=1`**, idx10 a cero | `0x48` | `0x10100001` / `0x10100001` | +766 B (sectores 236/237/1514/1515), `0x9D400` intacto |
| `run-r2b` | **v3**, imagen de `run-r1v3` | `nh=2`, `idx10 handle=2 valido=1 om=6` | `0x45` | `0x10100003` / `0x10100003` | 6 sectores: 236/237 **492/493** 1514/1515 (`0x9D400` intacto) |
| `run-r2c` | **v3**, igual, con la imagen extraída | `nh=2`, `idx10 handle=2` | `0x45` | `0x10100003` | 1160 B: 236/237 492/493 1514/1515 |

La imagen escrita por `run-r1v3` (`run-r1v3/nflash4.img`, 10 485 760 B,
sha256 `609afa7308d10b9738e1677e48a67b9b040a42d6f4999df85ef1c8a3271ded9b`) contiene **una página de
control nueva** en `0x9D400` (`run-r1v3/pagina-9D400-antes.bin` / `-despues.bin`):

```
0x09d400  00 00 00 00 4a 00 4a 00 81 00 00 00 01 01 03 ff   cabecera 0x4a y entradas de 8 B
0x09d410  a0 00 00 00 00 01 01 ff 31 00 00 00 00 05 07 ff   <- 0x31 (la nueva) 0x05 0x07
0x09d7f8  c2 23 00 00 c2 02 00 00 8f d5 06 ac               seq 0x2C2 y cks
```
Es **byte a byte la misma** que la que obtuvo el otro agente
(`reports/evidence/fbm-initb-6-3-nflasha4-20261126/run5`, sha256 `609afa73…`) por la ruta
`InitB 6 3` + `CreateSector32` manual: dos caminos distintos, mismo NAND.

En `run-r2c` la página nueva va a **`0x3D800`** (sectores 492/493) con las mismas entradas
`81`, `a0`, `31` (`run-r2c/sector-492.bin`), y `0x9D400` **no se reescribe**: el DFB rota de
página de control en vez de duplicar la entrada. 236/237 y 1514/1515 son copias sin `0x31`
(páginas normales de arranque: también salen en `run-r2`, sin parche).

## 7. ¿Necesita contenido el sector? Lo que se ve

* **Dentro del mismo arranque no hace falta nada más**: `CreateSector32` + la entrada a mano bastan
  para que `ReadFirstPackData` pase de `0x10100001` a `0x10100003` (`run-r1v3`). En toda la pasada
  sólo se escriben **394 B**, y son la página de control del DFB en `0x9D400`, no datos del sector.
* **Para que sobreviva a un reinicio, sí falta algo**: `run-r2` (libmpr de fábrica, imagen con el
  sector) vuelve a `CheckExistSector(0x31)=0x48` y `0x10100001`. La explicación la da la medida del
  otro agente en `reports/evidence/fbm-initb-6-3-nflasha4-20261126/README.md` (fila
  `FILM-PB-1-SUB-FBM31` de `docs/PENDIENTES.md`): su ruta de consola escribe **tres** páginas
  (`0x9D400` tabla, `0xBD780` asignación y **`0x380000` datos base**) y «sin la tercera el sector
  existe pero `+8=0`». `WriteBaseData` escribe esa tercera con `FlashLib::TermSectorData(handle)`
  en `0x2B4164`; **mi cueva no la llama** (se queda en `CreateSector32` + entrada), y eso encaja con
  lo medido: el sector existe para el DFB en ese arranque (`0x45`) pero no para el del siguiente.
* La reproducción real no se prueba aquí: el arnés no reproduce vídeo; el otro agente clasifica
  `0x10100003` como tolerado en sus `run3`/`run6`. Es lo único que hay, y viene de su evidencia.

## 8. Qué NO está probado

* **Cámara**: nada. Ni `CreateSector32` ni el parche se han ejecutado en la cámara física.
* **Persistencia**: en el arnés el sector creado **no** lo ve `FBM::Init` del arranque siguiente
  (`CheckExistSector = 0x48` con la página ya en la imagen, `run-r2`), mientras que en el mismo
  arranque tras crearlo sí (`0x45`). Con el parche la cámara funcionaría (crea en cada arranque),
  pero **rotando una página de control de 1 KiB por arranque**. Si en la cámara `CheckExistSector`
  devuelve `0x45` con el sector ya presente, no habría rotación; eso **no** se puede decidir desde
  el arnés y es la primera medida a hacer en cámara.
* **Los 4 handles de la cámara**: el arnés sólo abre `0xA0` (la cámara tiene `0x30`, `0x62`, `0xA0`,
  `0xB2`). Es una diferencia de emulación del FBS, no del parche, y no se ha explicado.
* **`OpenSector32(0x31,0)`** devuelve `0x4` (y `GetSectorInfo(0) = 0x10100009`) incluso en la pasada
  buena; quien abre el sector es `CreateSector32`. No se ha investigado más.

## 9. Paquete y auditoría

No se ha construido ningún `.dat`: el entregable es el `.so` parcheado y su prueba, así que
`scripts/gui/audit_package_nflasha15.py` **no aplica**. La auditoría del ELF es
`parche_fbm31_v3.py` → `auditoria-parche-v3.txt` (§3) y la del tramo de código, `emula_cueva.py`
→ `emulacion-cueva-v3.txt` (§5).

## 10. Siguiente paso

1. Cámara: leer `base+0xA3699C` con la imagen que ya tiene el sector (`InitB 6 3` una vez) y ver si
   `CheckExistSector(0x31)` da `0x45`; si da `0x48`, el parche recreará el sector cada arranque.
2. Cámara: con el `libmpr.so` parcheado (sha256 `9be3731…`), reproducir el vídeo que falla y leer
   `0xA3699C`: `idx 10` debe salir `sector=0x31 handle!=0 valido=1 om=6`.
3. Persistencia y rotación: añadir a la cueva `FlashLib::TermSectorData(handle)` (`0x2B4164`, con
   `r0 = handle`) después de escribir la entrada —es el paso que `WriteBaseData` da en `0x2B4164` y
   el que crearía la página de datos base `0x380000`— y volver a medir `run-r2` con esa imagen.
   Si funciona, `CheckExistSector(0x31)` daría `0x45` en el 2º arranque y el sector se crearía **una
   sola vez**. No se ha hecho aquí por tiempo; es la mejora obvia y con la evidencia a favor arriba.
