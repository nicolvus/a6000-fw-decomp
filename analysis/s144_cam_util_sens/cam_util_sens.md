# S144 — `[CAM_UTIL_SENS]`: la utilidad de la memoria interna del sensor (A6000 fw3.21)

**Hito**: S144 · **Binario**: `analysis/rea-independent/input/av-cam.bin` (A6000 fw3.21, 11 427 236 B)
**Convención**: `vaddr = 0x43541000 + file_offset` (verificada en el repo; también válida para
A7S fw3.20 y A6300 fw2.01, verificado en S143 con la tabla «Sens»).
**Regla de referencias**: **estricta** (canónica, `analysis/s106_imaging_cap/scan_pic_refs_strict.py`;
mapa global `analysis/s106_imaging_cap/pic_refs_strict_global.json`). Los sitios puntuales se han
verificado **a mano** desensamblando (aritmética `ldr`/`add` re-hecha byte a byte con capstone 5.0.7).
**Script canónico**: `analysis/s144_cam_util_sens/scan_s144.py` → `cam_util_sens.json`.
**Auxiliares**: `dasm.py` (desensamblador con anotación PIC), `scan_callers.py` (llamantes y punteros
absolutos), `scan_pic_abs.py` (destinos PIC no-cadena), `ctx.py` (módulo de un sitio de llamada).

---

## 1. Resumen

| dato | valor |
|---|---|
| cadenas `[CAM_UTIL_SENS]` en A6000 fw3.21 | **21** (bloque `0x43cce1ea`–`0x43cce6ad`, con un hueco de 3 cadenas `[CAM_UTIL]`) |
| cadenas referenciadas | **21 / 21** (ninguna muerta) |
| sitios de referencia (regla estricta) | **39** |
| funciones que las referencian | **5** (`0x439012d0`, `0x43901d50`, `0x43902168`, `0x439023b8`, `0x43902418`) |
| cadenas `[CAM_UTIL_SENS]` en A7S fw3.20 | **0** |
| cadenas `[CAM_UTIL_SENS]` en A6300 fw2.01 | **0** |
| interiores de texto presentes en A7S / A6300 | **0 / 21** y **0 / 21** |

**Qué es.** `[CAM_UTIL_SENS]` es la etiqueta de diagnóstico de la **utilidad de cámara que gestiona
los ficheros de la memoria interna del sensor («IM»)**: abre un fichero por número/-dirección/tamaño
(«Debug IM ASync Open» / «Debug IM Sync Open»), le asigna un número de fichero («SET FILE NUM
Func»), y notifica el evento al gestor de servicio («UTIL MS Mgr) Call CB»). Además, es el
**callback de cambio de BKID** (bloque del sensor) que, cuando cambia el bloque, **monta o desmonta**
el servicio («Utility MS Mount Start» / «Utility MS UnMount Start», código `[CAMERA_ADJ]`).

Su **mecánica** es: escribir 4 parámetros en un bloque global y **enviar un mensaje OSAL** con una
plantilla fija — el mismo patrón, los mismos ids OSAL y el mismo log que usa su hermano
`[CAM_UTIL_ADJ]`.

**No es la vía de exposición.** El módulo no menciona ni toca obturación, iris, ISO ni lectura de
imagen (ver §7, con el negativo acotado).

---

## 2. Las 21 trazas, con dirección

Orden por vaddr. `sitio` = dirección del `add rX,pc`; `ldr` = `ldr rX,[pc,#imm]` emparejado
(regla estricta). Verificado a mano: `destino = pool + (dirección_del_add + 4)`.

