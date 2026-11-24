# G22 — Ingeniería inversa de libObj.so (fw 3.21): LRM de ExcMgr, SetInit de ModelStillRec y EE_START

Binario analizado: `analysis/camera-extract/usr/lib/libObj.so` (md5 `eb12512e6b74a940f1ae6de1c38477db`). Copia idéntica en rangos citados en `analysis/gui/g22/files-363/lib/libObj.so` (difieren 446 B en otra zona, comprobado byte a byte).

Método: **REA no disponible** (el demonio `session_daemon.py` para `libobj.sock` arranca `open_binary` pero falla al iniciar el auto-análisis de Ghidra; socket existe pero no escucha). Se usó **análisis estático con Capstone** (Thumb mode) sobre `libObj.so`, verificando instrucciones y bytes reales. `llvm-objdump -d` no sirve directamente porque el código es Thumb y el desensamblador lineal no distingue modo ARM/Thumb sin símbolos.

Etiquetas: **VERIFICADO** = leído en instrucciones/bytes reales; **INFERENCIA** = deducido de evidencia estática coherente; **NO_VERIFICADO** = hipótesis sin prueba.

---

## 1. Cambio del modo LRM de ExcMgr de 0x60 → modo que permite EFCS (0x75fa) y zoom

### 1.1 Función que escribe [gestor+0] y [gestor+1]

**`0x9919f0`** — Función de transición de modo LRM de ExcMgr. Prologue Thumb:

```
0x009919f0: push.w {r4, r5, r6, r7, r8, sb, lr}   ; VERIFICADO
0x009919f4: sub sp, #0xc
0x009919f6: mov r4, r0                            ; r4 = puntero gestor (ExcMgr)
0x009919f8: add r7, sp, #8
0x009919fa: mov r0, r1                            ; r0 = argumento (mensaje)
0x009919fc: mov r6, r1
0x009919fe: blx #0xe00a4                          ; obtiene categoría del mensaje
0x00991a02: mov r8, r0
0x00991a04: mov r0, r6
0x00991a06: blx #0xe0a68                          ; obtiene ID del mensaje
0x00991a0a: mov sb, r0
0x00991a0c: bl #0x951494
0x00991a10: cmp.w r8, #0x3100                     ; solo categoría 0x3100
0x00991a14: mov r5, r0
0x00991a16: bne.w #0x991bc4
```

Switch sobre ID del mensaje (categoría 0x3100), con escritura de modo en `[gestor+0]`:

```
0x00991a1a: movw r3, #0x7504                      ; caso 0x7504
0x00991a1e: cmp sb, r3
0x00991a20: beq.w #0x991ba6
0x00991a24: bhi #0x991a36
0x00991a26: cmp.w sb, #0x7500                     ; caso 0x7500 = EE_START_CMD
0x00991a2a: beq #0x991a96
0x00991a2c: subs r3, #2                           ; r3 = 0x7504 - 2 = 0x7502 = EE_NEUTRAL
0x00991a2e: cmp sb, r3
0x00991a30: bne.w #0x991bc4
0x00991a34: b #0x991a88
0x00991a36: movw r3, #0x766a                      ; caso 0x766a (guarda modo)
...
```

### 1.2 Escritura de [gestor+0] (modo actual) y [gestor+1] (modo anterior) — VERIFICADO en bytes

**Caso 0x7504 (handler en `0x991ba6`):** transita 0x60 → 0x61.

```
0x00991ba6: mov r0, r4
0x00991ba8: mov r1, r6
0x00991baa: bl #0x99197c
0x00991bae: ldrsb.w r3, [r4]                      ; r3 = [gestor+0] (modo actual)
0x00991bb2: cmp r3, #0x60                         ; ¿modo == 0x60?
0x00991bb4: bne #0x991bba                         ; si no, no cambia
0x00991bb6: adds r3, #1                           ; r3 = 0x61
0x00991bb8: strb r3, [r4]                         ; [gestor+0] = 0x61   ← VERIFICADO
0x00991bba: mov r0, r5
0x00991bbc: bl #0x9918c0
0x00991bc0: bl #0x98767c
```

**Caso 0x7500 = EE_START_CMD (handler en `0x991a96`):** transita 0x60 → 0x62/0x63/0x64/0x65/0x66/0x67/0x68 según parámetro `0x9503`.

