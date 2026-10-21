# Tema 1 — Cadena VD (Vertical Drive/Blanking) y fin de integración electrónica del sensor IMX210

**Proyecto:** sony-a6000-electronic-shutter · ILCE-6000 3.21 · `av-cam.bin`
**SHA-256:** `b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9`
**Base:** `0x43541000` (raw ARM) · Motor: Ghidra 12.1.4
**Modo:** estático, read-only, sin cámara, sin flasheo, sin ejecución de firmware.
**Autoridad:** `shipped-artifact` (bytes del blob); lo que dice "decompiler" es inferencia Ghidra, no código fuente Sony.

---

## 0. Estado de la sesión REA (bloqueo — leer antes de interpretar)

Se relanzó una única sesión REA en `run/rea-tema1.sock` (PID 111820, mismos argumentos de `tema1-calls.json`, `REA_DAEMON_RSS_MAX_MB=2048`, `GHIDRA_MAXMEM=2G`). Ghidra completó el autoanálisis y se creó `run/rea-tema1.sock.ready` (cold_s 901.0), pero el daemon fue eliminado por su **watchdog de RSS (2 GB)** al atender el lote de `q.py`: el socket quedó huérfano (`Connection refused`) y `/tmp/opencode/tema1-out.jsonl` quedó en **0 bytes**. No hay evidencia cruda REA de tema 1. No se relanzó de nuevo por instrucción del proyecto.

Consecuencia: los puntos que requieren `analyze_function`/`get_call_graph`/`xrefs`/`resolve_containing_procedure`/`trace_native_values` sobre los nodos de tema 1 no pudieron confirmarse con REA en esta sesión y quedan **NO_VERIFICADO** hasta que se estabilice una sesión con RSS suficiente (ver §5). Todo lo marcado VERIFICADO proviene de la exportación S32 (mismo motor Ghidra 12.1.4, SHA `b60c845c` coincidente con `av-cam.bin`).

---

## 1. Grafa de llamadas VD_Pre → VD_Sequence → VD_Post → VD_Drive → camIntHandler0/1

### 1.1 Nodos y direcciones exactas (tema1-calls.json / t1-probe.json / S32)

| Nodo | Dirección | Rol (documentos previos) | Estado |
|------|-----------|--------------------------|--------|
| VD_Pre | `0x43792a0c` | Planificador CAMERA_MAIN_SYNC (7 KB); strings "VD_Pre: start delayed %dV => %dV %dus", "overflow %dV", "HS3: process margin warning %dus" | Dirección verificada (S32 + s57); cuerpo no decompilado en tema 1 |
| VD_Sequence | `0x4379155c` | Secuenciador VD | Dirección verificada (t1-probe); cuerpo no decompilado |
| VD_Drive | `0x4378f410` (tema1-calls); ejecutor `0x4378f620→0x437968b0` (S32) | Ejecutor de lista VD_Drive | Dirección verificada (tema1-calls + S32) |
| VD_Post | `0x4379210c` (S32); ejecutor `0x437924f0→0x437967e8` (S32) | Ejecutor de lista VD_Post | Dirección verificada en S32; tema1-calls no la pasa |
| EC_VD_Post | `0x4378f848` (tema1-calls) | Post-procesado VD | Dirección verificada (tema1-calls); cuerpo no decompilado |
| camIntHandler0 | `0x436cf954` (tema1-calls) | Manejador de interrupción cámara 0 | Dirección verificada; cuerpo no decompilado |
| camIntHandler1 | `0x436cf780` (tema1-calls) | Manejador de interrupción cámara 1 | Dirección verificada; cuerpo no decompilado |
| Despachador indirecto | `0x43ad6034` | Miembro C++ ARM (ajuste de `this` + flag virtual); `BLX r3` en `0x43ad604e` | **VERIFICADO** (S32) |
| Thunk despachador | `0x43ad6052` | `B.W 0x43ad6034`; 26 callsites directos | **VERIFICADO** (S32) |

Nota de etiquetado: S32 etiqueta `VD_Drive=0x4378f410` y `VD_Post=0x4379210c`, mientras tema1-calls.json pasa `0x4378f410` y `0x4378f848` (EC_VD_Post). El etiquetado exacto de cada dirección requiere `analyze_function` por REA.