| # | vaddr cadena | texto | sitio | ldr | función |
|---|---|---|---|---|---|
| 1 | `0x43cce1ea` | `[CAM_UTIL_SENS]: CB for BKID change [BKID]:%x [Size]:%x` | `0x4390130e` | `0x43901306` | `0x439012d0` |
| 2 | `0x43cce222` | `[CAM_UTIL_SENS]:                    [SWFLG]:%x` | `0x43901326` | `0x43901324` | `0x439012d0` |
| 3 | `0x43cce251` | `[CAM_UTIL_SENS]:                    [MODEFLG]:%x` | `0x4390133a` | `0x43901338` | `0x439012d0` |
| 4 | `0x43cce322` | `[CAM_UTIL_SENS]:   Debug IM ASync Open start` | `0x43901d7c` | `0x43901d78` | `0x43901d50` |
| 5 | `0x43cce34f` | `[CAM_UTIL_SENS]: [FileNum]%04x [Adr]%x [Size]%x` | `0x43901d90` | `0x43901d88` | `0x43901d50` |
| 5 | `0x43cce34f` | (idem) | `0x43901f18` | `0x43901f10` | `0x43901d50` |
| 6 | `0x43cce37f` | `[CAM_UTIL_SENS]: [Flg]%04x [MountSTAT]%04x [FsysMode]%04x` | `0x43901db0` | `0x43901dae` | `0x43901d50` |
| 6 | `0x43cce37f` | (idem) | `0x43901f36` | `0x43901f34` | `0x43901d50` |
| 6 | `0x43cce37f` | (idem) | `0x439021c0` | `0x439021be` | `0x43901d50` |
| 7 | `0x43cce3b9` | `[CAM_UTIL_SENS]:   Debug IM ASync Open OSAL MEM ALLOC Error : %x` | `0x43901e06` | `0x43901dfc` | `0x43901d50` |
| 8 | `0x43cce3fa` | `[CAM_UTIL_SENS]: >>[FILE_NUM]%x [ADR]%x [SIZE]%x` | `0x43901e48` | `0x43901e42` | `0x43901d50` |
| 8 | `0x43cce3fa` | (idem) | `0x43902030` | `0x4390202a` | `0x43901d50` |
| 8 | `0x43cce3fa` | (idem) | `0x43902264` | `0x4390225e` | `0x43901d50` |
| 8 | `0x43cce3fa` | (idem) | `0x43902498` | `0x43902492` | `0x43902418` |
| 9 | `0x43cce42b` | `[CAM_UTIL_SENS]: >>[STAT]%x [FSYSMODE]` | `0x43901e6a` | `0x43901e68` | `0x43901d50` |
| 9 | `0x43cce42b` | (idem) | `0x4390204e` | `0x4390204c` | `0x43901d50` |
| 9 | `0x43cce42b` | (idem) | `0x43902286` | `0x43902284` | `0x43901d50` |
| 9 | `0x43cce42b` | (idem) | `0x439024c6` | `0x439024c4` | `0x43902418` |
| 10 | `0x43cce452` | `[CAM_UTIL_SENS]:   Debug IM ASync Open end [ErrInfo]%x [Flg]%x` | `0x43901eca` | `0x43901ec8` | `0x43901d50` |
| 11 | `0x43cce491` | `[CAM_UTIL_SENS]:   Debug IM Sync Open start` | `0x43901f04` | `0x43901f00` | `0x43901d50` |
| 12 | `0x43cce4bd` | `[CAM_UTIL_SENS]:  Debug IM Sync Open OSAL MEM ALLOC Error : %x` | `0x43901f8c` | `0x43901f82` | `0x43901d50` |
| 12 | `0x43cce4bd` | (idem) | `0x43902450` | `0x43902446` | `0x43902418` |
| 13 | `0x43cce4fc` | `[CAM_UTIL_SENS]:   >> [SndMsgErrInfo]%x` | `0x43902094` | `0x4390208a` | `0x43901d50` |
| 13 | `0x43cce4fc` | (idem) | `0x439022c6` | `0x439022bc` | `0x43901d50` |
| 13 | `0x43cce4fc` | (idem) | `0x4390250c` | `0x43902502` | `0x43902418` |
| 14 | `0x43cce524` | `[CAM_UTIL_SENS]:   >> [RcvMsgErr]%x` | `0x439020b6` | `0x439020ae` | `0x43901d50` |
| 14 | `0x43cce524` | (idem) | `0x439022e8` | `0x439022e0` | `0x43901d50` |
| 14 | `0x43cce524` | (idem) | `0x4390252e` | `0x43902526` | `0x43902418` |
| 15 | `0x43cce548` | `[CAM_UTIL_SENS]:   >> Recieve UnKnown Msg [CID]%x` | `0x439020e0` | `0x439020da` | `0x43901d50` |
| 15 | `0x43cce548` | (idem) | `0x43902312` | `0x4390230c` | `0x43901d50` |
| 15 | `0x43cce548` | (idem) | `0x43902558` | `0x43902552` | `0x43902418` |
| 16 | `0x43cce57a` | `[CAM_UTIL_SENS]:   Debug IM Sync Open end[Flg]%x` | `0x43902118` | `0x43902116` | `0x43901d50` |
| 16 | `0x43cce57a` | (idem) | `0x4390234a` | `0x43902348` | `0x43901d50` |
| 16 | `0x43cce57a` | (idem) | `0x43902590` | `0x4390258e` | `0x43902418` |
| 17 | `0x43cce5ab` | `[CAM_UTIL_SENS]: SET FILE NUM Func` | `0x43902180` | `0x4390217e` | `0x43902168` |
| 18 | `0x43cce5ce` | `[CAM_UTIL_SENS]: [FileNum]%02x [Adr]%x [Size]%x` | `0x43902198` | `0x43902190` | `0x43902168` |
| 19 | `0x43cce5fe` | `[CAM_UTIL_SENS]:   SET FILE NUM Func OSAL MEM ALLOC Error : %x` | `0x4390220e` | `0x43902204` | `0x43902168` |
| 20 | `0x43cce63d` | `[CAM_UTIL_SENS]: UTIL MS Mgr) Call CB [Flg]%x` | `0x439023d8` | `0x439023d6` | `0x439023b8` |
| 21 | `0x43cce66b` | `[CAM_UTIL_SENS]: UTIL MS Mgr) ## CALL BACK NULL Error!!! ##[Flg]%x` | `0x439023f0` | `0x439023ea` | `0x439023b8` |

Las 21 cadenas ocupan un bloque propio del *pool* de texto (`0x43cce1ea`–`0x43cce6ad`, NUL final
incluido), con **un único hueco**: entre `0x43cce251` y `0x43cce322` se intercalan **3** cadenas del
módulo hermano `[CAM_UTIL]` (`[CAM_UTIL]: EvtDrvnTsk) Send Err tid:%d->%d, func:%08x, arg:%x, %x`
`0x43cce282`, `[CAM_UTIL]: EvtDrvnTsk) Send Err Print Max...` `0x43cce2c5`,
`[CAM_UTIL]: Task tid:%d, func:%08x, arg:%x, %x` `0x43cce2f3`). Por tanto el módulo se compone de
**dos sub-bloques contiguos**: `0x43cce1ea`–`0x43cce251` (3 cadenas) y `0x43cce322`–`0x43cce66b`
(18 cadenas). El bloque está entre el de `[CAM_UTIL_ADJ]` (`0x43ccdcee`–`0x43cce0f2`, S143) y el de
`[CAMERA_ADJ]` (`0x43cce128`–`0x43cce1a7`).