```
0x00991a96: mov r1, r6
0x00991a98: mov r0, r4
0x00991a9a: bl #0x99197c
0x00991a9e: mov r0, r6
0x00991aa0: movw r1, #0x9503                      ; parámetro EE_TYPE
0x00991aa4: blx #0xe0c68                          ; lee parámetro 0x9503 del mensaje
0x00991aa8: cmp r0, #0
0x00991aaa: beq #0x991b78
0x00991aac: blx #0xde360
0x00991ab0: cmp r0, #6
0x00991ab2: mov r8, r0
0x00991ab4: beq #0x991b08                         ; 6 → 0x66
0x00991ab6: bgt #0x991ac4
0x00991ab8: cmp r0, #4
0x00991aba: beq #0x991ae4                         ; 4 → 0x63
0x00991abc: bgt #0x991af8
0x00991abe: cmp r0, #3
0x00991ac0: bne #0x991b48
0x00991ac2: b #0x991ad4                           ; 3 → 0x62
0x00991ac4: cmp r0, #8
0x00991ac6: beq #0x991b28                         ; 8 → 0x67
0x00991ac8: blt #0x991b18
0x00991aca: movw r3, #0x3a6
0x00991ace: cmp r0, r3                            ; 0x3a6 → 0x68
0x00991ad0: bne #0x991b48
0x00991ad2: b #0x991b38
0x00991ad4: movs r3, #0x62
0x00991ad6: mov r0, r5
0x00991ad8: strb r3, [r4]                         ; [gestor+0] = 0x62   ← VERIFICADO
0x00991ada: bl #0x9918c0
0x00991ade: bl #0x953b88
...
0x00991ae4: movs r3, #0x63
0x00991ae6: mov r0, r5
0x00991ae8: strb r3, [r4]                         ; [gestor+0] = 0x63   ← VERIFICADO
...
0x00991af8: movs r3, #0x64
0x00991afa: mov r0, r5
0x00991afc: strb r3, [r4]                         ; [gestor+0] = 0x64   ← VERIFICADO
```

**Caso 0x7502 = EE_NEUTRAL (handler en `0x991a88`):** transita cualquier modo → 0x60.

```
0x00991a88: movs r3, #0x60
0x00991a8a: strb r3, [r4]                         ; [gestor+0] = 0x60   ← VERIFICADO
```

**Caso 0x766a / 0x766c:** guarda/restaura modo en `[gestor+1]`.

```
0x00991a4e: ldrb r3, [r4]                         ; r3 = [gestor+0]
0x00991a50: strb r3, [r4, #1]                     ; [gestor+1] = [gestor+0] (guarda previo)  ← VERIFICADO
0x00991a52: movs r3, #0x69
...
0x00991a82: ldrb r3, [r4, #1]                     ; r3 = [gestor+1]
0x00991a84: strb r3, [r4]                         ; [gestor+0] = [gestor+1] (restaura)       ← VERIFICADO
```

### 1.3 Resumen del modo LRM

| Dirección | Función | Escritura | Modo | Significado |
|-----------|---------|-----------|------|-------------|
| `0x9919f0` | Transición LRM | `strb r3,[r4]` → `[gestor+0]` | 0x60 | Imagen en vivo en reposo (órdenes bloqueadas) |
| `0x991ba6` | Handler 0x7504 | `strb r3,[r4]` → `[gestor+0]` | 0x61 | Modo desbloqueado (cola de ejecución activa) |
| `0x991ad8/ae8/afc` | Handler 0x7500 (EE_START) | `strb r3,[r4]` → `[gestor+0]` | 0x62–0x68 | Modo activo según parámetro 0x9503 |
| `0x991a88` | Handler 0x7502 (EE_NEUTRAL) | `strb r3,[r4]` → `[gestor+0]` | 0x60 | Vuelve a reposo |
| `0x991a50` | Handler 0x766a | `strb r3,[r4,#1]` → `[gestor+1]` | previo | Guarda modo anterior |
| `0x991a84` | Handler 0x766c | `strb r3,[r4]` → `[gestor+0]` | restaurado | Restaura modo |

**EVENTO que cambia el modo de 0x60:** **`0x7504`** (categoría `0x3100`) transita `0x60 → 0x61`. También **`0x7500` (EE_START_CMD)** con parámetro `0x9503` transita `0x60 → 0x62..0x68`. Mientras el modo es `0x60`, el `tbb` en `0x9967d0` lleva al caso 0 (`0x9952b6`) que encola la orden sin ejecutarla; las órdenes EFCS (0x75fa) y zoom quedan esperando.

