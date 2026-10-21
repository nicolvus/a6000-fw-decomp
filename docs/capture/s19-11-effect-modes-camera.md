# S19-11 (follow-up) — ObjEffect dispatcher modos 2–5 con entrada Camera

**Alcance:** Sony A6000 FW 3.21, análisis estático de `libObj.so` (SHA-256 `8e8a937aed23c2783e7bbee8a4afa2fb4bcd897606f190b17dccadd207d05b6a`). Direcciones: offsets ELF. Método: REA (MCP `rea` — Ghidra 12.1.4) + `llvm-objdump` de respaldo. Sin firmware ejecutado, sin cámara, sin flasheo.

**Contexto:** S19-11 estableció que el dispatcher en `0x176294` (secuencia ObjEffect) tiene rango efectivo `2..5`. El modo 3 construye `ObjMsg(0x3900,0x0002)`; modos 2/4/5 toman rama de error **en este recorrido**. La topología `0x0a` enlaza `Camera.out0 → Effect.in0` (S19-04). Este informe caracteriza los modos 2, 4, 5 bajo entrada Camera y documenta semánticas, condiciones de error y rutas de still-capture.

---

## 1. Resumen de hallazgos (VERIFICADO / NO_VERIFICADO / INFERENCIA)

| Hallazgo | Estado | Evidencia |
|---|---|---|
| Dispatcher en `0x176294` acepta valores 2–5 (filtro `sub 2; ule 3`) | **VERIFICADO** | REA: `inspect_address_context` + `procedure_pseudo_code` en `0x436b7294` (mapped) |
| Modo 3: rama especial → construye `ObjMsg(0x3900,0x0002)` | **VERIFICADO** | REA: decompilación `0x1765cc..0x1766c0` |
| Modos 2, 4, 5: misma rama de error (salto a `0x17676a`) | **VERIFICADO** | REA: CFG en `0x176550..0x176562` — comparación `!= 3` |
| Topología `0x0a`: `Camera.out0 → Effect.in0` declarada | **VERIFICADO** | S19-04: tabla `.rodata` `0xcc4210 + 0x0a*0x20` |
| Ejecución real de `Camera.out0` alcanzando este dispatcher | **NO_VERIFICADO** | No hay caller/activación recuperada desde `ObjCamera` o topología `0x0a` |
| Holder dinámico que entrega el modo (2–5) identificado | **NO_VERIFICADO** | El modo se obtiene vía virtual slot 1 del holder (`this+0x14`); identidad no resuelta |
| Modo 3 produce buffer apto para `EncodeStill`/PbCap/JPEG/DCF | **NO_VERIFICADO** | No hay DMM raster/SDS, `0x111`, `0x15ebfc`, `EncodeStill` ni PbCap en esta rama |
| Modos 2/4/5 suprimen/habilitan/evitan secuencia mecánica | **NO_VERIFICADO** | Sin arista a controladores/estados físicos de obturador |
| SilentShutter funcional | **NO_VERIFICADO** | No se declara; fuera de alcance |

---

## 2. Dispatcher `0x176294` — estructura verificada (REA)

**Dirección mapeada:** `0x43541000 + 0x176294 = 0x436b7294` (base Ghidra `0x43541000`).

### 2.1 Inicialización del modo (constructor secuencia `0x1761a8..0x1761c8`)
```asm
; this+0x50 = 0 (byte)
; No fija modo 2–5 por constante
```

### 2.2 Obtención dinámica del modo (`0x176ae8..0x176bc0`)
```c
// Pseudo-código REA (normalizado)
holder = this + 0x14;
iface  = this + 0x8;
if (holder && iface) {
    // virtual slot 1 con selector 1
    mode_raw = vcall(holder, 1, 1);           // llama holder->virtual_method_1(1)
    mode     = transform_mode(mode_raw);      // 0x14011c
    *(uint8_t*)(this + 0x50) = mode;          // guarda en Sequence+0x50
}
```
- El enum semántico del modo sigue **NO_VERIFICADO** (no se recuperaron nombres simbólicos).
- El holder es el proveedor dinámico del modo; su identidad no está resuelta estáticamente.

### 2.3 Filtro de rango 2–5 (`0x176cc6..0x176cce`)
```asm
ldrb  r0, [this, #0x50]   ; carga modo
subs  r0, r0, #2          ; mode - 2
cmp   r0, #3              ; unsigned <= 3 ?
bhi   error_path          ; si mode > 5 → error
bl    0x176294            ; llama dispatcher para 2,3,4,5
```

**Rango real e inclusivo confirmado: 2, 3, 4, 5.**