---

## 3. Las 5 funciones

Límites verificados por desensamblado (prólogo `push` … `lr` / epílogo `pop` … `pc`).

### 3.1 `0x439012d0` – `0x43901380` : callback de cambio de BKID (3 trazas)

- Prólogo `push {r0,r1,r2,r4,r5,r6,r7,lr}`; epílogo `pop.w {r4,r5,r6,r7,lr}` + `b.w 0x43901274`.
- **No la llama ningún `bl`** (0 llamadas en toda la imagen). Se registra como **puntero absoluto de
  4 B** `0x439012d1` en `0x44022d84` → es un **callback** (tabla de punteros de función de la zona
  `0x4402xxxx`; la naturaleza exacta de esa tabla —vtable o registro de callbacks— es **NO VERIFICADO**).
- `0x439012d4` `mov.w r0,#0xb50000` (inmediato confirmado con `llvm-mc`: `4f f4 35 00`) y
  `0x439012da` `bl 0x43561394` (thunk que despacha por vtable en `[obj+0x28c]`) → devuelve en `r0`
  (que pasa a `r4`) el **tamaño** del bloque, tal como lo rotula la traza «[Size]:%x».
- `0x439012ee` `blx 0x439c5320` copia **r4 bytes** (el tamaño del bloque, devuelto por la llamada de
  servicio con id `0xb50000`) desde `r7` (=arg2, origen) hacia el objeto `[r5]` de la base
  `0x4401eee4` (`ldr r5,[pc,#0x8c]`@`0x439012de` → pool `0x0071dbfc` → `0x4401eee4`).
  `0x439c5320` es un `memcpy(dst=r0, src=r1, n=r2)` (copia de bloques de 16 B en `0x439c534e`).
- `0x439012f4` `ldrb r3,[r3,#2]`; si vale `1` → `bl 0x43900e30` («Utility MS **Mount** Start»);
  si vale `0` → `bl 0x43900f18` («Utility MS **UnMount** Start»). Ambas son funciones de
  `[CAMERA_ADJ]` (hermanas de ADJ), que despachan por `0x439009f0` (el despachador de `[CAM_UTIL_ADJ]`).
- Registra `BKID` (arg0 = `r6`), `Size` (`r4`), `SWFLG` (`[obj+2]`) y `MODEFLG` (`[obj+3]`).
- Fija 4 parámetros con `0x4390129c` (bytes +8..+0xb) y `0x43901274` (u32 en +8).

### 3.2 `0x43901d50` – `0x43902168` : «Debug IM ASync Open» (17 trazas)

Función grande (1 048 B) con **dos caminos**: `0x43901d68` `cmp.w fp,#0` / `beq.w 0x43901ef8` →
si el 4.º argumento (`fp`) es 0, entra en el **camino síncrono** (que emite las trazas 11–16), y si
no, en el **asíncrono** (trazas 4–10). Por eso las trazas «Debug IM Sync Open» aparecen atribuidas
aquí *y* a la función gemela `0x43902418`.

- Camino asíncrono: log «start» → log `[FileNum][Adr][Size]` → log `[Flg][MountSTAT][FsysMode]`
  (los tres varargs son, respectivamente, el byte «Flg» `0x43fa2d23`, el valor devuelto por
  `0x43900ff8` = `0x43fa29f0`, y el byte `+3` de la tabla de objetos) → reserva un mensaje OSAL de
  `0x18` (24) B con `osal_try_valloc_msg` (`0x435612d0`) → rellena la estructura
  (`[r4+2]`=FileNum, `[r4+4]`=Adr, `[r4+8]`=Size, `[r4+0xc]`=MountSTAT, `[r4+0xd]`=FsysMode,
  `[r4+0xe..+0x14]`=puntero al mensaje) → `osal_snd_msg` (`0x4356120c`).
- Camino síncrono: además recibe el mensaje (`0x43561260`), distingue «SndMsgErrInfo»,
  «RcvMsgErr» y «Recieve UnKnown Msg [CID]» y termina con «Debug IM Sync Open end[Flg]%x».
- **Nota de redacción**: las trazas «… OSAL MEM ALLOC Error : %x» se emiten en la rama **de éxito**
  de la reserva (p. ej. `0x43901e06` se alcanza con `r0` = puntero **no nulo**; la rama de fallo
  va a `0x43901e16`). El texto dice «Error» pero el argumento es el puntero reservado. Se reporta
  tal cual; la intención del firmware es **NO VERIFICADA**.

### 3.3 `0x43902168` – `0x439023b8` : «SET FILE NUM Func» (10 trazas)

- Argumentos: `r0` = FileNum, `r1` = Adr, `r2` = Size (verificado en los 3 llamantes de
  `[IMAGING_CAP]`, p. ej. `0x43782644`: `r1 = base+offset`, `r2 = size`).
- `0x43902174` `bl 0x43900ff8` → devuelve el **byte global `0x43fa29f0`** (el «MountSTAT» /
  «STAT» de las trazas).
- Escribe los 4 parámetros (`0x43901ccc`, `0x43901d00`) y **envía el mensaje OSAL** con la
  plantilla de 12 B (`0x43901c04`).