Verificación del `tbb` en `0x9967d0` (Thumb, desde `0x9967d1`):

```
0x009967d1: lsls r0, r5, #0xb
0x009967d3: lsls r0, r6, #0x17
0x009967d5: strh r3, [r1, #0x28]
0x009967d7: strh r5, [r0, #0x2c]
```

(solo los primeros instructions son legibles antes de que Capstone alcance datos no-instrucción; el `tbb` y su tabla de saltos están en esta zona, coherente con lo documentado en §11 de g22-respuesta-efcs-objcamera.md)

---

## 2. SetInit de ModelStillRec y EE_START (pvt_ExeEEStartForSetInit)

### 2.1 Función SetInit: `0x68b4bc` — VERIFICADO

```
0x0068b4bc: push.w {r4, r5, r6, r7, r8, sb, sl, lr}
0x0068b4c0: sub.w sp, sp, #0x258
0x0068b4c4: ldr r1, [pc, #0x378]
0x0068b4c6: movs r2, #0
0x0068b4c8: add r7, sp, #8
0x0068b4ca: mov r4, r0                          ; r4 = objeto ModelStillRec
...
0x0068b4d8: bl #0x67a340                        ; init
0x0068b4dc: mov r0, r4
0x0068b4de: add r5, pc
0x0068b4e0: bl #0x13200a                        ; obtiene objeto/propiedad
...
0x0068b61c: movs r3, #2
0x0068b61e: mov r0, r4
0x0068b620: str.w r3, [r4, #0x1c8]              ; estado = 2
...
0x0068b622: bl #0x68e0ce                        ; [obj+0x464], slot 0, valor 0x0a  (SET)
0x0068b62e: bl #0x68e0ce                        ; [obj+0x468], slot 0, valor 3        (ACT)
...
0x0068b662: movs r1, #0
0x0068b664: ldr.w r0, [r4, #0x4a0]
0x0068b668: mov r2, r1
0x0068b66a: bl #0x68e0ce                        ; notificación aviso 0x4f a la vista
...
0x0068b67a: add.w r6, r4, #0x88
0x0068b67e: mov r0, r6
0x0068b680: bl #0x68a38c
0x0068b684: str.w r0, [r7, #0x244]
```

SetInit guarda los slots `SET`/`ACT` (vía `0x68e0ce`, idéntico a `pvt_subActionObjectFrontEShutterModeCmpEvt` en `0x678d3c`) y emite el aviso `0x4f` a la vista. Coherente con el modelo de EFCS (§4 de g22-respuesta-efcs-objcamera.md).

### 2.2 Switches que llaman a SetInit — VERIFICADO en bytes

**`0x699d72`** (llama a SetInit, registra handler para msg `0x7501` cat `0x3100`):

```
0x00699d70: mov r0, r4
0x00699d72: bl #0x68b4bc                        ; ← LLAMA A SETINIT   ← VERIFICADO
0x00699d76: mov r0, r7
...
0x00699db8: bl #0x13200a
0x00699dbc: mov r1, r0
0x00699dbe: mov.w r2, #0x3100                   ; categoría
0x00699dc4: movw r3, #0x7501                    ; mensaje 0x7501
0x00699dc8: bl #0x44a284                        ; registra handler
```

**`0x69a7ce`** (llama a SetInit, registra handler para msg `0x753f` cat `0x3100`):

```
0x0069a7ce: bl #0x68b4bc                        ; ← LLAMA A SETINIT   ← VERIFICADO
0x0069a7d2: mov r0, r7
...
0x0069a7fc: mov.w r2, #0x3100                   ; categoría
0x0069a800: movw r3, #0x753f                    ; mensaje 0x753f
0x0069a808: bl #0x44a284                        ; registra handler
```

**`0x69abc8`** (rama a SetInit, registra handler para msg `0x8514` cat `0x3100`):

```
0x0069abc8: b.w #0x68b4bc                       ; ← RAMA A SETINIT    ← VERIFICADO
...
0x0069ac0c: mov.w r2, #0x3100                   ; categoría
0x0069ac10: movw r3, #0x8514                    ; mensaje 0x8514
0x0069ac18: bl #0x44a284                        ; registra handler
```

### 2.3 Función que emite EE_START: `pvt_ExeEEStartForSetInit` = `0x67ccd0` — VERIFICADO

