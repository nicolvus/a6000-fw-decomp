# S19-01 Follow-up — Puente entre dominio local 0x100..0x207 y dominio CamUser 0x3011/0x40193

**Estado:** PARCIAL — El mecanismo estático de registro del dispatcher local está verificado; el receptor/registro de la cola `0x40193` y la traducción `0x3011/0x3013/0x3015` → `0x100..0x207` **NO VERIFICADOS**.

---

## 1. Resumen de la cadena de evidencia

```
RelMgr (0x4379d838)
  ├─ Envía ObjMsg 0x3013 / 0x3015 → cola 0x40193          [VERIFICADO]
  └─ Envía ObjMsg tipo 2, id 0x3011 → cola 0x40193        [VERIFICADO]
       └─ Receptor/adaptador de cola 0x40193               [NO_VERIFICADO]

Tabla estática 0x43fcd5b4
  └─ Slot 0x43fcd5d0 = 0x43807f4d (Thumb)                  [VERIFICADO]
       └─ Dispatcher local 0x43807f4c
            └─ Caso 0x100 → 0x43807d80 → 0x43809ed8 → CaptureStart  [VERIFICADO]
```

**Topología crítica:** `0x3011/0x3013/0x3015` son IDs ObjMsg de **CamUser**; `0x100..0x207` son códigos del **mensaje local** que consume el dispatcher registrado en `0x43fcd5d0`. **No son equivalentes** y no debe asumirse traducción automática.

---

## 2. Evidencia VERIFICADA

### 2.1 Tabla estática de registro (0x43fcd5b4)

**Dirección base:** `0x43fcd5b4` (en `.data` / `.rodata` del firmware)

**Contenido (lectura cruda, little-endian):**

| Offset | Valor (VA) | Thumb entry | Función destino | Notas |
|--------|------------|-------------|-----------------|-------|
| +0x00  | 0x43fffd94 | — | Descriptor | Puntero a estructura |
| +0x04  | 0x43b0173b | 0x43b0173b | `func_0x43b0173a` | Handler hermanado |
| +0x08  | 0x43b016f9 | 0x43b016f9 | `func_0x43b016f8` | Handler hermanado |
| +0x0C  | 0x43b0177d | 0x43b0177d | `func_0x43b0177c` | Handler hermanado |
| +0x10  | 0x43b017e5 | 0x43b017e5 | `func_0x43b017e4` | Handler hermanado |
| +0x14  | 0x43b01721 | 0x43b01721 | `func_0x43b01720` | Handler hermanado |
| +0x18  | 0x43b016a3 | 0x43b016a3 | `func_0x43b016a2` | Handler hermanado |
| **+0x1C** | **0x43807f4d** | **0x43807f4d** | **0x43807f4c** | **Dispatcher local (Thumb)** |
| +0x20  | 0x43807d81 | 0x43807d81 | 0x43807d80 | Handler caso 0x100 (Thumb) |
| +0x24  | 0x43b017a3 | 0x43b017a3 | `func_0x43b017a2` | Handler hermanado |
| +0x28  | 0x43b016f7 | 0x43b016f7 | `func_0x43b016f6` | Handler hermanado |
| +0x2C  | 0x43807f55 | 0x43807f55 | 0x43807f54 | Entry alternativo dispatcher |
| +0x30  | 0x43b016ff | 0x43b016ff | `func_0x43b016fe` | Handler hermanado |

**Método de verificación:** `xxd` directo sobre `av-cam-analysis-view.elf` (base `0x43541000`), offset archivo `0xA8C5B4`.

**Referencia cruzada:** GOT `0x44022c04` → `0x43fcd468` (tabla de familia/vtable CamUser) referencia esta zona.

**Conclusión:** La presencia del puntero Thumb `0x43807f4d` en `0x43fcd5d0` prueba **registro declarativo estático** del dispatcher local. **No prueba** que el dispatcher se ejecute ni que reciba mensajes de la cola `0x40193`.

---

### 2.2 Dispatcher local (0x43807f4c)

**Desensamblado (llvm-objdump, Thumb):**