- Devuelve un puntero/resultado en `r0` (0 si falla) → es lo que los llamantes usan como
  «manejador de fichero» (de ahí el nombre de la función que lo invoca en el firmware:
  `cam_util_debug_file_write`, §5).

### 3.4 `0x439023b8` – `0x43902418` : «UTIL MS Mgr) Call CB» (2 trazas)

- Pone a 0 un byte global (`0x43fa2d23` = el «**Flg**»: `ldr r4,[pc,#0x48]`@`0x439023bc`, pool
  `0x006a0961`@`0x43902408`), carga un **puntero a función** desde un global (`0x43f062d4`:
  `ldr r3,[pc,#0x48]`@`0x439023c2`, pool `0x00603f0c`@`0x4390240c` — justo 12 B después del bloque de
  parámetros `0x43f062c8`) y, si no es nulo, lo invoca con `blx r3`.
- Log «UTIL MS Mgr) Call CB [Flg]%x» con el byte global, o «## CALL BACK NULL Error!!! ##[Flg]%x»
  si el puntero es nulo.
- Devuelve la terna `(2, 1, 0xff)` o `(2, 1, 0xcc)` y encadena en `0x43901ccc`.
- **La llama `tsk_cam_adjctrl`** (`[CAM_UTIL_ADJ]`) en `0x43900c9c`, cuando el código de comando
  recibido es `0` (verificado en S143).

### 3.5 `0x43902418` – `0x43902604` : «Debug IM Sync Open» (7 trazas)

Función **gemela** del camino síncrono de `0x43901d50` (misma lógica, mismas trazas, sitio de
emisión propio). La llama un único sitio, `0x437894dc`, dentro de un despachador de comandos que
comprueba el código `0x63` en `[r4+0x1a]` y un valor `0x4650` antes de invocarla.

### 3.6 Ayudantes verificados (sin traza propia del módulo)

| vaddr | papel (verificado por desensamblado) |
|---|---|
| `0x43900ff8` | devuelve el byte global `0x43fa29f0` («MountSTAT» / «STAT») |
| `0x43900e30` | `[CAMERA_ADJ] Utility MS Mount Start` (despacha con `0x439009f0`, id de comando `6`) |
| `0x43900f18` | `[CAMERA_ADJ] Utility MS UnMount Start` (id de comando `7`) |
| `0x43901150` | log del módulo (formatea con `0x439c5004` y envía con `osal_snd_msg`) |
| `0x43901b7c` | 2.ª copia del ayudante de log (misma estructura) |
| `0x43901274` | escribe un u32 en `+8` del bloque de parámetros global |
| `0x4390129c` | escribe 4 bytes (`+8`,`+9`,`+0xa`,`+0xb`) del bloque de parámetros global |
| `0x43901c04` | **envía** el mensaje OSAL: reserva `0x2c` B, copia 12 B de la plantilla, `osal_snd_msg` |
| `0x43901ca0` | escribe u16 en `+8` y 0 en `+0xa` del bloque global |
| `0x43901ccc` | escribe 4 bytes (`+8`..`+0xb`) del bloque global |
| `0x43901d00` | escribe un u32 en `+8` del bloque global |
| `0x43901380` | indexa una tabla global con `r0` (usado por `0x4382ce82`) |

**Globales del módulo** (aritmética `ldr`/`add` re-hecha a mano):

| global | cómo se calcula | para qué |
|---|---|---|
| `0x43f062c8` | `ldr r4,[pc,#0x24]`@`0x43901cce` (pool `0x006045f2`@`0x43901cf4`) + `add r4,pc`@`0x43901cd2` | bloque de parámetros **y** plantilla de 12 B del mensaje OSAL (los bytes `+8..+0xb` son los 4 parámetros) |
| `0x43fa29f0` | `ldr r3,[pc,#4]`@`0x43900ff8` (pool `0x006a19f2`@`0x43901000`) + `add r3,pc`@`0x43900ffa` | byte «MountSTAT» / «STAT» (lo devuelve `0x43900ff8`) |
| `0x43fa2d23` | `ldr r7,[pc,#0x240]`@`0x43901d78` (pool `0x006a0fa1`@`0x43901fbc`) + `add r7,pc`@`0x43901d7e` — y `ldr r4,[pc,#0x48]`@`0x439023bc` (pool `0x006a0961`@`0x43902408`) + `add r4,pc`@`0x439023be` | byte «**Flg**»: lo leen las trazas `[Flg]%04x` y lo pone a 0 «UTIL MS Mgr) Call CB» |
| `0x43f062d4` | `ldr r3,[pc,#0x48]`@`0x439023c2` (pool `0x00603f0c`@`0x4390240c`) + `add r3,pc`@`0x439023c4` | puntero al **callback del gestor MS** (invocado con `blx r3`); está 12 B después del bloque de parámetros |
| `0x4401eee4` | `ldr r5,[pc,#0x8c]`@`0x439012de` (pool `0x0071dbfc`) / `ldr r4,[pc,#0x258]`@`0x43901d56` (pool `0x0071d182`) | tabla de objetos global que usan tanto el CB de BKID como la apertura de fichero |

**Ids OSAL (idénticos a los de `[CAM_UTIL_ADJ]`)**

| id | valor | dónde |
|---|---|---|
| mensaje de **log** | `0x008f0139` | `0x4390073c` (ADJ), `0x43901164` y `0x43901b90` (SENS) |
| mensaje de **comando** | `0x008f013a` | `0x43900930` (ADJ), `0x43901c08` (SENS) |

