# FILM-PB-1 / sub-executility — Quién ejecuta `FlashLib::Init`, qué es la "utilidad 1" y de qué depende

26-11-2026 · Binario: `firmware/extracted/fw321/…/dev/nflasha15_unpacked_unpacked/lib/libmpr.so`
(fw 3.21, 10 321 204 B) + `libmprctrl.so`, `libbackup.so`, `libtestcmd*.so`, `libIMDB.so`,
`scenario/MPR_SCN_FLASH_BACKUP_INIT.so`, `scenario/MPR_SCN_EXEC_FACTORY_MODE.so`, y contraste con
`a6300-fw201` y `a7s-fw320`. **Direcciones = VA del ELF (base 0)**; desensamblado propio
(capstone Thumb-2, PLT resuelto por orden de `.rel.plt`). Evidencia:
[reports/evidence/film-pb-1-sub-executility-20261126/](evidence/film-pb-1-sub-executility-20261126/)
(índice en su `INDEX.md`). **Sólo análisis estático: no se ejecutó firmware ni se tocó la cámara.**

Continúa [sub-backup-store-20261126](film-pb-1-sub-backup-store-20261126.md) y **corrige su punto
[7. NO_VERIFICADO] nº 1** (ver §2.4).

---

## 0. Resumen (17 líneas)

1. `0x722BCC` = `MprIf::ExecMprUtility(MPR::UtilityCmdId,void*)`, thunk **exportado** de 40 B: registra
   `MprIfLog::AsyncApiCall<unsigned short>(0x40000005, 0, id)` y salta con `b.w` a `0x4500CC`.
2. `0x4500CC` = implementación local: mutex del *api id*, comprobación de sesión (`[this+4]->vt[0x18]`),
   petición de 9 B `{u32 id; u8 conDato; u8 dato[4]}` hacia `0x436408`; devuelve **9** si la sesión no vive.
3. `0x436408` exige `[obj+0x1F0]==2`, valida `id ≤ 4` con máscaras (`0x16` → ids **1,2,4 sin dato**;
   `0x9` → ids **0,3 con dato**) y reparte la orden entre **5** gestores de medio.
4. **La utilidad 1 es `init`**: el parser de consola `MprIfMcmd::ExecMprUtility` (`0x72DD98`) mapea
   `quickFormat→0`, **`init→1`**, `fullFormat→3`, `check→4` y `flush→`su argumento.
5. Quien la pide: los escenarios `MPR_SCN_FLASH_BACKUP_INIT.so` (`0x6DE`, `r1=1,r2=0`) y
   `MPR_SCN_EXEC_FACTORY_MODE.so` (`0x79E`), lanzados por `libtestcmd_scn.so`
   (`dlopen("/usr/scenario/<n>.so")` + `dlsym("scenario_run")`), y el comando de consola
   `MPR FUNCRECOVERY ExecMprUtility init` (`0x72DE24`).
6. **En el arranque no la pide nadie**: ni `init`, ni `im.elf`, ni `libObj`, ni `libmpr`.
7. **CORRECCIÓN al informe del 26-11**: `FlashLib::Init` **sí tiene llamante** — `0x7126E2` (`blx` a su
   stub PLT `0x11DFE8`), en la misma cadena que 6 bytes después llama a `BackupMgr::Init` (`0x7126E6`).
8. Cadena de arranque completa: IMDB → `libmprctrl.so`/`InfraMprCtrl_Init` → `MprCtrl::Init` →
   `MprIf::Create` (`0x71CC20`) → `0x712530` → **`FlashLib::Init`** → `BackupMgr::Init`.
9. El "sin llamante" anterior era un **fallo de escaneo**: los `blx <stub PLT>` no se enmascaraban a
   palabra (`Align(PC,4)+imm`) y desaparecían del recuento (bug también en `elftool.py calls()`).
   Corregido: `FlashLib::Init` tiene exactamente 1 llamante en a6000, a6300 y a7s.
10. Por tanto **la utilidad 1 no es la vía de arranque** y su ausencia no explica el fallo; `m_enableFlag`
    no depende de ella.
11. `m_enableFlag` se pone a **1 al principio** de `FlashLib::Init`, desde `GetEepData(0x003C00BF)` =
    `Backup_read` (IPC al servicio BKUP de `libbackup.so`): bit0=0 → 1; bit0=1 → **0**; lectura fallida → 1.