```
0x0067ccd0: push {r4, r5, r7, lr}
0x0067ccd2: mov r5, r1                          ; r5 = segundo argumento
0x0067ccd4: sub sp, #0x10
0x0067ccd6: ldr r1, [pc, #0x64]
0x0067ccd8: movs r2, #0
0x0067ccda: add r7, sp, #8
0x0067ccdc: mov r4, r0                          ; r4 = primer argumento (objeto)
0x0067ccde: add r1, pc
0x0067cce0: mov r3, r2
0x0067cce2: mov r0, r7
0x0067cce4: str r2, [sp]
0x0067cce6: bl #0x67a340                        ; init
0x0067ccea: mov r0, r4
0x0067ccec: bl #0x1209ca                        ; obtiene algo
0x0067ccf0: cmp r0, #9
0x0067ccf2: bne #0x67cd1c                       ; si != 9, llama a 0x67cbf8
0x0067ccf4: mov r0, r4
0x0067ccf6: movs r1, #0x19
0x0067ccf8: bl #0x131e94
0x0067ccfc: cbz r0, #0x67cd14
0x0067ccfe: ldr r2, [pc, #0x40]
0x0067cd00: movs r3, #0
0x0067cd02: mov r0, r4
0x0067cd04: str r3, [sp]
0x0067cd06: mov.w r1, #0x558
0x0067cd0a: add r2, pc
0x0067cd0c: adds r3, #9
0x0067cd0e: bl #0x68d302                        ; envía mensaje (EE_START)
0x0067cd12: b #0x67cd24
0x0067cd14: mov r0, r4
0x0067cd16: bl #0x67c95c
0x0067cd1a: b #0x67cd24
0x0067cd1c: mov r0, r4
0x0067cd1e: mov r1, r5
0x0067cd20: bl #0x67cbf8                        ; reenvía a 0x67cbf8
0x0067cd24: mov r0, r7
0x0067cd26: bl #0x67a208
0x0067cd2a: add.w r7, r7, #8
0x0067cd2e: mov sp, r7
0x0067cd30: pop {r4, r5, r7, pc}
```

En `0x67cbf8`, la rama que emite EE_START llama a `pvt_ExeEEStartCmd` (`0x67c568`):

```
0x0067cc76: bl #0x443db8
0x0067cc7a: mov r0, r4
0x0067cc7c: bl #0x67c568                        ; pvt_ExeEEStartCmd (0x67c568) — emite EE_START (0x7500)
```

### 2.4 EVENTO que activa SetInit

Los switches en `0x699d72`, `0x69a7ce` y `0x69abc8` son **handlers de mensajes** registrados para:
- `0x7501` (categoría `0x3100`) — desde `0x699dc4`
- `0x753f` (categoría `0x3100`) — desde `0x0069a800`
- `0x8514` (categoría `0x3100`) — desde `0x0069ac10`

La llegada de cualquiera de estos mensajes activa el switch correspondiente, que llama a `SetInit` (`0x68b4bc`), que a su vez llama a `pvt_ExeEEStartForSetInit` (`0x67ccd0`), que emite **`EE_START` = `0x7500`** (categoría `0x3100`, parámetro `0x9503`).

En el arnés, ninguna de estas rutinas se ejecuta en arranque en frío (verificado con trampas: `0x699d72`, `0x69a7ce`, `0x69abc8`, `0x68b4bc`, `0x67ccd0` nunca disparan). La causa es que `POSTROOTEV=11004002:e3` crea los modelos `F00_*` después del `Ts` (`0x11004012`) de `STARTEV`, así que `ModelStillRec` nunca recibe `Md`/`Ms` y nunca ejecuta su acción `SetInit`.

---

## 3. Qué evento/mensaje falta

| Objetivo | Evento/mensaje que falta | Categoría | Cómo se activa |
|----------|-------------------------|-----------|----------------|
| Cambiar LRM `0x60 → 0x61` | **`0x7504`** | `0x3100` | Mensaje a ExcMgr; handler en `0x991ba6` hace `cmp [gestor+0], #0x60; strb #0x61, [gestor+0]` |
| Cambiar LRM `0x60 → 0x62..0x68` | **`0x7500` (EE_START_CMD)** con param `0x9503=3` | `0x3100` | Handler en `0x991a96` lee `0x9503` y escribe modo en `[gestor+0]` |
| Lanzar SetInit de ModelStillRec | **`0x7501`** / **`0x753f`** / **`0x8514`** | `0x3100` | Activa switches en `0x699d72` / `0x69a7ce` / `0x69abc8`, que llaman a `0x68b4bc` |
| Emitir EE_START (`0x7500`) | SetInit (`0x68b4bc`) → `pvt_ExeEEStartForSetInit` (`0x67ccd0`) | — | Tras SetInit, `0x67ccd0` llama a `0x67c568` (`pvt_ExeEEStartCmd`) que emite `0x7500` |