---

## 4. Funciones que las referencian y quién las referencia

### 4.1 Quién llama a las 5 funciones (barrido de `bl`/`blx` de 16 y 32 bits + punteros de 4 B)

| función | nº de `bl` | sitios | punteros absolutos |
|---|---|---|---|
| `0x439012d0` (CB de BKID) | **0** | — | `0x44022d84` (`0x439012d1`) |
| `0x43901d50` (ASync Open) | **17** | `0x4376bf92`, `0x43783136`, `0x437ee214`, `0x4387375c`, `0x43873b5c`, `0x43873b96`, `0x43873bec`, `0x43873c0c`, `0x43873c3a`, `0x4387883c`, `0x4387888a`, `0x438b834a`, `0x439f7bda`, `0x439f7c7c`, `0x439f7d4e`, `0x439f7e34`, `0x43b723b8` | — |
| `0x43902168` (SET FILE NUM) | **4** | `0x43782644`, `0x43782650`, `0x43782904`, `0x4382cea2` | — |
| `0x439023b8` (UTIL MS Call CB) | **1** | `0x43900c9c` (dentro de `tsk_cam_adjctrl`, S143) | — |
| `0x43902418` (Sync Open) | **1** | `0x437894dc` | — |

### 4.2 Módulos desde los que se llama (atribución por la traza más cercana del código llamante)

| sitio | módulo | evidencia (traza del código llamante) |
|---|---|---|
| `0x4376bf92` | `[CAMERA_MAIN_LC]` | `[CAMERA_MAIN_LC]: MS_Writer: disable addr! memmapID: %d` (`0x43c9d45c`) |
| `0x43783136` | `[IMAGING_CAP]` | `[IMAGING_CAP]: MemAreaMSDebug) Exec MS Dump: filename FILE%04x, addr 0x%08x, size 0x%08x` (`0x43c9f2dd`) |
| `0x437ee214` | `[IMAGING_CAP]` | `[IMAGING_CAP]: dmm Open Err: unit_hanlde[0x%08x], err[%d]` |
| `0x4387375c`…`0x43873c3a` | `[CAMERA_MAIN_TC]` | `[CAMERA_MAIN_TC]: TC:APL:Err: MS Log1st %d 0x%X` (`0x43cb6d12`) |
| `0x4387883c`, `0x4387888a` | `[CAMERA_MAIN_TC]` | `[CAMERA_MAIN_TC]: TC:DDT:Err: Osal Rsv Msg %d` (`0x4387870e`) |
| `0x438b834a` | `[CAMERA_MAIN_YC]` | `[CAMERA_MAIN_YC]: [Error] WiriteMsDebug = %x` (`0x43cc56af`) |
| `0x439f7bda`…`0x439f7e34` | `[IDT]` / `[IDT_OPD]` | `[IDT]: miniRAW Addr  : %08x` (`0x43cf4100`), `[IDT]: CC EC Result Addr  : %08x` (`0x43cf41ed`) |
| `0x43782644`, `0x43782650`, `0x43782904` | `[IMAGING_CAP]` | `[IMAGING_CAP]: <SACC_Debug> Capture_MemOpen() error` (`0x43c9eece`) y `[IMAGING_CAP]: ## Error : cam_util_debug_file_write(%d) %s : %d` (`0x43c9f336`) |
| `0x43900c9c` | `[CAM_UTIL_ADJ]` | `tsk_cam_adjctrl` (S143) |

**Lectura**: `[CAM_UTIL_SENS]` es la pieza que **escribe volcados de imagen (RAW/YC) en la memoria
interna del sensor** para diagnóstico (`MemAreaMSDebug`, `SACC_Debug`, `miniRAW`, `WiriteMsDebug`,
`MS_Writer`): la llaman precisamente los módulos que necesitan volcar datos al sensor.

---

## 5. Ficheros fuente

**No se ha podido atribuir un fichero fuente propio al módulo**: ninguna de las 21 trazas, ni
ninguna de las 5 funciones ni de sus ayudantes referencia un nombre `.cpp`/`.h`. Recalculado sobre
todo el binario (625 cadenas del *pool* terminan en `.cpp`/`.c`/`.h`/`.hpp`): **ninguna** referencia
PIC cae en la banda `0x43900000`–`0x43910000` (la banda donde vive todo el módulo).
→ **NO VERIFICADO / no consta**.

Lo que sí es verificable:

- El firmware **nombra la función** `cam_util_debug_file_write` dentro de mensajes de error de
  `[IMAGING_CAP]` (`0x43c9ef02`, `0x43c9f336`) y de «CCC» (`0x43cb50cf`). Ese es el nombre de la
  rutina que **usa** este módulo (la ruta `SACC_Debug`/`MemAreaMSDebug`).
- El firmware **nombra** la familia `MemAreaMSDebug` / `MemAreaMSDebug_RAW` / `_YC` / `_Base`
  (`0x43c9f2dd`, `0x43c9f3a0`, `0x43c9f40c`, `0x43c9f4f1`), también en `[IMAGING_CAP]`.
- Los ficheros `amSensCtrlCore.cpp` (`0x43cdb45a`), `amSensCtrlIf.cpp` (`0x43cd88cc`),
  `amSensMsgIf.cpp` (`0x43cd2eb3`) y sus gemelos `mcSens*.cpp` existen en el binario (S143) y
  pertenecen a la capa «Sens» del driver, en la banda `0x4391xxxx`–`0x4392xxxx`; **no hay ninguna
  referencia** entre sus sitios y los de este módulo → la pertenencia a la familia `amSens*` es
  **inferencia, no prueba**.

