# S66-C — Lente: ruta de FW-update, bus BonoboDSP, bus cuerpo↔lente y A6000 vs A7S

Todo lo siguiente está verificado por desensamblado Capstone + búsqueda exacta de bytes
sobre `av-cam.bin` (A6000, base lógica `B = 0x43541000`, sha256 `b60c845ccb90…`) y, para la
comparación, sobre el `av-cam.bin` de A7S (`firmware/extracted/a7s-fw320/…/av-cam.bin`).
Marca temporal de la evidencia: sesión actual. Herramientas: `analysis/s58/tdis.py`,
`analysis/s66/{lens_strings_addr,pic_refs}.py`.

Convención: **VERIFICADO** = leído en bytes/instrucciones reales; **INFERENCIA** = deducción
a partir de verificados (se indica el salto); **NO_VERIFICADO** = no confirmado aún.

Direcciones de cadena halladas SIEMPRE por `.find()` de bytes exactos, nunca aritmética.

---

## 1. Ruta de actualización de firmware de la lente

### 1.1 Emisor de firmware `[BL]` por CAIF/C3P — `0x436fe070`
Función (cluster `0x436fe070–0x436fea24`). `r0` = contexto; lee `state = *(u8*)(ctx+2)` y
bifurca en 3 casos (`0x436fe08e`: `cmp r5,#4; beq`, `cmp r5,#6; beq`, `cmp r5,#0`):

- **state 0** (`0x436fe09c`): prepara cabecera `u16` a `-1`, y llama al **envío asíncrono CAIF**
  `bl 0x436ba2c8` con argumentos **`(9, 1, 4, buf+4)`** → mensaje "LUPDT_INFO". Si falla, log
  `[MOUNT_ERROR]: [BL]FirmUp Error : CAIF CASND LUPDT_INFO` (cadena `0x43c9a09f`, ref PIC en `0x436fe0c0`).
- **state 4** (`0x436fe0cc`): transfiere un chunk de firmware. `ldr r2,[r5,#8]; subs r2,#1` y compara
  con el índice actual → calcula bandera fin (`ite gt`). Copia `0x100` bytes (`mov r2,#0x100; blx 0x439c5320`
  = memcpy) con destino `smlabb r1,r3,r1,r2` (offset = índice × 0x100). Luego llama
  `bl 0x436ba2c8` con **`(9, 5, 0x104, buf)`** → mensaje "LUPDT_DATA". Fracaso ⇒ log
  `FirmUp Error : CAIF CASND LUPDT_DATA` (`0x43c9a0d7`, ref en `0x436fe11e`).
  ⇒ **VERIFICADO**: el payload LUPDT_DATA mide `0x104` B = 4 B cabecera + `0x100` B de datos.
- **state 6** (`0x436fe12e`): sólo devuelve código (sin enviar). Salida unificada vía
  `b.w 0x436fe994` = **`LensFirmUpdateResult`** (ver 1.4).

Registro de chunk: `u16` en `buf[0]` (contador, `strh`/`uxth`), `u8` fin en `buf[2]`.

### 1.2 Despachador UUD (`UUD CallBack`) — `0x436fe500`
`tbb [pc, r3, lsl #1]` sobre `msg = *r0`, con `cmp r3,#4; bhi` ⇒ **5 mensajes (0..4)**. Refs de
cadenas verificadas por `pic_refs` (string → `add rd,pc` → caso):

| msg | log | string | ref |
|-----|-----|--------|-----|
| 0 | `UUD CallBack : MSGID_GET_VERSION` | `0x43c98201` | `0x436fe64a` |
| 1 | `UUD CallBack : MSGID_GET_FORCE_FIRMUP` | `0x43c98234` | `0x436fe672` |
| 2 | `UUD CallBack : MSGID_FIRM_UP_REQ` | `0x43c9826c` | `0x436fe726` |
| 3 | `UUD CallBack : MSGID_PREPARE_UPDATE` | `0x43c9829f` | `0x436fe80c` |
| 4 | `UUD CallBack : MSGID_UNPLUG_USB` | `0x43c982d5` | `0x436fe842` |
| def | `UUD CallBack : meg_id illegal` | `0x43c98307` | `0x436fe856` |

⇒ **VERIFICADO** el mapa CMD_ID entrante (la lente llama a la cámara con estos 5 IDs).