Cadena completa esperada:
```
0x7504 (cat 0x3100) → [gestor+0] = 0x61
    → mensaje 0x7501/0x753f/0x8514 (cat 0x3100) → SetInit (0x68b4bc)
    → ExeEEStartForSetInit (0x67ccd0) → pvt_ExeEEStartCmd (0x67c568)
    → EE_START 0x7500 (cat 0x3100, param 0x9503=3) → [gestor+0] = 0x62
    → órdenes EFCS (0x75fa) y zoom pasan al despachador de ObjCamera
```

---

## 4. Recomendación de implementación en sonyshim.c o live.py

### Opción A (máxima fidelidad, nativa)

Arreglar el despacho de mensajes para que las órdenes EFCS (0x75fa) y zoom lleguen al despachador de `ObjCamera` (`0xad4ce4`, caso `0x75fa` en `0xad76f2`). La orden se corta antes en la entrega por MWF (`CAMUSER_OBJCAME` bloqueado en `rcv_msg qid=0x2015d`, modo LRM `0x60`). Requeriría:

1. Resolver el primer bloqueo: `CAMUSER_OBJCAME` espera `rcv_msg qid=0x2015d`; responder dataflow a `0x50004` con eco del pin (ya implementado, `ACKQ0=58003f,50004`).
2. Resolver el segundo bloqueo: el receptor de órdenes de `ObjCamera` (`0xae892c`) no se ejecuta con `0x7500`. Causa no identificada.
3. Resolver el tercer bloqueo: modo LRM `0x60` en `[gestor+0]` bloquea todas las órdenes en `0x995c58` (`SendEvent` a `ExcMgr`). Enviar `0x7504` o `0x7500` para cambiar el modo.

Dado que el segundo bloqueo no tiene causa identificada, la opción A no es viable sin más investigación en vivo.

### Opción B (emulación equivalente, recomendada)

Implementar en `sonyshim.c` (o `live.py`) una trampa que, al detectar `IssueCommandAsync` a `ObjCamera` (objeto 8) con `ObjMsg` categoría `0x3100`, id `0x75fa` (EFCS) o `0x7612`/`0x7614` (zoom), fabrique la respuesta nativa:

**En sonyshim.c, en el envoltorio de `IssueCommandAsync` (tras `ra=libObj+0x689745`):**

```c
// Si el llamante es pvt_SetFrontEShutterMode (libObj+0x689745) y r5 ∈ {0x2b4, 0x2b5}:
// 1. Fabricar mensaje 0x7504 (cat 0x3100) a ExcMgr para cambiar LRM 0x60 → 0x61
// 2. Llamar a SetInit de ModelStillRec (0x68b4bc) o directamente a pvt_ExeEEStartForSetInit (0x67ccd0)
// 3. Emitir EE_START: ObjMsg(0x3100, 0x7500) con param 0x9503=3 → [gestor+0] = 0x62
// 4. Emitir CMP 0x75fb y EVT 0x85a6 al emisor (parámetros 0x9777=v, 0x9778=v, 0x9502=0xf000)
// 5. Escribir Backup 0x107086e = 01 (si v=0x2b4) o 02 (si v=0x2b5), 1 byte
```

**Pasos concretos:**

1. **Trampa en `IssueCommandAsync`** (ya existe en el shim, perfil `efcs`): aceptar la orden y, en lugar de solo emular el efecto, publicar los mensajes reales.
2. **Fabricar `0x7504`**: enviar mensaje categoría `0x3100`, id `0x7504` a la cola de ExcMgr para forzar `[gestor+0] = 0x61`. Esto desbloquea la cola de ejecución (`0x993d10`, `0x9948d4`).
3. **Publicar evento de activación de SetInit**: enviar mensaje `0x7501` (categoría `0x3100`) al handler en `0x699d72` (o `0x753f` → `0x69a7ce`, o `0x8514` → `0x69abc8`) para que llame a `SetInit` (`0x68b4bc`).
4. **Emitir EE_START**: tras SetInit, `pvt_ExeEEStartForSetInit` (`0x67ccd0`) llama a `pvt_ExeEEStartCmd` (`0x67c568`) que emite `ObjMsg(0x3100, 0x7500)` con parámetro `0x9503=3`. Esto transita `[gestor+0] = 0x62` y las órdenes EFCS/zoom pasan al despachador.
5. **Emitir CMP y EVT** (opcional, para máxima fidelidad): `ObjMsg(0x3100, 0x75fb)` con `0x9777=v`, `0x9502=0xf000`; y `ObjMsg(0x3100, 0x85a6)` con `0x9777=v`, `0x9778=v`.
6. **Escribir Backup**: `0x107086e ← 01` (EFCS on) o `02` (EFCS off), 1 byte, vía servicio de backup del shim.