12. Si el flag quedara 0: todo `FlashLib*` devuelve error, `CheckExistSector` → `-1`, los 30 *readers*
    quedan con handle 0, `ReadFirstPackData` → `0x10100001` e `IsNeedRepairFlashBackup` → 1.
13. Se pierden los índices FBS de AVCHD/M2PS/DCF/MP4 (una sola ranura: `0x30/0x31`, `0x62`, `0xb2`).
    XAVC/CSVC (`0x80-0x83`) y FSYS (`0x70`) **no** usan FBS.
14. Modo de arranque: en frío se ejecuta la cadena; en caliente (WBI) no se ejecuta nada y el estado
    viene de la instantánea de RAM. La **ruta** de la utilidad no depende del modo.
15. Dependencias reales: `/dev/nflasha4` \| `/dev/cnflasha4` + `/sys/block/nflasha0/nflasha0p4/start`;
    el servicio BKUP; y para la vía manual el fichero `/usr/scenario/MPR_SCN_FLASH_BACKUP_INIT.so`.
    **Nada de `/setting` ni de variables de entorno del proceso.**
16. Comprobación en cámara: base de `libmpr` por `/proc/$(pidof im.elf)/maps`, leer `base+0xA36C78` (1 B)
    y `base+0xA3699C` (0x258 B); `grep` de `[DFB]not initialized yet`, `[DFB]call api (DvdFlashBackupLib::Init) result:blockNum[…]` (`0x7E3CCE`),
    `[FBM]Init()`, `need repair FlashBackup`, `[NBL] GetEepData()`.
17. Prueba discriminante: lanzar la utilidad 1 desde consola; si el flag y la tabla no cambian, queda
    demostrado que **la utilidad 1 no toca FlashLib**.

---

## 1. Traza completa de la utilidad 1 (pregunta 1)

### 1.1 `0x722BCC` — `MprIf::ExecMprUtility(MPR::UtilityCmdId, void*)`

Símbolo real del `.dynsym` (`_ZN5MprIf14ExecMprUtilityEN3MPR12UtilityCmdIdEPv`, 40 B, GLOBAL/FUNC);
[01-thunk-722bcc.txt](evidence/film-pb-1-sub-executility-20261126/01-thunk-722bcc.txt):

```
00722bcc  push.w {r4,r5,r6,r7,r8,lr}
00722bd0  mov r4,r1            ; cmdId
00722bd2  mov r6,r0            ; this
00722bd4  mov r5,r2            ; arg
00722bd6  movs r1,#0
00722bd8  uxth r2,r4
00722bdc  ldr r0,=0x40000005   ; id de log del API
00722bde  blx MprIfLog::AsyncApiCall<unsigned short>
00722be2  ldr r0,[r6]          ; this->m_pImpl
00722be4  mov r1,r4
00722be6  mov r2,r5
00722be8  pop.w {r4,r5,r6,r7,r8,lr}
00722bec  b.w 0x4500cc         ; tail-call a la implementación local
```

Es un **forwarder con traza**: la orden queda registrada en `MprIfLog` (id `0x40000005`) y el trabajo lo
hace `0x4500CC`. No hay tabla de utilidades ni `switch` aquí.

### 1.2 `0x4500CC` — implementación (sin nombre en `.dynsym`)

[02-impl-4500cc.txt](evidence/film-pb-1-sub-executility-20261126/02-impl-4500cc.txt):

```
004500cc  push {r4,r5,r6,r7,lr}; sub sp,#0x14
004500d4  ldr r1,=0x40000005 ; bl 0x449D84      ; lock del api id (r4=this, r5=cmd, r6=arg)
004500de  ldr r0,[r4,#4]                        ; this->m_pIf
004500e2  ldr r3,[r0]     ; ldr r3,[r3,#0x18]   ; método virtual 6 de la interfaz
004500e6  blx r3                                ;  != 0  -> sesión/medio vivo
004500e8  cbnz r0,0x4500FE
004500ea  MprIfLog::AsyncApiDone(0x40000005, 9) ; si no vive: traza "done 9"
004500f2  unlock; 00450128 mov r0,r5 (=9); return 9
004500fe  str r5,[r7,#4]                        ; petición: +0 = cmdId
00450100  cbz r6, ...                           ;  +4 = 1 y +5..+8 = 4 B del arg, o +4 = 0
00450118  ldr r0,[r4,#4] ; bl 0x436408          ; entrega y recoge estado
00450122  unlock ; return estado
```