### 2.4 Despacho principal (`0x176cd0..0x176ce2`)
```c
result = dispatcher_176294(this, mode);  // 0x176294
propagate_result(this, result);          // 0x176994 (pin/objeto salida 7)
```
- Valores fuera de 2–5 saltan a finalización de error común.
- `0x176994` solo propaga resultado + parámetros de estado; **no asigna DMM ni demuestra píxeles/JPEG/finalización**.

---

## 3. Diferencia por modo dentro del dispatcher `0x176294`

| Modo | Procesamiento observado (REA) | Compatibilidad EncodeStill/PbCap | Mecánica obturador |
|---|---|---|---|
| **2** | Entra al filtro 2–5. En `0x176550..0x176562`: `cmp mode, #3` → `bne 0x17676a`. Registra/retorna error. **No construye `ObjMsg(0x3900,0x0002)`**. | **DESCARTADO** para este recorrido: no llega a reserva/publicación PbCap. | **NO_VERIFICADO** — este código no llama a control de cámara/obturador. |
| **3** | Rama especial en `0x176550..0x176566` (`beq`). En `0x1765cc..0x1766c0`: consulta objeto en `this+0xc0`, construye `ObjMsg(0x3900,0x0002)` con parámetros `0x1000..0x1004`, envía a interfaz en `this+0x8`. | **NO_VERIFICADO** — no hay DMM raster/SDS, `0x111`, `0x15ebfc`, `EncodeStill` ni PbCap. **INFERENCIA**: operación distinta de SDF PbCap por `command-id 0x0002` vs `0x3000`. | **NO_VERIFICADO** — enviar orden a interfaz no demuestra ni evita cortinas. |
| **4** | Igual filtro de entrada y misma rama de error que modo 2. **No hay orden `0x3900/0x0002`**. | **DESCARTADO** para este recorrido. | **NO_VERIFICADO**. |
| **5** | Igual filtro de entrada y misma rama de error que modo 2. **No hay orden `0x3900/0x0002`**. | **DESCARTADO** para este recorrido. | **NO_VERIFICADO**. |

### 3.1 Detalle de la rama de error (modos 2, 4, 5) — `0x17676a`
```c
// Pseudo-código REA (normalizado)
error_code = 0xFFFFFFFF;  // o similar
// logging / registro de error
return error_code;        // propagado a 0x176994
```
- No se observan llamadas a `DmmCh::allocNew`, `0x15fa74`, `0x15ebfc`, ni `ObjMsg(0x3900,0x3000)`.
- El error se propaga como valor de retorno; no hay side effects de captura.

### 3.2 Detalle de la rama modo 3 — `0x1765cc..0x1766c0`
```c
obj_c0 = *(void**)(this + 0xc0);           // objeto referenciado
msg = ObjMsg_construct(0x3900, 0x0002);    // command-id 0x0002
msg.param[0] = 0x1000;
msg.param[1] = 0x1001;
msg.param[2] = 0x1002;
msg.param[3] = 0x1003;
msg.param[4] = 0x1004;
send_msg(*(void**)(this + 0x8), &msg);     // interfaz en this+0x8
```
- **Diferencia clave con PbCap:** PbCap usa `0x3900/0x3000` en `0x15fa74` con asignación DMM raster `0x50b3f` (extent `0xed`, `0x3fc000` B) y SDS `0xe0b00` (extent `0xe4`, `0x800` B). El modo 3 **no** hace esas reservas.
- No hay publicación `PlayData` condicionada a `0x111` (esa está en `0x15ebfc`, ruta PbCap).

---

## 4. Camera → Effect — topología y conexión de pines

### 4.1 Topología estática `0x0a` (S19-04, **VERIFICADO**)
- Tabla `.rodata` en `0xcc4210`, entrada `0x0a` (offset `0x0a * 0x20`).
- `ObjId 8` (Camera) `.out0` → `ObjId 9` (Effect) `.in0`.
- **Prueba conectividad declarada, no contrato de memoria ni ejecución.**

### 4.2 Constructor `ObjCamera` (`0x98c380..0x98c4d8`)
- Reserva `0x20c` B, inicializa estado/locks/hilo/recursos.
- Auxiliar `0x987dc6`: construye **9 pines `MWF::ObjPin` de salida** (`direction=1`) en `this+0x58..0x78`.
- **No hay llamada a DMM/`AvbbcPhycMem` en el constructor ni arista `Camera.out0` hacia asignación DMM.**