**En live.py:** equivalente, usando el mecanismo de inyección de mensajes (`INJECT` o similar) a las colas `0x2015d` (ObjCamera) y la cola de ExcMgr, con los IDs de mensaje anteriores.

### Ficheros afectados

- `scripts/gui/harness/shim/sonyshim.c`: envoltorio de `IssueCommandAsync`, sección EFCS (perfil `efcs`).
- `scripts/gui/harness/live.py`: si se prefiere publicar eventos desde Python en lugar de C.

### Verificación

- Arranque en frío con `0x107086e = 02` → fila «Desactivar».
- Activar EFCS → `nvram.json` `107086e = 01`, fila cambia a «Activar».
- Modo LRM `[gestor+0]` pasa de `0x60` a `0x61` (tras `0x7504`) y luego a `0x62` (tras EE_START).
- `NV 107086e 01/02` aparece en el registro del shim.

---

## 5. Nivel de evidencia

| Hallazgo | Dirección | Etiqueta | Base |
|----------|-----------|----------|------|
| Función que escribe `[gestor+0]` (LRM) | `0x9919f0` | VERIFICADO | Capstone Thumb: `push.w`, `mov r4,r0`, `strb r3,[r4]` |
| Escritura `[gestor+0]=0x61` (0x7504) | `0x991bb8` | VERIFICADO | `strb r3,[r4]` tras `cmp r3,#0x60` |
| Escritura `[gestor+0]=0x62/0x63/0x64` (EE_START) | `0x991ad8/0x991ae8/0x991afc` | VERIFICADO | `strb r3,[r4]` con `movs r3,#0x62/#0x63/#0x64` |
| Escritura `[gestor+1]` (guarda modo) | `0x991a50` | VERIFICADO | `strb r3,[r4,#1]` |
| Restauración `[gestor+0]` | `0x991a84` | VERIFICADO | `strb r3,[r4]` tras `ldrb r3,[r4,#1]` |
| Handler 0x7504 | `0x991ba6` | VERIFICADO | `cmp r3,#0x60; adds r3,#1; strb r3,[r4]` |
| Handler EE_START (0x7500) | `0x991a96` | VERIFICADO | lee param `0x9503`, switch a modos `0x62..0x68` |
| SetInit de ModelStillRec | `0x68b4bc` | VERIFICADO | `push.w`, llama a `0x68e0ce` (slots SET/ACT), aviso `0x4f` |
| Switch SetInit #1 | `0x699d72` | VERIFICADO | `bl #0x68b4bc` |
| Switch SetInit #2 | `0x69a7ce` | VERIFICADO | `bl #0x68b4bc` |
| Switch SetInit #3 | `0x69abc8` | VERIFICADO | `b.w #0x68b4bc` |
| pvt_ExeEEStartForSetInit | `0x67ccd0` | VERIFICADO | `push`, llama a `0x68d302` (envía msg) y `0x67cbf8` |
| pvt_ExeEEStartCmd (emite EE_START) | `0x67c568` | VERIFICADO | llamado desde `0x67cc7c` en `0x67cbf8` |
| Evento SetInit (msg) | `0x7501` / `0x753f` / `0x8514` | VERIFICADO | `movw r3,#0x7501/#0x753f/#0x8514` en registros de handler |
| REA (MCP rea / session_daemon) | N/A | NO_VERIFICADO | Demonio falló al iniciar Ghidra (cold start); se usó análisis estático con Capstone |

---

**Archivos fuente analizados:**
- `analysis/camera-extract/usr/lib/libObj.so` (md5 `eb12512e...`)
- `analysis/gui/g22/files-363/lib/libObj.so` (md5 `010a133e...`, rangos citados idénticos byte a byte)
- `scripts/gui/harness/shim/sonyshim.c`
- `docs/gui/g22-respuesta-efcs-objcamera.md` (contexto previo, confirmado contra bytes)