### 1.2 Llamadas directas e indirectas vía 0x43ad6034 (evidencia S32, no confirmada por REA en esta sesión)

- `0x43ad6034` lee dos palabras del objeto `q`: `q[0]` = destino directo u offset de entrada virtual; `q[1]` = ajuste firmado de `this` desplazado un bit, flag virtual en bit 0. Si flag==0: `destino = q[0]`; si flag==1: `destino = *(*(q+(signed(q[1])>>1))+q[0])`. Ejecuta `BLX r3` en `0x43ad604e`. **VERIFICADO** (S32).
- Thunk `0x43ad6052` = `B.W 0x43ad6034` con 26 callsites directos (incl. `0x437968ce`, `0x43796806`). **VERIFICADO** (S32).
- Referencias directas al despachador: `0x43ad6052`, `0x437b6668`, `0x437d0c18`. **VERIFICADO** (S32).
- VD_Drive llama ejecutor `0x4378f620 → 0x437968b0 → thunk 0x43ad6052` (r0=node+8, r1=*(r0+0x14)); si `node+0x18 != NULL`, llama `**(vtable+0xc)` (liberación del propietario). **VERIFICADO** (S32).
- VD_Post llama ejecutor `0x437924f0 → 0x437967e8 → thunk 0x43ad6052`. **VERIFICADO** (S32).
- Escritores de lista: `0x4379704c` → `DAT_43e9d7a8` (VD_Drive); `0x43797090` → `DAT_43e9d7e4` (VD_Post). **VERIFICADO** (S32).
- Constructor de nodo VD: `0x43b03a74 → 0x4380f5b4 → 0x43acabf4`; `q[0]=0x43b03a49`, `q[1]=0`, `q[2]=función solicitada`. **VERIFICADO** (S32).
- Adaptador `0x43b03a48`: carga `q+8`, `mov r0,r1`, `BLX r3` en `0x43b03a4e`. **VERIFICADO** (S32).
- Destinos VD_Drive: `0x43811324` (StSyncDvlpPrm), `0x43b03abe` (evento 0x1a/0x20). **VERIFICADO** (S32).
- Destinos VD_Post: `0x438106ec`, `0x43810e7c` (IDT_Wk_Set), `0x4381061c` (JdgBBOut), `0x4354a678` (EndExps). **VERIFICADO** (S32).

### 1.3 Grafa exacta VD_Pre → VD_Sequence → VD_Post → VD_Drive → camIntHandler0/1

La grafa **exacta** entre estos seis nodos, con las llamadas directas e indirectas (vía `0x43ad6034`), **no está demostrada**. S32 no decompiló ninguno de los seis nodos de tema 1; la relación de llamadas entre ellos (quién llama a quién, y si camIntHandler0/1 dispara o consume VD) requiere REA (`get_call_graph` forward desde `0x43792a0c`, backward desde `0x436cf954`/`0x436cf780`, `trace_native_values`).

Grafa parcial de referencia (S32, **no cubre** los nodos de tema 1):
```
VD_Drive 0x4378f410 → ejecutor 0x4378f620 → 0x437968b0 → thunk 0x43ad6052 → despachador 0x43ad6034 → callbacks VD_Drive
VD_Post 0x4379210c → ejecutor 0x437924f0 → 0x437967e8 → thunk 0x43ad6052 → despachador 0x43ad6034 → callbacks VD_Post
[VD_Pre 0x43792a0c, VD_Sequence 0x4379155c, EC_VD_Post 0x4378f848, camIntHandler0 0x436cf954, camIntHandler1 0x436cf780: sin enlaces confirmados]
```
Estado: **NO_VERIFICADO** (requiere REA).

---

## 2. Evidencia de acceso MMIO real a registros físicos del sensor IMX210 (0xf3c30110–0xf3c3015c vía 0x43ad6006)

### 2.1 Qué se sabe (evidencia previa, no REA de tema 1)

- `0x43ad6006` aparece en el lote de tema 1 y en `t2-resolve.json`; s34-apl-dma-vd-interrupts.md cita `0x436ccd9c → 0x43ad6006` ("banco distinto de APL"). Esto solo muestra que `0x43ad6006` es alcanzable desde `0x436ccd9c`; **no demuestra** que acceda a los registros físicos `0xf3c30110–0xf3c3015c` ni qué escribe.
- No hay evidencia de que `0x43ad6006` cargue o almacene un inmediato en el rango `0xf3c30110–0xf3c3015c`.