### 1.3 Recepción de comandos de actualización `[L->B]` (montura)
Función de cola `0x436e540c(state)` (estados 0..5, `cmp r0,#5; bhi`); guardado global y
`bl 0x435612d0` (asignador/cola CAIF). Receptores que la invocan:

- **`[L->B]UPDATE_ON`** — `0x436e54aa` (ref string `0x43c97eb8`). Extrae payload vía
  `bl 0x43ad9d58` (deque), comprueba `ldrb [r3,#1]`, y llama `bl 0x436e540c(1)`. Log de confirmación
  `[L->B]UPDATE_ON` (`0x43c97eb8`) / error `[L->B]UPDATE_ON_NG` (`0x43c97ed9`).
- **`[L->B]UPDATE_DATA`** — `0x436e54f8` (refs `0x43c97efb`, `0x43c97f1c`). `movs r2,#0x15` y
  `bl 0x43ad9d58` ⇒ **el ID de comando en la cabecera es `0x15`**. Hace `bl 0x436e540c(2)`.
  ⇒ INFERENCIA (por el literal `0x15` y el nombre): encola los chunks que luego el emisor `0x436fe070`
  (state 4) reenvía por CAIF.
- **`[BL]PREPARE UPDATE CHECK`** — `0x436e55b8`. Máquina con `ldr r3,[r4,#0x14]; cmp r3,#1` y
  dispatch por `ldrb [r4]` sobre valores `0x13`, `5/6`, `0xfe`, `0xff` (`0x436e55d8–0x436e55ee`).
  Estados destino `0x436e5602` / `0x436e5612`.

### 1.4 `LensFirmUpdateResult` — `0x436fe994`
Punto de salida común del emisor. Cadenas asociadas (todas presentes, verif. por `.find`):
`LensFirmUpdateResult : Error Code = %d` (`0x43c9…`), `: Illegal Error Code = %d`, y las de
`GetLensVersion Error : ERRCD_FIRMUP_UNSUPPORT / FIRM_ERROR / LENS_UNMOUNT`,
`FirmUpReq Error : ERRCD_FIRMUP_BUSY / PARAM_ERROR / CAIF REQ ERROR`. ⇒ **VERIFICADO** existencia
y uso en la ruta; el mapeo numérico concreto de `Error Code` es NO_VERIFICADO.

### 1.5 Constructores de trama de update/monitor `[B->L]` (montura → lente)
Todos terminan en `bl 0x436e1254(buf, descriptor)` (ensamblador de trama, ver §2). El **ID de
comando va en el primer byte del payload**:

| cmd byte | función | log (string @ dir) |
|----------|---------|--------------------|
| `0x07` | `0x436e4444` ATTACH_INFO1 | `[B->L]ATTACH_INFO1` `0x43c978f9` |
| `0x15` | `0x436e4800` UPDATE_DATA (payload `0x400` B) | `[B->L]UPDATE_DATA` |
| `0x16` | `0x436e472c` LENS_SLEEP | (log cmd `0x1003`) |
| `0x2B` | `0x436e509c` ALPHA_LENS_INFO | `[B->L]ALPHA_LENS_INFO:%d` `0x43c97dd6` |
| `0x0A` | `0x436e51ac` CS_CREDIT | `[B->L]CS_CREDIT=%d` `0x43c97e00` |
| — | `0x436e4b24` CS_CHECK_CMD (payload `0x20`) | — |
| — | `0x436e5088` CS_CREDIT `[L->B]` recv | `[L->B]CS_CREDIT` `0x43c97db7` |

`0x436e4800` (UPDATE_DATA): `sub sp,#0x408`, `memset(sp,0,0x408)`, `movs r3,#0x15; strb [r0],#8`
(escribe `0x15` en `[buf+0]`), luego `mov r2,#0x400; blx 0x439c5320` (memcpy de 1024 B) ⇒
**VERIFICADO**: payload de `0x400` B tras 8 B de cabecera.

### 1.6 CS_CREDIT y LIF CREDIT
- **CS_CREDIT `[B->L]`** — `0x436e51ac`: `movs r3,#0xa; strb r3,[r0,#-0x14]!` ⇒ **cmd byte `0x0A`**.
  Dispatch por `cmp r6,#1 / cmp r6,#2`; copia 8+8 B con `blx 0x439c5320` (memcpy). Log
  `[B->L]CS_CREDIT=%d`.
- **CS_CREDIT `[L->B]`** — `0x436e5088`: recibe, log `[L->B]CS_CREDIT`. ⇒
  INFERENCIA: intercambio de "crédito" de flujo CS (chip-select / clock) cuerpo↔lente.