---

## 6. Relación con `[CAM_UTIL_ADJ]` (S143) y con los comandos «Sens»

### 6.1 Hermanía de código (verificada)

| rasgo | `[CAM_UTIL_ADJ]` (S143) | `[CAM_UTIL_SENS]` (S144) |
|---|---|---|
| banda de código | `0x439007b0`–`0x43900d30` | `0x439012d0`–`0x43902604` |
| id OSAL del **log** | `0x008f0139` (`0x4390073c`) | `0x008f0139` (`0x43901164`, `0x43901b90`) |
| id OSAL del **comando** | `0x008f013a` (`0x43900930`) | `0x008f013a` (`0x43901c08`) |
| id de módulo en el log | `r0 = 0xb5` (`0x43900a8c`) | `r0 = 0xb5` (`0x43901d82`, `0x439023d0`) |
| patrón de parámetros | 4 bytes en `+8..+0xb` de un bloque global (`0x439009f0`) | 4 bytes en `+8..+0xb` de un bloque global (`0x43901ccc`) |
| envío | `osal_try_valloc_msg`(`0x2c`) + plantilla de 12 B + `osal_snd_msg` (`0x4390092c`) | idéntico (`0x43901c04`) |

→ **El mismo id de módulo OSAL (0xb5), los mismos dos ids de mensaje y el mismo patrón de
bloque de parámetros**: son dos implementaciones hermanas de la misma interfaz de servicio.

### 6.2 Dependencia cruzada (verificada, bidireccional)

1. `[CAM_UTIL_ADJ] → [CAM_UTIL_SENS]`: `tsk_cam_adjctrl` (`0x43900c44`) llama a
   `0x439023b8` («UTIL MS Mgr) Call CB») en `0x43900c9c` cuando el código de comando es `0`.
2. `[CAM_UTIL_SENS] → [CAM_UTIL_ADJ]/[CAMERA_ADJ]`: el callback de BKID (`0x439012d0`) llama a
   `0x43900e30` («Utility MS Mount Start») en `0x439012fa` y a `0x43900f18` («Utility MS UnMount
   Start») en `0x43901302`; ambas despachan por `0x439009f0`, el despachador de `[CAM_UTIL_ADJ]`,
   con los ids de comando `6` y `7`.

Es decir: el gestor de ajuste pide al gestor «MS» que notifique el evento, y este último avisa de
un cambio de BKID, que a su vez monta/desmonta el servicio. **Ciclo de servicio cerrado entre los
dos módulos.**

### 6.3 Con los comandos «Sens»

La **tabla de comandos «Sens»** (51 entradas de 12 B `{cmd u32, size u32, str_ptr u32}` en
`0x43fe858c`, A6000) es **común a los tres firmwares** (S143) y su vocabulario es:
`TskJob*`, `SaveUsr:*` (POFF/POW/CAM), `Sens:Bk*` (escritura/sincronización de **bloques**),
`Sens:AdjCmd CAIF` / `Sens:AdjCmd DwnCamera` / `Sens:DwnCamera Done` (descarga de calibración),
`Sens:RAM Write` / `Sens:RAM Read` y códigos de error (`Sens:Invalid block/code/offset/size`,
`Sens:Read only`, `Sens:Write only`, `Sens:no buf`, `Sens:System error`).

- **Ninguna** de esas 51 entradas tiene que ver con la apertura de ficheros de la memoria interna
  («Debug IM …», «SET FILE NUM»): son el canal de **escritura de bloques/calibración** del sensor,
  no el canal de ficheros.
- La relación con `[CAM_UTIL_SENS]` es de **capas vecinas**, no de canal común: ambos escriben en
  la RAM del sensor, pero por caminos distintos (el canal «Sens» va por el driver del sensor
  `amSens*`; `[CAM_UTIL_SENS]` va por el bloque de parámetros global + mensaje OSAL).
  **NO VERIFICADO** que el bloque de parámetros `0x43f062c8` termine en el mismo destino que el
  canal «Sens».

### 6.4 Vecindario de código (banda `0x43900000`–`0x43910000`, regla estricta)

| prefijo | cadenas | funciones |
|---|---|---|
| `(sin etiqueta)` | 274 | 119 |
| `[CAM_DMM]` (S113) | 54 | 14 |
| **`[CAM_UTIL_SENS]`** | **21** | **5** |
| `[CAM_UTIL_ADJ]` (S143) | 22 | 3 |
| `[CAM_UTIL]` | 7 | 5 |
| `[ZPD]` | 5 | 4 |
| `[CAMERA_ADJ]` | 3 | 3 |

---

## 7. Interés para la línea del obturador (iris / ISO / shutter / lectura del sensor)

**Veredicto: el módulo NO pasa tiempos de obturación, iris, ISO ni parámetros de lectura al sensor.**

Criterio y evidencia:

1. **Vocabulario**: las 21 trazas usan exclusivamente `BKID`, `Size`, `SWFLG`, `MODEFLG`,
   `FileNum`, `Adr`, `Size`, `Flg`, `MountSTAT`, `FsysMode`, `FILE_NUM`, `ADR`, `SIZE`, `STAT`,
   `FSYSMODE`, `SndMsgErrInfo`, `RcvMsgErr`, `CID`, `ErrInfo`, `CALL BACK NULL`. No aparece
   **ninguna** palabra de obturación, iris, ISO, exposición, obturador electrónico ni tiempo de
   exposición.