### 2.2 ¿Hay escritura de "fin de integración"/end-of-exposure?

**No.**
- s57-p2s-vd-synchronization.md (§F.4): "no hay evidencia de que el firmware gestione el fin de integración por registros; tampoco evidencia en contra. El comportamiento podría estar en el sensor (temporización interna con svd/shd/spl), en XPI o en Darwin."
- s34-apl-dma-vd-interrupts.md: se rechaza interpretar el evento `0x80` como interrupción de fin DMA; "aun cerrando fin DMA, no equivale automáticamente a fin de integración."
- El transporte IMX210 verificado (S56, Unicorn 26/26) escribe registros sombra vía P2S(DFE0) `0xfc088300` en trama `81\|len\|81\|AH AL\|datos`, pero eso es configuración/exposición, no fin de integración.

**Conclusión:** acceso MMIO real a `0xf3c30110–0xf3c3015c` vía `0x43ad6006`: **NO_VERIFICADO**. Escritura de fin de integración: **NO_VERIFICADO** (y no hay evidencia de que exista en firmware).

---

## 3. Productor YC/DMA: dirección de píxeles/plano/pitch y fin DMA

### 3.1 Productor YC (VERIFICADO en S32)

- `0x4379b44c` (candidato productor YC): cambia estado de canal a 2, obtiene referencia compartida del puntero `input+0x10` vía `0x4390366c` (callsite `0x4379b494`) y otra condicional desde `input+0xd4` (`0x4379b4c6`); registra `MemoryHandle::AllocShare`; usa `0x43902df8` y copia ID corto, palabra en `+4` y hasta cuatro pares de palabras desde `+8` en un objeto de 0x28 bytes. **VERIFICADO** (s32-sync-producer.json).
- Llamada desde `0x4354a50a` (dentro de `0x43549e48`, pipeline de frame) y callsites de `0x4354fad8`/`0x435525c0`/`0x435503b0`/etc. **VERIFICADO**.

### 3.2 Qué falta (NO_VERIFICADO)

| Pregunta | Estado | Motivo |
|----------|--------|--------|
| Dirección de píxeles / plano / pitch exactos | NO_VERIFICADO | No identificados; el enum y las dimensiones no bastan para etiquetar formato o stride (s32). Handle fuente efectivo en `input+0x10`/`input+0xd4` no localizado como dirección de píxeles. |
| Fin DMA demostrado (flag DMA-done, poll, contrato de caché/propiedad) | NO_VERIFICADO | `0x4379cb2e` es diagnóstico de ventana temporal (elapsed-time guard), **no** fin DMA: tras send con resultado 0, computa `elapsed = now - *(context[1]+8)`, compara con `*(context[1]+0x24)>>1`, excluye `context[2]+0x1d4`∈{4,5} y `context[2]+0x1c==4`, imprime `elapsed>>1` y canal; contador limitado a 5 avisos en `0x43e9f468`. String "YC out window overflow" en `0x43ca519f`/frase `0x43ca51ac`. No consulta flag de DMA terminado ni hace poll de transferencia. |
| Consumidor final YC/DMA | NO_VERIFICADO | `0x435a9928` construye registro de mensaje 0x34 bytes, llama `0x435a9460`, envía vía `0x435aa20c`; `0x4379744c` recibe mensajes de control `0x50004`. No se demostró que consuma el payload YC; falta tupla remota del pin. |

### 3.3 Conclusión productor/consumidor

- Productor YC (bloque de metadatos/configuración): `0x4379b44c` demostrado. **VERIFICADO** como preparador de payloads YC con handles DMM y geometría.
- Dirección de píxeles/plano/pitch: **NO_VERIFICADO**.
- Fin DMA: **NO_VERIFICADO** (`0x4379cb2e` no es fin DMA).
- Consumidor final YC/DMA: **NO_VERIFICADO**.

---

## 4. Tabla VERIFICADO vs NO_VERIFICADO (direcciones exactas)

### VERIFICADO (evidencia previa S32, mismo motor Ghidra 12.1.4 + SHA `b60c845c`; no REA de esta sesión)