La petición es de **9 bytes** (`0x436408` sólo lee `[+0]` y `[+4]`, y como mucho 4 B de `[+5]`). El
resultado **9** es el código "API no disponible" que ya está documentado en
[sub-logs-20261127](film-pb-1-sub-logs-20261127.md).

### 1.3 `0x436408` — despacho real (capa de medios)

[03-media-dispatch-436408.txt](evidence/film-pb-1-sub-executility-20261126/03-media-dispatch-436408.txt):

```
00436414  ldr r3,[r0,#0x1f0] ; cmp r3,#2 ; bne -> 0x436572 (return sin hacer nada)
0043641e  ldr r3,[r1]        ; cmdId
00436420  cmp r3,#4          ; bhi -> 0x436576 (error)
00436426  movs r2,#1 ; lsls r2,r3
0043642a  tst.w r2,#0x16     ; ids 1,2,4
0043642e  bne 0x436442       ;   exigen [+4]==0
00436430  tst.w r2,#0x9      ; ids 0,3
00436434  beq 0x436576       ;   exigen [+4]!=0  (el "5C E0 C5 79")
00436466  bucle r4=0..4: ldr r0,[r6,#0x1ec]; bl 0x4478C0(...,r4,&out)   ; 5 gestores
0043649e  bucle: bl 0x447840(...,h[i])                                   ; abre/valida
004364ce  tbb [pc,r3]        ; salto por id -> trabajo por comando
```

Las **5** iteraciones son la clave de por qué "quickFormat/fullFormat" llevan un paquete de 4 B y
"init/flush/check" no: el `id 1` es la orden **sin argumento** que inicializa cada medio.

### 1.4 Qué utilidad es la 1 — dos pruebas independientes

| Prueba | Evidencia |
|---|---|
| Parser de consola `MprIfMcmd::ExecMprUtility` (`0x72DD98`): `strcmp` con `"quickFormat"`→`r1=0`, `"fullFormat"`→`r1=3`, **`"init"`→`movs r1,#1`** (`0x72DDFE`), `"check"`→`r1=4` (`0x72DE02`); y el error imprime `"ex) MPR FUNCRECOVERY ExecMprUtility [commandId"` (`0x92CA61`) | [04-console-parser-72dd98.txt](evidence/film-pb-1-sub-executility-20261126/04-console-parser-72dd98.txt) |
| Máscaras de argumento en `0x436408`: `0x16` = bits 1,2,4 (sin dato) y `0x9` = bits 0,3 (con dato). El parser pasa el paquete `5C E0 C5 79` **sólo** para 0 y 3 | [03](evidence/film-pb-1-sub-executility-20261126/03-media-dispatch-436408.txt) |

⇒ `MPR::UtilityCmdId 1 = "init"` (inicialización del subsistema de medios por la vía de la API).

---

## 2. Quién invoca `ExecMprUtility(1)` en el arranque (pregunta 2)

### 2.1 Lo que hay: dos escenarios y un comando de consola. Nada más.

| Llamante | Sitio | Argumentos | Cómo se lanza |
|---|---|---|---|
| `MPR_SCN_FLASH_BACKUP_INIT.so` → `scenario_run` | `0x6DE` (stub PLT `0x5C0`) | `r1=1`, `r2=0` | `libtestcmd_scn.so` → `dlopen("/usr/scenario/MPR_SCN_FLASH_BACKUP_INIT.so")` + `dlsym("scenario_run")` |
| `MPR_SCN_EXEC_FACTORY_MODE.so` → `scenario_run` | `0x79E` (stub PLT `0x6DC`) | `r1=1`, `r2=0` | ídem, nombre `MPR_SCN_EXEC_FACTORY_MODE` |
| `MPR_SCN_INSTALL_MAP_DEMOMOVIE.so` | `0x5460` (stub PLT `0x29FC`) | — | ídem |
| `MprIfMcmd::ExecMprUtility` (grupo de consola `MPR`) | `0x72DE24` (stub PLT `0x11F134`) | id del subcomando | consola: `MPR FUNCRECOVERY ExecMprUtility init` |