2. **Negativo automático**: recalculado sobre las 21 cadenas del módulo **y** las 47 cadenas
   referenciadas por el código de la banda `0x43901000`–`0x43902610` (tokens `shut`, `shutter`,
   `iris`, `aperture`, `iso`, `exposure`, `exp.`, `silent`, `elec`, `efcs`, `frame`, `fps`,
   `speed`): **0 coincidencias** (campo `negativo_obturador_iris_iso` del JSON, objeto vacío).
3. **Destinos de llamada** de las 5 funciones: sólo `0x4356120c/0x43561260/0x435612d0/0x435612ec`
   (OSAL: enviar/recibir/liberar/asignar mensaje), `0x43561324`/`0x43561394` (thunks de vtable),
   `0x439c5004` (formatear), `0x439c5320` (memcpy), `0x43b2a18e` (stub), y ayudantes **propios del
   módulo o de sus hermanos ADJ**. **Ninguna** API de obturación, iris o ISO.
4. **Los datos que transporta** son de fichero de memoria: número de fichero, dirección, tamaño y
   un estado (`Flg`/`MountSTAT`/`FsysMode`). Un control de exposición en un cuerpo con obturador
   electrónico seguiría por `[IMAGING_CAP]` (S106) / el driver del imager (S115), no por aquí.
5. **Matiz importante**: el módulo *sí* escribe **dentro** del sensor (fichero de memoria interna),
   y por tanto en un cuerpo con más funciones podría coincidir con algún parámetro. Pero este
   módulo **no sabe qué contiene** el fichero: sólo reenvía `FileNum`/`Adr`/`Size`. Qué datos se
   volcan (RAW, YC, miniRAW) lo decide el llamador (`MemAreaMSDebug`, `SACC_Debug`, `IDT`).
   → **Sin efecto en S51 (A/B/C = NO).**

---

## 8. Diferencial A6000 fw3.21 / A7S fw3.20 / A6300 fw2.01

### 8.1 La etiqueta `[CAM_UTIL_SENS]` es **propia de la A6000 fw3.21**

| marcador | A6000 fw3.21 | A7S fw3.20 | A6300 fw2.01 |
|---|---|---|---|
| token `[CAM_UTIL_SENS]` | **21** | **0** | **0** |
| interiores de las 21 trazas presentes | 21/21 | **0/21** | **0/21** |
| `UTIL MS Mgr` | 2 | 0 | 0 |
| `Debug IM ASync Open` | 3 | 0 | 0 |
| `Debug IM Sync Open` | 3 | 0 | 0 |
| `SET FILE NUM` | 2 | 0 | 0 |
| `CB for BKID change` | 1 | 0 | 0 |
| `SWFLG` / `MODEFLG` | 1 / 1 | 0 / 0 | 0 / 0 |
| `FileNum` / `MountSTAT` / `FsysMode` | 2 / 1 / 1 | 0 / 0 / 0 | 0 / 0 / 0 |
| `CALL BACK NULL` | 1 | 0 | 0 |
| `[CAM_UTIL_ADJ]` (S143) | 22 | 0 | 0 |
| `[CAM_UTIL]` / `[CAMERA_ADJ]` | 10 / 3 | 0 / 0 | 0 / 0 |

### 8.2 Pero la **funcionalidad sí existe en los otros dos firmwares**