```asm
43807f4c:  push.w {r0-r8, lr}
43807f50:  movw  r2, #0x206          ; límite superior caso default
43807f54:  ldr   r3, [r1]            ; r3 = *r1 (msg_id)
43807f56:  mov   r4, r0
43807f58:  mov   r5, r1
43807f5a:  cmp   r3, r2
43807f5c:  beq.w 43808552            ; caso 0x206
43807f60:  bgt   43807fbe            ; > 0x206 → rango 0x8201..0x8306
43807f62:  movw  r2, #0x103
43807f66:  cmp   r3, r2
43807f68:  beq.w 438080aa            ; caso 0x103
43807f6c:  bgt   43807f94            ; > 0x103 → casos 0x104, 0x201, 0x202
43807f6e:  cmp.w r3, #0x100          ; *** CASO 0x100 ***
43807f72:  beq.w 438082ce            ; → salta a handler 0x43807d80
...
43807fbe:  cmp.w r3, #0x8300         ; rango 0x8201..0x8306
43807fc2:  beq.w 4380836e            ; caso 0x8300
...
```

**Lógica discriminante verificada:**
- `r1` = puntero a estructura de mensaje local
- Primer `u32` (`*r1`) = `msg_id`
- Rango `0x100..0x207` → dispatcher local (incluye `0x100`, `0x101`, `0x102`, `0x103`, `0x104`, `0x201`, `0x202`)
- Rango `0x8201..0x8306` → segundo dominio (handlers separados)
- Default `0x206` → handler genérico

---

### 2.3 Handler caso 0x100 → 0x43807d80 → 0x43809ed8

**Flujo verificado por desensamblado:**

1. **Dispatcher** `0x43807f4c` caso `0x100` → `bl 0x43807d80` (en `0x438082ce`)
2. **Handler** `0x43807d80` contiene **4 llamadas directas** a `0x43809ed8` (instalador `CaptureStart`):
   - `0x43807e74`: `bl 0x43809ed8`
   - `0x43807eb4`: `bl 0x43809ed8`
   - `0x43807eee`: `bl 0x43809ed8`
   - `0x43807f2a`: `bl 0x43809ed8`

**Descompilación de 0x43809ed8 (Ghidra/liro-camuser.json):**

```c
undefined4 candidate_43809ed8(undefined4 param_1, undefined4 param_2) {
    undefined4 uVar1;
    undefined1 auStack_2c[24];
    
    uVar1 = FUN_437de2fc();                    // Obtiene contexto/objeto
    FUN_43ada220(auStack_2c, DAT_44021ed0);   // Prepara callback
    FUN_439018b0(uVar1, auStack_2c, param_2, 0); // Registra callback 0x439018b0
    func_0x43b0172c(param_1, 0);              // Llama sobre objeto recibido
    FUN_43ae85d4(param_2, 0, 0, 0);           // Limpieza
    return 0;
}
```

**Conclusión:** La ruta local `0x100 → 0x43807d80 → 0x43809ed8 → CaptureStart` está **completamente verificada estáticamente**. El instalador arma el callback `0x439018b0` y llama `0x43b0172c` sobre el objeto recibido.

---

### 2.4 Emisor CamUser: RelMgr → cola 0x40193

**Funciones de envío verificadas (liro-relmgr-helpers.json):**

| Función | Msg ID | Cola | Tipo ObjMsg |
|---------|--------|------|-------------|
| `0x4379d3f8` | `0x300f` | `0x40193` | Tipo 4 |
| `0x4379d42c` | `0x302d` | `0x40193` | Tipo 4 |
| `0x4379d460` | `0x301d` | `0x40193` | Tipo 4 |
| `0x4379ea40` | `0x3013` | `0x40193` | Tipo 2 |
| `0x4379eb0c` | `0x3015` | `0x40193` | Tipo 2 |
| `0x4379eba8` | `0x3011` | `0x40193` | **Tipo 2** (disparo) |

**Código de envío (patrón común):**
```asm
movw r1, #0x3011          ; Msg ID
...
ldr  r2, =0x40193         ; Queue ID (literal pool)
bl   0x43aea58c           ; osalQueueSend / MWF::SendMessage
```

**Verificación:** Literal `0x40193` aparece 50+ veces en el binario, **todas como emisores** (argumento `r2` de `bl 0x43aea58c` / `0x43aea5be` / `0x43aea5f0`). **Ninguna como receptor**.

---

### 2.5 Tabla de arbitraje/permisos 0x3011 (0x43ffdd30)

**Estructura:** Filas de 16 bytes `{función_guarda, msg_id, estado, msg_siguiente}`