- **LIF CREDIT** — `0x436e37ea` (ref string `0x43c971b4`): log
  `[BL ERR]LIF CREDIT RegistErro Lens doesn't know = %d`. La función `0x436e3754` es el helper.
- **LIF Command Change** — `0x436e2e50` (ref `0x43c970c7`): log `LIF Command Change : 0x%X >>> 0x%X`.
  Lee un `u16` en `[ctx+0x24]`, hace `sub r2,r3,#0xc00; cmp r2,#7; bhi; tbb [pc,r2]` ⇒
  **dispatch de comandos LIF sobre el rango `0xC00..0xC07`** (verif.: `movw r2,#0xc00`,
  `movw r1,#0xc02`, `movw r2,#0xc03`). ⇒ VERIFICADOS el rango y el `tbb`; el semántico de cada
  sub-comando es INFERENCIA.

### 1.7 Capa CAIF/C3P de envío asíncrono — `0x436ba2c8`
`0x436ba2c8(r0=tag, r1=cmd, r2=len, r3=data)`:
- `bl 0x435612d0` (asigna `0x14`=20 B, `r3=1`).
- Rellena: `strb r2(=2) [p]`, `strb r6(tag) [p+5]`, `adds r2,#0xee; strb r2 [p+4]` (⇒ `[p+4] = 0xF0`
  cuando `r2=2`, byte de **cabecera Darwin/CAIF**), `strb r5(cmd) [p+6]`, `strh r4(len) [p+8]`,
  `str r7(data) [p+0xc]`.
- `bl 0x4356120c` ⇒ despacha por vtable `[obj+0x14]` → `ldr r3,[r3,#0x1d4]; blx r3` (ver §2, es la
  misma familia de stubs `0x4356120c/0x43561228/…` con offsets `0x1d4/0x1d8/0x1dc/0x1e0`).

⇒ **VERIFICADO** que el update de firmware viaja por el canal **asíncrono CAIF/C3P** (tag 9) con
byte de cabecera `0xF0`, cmd en `[p+6]`, longitud u16 en `[p+8]` y payload en `[p+0xc]`. El destino
final (MCU vs bus de lente) queda **NO_VERIFICADO** (coincide con el antecedente S53 sin cerrarse).

---

## 2. Formato de trama del bus cuerpo↔lente (análisis `0x436e2700–0x436e2854`)

Analizador de trama recibido. Estructura derivada de las instrucciones (VERIFICADO):
- `ldrb r2,[r5]` ⇒ **cabecera `0xF0`** (`cmp r2,#0xf0; beq`). Fallo ⇒ log `[BL]HEADER_NG`
  (`0x43c96dda`, refs `0x436e2746/0x436e2750`), código de error `r0=3`.
- Longitud: `ldrb [r5,#2]` desplazada 8 (`lsl.w r8,r8,#8`) + `ldrb [r5,#1]` ⇒ **u16 big-endian** en
  los bytes +1..+2 (`uxth`). ⇒ longitud = `(len_hi<<8)|len_lo`.
- **Pie**: `ldrb [r3,#2]` de la última posición, `cmp r3,#0x55; beq` ⇒ **`0x55` de cierre**. Fallo ⇒
  `[BL]FOOTER_NG` (`0x43c96df7`, refs `0x436e2770/0x436e277a`), `r0=5`.
- **Checksum u16**: `sub r1,r8,#4` (longitud−4) y `bl 0x43ada0a8` (función checksum, que a su vez
  `b.w 0x43b7b25e`). Compara con `sb` (los 2 bytes antes del pie). Fallo ⇒ `[BL]CHECKSUM_NG`
  (`0x43c96e14`, refs `0x436e27b2/0x436e27bc`), `r0=4`.
- **CommType**: `ldrb r3,[r5,#3]; and r3,#7; subs r3,#1; cmp r3,#2; bls` ⇒ campo de 3 bits en el
  byte +3, valores válidos **1..3** (`1`,`2`,`3`). Fuera ⇒ `[BL]COMMTYPE_NG` (`0x43c96e52`,
  refs `0x436e280c`), error `r0=7`, y `str r3(=6),[sp,#0x28]`. Un segundo paso (`0x436e282e`) exige
  `commtype==1` para el sub-caso `r2=1`.
- Existe también `[BL]DATASIZE_NG` (`0x43c96e33`) para longitud inválida.