[12-utilidad-1-quien-la-pide.txt](evidence/film-pb-1-sub-executility-20261126/12-utilidad-1-quien-la-pide.txt),
[08-scenario-run…](evidence/film-pb-1-sub-executility-20261126/08-scenario-run-MPR_SCN_FLASH_BACKUP_INIT.txt),
[09-testcmd-scn-open-dlopen.txt](evidence/film-pb-1-sub-executility-20261126/09-testcmd-scn-open-dlopen.txt).

El escenario, literalmente: `puts("MPR_FLASH_BACKUP_INIT Start")` →
`GetMprIfInstance()` → `printf("p_mprIf 0x%x")` → `puts("mp_mprIf->ExecMprUtility Start")` →
`ExecMprUtility(1,NULL)` → `puts("... End")`; si devuelve ≠0 imprime `"… End Err 0x%x"` y lo deja en
`buf[0]`. **La única condición** es `buf_size ≥ 4` (`0x6AE`); no mira `/setting`, ni ficheros, ni entorno.

### 2.2 No hay llamante en el arranque — y no hace falta

* `init` (ramdisk) lanza `im.elf`, que carga `/usr/lib/libObj.so`; ni `init`, ni `im.elf`, ni `libObj` importan
  `ExecMprUtility` (`grep` de `_ZN5MprIf14ExecMprUtility` en las 3 firmwares: sólo `libmpr.so` y los 3
  escenarios). Los bloques `99 02 15 01 01 0b 81 08 "MPR_SCN_FLASH_BACKUP_INIT"` que aparecen en
  `libObj.so`, `libsencore.so`, `libInfraMediaCommon.so`, `adjstctl.elf` y
  `MPR_SCN_INSTALL_MAP_DEMOMOVIE.so` **no están referenciados por ninguna instrucción**: barrido de
  literales `u32` en todo el fichero (0 aciertos) y del idiom `ldr rX,[pc]; add rX,pc` con ventana ±96 B
  (0 aciertos; el mismo escáner encuentra 223 referencias normales en `libsencore.so`). Son la tabla
  generada de nombres de comandos, sin consumidor en este build.
* El motor de escenarios **sí está cargado** en el arranque (`libtestcmd_scn.so`/`testcmd_scn_init`
  figura en la tabla por defecto de `libIMDB.so`), pero sólo actúa al recibir una petición de
  `libtestcmd.so` (`testcmd_run_scenario`, `0x14A4`), que usan las herramientas de consola
  (`scenario.elf`, `sndcmd.elf`), no el arranque.

### 2.3 La vía de arranque real: `FlashLib::Init` se llama directamente

```
IMDB (libIMDB.so, tabla "IMDB:default")
  └─ libmprctrl.so : InfraMprCtrl_Init (0x13CEC)
       └─ MprCtrl::Init (0x11718)
            └─ 0x11B84  blx MprIf::Create            (stub PLT 0xFD94)
                 └─ libmpr.so  MprIf::Create (0x71CC20)
                      └─ 0x71CC7A  bl 0x712530       (cadena de init de MPR)
                           ├─ 0x7126E2  blx FlashLib::Init(SystemType)   [stub PLT 0x11DFE8]
                           ├─ 0x7126E6  bl  BackupMgr::Init()            [= 0x2B4820]
                           └─ 0x7126EA… 0x71271A  bl <otras 14 init>
```

[11-arranque-cadena-MprIf-Create.txt](evidence/film-pb-1-sub-executility-20261126/11-arranque-cadena-MprIf-Create.txt).
Contraste a6300 fw2.01: la **misma** cadena, con `bl FlashLib::Init` en `0x7897D6` y el resto de `bl`
idéntico en orden ⇒ es código común, no un parche del CFW.

**Conclusión de (2)**: la utilidad 1 **no se ejecuta en el arranque** en ninguna cámara de esta familia;
`FlashLib::Init` corre por `MprIf::Create`, y `ExecMprUtility(1)` es la vía **manual/de test** para
repetir esa inicialización desde consola o desde un escenario de fábrica.