**Entrada para 0x3011 estado 2 (verificada en shutter-trigger-chain-0x3011.md):**
```
{ 0x437fd0e1, 0x3011, 2, 0x3010 }
```

**Función guarda 0x437fd0e0:** Devuelve puntero a registro constante `0x43bf3626` (byte `02`). **No contiene callback ni referencia al dispatcher local.**

**Conclusión:** La tabla es de **arbitraje/permisos** (determina si la petición procede), **no de despacho de ejecución**. No conecta con el dominio local `0x100..0x207`.

---

## 3. NO VERIFICADO — Brechas críticas

### 3.1 Receptor/registro de la cola 0x40193

| Búsqueda | Resultado |
|----------|-----------|
| Literal `0x40193` como destino de registro (`osalQueueCreate`, `msgQueueRegister`, callback registration) | **NO ENCONTRADO** |
| Xrefs a `0x40193` en contexto de recepción | **Solo emisores** (50+ sitios, todos `bl osalQueueSend`) |
| Función que registra handler para `0x3011/0x3013/0x3015` | **NO LOCALIZADA** |
| Tabla de traducción `0x3011` → `0x100` | **NO EXISTE** como estructura estática |

**Candidatos previos descartados (sesiones 17-18):**
- `0x43792a0c`: Opera sobre mailbox `0x30001` (respuestas a RelMgr), **sin literal `0x40193`**
- `0x438089d4`: Dispatcher de IDs `0x300..0x331` (CAIF/exposición), **sin `0x3011` ni `0x40193`**

**Hipótesis abierta:** El registro usa **ID de buzón compuesto** o **tabla dinámica** (no comparación literal), similar a `TM::createLifeCycles` → callback registration vía vtable en `libObj.so`, pero en LIRO (`av-cam.bin`).

---

### 3.2 Traducción 0x3011/0x3013/0x3015 → 0x100..0x207

| Elemento | Estado |
|----------|--------|
| Conversión estructural ObjMsg → mensaje local | **NO VERIFICADA** |
| Tabla de mapeo estática | **NO ENCONTRADA** |
| Función adaptadora (recibe de cola 0x40193, emite msg_id 0x100 al dispatcher) | **NO LOCALIZADA** |
| Prueba de que `0x3011` causa ejecución de caso `0x100` | **NO EXISTE** (solo inferencia por topología) |

**Evidencia en contra de equivalencia simple:**
- `0x3011` es `u16` ObjMsg ID (16 bits)
- `0x100` es `u32` local message code (32 bits, primer campo de estructura)
- La tabla de permisos `0x43ffdd30` devuelve **registros de condiciones**, no códigos locales
- El dispatcher local **no compara** `0x3011`, `0x3013`, `0x3015` en ningún `cmp`/`movw`

---

### 3.3 Ejecución real del dispatcher registrado

| Hecho | Estado |
|-------|--------|
| Slot `0x43fcd5d0` contiene puntero a `0x43807f4c` | **VERIFICADO** (registro declarativo) |
| Dispatcher `0x43807f4c` se ejecuta en runtime | **NO VERIFICADO** |
| Mensaje `0x100` se entrega al dispatcher | **NO VERIFICADO** |
| El camino `0x3011` → cola `0x40193` → receptor → traducción → `0x100` → dispatcher | **CADENA ROTA** (eslabón central faltante) |

**Principio metodológico:** **Registro ≠ Ejecución**. La presencia de un puntero en tabla estática no implica que el callback sea invocado ni que pertenezca a la cola `0x40193`.

---

## 4. INFERENCIA (hipótesis de trabajo, no probadas)

| Hipótesis | Fundamento | Riesgo |
|-----------|------------|--------|
| Existe tarea receptora de `0x40193` que traduce ObjMsg → mensaje local | Arquitectura típica Sony: CamUser → RelMgr → CaptureManager | Puede ser callback indirecto vía vtable/OSAL no visible estáticamente |
| La traducción usa campo `msg_id` de estructura recibida | Dispatcher local lee `*r1` (primer u32) | Estructura ObjMsg distinta de estructura mensaje local |
| `0x3011` (disparo) mapea a `0x100` (CaptureStart) | Coherencia semántica: ambos = "inicio captura" | Sin evidencia de código de mapeo |
| Registro de cola usa `MWF::ObjMsgQueue::RegisterHandler` o similar | `libMWF.so` contiene `ObjMsgQueue` (ver s18-connect-callsite-analysis.md) | `libMWF.so` no cargado en este análisis; LIRO puede usar OSAL distinto |