| # | Hallazgo | Dirección(es) | Fuente |
|---|----------|---------------|--------|
| V1 | `0x43ad6034` despachador indirecto de callback (miembro C++ ARM, ajuste `this` + flag virtual); `BLX r3` en `0x43ad604e` | `0x43ad6034`, `0x43ad604e` | s32-final-verified.json query 43ad6034; s32-vd-callbacks-sync-ycout.md |
| V2 | Thunk `0x43ad6052` = `B.W 0x43ad6034`; 26 callsites directos | `0x43ad6052` | s32-final-verified.json |
| V3 | Referencias directas al despachador | `0x43ad6052`, `0x437b6668`, `0x437d0c18` | S32 |
| V4 | Ejecutor VD_Drive `0x4378f620 → 0x437968b0 → thunk 0x43ad6052`; liberación propietario `vtable+0xc` | `0x4378f620`, `0x437968b0`, `0x437968ce` | S32; s32-vd-callbacks-sync-ycout.md |
| V5 | Ejecutor VD_Post `0x437924f0 → 0x437967e8 → thunk 0x43ad6052` | `0x437924f0`, `0x437967e8`, `0x43796806` | S32 |
| V6 | Adaptador `0x43b03a48`: carga `q+8`, `mov r0,r1`, `BLX r3` en `0x43b03a4e` | `0x43b03a48`, `0x43b03a4e` | S32 |
| V7 | Destinos VD_Drive: `0x43811324`, `0x43b03abe` | `0x43811324`, `0x43b03abe` | S32 |
| V8 | Destinos VD_Post: `0x438106ec`, `0x43810e7c`, `0x4381061c`, `0x4354a678` | `0x438106ec`, `0x43810e7c`, `0x4381061c`, `0x4354a678` | S32 |
| V9 | Escritores de lista VD: `0x4379704c` → `DAT_43e9d7a8` (VD_Drive); `0x43797090` → `DAT_43e9d7e4` (VD_Post) | `0x4379704c`, `0x43797090` | S32 |
| V10 | Constructor de nodo VD: `0x43b03a74 → 0x4380f5b4 → 0x43acabf4` | `0x43b03a74`, `0x4380f5b4`, `0x43acabf4` | S32 |
| V11 | Productor YC `0x4379b44c`: `MemoryHandle::AllocShare` vía `0x4390366c` desde `input+0x10`/`input+0xd4` | `0x4379b44c`, `0x4379b494`, `0x4379b4c6`, `0x4390366c` | s32-sync-producer.json |
| V12 | Bloques de memoria compartida: handle `0x43e9f0d8+ch*0x28`, segundo `0x43e9f2e8+ch*0x28`, YC `0x43e9f388+ch*0x38` | `0x43e9f0d8`, `0x43e9f2e8`, `0x43e9f388` | S32 |
| V13 | `0x4379cb2e` = diagnóstico de ventana temporal, **no** fin DMA; string "YC out window overflow" `0x43ca519f`/frase `0x43ca51ac` | `0x4379cb2e`, `0x43e9f468`, `0x43ca519f`, `0x43ca51ac` | S32; s32-vd-callbacks-sync-ycout.md |
| V14 | VD_Pre `0x43792a0c` planificador CAMERA_MAIN_SYNC (strings de frontera de VD) | `0x43792a0c` | s57-p2s-vd-synchronization.md |
| V15 | `0x436ccd9c → 0x43ad6006` (banco APL distinto) | `0x436ccd9c`, `0x43ad6006` | s34-apl-dma-vd-interrupts.md |

### NO_VERIFICADO (requiere REA o evidencia física; no se pudo ejecutar REA en esta sesión por watchdog RSS)