### 2.4 Corrección del punto [7. NO_VERIFICADO] nº 1 del informe del 26-11

El informe anterior concluyó "`FlashLib::Init` no tiene llamante interno (ni `bl`, ni PLT, ni puntero
literal)". Es **falso**, y el motivo es un bug del escáner: para `BLX` inmediato el destino es
`Align(PC,4) + imm`, y ni el script previo ni `/tmp/tools/elftool.py calls()` enmascaran los dos bits
bajos, así que **toda llamada `blx <stub PLT>` desaparecía**. Con la máscara aplicada:

| Símbolo | a6000 fw3.21 | a6300 fw2.01 | a7s fw3.20 |
|---|---|---|---|
| `FlashLib::Init` | **1** → `0x7126E2` (PLT `0x11DFE8`) | **1** → `0x7897D6` | **1** → `0x712786` (PLT `0x11DFF0`) |
| `FlashLib::WarmBootInit` | 2 → `0x2B4AB0`, `0x2B6894` | 2 → `0x2CE42C`, `0x2E05FC` | 2 → `0x2A3F28`, `0x2B6088` |
| `FlashLib::Resume` | 1 → `0x664382` | 1 → `0x6CB98E` | 1 → `0x6630B2` |
| `MprIf::ExecMprUtility` | 1 → `0x72DE24` (consola) | 1 → `0x79D05C` | 1 → `0x724230` |

[13-correccion-escaneo-blx.txt](evidence/film-pb-1-sub-executility-20261126/13-correccion-escaneo-blx.txt)
y [10-barrido-llamantes-FlashLib.txt](evidence/film-pb-1-sub-executility-20261126/10-barrido-llamantes-FlashLib.txt).
Advertencia para el resto del corpus: **cualquier "no tiene llamantes" basado en `elftool.py calls()`
puede ser un falso negativo** si la llamada va por PLT con `blx`.

---

## 3. Si la utilidad 1 no se ejecuta: qué pasa de verdad con el flag (pregunta 3)

### 3.1 El flag no depende de la utilidad

`FlashLib::Init` (`0x2B696C`, [05](evidence/film-pb-1-sub-executility-20261126/05-flashlib-init-2b696c.txt)):

```
002b6974  add  r2,r7,#8 ; strb r4,[r2,#-1]!   ; buffer = 0
002b6982  ldr  r0,=0x003C00BF ; movs r1,#1 ; bl 0x2B1468      ; GetEepData -> Backup_read
002b6988  ldrb r3,[r7,#7]      ; byte leído
002b698c  tst.w r3,#1 ; bne 0x2B6998         ; bit0==1 -> m_enableFlag = 0
002b6994  strb r1,[r2]   (r2 = &0xA36C78)    ; si bit0==0 -> m_enableFlag = 1   <-- literal 0x2B6B64
002b6998  strb r4,[r2]                       ; m_enableFlag = 0
002b69b0  blx FlashLib::MutexLock ; bl 0x2B0FFC(SystemType,&blockNum,&sectorNum,&sectorSize)
```

Corrección de forma: el literal con `&m_enableFlag` está en **`0x2B6B64`**, pero **las instrucciones que
escriben son `0x2B6994` (1) y `0x2B6998` (0)**. Y lo importante: **el flag se fija antes de la
geometría**. `0x2B1468` es `GetEepData()` y su lectura es `Backup_read` (PLT `0x11E8C4` →
`libbackup.so`, servicio "BKUP"); si la lectura falla, el buffer queda 0 ⇒ **flag = 1**.

⇒ Un `m_enableFlag == 0` sólo puede venir de **(a)** que el byte `0x003C00BF` del backup tenga bit0 = 1, o
**(b)** que `FlashLib::Init` no se haya ejecutado nunca. **La utilidad 1 no aparece en la ecuación.**

### 3.2 Cadena de consecuencias si el flag es 0

1. Todos los `FlashLib::*` que consultan el flag salen por el camino de error
   ([22-enableflag-xrefs.txt](evidence/film-pb-1-sub-backup-store-20261126/22-enableflag-xrefs.txt): 34
   lecturas, 1 escritura).