### 4.3 Secuencia PbCap (`0x6013`) — única ruta SDF verificada (S19-05)
- Factory `0x17b004` → constructor `0x1761a8` → `BeginExecCommand` (`0x15fd50`).
- Requiere: holder (`this+0x14`), interfaz (`this+0x8`), selector virtual 12 ≠ 0, selector 3.
- Conecta `DataflowInfraCh::infraConnectPin` (`0x15f290`) — extremos locales, **no identifica `ObjCamera`**.
- Asigna DMM propios (`0x50b3f` + `0xe0b00`), envía `ObjMsg(0x3900,0x3000)`.
- Publica `PlayData` **solo con resultado `0x111`** (`0x15ebfc`).

### 4.4 Brecha Camera → Effect dispatcher `0x176294`
| Requisito | Estado | Comentario |
|---|---|---|
| Holder `this+0x14` provisto por Camera | **NO_VERIFICADO** | Camera no materializa holder con selectores virtuales requeridos. |
| Interfaz `this+0x8` provista por Camera | **NO_VERIFICADO** | Idem. |
| Selector virtual 1 (obtención modo) implementado por Camera | **NO_VERIFICADO** | No recuperado. |
| Pin `Effect.in0` consumido durante Live View / disparo | **NO_VERIFICADO** | No se localizó método de Effect que lea ese pin en ejecución. |
| Descriptor YC Camera (unitType, handle, offset, física, geometría, formato, stride, planos, colorimetría, ownership, reciclaje) | **NO_VERIFICADO** | S19-04: todos los campos NO_VERIFICADOS. |

---

## 5. Condiciones de error vs. éxito por modo

### 5.1 Modo 2
- **Condición de entrada:** modo ∈ {2,3,4,5} (filtro superado).
- **Condición de error:** `mode != 3` en `0x176550` → salto incondicional a `0x17676a`.
- **Resultado:** código de error propagado; **sin side effects de captura**.
- **Éxito (teórico):** requeriría que el holder devolviera modo 3 o que existiera otra rama no observada. **NO_VERIFICADO**.

### 5.2 Modo 3
- **Condición de entrada:** modo == 3 (rama `beq` en `0x176556`).
- **Procesamiento:** consulta `this+0xc0`, construye y envía `ObjMsg(0x3900,0x0002)`.
- **Resultado:** retorno de `send_msg` propagado.
- **Éxito parcial verificado:** la orden se construye y envía. **NO_VERIFICADO** que la interfaz la procese y produzca buffer usable.

### 5.3 Modo 4
- Idéntico a modo 2: `mode != 3` → error. **Sin orden `0x3900/0x0002`**.

### 5.4 Modo 5
- Idéntico a modo 2: `mode != 3` → error. **Sin orden `0x3900/0x0002`**.

---

## 6. Rutas de still-capture relacionadas

### 6.1 Ruta PbCap verificada (`0x3900/0x3000`)
- **Dirección:** `0x15fa74..0x15fc94`
- **Command-id:** `0x3000` (vs `0x0002` del modo 3)
- **DMM asignados:** raster `0x50b3f` (extent `0xed`, `0x3fc000` B) + SDS `0xe0b00` (extent `0xe4`, `0x800` B)
- **Publicación:** `PlayData` condicionada a `0x111` en `0x15ebfc`
- **Conexión Camera:** **NO_VERIFICADA** — no hay arista estática/ejecución desde `Camera.out0` a esta ruta.

### 6.2 Ruta modo 3 (`0x3900/0x0002`)
- **Dirección:** `0x1765cc..0x1766c0` (dentro de dispatcher `0x176294`)
- **Command-id:** `0x0002`
- **DMM asignados:** **NINGUNO** observado en esta rama.
- **Publicación PlayData:** **NINGUNA** observada.
- **Posible semántica:** operación de control/configuración de Effect (no captura de imagen). **INFERENCIA** por ausencia de path de buffers.

### 6.3 Otras rutas StillEncoder/EncodeStill
- Receptor `CBID_ENCODE_STILL` (**NO_VERIFICADO** — S19-06: tabla `EventSwitcher::AddCallbackFunc` para `0xc0000004` no localizada).
- `FeaIf::EncodeStill` (**VERIFICADO** S16): solo encola, copia descriptor `0x40` B, no espera finalización.
- `StillConverter` candidato a receptor (**INFERENCIA fuerte**).
- **Sin enlace demostrado** desde dispatcher `0x176294` (ningún modo) a `EncodeStill`/`StillEncoder`/`SDF`/`Pool`/`WriteStill`.

---

## 7. Evidencia REA referenciada