| marcador | A6000 | A7S | A6300 | lectura |
|---|---|---|---|---|
| `cam_util_debug_file_write` | **3** | **2** | **2** | la función que usa este módulo ya existe en los tres cuerpos (en la A6000 hay una 3.ª mención «CCC: ## Error : cam_util_debug_file_write : %d») |
| `MemAreaMSDebug` | 4 | **4** | **10** | la vía de volcado «MS Debug» ya existe en los tres |
| `WiriteMsDebug` | 1 | 1 | 1 | ídem |
| `BKID` | 28 | 23 | 22 | el concepto de bloque del sensor es común |
| `Sens:` (canal de comandos) | 27 | **27** | **27** | la capa de comandos «Sens» es idéntica en los tres |

→ **Conclusión**: lo nuevo en la fw3.21 de la A6000 es la **instrumentación** (la etiqueta
`[CAM_UTIL_SENS]` y sus 21 mensajes), no la función. Es el mismo patrón que S143 con su hermano
`[CAM_UTIL_ADJ]`, S120 (`[IDT_OPD]`) y S126 (`[CAMERA_MAIN]`): **etiquetado nuevo, misma lógica**.
Lo que **no** se ha verificado es si el *código* equivalente existe con otro nombre en A7S/A6300
(no se ha re-mapeado el árbol de llamadas de esos binarios) → **NO VERIFICADO**.

---

## 9. NO VERIFICADO / abierto

1. **Qué es «IM»** y **qué es «MS»**: el firmware usa las siglas sin desarrollarlas en ningún byte
   (`IM ASync/Sync Open`, `UTIL MS Mgr`, `Utility MS Mount/UnMount`, `MemAreaMSDebug`,
   `MS_Writer`). **No se desarrolla la sigla.** Lo único comprobable es el término completo
   `cam_util_debug_file_write` (nombre de función en un mensaje de error).
2. **Naturaleza de la tabla de punteros de `0x44022d84`**: se sabe que contiene `0x439012d1`
   (el CB de BKID) y muchos otros punteros a función; no se ha averiguado si es una *vtable* de C++
   o un registro de callbacks. **NO VERIFICADO**.
3. **Significado de `BKID`, `SWFLG`, `MODEFLG`, `MountSTAT`, `FsysMode`, `Flg`**: los prints los
   nombran; su semántica y el bloque del sensor al que corresponden, **NO VERIFICADOS** en este
   hito.
4. **Los 51 comandos «Sens»** (S143) no contienen ninguna entrada de apertura/lectura de ficheros
   de la memoria interna; **no se ha identificado** el canal exacto por el que «Debug IM Open» y
   «SET FILE NUM» llegan al driver del sensor. **NO VERIFICADO**.
5. **Las trazas «… OSAL MEM ALLOC Error : %x»** se emiten en la rama de **éxito** de la reserva de
   memoria (verificado en `0x43901e06` y `0x43901f8c`); la intención del firmware es
   **NO VERIFICADA** (¿mensaje reutilizado?).
6. **Id de comando `0x63`** que comprobaba el despachador `0x4378947c` antes de llamar a
   `0x43902418`: sin decodificar. **NO VERIFICADO**.
7. **Contenido de la plantilla de 12 B** del mensaje OSAL: la base `0x43f062c8` está **a cero en el
   fichero** (se inicializa en runtime); no se ha averiguado quién la rellena ni con qué valores.
   **NO VERIFICADO**. (La tabla estática `{0x00e200e1, 0x00e400e3, 0x00e600e5}` de `0x43c04d70`,
   citada en S143, es un objeto distinto.)
8. **Presencia del código equivalente** en A7S fw3.20 y A6300 fw2.01: sólo se ha comprobado la
   *funcionalidad* por marcadores de texto (§8.2); no se han re-mapeado las llamadas.
   **NO VERIFICADO**.
9. **Fichero fuente**: no consta (§5).

---

## 10. Revisión del agente principal

*(vacío — pendiente de revisión)*

---

## Reproducir

```bash
.venv/bin/python analysis/s144_cam_util_sens/scan_s144.py        # -> cam_util_sens.json
.venv/bin/python analysis/s144_cam_util_sens/scan_callers.py 0x439012d0 0x43901d50 0x43902168 0x439023b8 0x43902418
.venv/bin/python analysis/s144_cam_util_sens/dasm.py 0x439012d0 0x43901380
.venv/bin/python -m pytest tests/test_s144_cam_util_sens.py -q
```

---

## Revisión del agente principal (22-10-2026)

**Verificado y aceptado (22 tests del hito + comprobaciones a mano):**

1. **Recuento y rango**: 21 apariciones de `[CAM_UTIL_SENS]` en la A6000 fw3.21 entre
   `0x43cce1ea` y `0x43cce66b`; **0** en la A7S fw3.20 y el A6300 fw2.01 → la etiqueta es **propia
   de la fw3.21**; en el bloque hay además 3 cadenas `[CAM_UTIL]` intercaladas (`0x43cce282`–`0x43cce2f3`).
2. **Estructura verificada**: 21/21 referenciadas con **39 sitios** (regla estricta) en **5
   funciones** — `0x439012d0` (CB de BKID), `0x43901d50` (Debug IM ASync Open, con camino sync en
   `0x43901ef8`), `0x43902168` (SET FILE NUM), `0x439023b8` (UTIL MS Mgr Call CB) y `0x43902418`
   (Debug IM Sync Open) — más los globales `0x43f062c8` (plantilla), `0x43fa29f0` (MountSTAT),
   `0x43fa2d23` (Flg), `0x43f062d4` (puntero al callback del gestor MS) y la tabla de objetos
   `0x4401eee4`.
3. **Dependencia cruzada ADJ↔SENS verificada**: ADJ→SENS en `0x43900c9c` y SENS→ADJ/`[CAMERA_ADJ]`
   en `0x439012fa` (Mount) y `0x43901302` (UnMount) → los dos módulos de S143/S144 son **el mismo
   par**: la vía de ajuste hacia el sensor.
4. **Ids OSAL compartidos** con `[CAM_UTIL_ADJ]`: log `0x008f0139`, comando `0x008f013a`, id de
   módulo `0xb5` → confirma que ADJ y SENS son dos vistas del mismo gestor.
5. **Diferencial**: la etiqueta es 21/0/0 y los interiores 0/21 y 0/21, **pero la funcionalidad sí
   existe en los tres** (`cam_util_debug_file_write` 3/2/2, `MemAreaMSDebug` 4/4/10, `Sens:` 27/27/27)
   → lo nuevo en la fw3.21 es la **instrumentación**, no la función.
6. **Negativo acotado**: 0 coincidencias de `shut`/`iris`/`iso`/`exposure`/`silent`/`elec`/`efcs`/`fps`
   en las 21 trazas ni en las 47 cadenas de la banda `0x43901000`–`0x43902610`; los únicos destinos
   de llamada son OSAL, thunks y memcpy → **sin efecto en S51**.
7. **Detalle útil para el resto de la línea**: las **17 llamadas** a `0x43901d50` desde
   `[CAMERA_MAIN_LC]`, `[IMAGING_CAP]`, `[CAMERA_MAIN_TC]`, `[CAMERA_MAIN_YC]`, `[IDT]`/`[IDT_OPD]`
   identifican `cam_util_debug_file_write` como la pieza que **vuelca imagen (RAW/YC) en la memoria
   del sensor** → es un sumidero de depuración transversal, no un módulo de captura.