2. `FlashLib::CheckExistSector` (`0x2B8B48`) → `0xFFFFFFFF` para los 30 fileTypes (nunca `0x45`).
3. Los dos bucles (`BackupMgr::Init` `0x2B4820`, `BackupMgr::WarmBootInit` `0x2B4624`) escriben
   `+0x00 fileType`, `+0x08 0`, `+0x0C 0`, **`+0x04 = 0`** en `0xA3699C` → las 30 entradas sin *reader*.
4. `ReadFirstPackData` (`0x2B3948`) corta en `0x2B39EE` con **`0x10100001`**.
5. `IsNeedRepairFlashBackup` (`0x2B8950`) devuelve **1** cuando `m_enableFlag==0` (`0x2B89A8`), su llamante
   escribe `need repair FlashBackup` (`0x7E8811`; el literal base `0x7E880E` es `"NO need repair FlashBackup"` y el código salta 3 bytes cuando sí hace falta) y encadena `CheckAndRepairFlashBackup`.

### 3.3 Qué se lleva por delante en MSV / DCF / XAVC

La tabla de nombres FBS (`0x9D2154…`, `flag=ptr a nombre`;
[18-fbs-name-table.txt](evidence/film-pb-1-sub-backup-store-20261126/18-fbs-name-table.txt) y
[19-sector-names.txt](evidence/film-pb-1-sub-backup-store-20261126/19-sector-names.txt)) dice a qué
subsistema pertenece cada uno de los 30 *readers*:

| fileType | Nombre FBS | ¿Lo usa una ILCE-6000? |
|---|---|---|
| `0x10/0x11/0x12` | DVD AVCHD / DVD VR / DVD +VR | no (linaje Handycam) |
| `0x20/0x21` | HDD AVCHD / HDD M2PS+HDM | no |
| `0x28/0x29` | FLH AVCHD / FLH M2PS+HDM | no (flash interno de vídeo) |
| `0x2C/0x2D` | SSD AVCHD / SSD M2PS+HDM | no |
| **`0x30/0x31`** | **MS1 AVCHD / MS1 M2PS+HDM** | **sí** (índice AVCHD de la tarjeta) |
| `0x38/0x39` | MS2 AVCHD / MS2 M2PS+HDM | no (2.ª ranura) |
| `0x40` | VF/tmpVMGI | no |
| `0x60/0x61/0x68/0x6C` | DVD/HDD/FLH/SSD DCF | no |
| **`0x62`** | **MS1 DCF** | **sí** (journal DCF) |
| `0x63` | MS2 DCF | no |
| `0x90/0x91/0x92` | USB AVCHD / M2PS / DCF | no |
| `0xA0` | DCF DIFF | sí (comparador DCF) |
| `0xB1/0xB8/0xBC/0xBD` | HDD/FLASH/SSD/USB MP4 | no |
| **`0xB2`** | **MS1 MP4** | **sí** (índice MP4) |

Y la tabla tiene entradas que **no** están entre los 30 *readers*: `0x70 FSYS`, `0x80-0x83`
`AVI1..AVI4 (CSVC1..CSVC4)` ⇒ **XAVC no usa sectores FBS**. Consecuencia fina y útil para el
diagnóstico: un fallo **sólo de XAVC** no se explica por este camino; el síntoma global (ni AVCHD ni MP4
ni el índice de vídeo, con miniaturas de foto bien) sí es compatible, porque las fotos se enumeran por
recorrido de directorios DCF y no por el índice FBS.

---

## 4. ¿Depende del modo de arranque, de `/usr`, de `/setting` o del entorno? (pregunta 4)