---

## 5. Método y fuentes

| Herramienta | Uso |
|-------------|-----|
| `llvm-objdump -d --triple=thumbv7-none-eabi av-cam-analysis-view.elf` | Desensamblado directo de `0x43807f4c`, `0x43807d80`, `0x43809ed8`, RelMgr senders |
| `xxd` lectura cruda | Tabla `0x43fcd5b4`, GOT `0x44022c04`, tabla arbitraje `0x43ffdd30` |
| Búsqueda binaria (`mmap` + `find`) | Localización de literales `0x40193`, `0x3011`, `0x3013`, `0x3015` |
| Ghidra exports previos (`liro-camuser.json`, `liro-relmgr-helpers.json`, `liro-h3011b.json`) | Descompilación de `0x43809ed8`, funciones RelMgr senders, handler `0x4381c628` |
| Documentos previos | `s19-s2-domain-bridge.md`, `shutter-trigger-chain-0x3011.md`, `s17-main-s2-integration.md`, `s18-claude-c-relmgr.md` |

**No se usó:** Ghidra interactivo, REA MCP (daemon inestable), ejecución de firmware, hardware.

---

## 6. Conclusión y siguiente paso

### Lo que SÍ está probado (VERIFICADO):
1. ✅ Tabla estática `0x43fcd5b4` registra dispatcher local `0x43807f4c` en slot `0x43fcd5d0`
2. ✅ Dispatcher discrimina `0x100..0x207` y para `0x100` llama `0x43807d80`
3. ✅ `0x43807d80` tiene 4 llamadas directas a instalador `CaptureStart` `0x43809ed8`
4. ✅ RelMgr emite `0x3011`/`0x3013`/`0x3015` tipo 2 → cola `0x40193`
5. ✅ Tabla `0x43ffdd30` arbitra `0x3011` (permiso/estado), **no despacha**

### Lo que NO está probado (NO_VERIFICADO):
1. ❌ Receptor de la cola `0x40193` (código que hace `osalQueueReceive` / registra callback)
2. ❌ Traducción/mapeo `0x3011/0x3013/0x3015` → `0x100..0x207`
3. ❌ Entrega real de mensaje `0x100` al dispatcher registrado
4. ❌ Ejecución del camino completo `CamUser → 0x3011 → 0x100 → CaptureStart`

### Siguiente tarea (S19-02):
**Localizar el consumidor de la cola `0x40193`** mediante:
1. Análisis de `libMWF.so` / `libBizFw2.so` (colas ObjMsg) — ver `s18-connect-callsite-analysis.md` §5 bibliotecas candidatas
2. Búsqueda de registro de callback OSAL (`osalQueueCreate` + `osalQueueRegisterHandler` o equivalente)
3. Seguimiento data-flow desde `0x43aea58c` (send) hacia la contraparte receive
4. **No** asumir que la tabla estática `0x43fcd5b4` está conectada a `0x40193` — son dominios distintos hasta probar lo contrario

---

## 7. Clasificación final de hallazgos

| Categoría | Items |
|-----------|-------|
| **VERIFICADO** | Tabla `0x43fcd5b4` + slot `0x43fcd5d0`; Dispatcher `0x43807f4c` lógica casos; Handler `0x43807d80` → `0x43809ed8` ×4; RelMgr senders `0x3011/0x3013/0x3015` → `0x40193`; Tabla arbitraje `0x43ffdd30` estructura y entrada `0x3011` |
| **NO_VERIFICADO** | Receptor cola `0x40193`; Traducción `0x3011→0x100`; Ejecución dispatcher registrado; Enlace funcional CamUser→CaptureStart |
| **INFERENCIA** | Existencia de tarea receptora; Uso de ID compuesto/tabla dinámica para registro; Mapeo semántico `0x3011`≈`0x100` |
| **DESCARTADO** | Que slot en tabla = prueba de ejecución; Que `0x43792a0c` o `0x438089d4` sean consumidores de `0x40193`; Que tabla `0x43ffdd30` contenga callback local |

---

**Generado:** 2026-10-21 | **Firmware:** ILCE-6000 3.21 (`av-cam.bin` SHA256 `b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9`) | **Base:** `0x43541000`