Resumen de trama: **`[0xF0][len_hi][len_lo][commtype&7 …][payload …][cksum_hi][cksum_lo][0x55]`**,
con checksum de `len−4` bytes y commtype∈{1,2,3}. ⇒ **VERIFICADO** (esto cierra el hueco que
`docs/capture/s66-lens-mount.md` §4 marcaba como "formato NO determinado"; ver §5.

---

## 3. Handshake físico cuerpo↔lente (CS/DATA, CHG FREQ, UART, VSYNC)

### 3.1 Mando por CS/DATA (máquina `tbb`) — `0x436e48fc`
`tbb [pc, r3]` sobre `ldr r3,[r6,#0x10]; cmp r3,#3` ⇒ **4 estados**. Cada rama imprime un log y
llama `bl 0x436e41e4` (logger de montura, `r0=0x125`). Cadenas verificadas por `.find` + ref:
- estado 0: `[BL][HS]CS_HIGH` (`0x43c97ac6`, refs `0x436e4938`, `0x436e4da2`)
- estado 1: `[BL][HS]DATA_HIGH` (`0x43c97ae5`)
- estado 2: `[BL][HS]CS_LOW` (`0x43c97b06`)
- completo: `[BL][HS]COMPLETE` (`0x43c97b24`, refs `0x436e49f6`, `0x436e4e20`)

Secuencia de tiempos con `movw r0,#0x1388` (=5000, ms de espera). ⇒ **VERIFICADO**: el handshake
[HS] alterna CS_HIGH → DATA_HIGH → CS_LOW → COMPLETE (protocolo de 2 líneas CS + DATA).

### 3.2 UART a 750 / 1500 Hz — `0x436e65bc`
Referencia la cadena `[BL]UART_HZ 750:%d 1500%d` (`0x43c98540`, ref `0x436e65bc`). Estados
mediante `bl 0x436e4eb4; cmp r0,#0; ite eq moveq r6,#3 / movne r6,#1`. Log de fallo
`[L->B]UART_HZ NG` (`0x43c98569`, refs `0x436e6634/0x436e6642` vía `print 0%d`). Cadena
`750:%d 1500%d` (`0x43c9855b`) ⇒ dos buckets de frecuencia. Completado:
`[BL]UART_HS_COMPLETE` (`0x43c985b9`) y `…NO_WAIT` (`0x43c9858d`).
⇒ **VERIFICADO** la existencia de la conmutación 750/1500 y del HS_COMPLETE; los valores exactos
de 750/1500 como inmediatos en esta función son **NO_VERIFICADOS** (no aparecen `movw #0x2ee/#0x5dc`
en el rango montura; sólo el formato de log los nombra).

### 3.3 CHG FREQ (cambio de frecuencia) — `0x436e5b7e`
Referencia `[BL]CHG FREQ, %d, %d, %d` (`0x43c983cd`, ref `0x436e5b7e`). La función
(`0x436e5b40`) compara `cmp r2,#1`, escribe estructura `{freq_now, freq_send, …}` y llama al
logger con 3 args en stack (`str r2,[sp]; str …,[sp,#4]; str …,[sp,#8]`).
- Espera asociada: `[BL]FREQ Now:%d, Send:%d` (`0x43c98955`, ref `0x436e7410` en `0x436e73b0`).
- Estados de espera (`0x436e73b0–0x436e7410`): `[BL]WAIT CHGFREQ2` (`0x43c98915`), `[BL]WAIT NEXTVD`
  (`0x43c98936`), con `str r3(=5/6),[r4,#8]` como selector de estado.
⇒ **VERIFICADO** la máquina de cambio de frecuencia con espera a CHGFREQ y a **NEXTVD (next VD =
próximo barrido vertical)**; el rol concreto de VSYNC como referencia de temporización es
INFERENCIA (el nombre NEXTVD + `ECLIPSE_COM_STATE is INIT in VSYNC`, ver §3.5).

### 3.4 System Hz — `0x436e4528`
Referencia `[BL]SYSTEM_HZ:%d` (`0x43c9795f`, ref `0x436e4528`). ⇒ VERIFICADO existencia del
registro de frecuencia de sistema.

### 3.5 EclipseDataComState (estado de comunicación de datos con la lente)
Estado global; setter `0x436e3bc8` (log `[BL]EclipseDataComState [%d] => [%d]`, `0x43c9734d`, ref
`0x436e3be0`). Otros puntos:
- `0x436e3f2c` — log `…from STANDBY to START` (`0x43c976d3`) y `[BL]ZPD change … STANDBY to START`
  (`0x43c976b5`, ref `0x436e3f2c`) ⇒ transición **STANDBY → START** disparada por **ZPD** (zero
  power detect / detección de presencia de lente).
- `0x436e3f48` — `Mount_InitializeEclipseComState` (log `0x43c976fd`, `0x43c97754`:
  `Mount_EclipseComInit Mount_DividedInfo.cpp line %d`).
- **`0x436e3b82`** — log `[MOUNT_ERROR]: [BL]ECLIPSE_COM_STATE is INIT in VSYNC at
  Mount_DividedInfo.cpp %d` (`0x43c972fb`, ref `0x436e3b82`); usa `movs r4,#0xdb` (línea 219) y
  `b.w 0x43902718` (print). ⇒ **VERIFICADO** que el estado Eclipse se consulta en cada **VSYNC** y
  que `INIT` es un estado temprano anómalo ahí.
- Estados nombrados: `STANDBY` (`0x43c976ec`, `0x43c97a9d`, `0x43c98990`), `START` (en los mensajes
  anteriores). El resto de la enumeración numérica es **NO_VERIFICADO**.

---

## 4. Bus BonoboDSP `[LENS_PDR]`

Cluster `0x437089da–0x43708c36`. Cadenas (prefijo `[LENS_PDR]`, `.find` exacto):
- `BonoboDSP_Send: Data latch failed!` `0x43c9a7ca` (ref `0x43708a5c`)
- `BonoboDSP_Send:[ch0]Data latch failed!` `0x43c9a7fa` (ref `0x43708b78`)
- `BonoboDSP_Send:[ch1]Data latch failed!` `0x43c9a82e` (ref `0x43708be6`)
- `BonoboDSP_Rcv: paritycheck_error!` `0x43c9a862` (ref en `0x43708c1c`, vía el despachador)

### 4.1 Getter de canal (2 canales) — `0x437089d4` / `0x437089da`
Lectura de un registro: `ldrb r2,[r3]; and r2,#4; rsbs r2,r2,#1; it lo movlo r2,#0` (bit 2 ⇒ flag).
Construye campos **u32 big-endian de 3 bytes**: `ldrb [r3,#5/#6/#7]` con `lsl #0x10 / #8` ⇒
`val = (b5<<16)|(b6<<8)|b7` → `[out+4]`; luego `[r3,#9/#0xa/#0xb]` → `[out+8]`; `[r3,#0xc/…]`…
⇒ **VERIFICADO** lectura de sensores de 3 bytes BE por canal.

### 4.2 Parseo de respuesta — `0x43708a88` / `0x43708a8e`
Parsea una respuesta de **`0x22` = 34 B** con `bl 0x43adcaca` (parser de bus). Determina canal:
`ch0 = sp[7] & 4`, `ch1 = sp[7] & 8` (según hallazgo previo). Logs `[ch0]`/`[ch1]` en `0x43708b78`/
`0x43708be6`. Camino de paridad → `0x43708c1c` `paritycheck_error`.

### 4.3 Despachador y empaquetado — `0x43708cc4`, `0x43708c74`
- `0x43708cc4`: msg tipo 2 → subtipo 1 ⇒ `0x437089d4` (getter), subtipo 2 ⇒ `0x43708a88` (parseo).
- `0x43708c74`: empaquetado de 0x20+ B (campos en `[r1+0x4..0x29]`).

### 4.4 Capa física / MMIO
- Literal **`0xf292d000`** (dirección de periférico) en `0x437072a8` (y contexto en `0x43707280`).
  ⇒ INFERENCIA: base MMIO del DSP/transporte.
- Rutas de envío (`0x43708480–0x4370855a`, `0x43708300–0x4370836e`) usan `ldr r0,[pc,#…] #0x740017`
  y `bl 0x43561228` / `bl 0x4390406c` (mismos stubs de envío CAIF/C3P, vtable `+0x1d8`) ⇒
  el tráfico DSP también pasa por el canal de mensajes CAIF/C3P. El "latch failed" se señala con
  `movs r0,#0x16` (código) y `bl 0x43707324`.
- Propósito: INFERENCIA parcial. Dos canales (ch0/ch1) con sensores de 3 B y paridad; la región
  `0x43c9f7…` en A6000 contiene nombres de lentes, y `[LENS_PDR]` sugiere *Lens Power/Position Data
  Register*. Rol exacto (¿AF/óptica? ¿sensores de la lente?) **NO_VERIFICADO**.

---

## 5. Comparación A6000 vs A7S

Mapeo de direcciones A7S confirmado por `.find`: las strings A7S están en un rango distinto
(p. ej. LUPDT_INFO: A6000 `0x43c9a09f` vs A7S `0x43c9f7ff`; BonoboDSP A7S `0x43ca167b–0x43ca16ef`).

| Subsistema | A6000 | A7S |
|------------|-------|-----|
| `[MOUNT_]` (prefijo completo `[MOUNT_DEBUG]/[MOUNT_ERROR]…`) | **223** | **0** |
| `[BL]` (sin prefijo de módulo) | presente | **75** |
| Ruta FW-update (`FirmUp/LUPDT/FirmUpReq/GetLensVersion/LensFirmUpdateResult`) | sí | **SÍ** (p.ej. `LUPDT_INFO` `0x43c9f7ff`, `PREPARE UPDATE TIME_OUT` `0x43ca0fc1`, `UUD CallBack : meg_id illegal` `0x43ca0ff0`, `LensFirmUpdateResult` `0x43ca100b`, `FirmUpReq Error` `0x43ca0f2f`, `GetLensVersion Error` `0x43ca111e`) |
| `PREPARE UPDATE REQ/OK/NG`, `MSGID_*` literales | sí | **NO** (sólo TIME_OUT e `meg_id illegal`) |
| `UPDATE_ON/DATA`, `CS_CREDIT`, `LIF CREDIT`, `LIF Command Change` | sí | **NO** |
| `UART_HZ` | `[BL]UART_HZ 750…` + NG | sólo `[BL][L->B]UART_HZ NG` (`0x43ca1239`) — **sin** el de 750/1500 |
| `[HS]CS_HIGH/DATA_LOW/…` | sí | sólo `[BL][HS]POWER SEQ / POWER OFF SEQ TIME OUT` (`0x43ca1069/0x43ca1084`) |
| `CHG FREQ`, `EclipseDataComState`, `SYSTEM_HZ`, `NEXTVD` | sí | **NO** |
| `[LENS_PDR]:` (prefijo) | 4 | **0** |
| `BonoboDSP_Send/Rcv` (cadenas) | 4 (con `[LENS_PDR]:`) | **4 (sin prefijo)**: `BonoboDSP_Send: Data latch failed!` `0x43ca167b`, `[ch0]` `0x43ca169f`, `[ch1]` `0x43ca16c7`, `Rcv: paritycheck_error!` `0x43ca16ef` |

Conclusión: **A7S conserva el subsistema de actualización de firmware y el bus BonoboDSP, pero NO
tiene** el prefijo de depuración `[MOUNT_DEBUG]`, ni el handshake de montura detallado
(CS/DATA `[HS]`, CHG FREQ 750/1500, EclipseDataComState, NEXTVD), ni los comandos CS_CREDIT / LIF
/ UPDATE_ON / UPDATE_DATA. ⇒ INFERENCIA: A7S (cuerpo menor/otra gama) usa un protocolo de montura
más simple (sólo power-seq y UART_HZ NG), compartiendo la capa BonoboDSP y la ruta CAIF de firmware.
El código A6000 del emisor/dispatcher no se pudo contrastar byte-a-byte con A7S porque A7S no expone
esas funciones bajo las mismas cadenas (el cluster A7S de FW-update vive en otra región y no se
localizó su función equivalente por PIC en esta sesión) ⇒ comparación de código **NO_VERIFICADO**;
la comparación de cadenas/strings sí es **VERIFICADA**.

---

## 6. Notas de método y relaciones con otros hitos
- Formato de trama (§2) cierra el ítem "formato de trama y tabla nombre↔ID NO determinados" que
  `docs/capture/s66-lens-mount.md` §4 dejaba abierto, y añade la tabla cmd-byte↔función (§1.5).
- La capa de envío CAIF/C3P (`0x436ba2c8`, stubs `0x4356120c/228`) coincide con el antecedente S53
  (`docs/capture/s52-*.md`, `analysis/s53/`): byte de cabecera Darwin `0xF0`, cmd y longitud u16.
  El destino final del update (MCU vs bus de lente) sigue **NO_VERIFICADO** (mismo hueco que S53).
- Sesión REA (`run/rea.sock`) no estuvo disponible (demonio reiniciado por otros subagentes; análisis
  en frío ~8-10 min). Toda la evidencia es por Capstone+bytes, sin depender de REA.