| Factor | Ruta de la **utilidad 1** | Ruta de **arranque** (`FlashLib::Init` → `BackupMgr::Init`) |
|---|---|---|
| **Arranque en frío** | no interviene | **se ejecuta siempre** (cadena de `MprIf::Create`) |
| **Arranque caliente (WBI)** | no interviene | **no se ejecuta**: no hay `init`; el estado (flag + tabla `0xA3699C`) es el de la instantánea de RAM. Ver [sub-arranque-wbi-20261128](film-pb-1-sub-arranque-wbi-20261128.md) |
| **Fichero en `/usr`** | sí: `/usr/scenario/MPR_SCN_FLASH_BACKUP_INIT.so` debe existir y ser `dlopen`-able (`libtestcmd_scn.so`: `"/usr/scenario/"` + `"%s%s%s"`) | no (`libmpr.so` ya está cargado) |
| **`/setting`** | no | no (el único `/setting` del arranque es `/setting/mode/dmode` y `/setting/sen/smode`, que sólo ramifican `init` a `ADJUST`/`BIS`) |
| **Variables de entorno** | no | no (`libmpr` no llama a `getenv`; las que pone `im.elf` son `HOME PATH TOPRC MALLOC_OPTIONS LT_ABORTREASON` y las opciones `boot=/app_argv=/debug=`) |
| **Dispositivos/hw** | no | sí: `/dev/nflasha4` \| `/dev/cnflasha4` y `/sys/block/nflasha0/nflasha0p4/start` (DFB) |
| **Servicio BKUP** | no | sí: `Backup_read(0x003C00BF)` (`libbackup.so` va antes que `libmpr.so` en la tabla IMDB) |

Dos matices que sí dependen del modo de arranque:

* **`FlashLib::WarmBootInit` + `BackupMgr::WarmBootInit`** existen como pareja en un envoltorio propio,
  `0x2B4AAC` ([06](evidence/film-pb-1-sub-executility-20261126/06-wbi-wrapper-2b4aac.txt)):
  `blx FlashLib::WarmBootInit` → `bl BackupMgr::WarmBootInit` → `return 0`. Está referenciado por un
  descriptor `{fn=0x2B4AAD, nombre="WarmBootInit"}` en `.rodata` (`0x7E8100`), junto a otros descriptores
  de la familia DFB (`SetSectorManagerTable` `0x7E7C6F`, `InitBackupData` `0x7E7C2E`), es decir: es una
  **entrada de consola/test**, no un paso del arranque. El otro disparador es `BackupMgr::Event(0)`
  (`0x2B4810` `b.w 0x2B4624`), que exige que FlashLib esté vivo.
* **`FlashLib::WarmBootInit` no escribe `m_enableFlag`** (`0x2B6788`:
  [07](evidence/film-pb-1-sub-executility-20261126/07-flashlib-warmbootinit-2b6788.txt) → `MutexLock`,
  `0x2B1008`, `0x2B1310`; ni una escritura a `0xA36C78`). Por tanto el camino caliente **re-registra los
  30 readers pero sigue dependiendo del flag** que puso (o no) el arranque en frío.

---

## 5. Conclusión y cómo se comprueba en la cámara (pregunta 5)

### 5.1 Conclusión

* **¿Es plausible que la utilidad 1 no se ejecute?** No sólo es plausible: **es lo normal**. En toda la
  familia (a6000/a6300/a7s) el único disparador son dos escenarios de test y un comando de consola; el
  arranque no la usa. Que no se ejecute **no tiene ninguna consecuencia** sobre `m_enableFlag`.
* **¿Es plausible que falle?** Sí, y fallaría "limpio": `0x4500CC` devuelve **9** si la sesión no está
  viva (`[this+4]->vt[0x18] == 0`) y el escenario lo imprime como `MPR_FLASH_BACKUP_INIT End Err 0x9`.
  Pero, otra vez, ese 9 no toca el flag.
* **La causa del síntoma está en la ruta de arranque**, no en la utilidad: `FlashLib::Init` se llama
  (`0x7126E2`) y fija el flag a 1 salvo que el byte `0x003C00BF` del backup traiga bit0 = 1; después
  `0x2B0FFC` tiene que dejar `blockNum/sectorNum/sectorSize` válidos y `DFB::CheckExistFile` devolver
  `0x45`. Los tres candidatos reales son, por este orden de probabilidad:
  1. **DFB no inicializado** (`[DFB]not initialized yet:CheckExistFile()` `0x7DE124`, retorno `0x4F`):
     falla `0x2B0FFC` por NAND interno (`/dev/nflasha4`, `nflasha0p4`), que es lo que ya apuntaba el
     informe del 26-11.
  2. **`m_enableFlag == 0`** por el byte de backup `0x003C00BF` (bit0 = 1) o por `Backup_read` con
     respuestas raras del servicio BKUP.
  3. Sectores FBS **destruidos** (`FlashBackupCheckAndDestroy`, `0x61DB54`) tras un `0x10100002`.

### 5.2 Comprobaciones en cámara (ninguna destructiva)