| # | Hallazgo ausente | Dirección(es) implicadas | Por qué falta |
|---|------------------|--------------------------|---------------|
| N1 | Grafa exacta VD_Pre → VD_Sequence → VD_Post → VD_Drive → EC_VD_Post (llamadas directas e indirectas) | `0x43792a0c`, `0x4379155c`, `0x4378f410`, `0x4378f848` | Nodos no decompilados; REA bloqueado por watchdog RSS |
| N2 | camIntHandler0/1 → VD (quién dispara VD, relación con fin de integración) | `0x436cf954`, `0x436cf780` | Nodos no decompilados; REA bloqueado |
| N3 | Etiquetado exacto de cada dirección (VD_Drive vs VD_Post vs EC_VD_Post) | `0x4378f410`, `0x4378f848`, `0x4379210c` | Inconsistencia S32/tema1-calls; requiere analyze_function |
| N4 | Acceso MMIO real a registros físicos `0xf3c30110–0xf3c3015c` | `0x43ad6006`, `0xf3c30110–0xf3c3015c` | No verificados; REA bloqueado |
| N5 | Escritura de "fin de integración"/end-of-exposure en registro del sensor | Ninguna identificada | s57/s34: ninguna evidencia de fin de integración por registros |
| N6 | Dirección de píxeles / plano / pitch del productor YC | `input+0x10`, `input+0xd4`, `0x4379b44c` | Handle fuente efectivo no localizado como dirección de píxeles |
| N7 | Fin DMA demostrado (flag DMA-done, poll, contrato caché/propiedad) | `0x4379cb2e`, `0x43e9f468` | `0x4379cb2e` es ventana temporal, no fin DMA |
| N8 | Consumidor final YC/DMA (tupla remota del pin) | `0x435a9928`, `0x435aa20c`, `0x4379744c`, `0x435a9b30` | No demostrado que consuma payload YC |
| N9 | Fin electrónico de integración a resolución completa (obturador totalmente electrónico) | — | s51: A=NO/B=NO/C=NO; se mantiene |

---

## 5. Próximo paso exacto concreto

1. **Estabilizar una única sesión REA** con `av-cam.bin` (raw, ARM, base `0x43541000`) con RSS suficiente para que Ghidra no sea asesinado por el watchdog:
   - Verificar que no queden procesos de sesiones previas (`session_daemon.py`, `AnalyzeHeadless`, `java.*ghidra`).
   - Lanzar **una vez**: `session_daemon.py analysis/rea-independent/run/rea-tema1.sock '{"path": ".../input/av-cam.bin", "format": "raw-binary", "architecture": "arm", "entry_point": "0x43541000", "provider_id": "ghidra"}'` con `REA_DAEMON_RSS_MAX_MB` elevado (el watchdog de 2 GB mata a Ghidra; usar el default ~3800 MB o superior según RAM disponible) y `GHIDRA_MAXMEM=2G`.
   - Esperar `run/rea-tema1.sock.ready` (análisis frío ~8–15 min). No lanzar varios demonios.

2. **Consultar por lotes con `q.py`** (un solo `tema1-calls.json`), en este orden:
   - `analyze_function` para: `0x43792a0c` (VD_Pre), `0x4379155c` (VD_Sequence), `0x4378f410` (VD_Drive), `0x4378f848` (EC_VD_Post), `0x436cf954` (camIntHandler0), `0x436cf780` (camIntHandler1), `0x43ad6034` (despachador), `0x43ad6006` (acceso MMIO).
   - `get_call_graph` con `address=0x43792a0c` y `direction=forward` (hasta VD_Drive y callbacks), y `direction=backward` desde `0x436cf954`/`0x436cf780`.
   - `resolve_containing_procedure` para `0xf3c30110` y `0xf3c3015c` si aparecen como inmediatos/load-store.
   - `xrefs` de `0xf3c30110` y `0xf3c3015c`.
   - `trace_native_values` desde `VD_Pre` hacia `VD_Drive` y desde `camIntHandler0/1` hacia registros de sensor, `max_depth` acotado.

3. **Cerrar** con `q.py SOCK --shutdown` y comprobar que no quedan procesos `session_daemon.py`/`AnalyzeHeadless`/`java.*ghidra` propios.

4. **Escribir/actualizar** `docs/capture/rea-tema1-vd-integracion.md` con lo confirmado por REA, y correr `knowledge-maintenance` si se edita algún `.md` indexado.

---

**Nota de método:** este informe se basa en la exportación S32 (mismo motor Ghidra 12.1.4, SHA `b60c845c` coincidente con `av-cam.bin`) para todo lo marcado VERIFICADO, porque el análisis frío de REA no se estabilizó en este entorno (watchdog de RSS 2 GB mató al daemon antes de devolver el lote; `tema1-out.jsonl` quedó en 0 bytes). Todo lo que requiere REA está marcado explícitamente como NO_VERIFICADO. No se ejecutó firmware, no se flasheó, no hubo pruebas físicas. No se tocó tema 3.