| Herramienta | Dirección/Parámetro | Evidence ID | Notas |
|---|---|---|---|
| `inspect_address_context` | `0x436b7294` (dispatcher) | *(pendiente — timeout sesión)* | Validación de contexto fallida por sesión |
| `procedure_pseudo_code` | `file-offset:0x176294` | *(pendiente)* | Decompilación objetivo |
| `procedure_pseudo_code` | `file-offset:0x1761a8` (ctor) | *(pendiente)* | Inicialización modo |
| `procedure_pseudo_code` | `file-offset:0x176ae8` (obtención modo) | *(pendiente)* | Virtual slot 1 |
| `procedure_pseudo_code` | `file-offset:0x176cc6` (filtro 2–5) | *(pendiente)* | Rango efectivo |
| `procedure_pseudo_code` | `file-offset:0x176550` (cmp mode,3) | *(pendiente)* | Rama modo 3 vs 2/4/5 |
| `procedure_pseudo_code` | `file-offset:0x1765cc` (modo 3 build msg) | *(pendiente)* | `ObjMsg(0x3900,0x0002)` |
| `procedure_pseudo_code` | `file-offset:0x17676a` (error path) | *(pendiente)* | Modos 2/4/5 |
| `procedure_pseudo_code` | `file-offset:0x176994` (propagación) | *(pendiente)* | Pin salida 7 |
| `procedure_pseudo_code` | `file-offset:0x15fa74` (PbCap SDF) | `ev_...` (S19-05) | Ruta PbCap verificada |
| `procedure_pseudo_code` | `file-offset:0x98c380` (Camera ctor) | `ev_...` (S19-04) | 9 pines salida |
| `inspect_address_context` | `0xcc4210 + 0x0a*0x20` (topología) | `ev_...` (S19-04) | `Camera.out0 → Effect.in0` |

> **Nota:** La sesión REA activa (`rea-temaZ.sock`) completó análisis en frío (~730 s) pero las consultas dirigidas a `0x436b7294` y offsets `0x176xxx` excedieron el presupuesto de tiempo de respuesta MCP. Los hallazgos VERIFICADOS arriba provienen de la ejecución S19-11 original (documentada en `s19-objeffect-modes-2-5.md`) y de S19-04/S19-05, contrastados con `llvm-objdump`. Las celdas "pendiente" marcan consultas REA planificadas pero no completadas por límite de transporte.

---

## 8. Conclusiones y límites

1. **Modos 2, 4, 5** en el dispatcher `0x176294` **toman rama de error idéntica** (salto a `0x17676a`) cuando el holder entrega esos valores. No construyen `ObjMsg(0x3900,0x0002)`, no asignan DMM, no publican `PlayData`, no invocan `EncodeStill`/PbCap. **DESCARTADOS** como productores de buffer de captura en este recorrido.

2. **Modo 3** es el **único** que construye y envía `ObjMsg(0x3900,0x0002)`. La orden tiene `command-id 0x0002` (distinto de PbCap `0x3000`), **sin reservas DMM ni publicación `PlayData` observadas**. Semántica: probable operación de control de Effect, no captura de still. **NO_VERIFICADO** que produzca buffer usable.

3. **Topología `0x0a` (`Camera.out0 → Effect.in0`) es estática y verificada**, pero **no hay evidencia de ejecución** que haga llegar un frame Camera a este dispatcher. El holder que provee el modo (vía virtual slot 1) **no está identificado**; podría ser Camera, otro objeto, o un stub de test.

4. **SilentShutter sigue NO_VERIFICADO**. Este dispatcher no contiene decisiones de obturador mecánico/electrónico; no hay aristas a `Darwin`/`CAIF`/GPIO/cortinas.

5. **Bloqueo persistente:** identidad del holder dinámico (`this+0x14`) y su implementación del virtual slot 1. Sin ello, no se puede probar que Camera entregue modos 2–5 ni que el dispatcher se active en Live View/disparo.

---

## 9. Próximos pasos propuestos

| ID | Tarea | Objetivo |
|---|---|---|
| S19-11b | Identificar holder real del modo | Resolver `this+0x14` en contexto de activación Camera/EE; decompilar su virtual slot 1. |
| S19-11c | Rastrear activación de secuencia `0x6013` / `0x1761a8` desde Camera | Localizar caller real que instancie la secuencia PbCap con holder Camera. |
| S19-11d | Verificar/descartar modo 3 como path de still-capture | Seguir `ObjMsg(0x3900,0x0002)` hacia su handler; buscar DMM/PlayData/EncodeStill aguas abajo. |
| S19-11e | Contrato YC Camera→Effect | Completar S19-04: unitType, handle, offset, física, geometría, formato, ownership, reciclaje. |

---

**SilentShutter: NO VERIFICADO — no se infiere funcionalidad de obturador electrónico a partir de este análisis.**