| # | Qué | Cómo | Lectura esperada |
|---|---|---|---|
| 1 | dirección real de `libmpr` | `cat /proc/$(pidof im.elf)/maps \| grep libmpr` | base `0x06xxxxxx` (VA + base) |
| 2 | **`m_enableFlag`** | `dd if=/proc/$(pidof im.elf)/mem bs=1 skip=$((base+0xA36C78)) count=1 \| hd` (ruta `chroot /android` con toybox, la del kit `camera_filmbp1_trace.py`) | `01` = flag OK ⇒ el fallo es DFB/sectores · `00` = nadie lo puso |
| 3 | **tabla de readers** | `… skip=$((base+0xA3699C)) count=600` (0x258 B) | 30 filas; `+4` (handle) ≠ 0 en las 3 útiles (`0x30/0x31/0x62/0xb2`) si está sano; todo 0 = roto |
| 4 | log del subsistema | `grep` en el log/monitor de: `[NBL] GetEepData() bkupErr:` (`0x7E5E74`), `[DFB]call api (DvdFlashBackupLib::Init) result:blockNum[…]` (`0x7E3CCE`), `[DFB]not initialized yet:CheckExistFile()` (`0x7DE124`), `[FBM]Init()  [entryNo:%d]` (`0x7E7C92`, 30 líneas), `[FBM]--Init()-OpenSector32()[errorFBS:%d][handle:%d]-` (`0x7E7CAC`), `need repair FlashBackup` (`0x7E8811`; el literal base `0x7E880E` es `"NO need repair FlashBackup"` y el código salta 3 bytes cuando sí hace falta) | sin `not initialized` y 30 líneas `[FBM]Init()` con `errorFBS:0` si está sano |
| 5 | nodos y sysfs del NAND | `ls -l /dev/nflasha4 /dev/cnflasha4`; `cat /sys/block/nflasha0/nflasha0p4/start` | deben existir/leer |
| 6 | **prueba de la utilidad 1** | consola: `MPR FUNCRECOVERY ExecMprUtility init` (o lanzar el escenario) | devuelve 0 y **no** cambia el flag ni la tabla ⇒ confirma que la utilidad no es la vía |
| 7 | forzar la pareja de recalentamiento | consola: comando `WarmBootInit` (handler `0x2B4AAC`) | re-registra readers; si la tabla sigue a 0 con flag=1, el fallo está en `CheckExistSector`/DFB |
| 8 | volcado de la propia tabla | consola grupo DFB: `GetSMI` / `Sector Manager Info Table` (`"  [SName]  [Handle]   [Status]…"`, `0x7E6BA4`) y `SetSMI` para reparar a mano | `Handle=0` en las 30 filas = tabla vacía |

Si (2) da `01` y (4) muestra `[DFB]not initialized yet`, el diagnóstico queda cerrado en la capa DFB y
**no** en el flag ni en la utilidad; si (2) da `00`, el siguiente paso es leer el byte `0x003C00BF` del
backup con el servicio BKUP, no tocar la utilidad.

---

## 6. NO_VERIFICADO

1. Qué enumeran exactamente las **5** ranuras de `0x436408` (`0x4478C0`): no se ha identificado la clase
   de esos objetos ni si una de ellas es el flash interno.
2. Significado completo de `MPR::UtilityCmdId == 2` (`flush`): el parser de consola le pasa el argumento
   crudo en vez de una constante, así que el nombre no está confirmado por código.
3. Si `Backup_read(0x003C00BF)` puede devolver bit0 = 1 en una ILCE-6000 de producción o es un resto del
   linaje Handycam: no hay evidencia de campo (haría falta el volcado del backup).
4. El contenido del descriptor `{0x2B4AAD,"WarmBootInit"}` (`0x7E8100`) se ha leído como par
   `{fn,nombre}` por vecindad con los otros descriptores DFB; no se ha localizado el iterador de esa
   tabla, así que "comando de consola" es la lectura más probable pero no está probada de punta a punta.
5. No se ha verificado si el CFW del proyecto recompone `/usr` de forma que falte
   `/usr/scenario/MPR_SCN_FLASH_BACKUP_INIT.so`; es irrelevante para el arranque pero afecta a la vía
   manual del punto (6) de §5.2.
