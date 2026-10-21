# S19-07 — CBID_ENCODE_STILL receiver investigation

## Contexto

Investigación de seguimiento a S19-06: localizar la tabla concreta registrada por `libObj.so:EventSwitcher::AddCallbackFunc` que contenga `0xc0000004` (`CBID_ENCODE_STILL`) y enlazarla (o refutarla) con `StillConverter`.

> **Restricción metodológica**: no inferir que FEA copia píxeles, termina la lectura, cancela ni libera en el retorno de `EncodeStill`.

---

## Cadena global de callback verificada (S19-06)

| Paso | Función | Dirección | Estado |
|---|---|---|---|
| 1 | `MprCtrl::Init` registra callback MPR | `libmprctrl.so:0x11b96..0x11ba2` | **VERIFICADO** |
| 2 | `MprIf::SetCallbackFunc` | `libmpr.so:0x71f7b8..0x71f7e8` | **VERIFICADO** |
| 3 | `FeaIf::MprIfCallbackPoint` invoca callback y notifica rango `0xc0000001..0xc0000091` | `libmpr.so:0x4502e8..0x450318` | **VERIFICADO** |
| 4 | `EventSwitcher::CallbackPoint` distribuye por `targetId`/`eventId` | `libmprctrl.so:0x1c88a..0x1c90c` | **VERIFICADO** |

El rango aceptado en `FeaIf::MprIfCallbackPoint`:
```asm
45030a: f104 4340     add.w   r3, r4, #0xc0000000
45030e: 3b01          subs    r3, #0x1
450310: 2b90          cmp     r3, #0x90        ; 0x90 = 144 decimal
450312: d803          bhi     0x45031c         ; fuera de rango -> no notifica
```
→ IDs válidos: `0xc0000001` .. `0xc0000091` (inclusive). `0xc0000004` está dentro.

---

## EventSwitcher — mecanismo de registro y despacho

### `EventSwitcher::AddCallbackFunc` (libmprctrl.so:0x1c792)

```asm
1c792: e92d 47f0     push.w  {r4, r5, r6, r7, r8, r9, r10, lr}
1c796: 4604          mov     r4, r0              ; this (EventSwitcher instance)
1c798: af00          add     r7, sp, #0x0
1c79a: 460e          mov     r6, r1              ; count
1c79c: 6900          ldr     r0, [r0, #0x10]     ; this+0x10 = lock
1c79e: 4615          mov     r5, r2              ; CallbackEntry* array
...
1c7c0: ea4f 1a05     lsl.w   r10, r5, #0x4       ; count * 16 (0x10 bytes per entry)
1c7c4: f7f2 edca     blx     MemUtil::MemSet     ; zero new entries
...
1c7d4: 60b5          str     r5, [r6, #0x8]      ; entry->eventId = r5 (wait - this is the loop)
1c7d6: 4652          mov     r2, r10             ; size = count*0x10
1c7d8: f7f3 e996     blx     MemUtil::MemCpy     ; copy CallbackEntry array
1c7dc: f108 000c     add.w   r0, r8, #0xc        ; list head (this+0xc)
1c7e0: 4631          mov     r1, r6              ; new cell
1c7e2: f7f3 eb02     blx     UtilList::AddCellToList
```
- Cada entrada `CallbackEntry` = **16 bytes (0x10)**:
  - `+0x0`: `targetId` (uint32)
  - `+0x4`: `eventId` (uint32) — **este es el CBID**
  - `+0x8`: callback function pointer
  - `+0xC`: context pointer

### `EventSwitcher::CallbackPoint` (libmprctrl.so:0x1c88a)

Recorre la lista enlazada (`UtilList`), compara:
```asm
1c8c0: 6848          ldr     r0, [r1, #0x4]      ; entry->eventId
1c8c2: 4548          cmp     r0, r9              ; r9 = eventId buscado
1c8c4: d10a          bne     siguiente
1c8c6: 58d3          ldr     r3, [r2, r3]        ; entry->targetId
1c8c8: b10b          cbz     r3, coincide        ; targetId==0 = comodín
1c8ca: 4553          cmp     r3, r10             ; r10 = targetId buscado
1c8cc: d106          bne     siguiente
1c8ce: ...           ; coincide -> llama EventSwitcher::Callback
```
- Si `targetId == 0` (comodín) **o** `targetId` coincide → invoca callback.

### `EventSwitcher::Callback` (libmprctrl.so:0x1c86c)

```asm
1c86c: b590          push    {r4, r7, lr}
1c86e: b083          sub     sp, #0xc
1c870: af02          add     r7, sp, #0x8
1c872: 68c8          ldr     r0, [r1, #0xc]      ; context
1c874: 9000          str     r0, [sp]
1c876: 688c          ldr     r4, [r1, #0x8]      ; callback function pointer
1c878: 6808          ldr     r0, [r1]            ; targetId (primer campo)
1c87a: 4611          mov     r1, r2              ; eventId
1c87c: 461a          mov     r2, r3              ; context
1c87e: 693b          ldr     r3, [r7, #0x10]     ; arg adicional
1c880: 47a0          blx     r4                  ; LLAMADA AL CALLBACK
```

---

## Búsqueda de registro para `0xc0000004` (CBID_ENCODE_STILL)

### En libObj.so

**Strings relacionadas con StillConverter y CBID_ENCODE_STILL** (offsets archivo, `strings -td`):

| Offset | String |
|---|---|
| 14522809 | `[MprAcsr] eventId : [CBID_ENCODE_STILL]` |
| 14565503 | `send StillConverter::MSGID_CONVERT_JPG_CMP` |
| 14567132 | `ObjConverter/StillConverter.cpp` |
| 14567317 | `Receive CBID_ENCODE_STILL` |
| 14567344 | `[StillConverter] ParseStillCnvCmd :` |
| 14567403 | `[StillConverter] DecodeJpgCmp :` |
| 14568170 | `[StillConverter] EncodeJpgCmp :` |
| 14568202 | `[StillConverter] AllocMemoryForEncodeStill :` |
| 14568394 | `[StillConverter] GetEncodeStillParam :` |
| 14577420 | `StillConverter::PARAMID_CB_ENCODE_STILL` |
| 14577460 | `StillConverter::PARAMID_IMAGE_SOURCE` |

**Llamadas a `EventSwitcher::AddCallbackFunc@plt` en libObj.so** (19 sitios encontrados):
```
0x720af6, 0x7ab9a8, 0x7e5892, 0x83485c, 0x85b9d6, 0x87e74c,
0x880952, 0x898652, 0x89929e, 0x8a4ba0, 0x8c97de, 0x8ce258,
0x8f783a, 0x8fdb98, 0x8ff12e, 0x8ff2d2, 0x8ff490, 0x8ff6c8,
0x8ff8ee, 0x8ffb10
```

**Análisis de candidatos** (muestra de 2):
- `0x720af6`: registra **60 callbacks** (r2=0x3c), datos en pila construidos dinámicamente.
- `0x7ab9a8`: registra **4 callbacks** (r2=0x4), estructura en pila con 4 entradas.

**Ninguno de los sitios inspeccionados contiene el literal `0xc0000004`** en los datos de la tabla de callbacks pasados a `AddCallbackFunc`. El valor `0xc0000004` **no aparece como inmediato** en `.text` ni `.rodata` de `libObj.so` ni de `libmpr.so` (búsqueda por `grep -a -P '\x04\x00\x00\xc0|\xc0\x00\x00\x04'` → 0 resultados).

### En libmpr.so / libmprctrl.so

- El literal `0xc0000004` **no se recupera como constante visible** en secciones de datos (la documentación S19-06 cita VA `0x759748` en `libmpr.so` pero no se ha confirmado en esta revisión).
- El rango `0xc0000001..0xc0000091` se construye **aritméticamente** en `FeaIf::MprIfCallbackPoint` (ver arriba), no como tabla de constantes.

---

## StillConverter — despachador interno (S20-P4)

### Código real localizado (libObj.so:0x91eb60–0x91ec74)

El bloque que usa la cadena `"Receive CBID_ENCODE_STILL"`:

```asm
91eb60: ldr   r3, [pc, #..]  @ 0x91ecb8  ; r3 = 0x40000023
91eb66: cmp   r1, r3
91eb6e: beq   91eb78                       ; rama alternativa (otro log)
91eb70: adds  r3, #0x59                    ; r3 = 0x4000007c
91eb72: cmp   r1, r3
91eb74: bne   91ec72                       ; otra rama
91eb76: b     91ebe0                       ; r1 == 0x4000007c -> "Receive CBID_ENCODE_STILL"
```

**En 0x91ebe0**:
- Loggea `"Receive CBID_ENCODE_STILL"` vía `MonCtrl::ConPutMessage`.
- Construye `ObjMsg(0x3a48)`, añade parámetro `0x103` con `Struct` de 12 bytes.
- Llama virtual `vtable+0xc` sobre objeto en `ctx+0x4c` (patrón `ObjPin::Send`).

**Hallazgo clave**: el ID comparado es **`0x4000007c`** (interno de StillConverter), **no** `0xc0000004`. La igualdad numérica entre el ID interno de StillConverter y el `CBID_ENCODE_STILL` crudo de FEA **no está demostrada**.

### Atribución a StillConverter

- **INFERENCIA fuerte** (no verificada por límites de función): el bloque cae en rango `[0x91395c, 0x921d56)` entre símbolos exportados `ObjStillRecorder_UnregisterCommand` y `ObjConverter_Create` (~58 KB). `llvm-objdump` etiqueta todo como `ObjStillRecorder_UnregisterCommand+offset` (artefacto de proximidad).
- **Evidencia de densidad de cadenas**: 8 referencias a `StillConverter.cpp` en 1.2 KB alrededor (`ParseStillCnvCmd`, `DecodeJpgCmp`, `FreeCnvMsg`, `CalcResizeInfo`, `CalcDstJpgImageInfo`, `SetRegionInfo`, `EncodeJpgCmp`, `send StillConverter::MSGID_CONVERT_JPG_CMP`).

---

## Tabla de verificación

| Hallazgo | Estado | Evidencia |
|---|---|---|
| Cadena global MPR→FEA→EventSwitcher | **VERIFICADO** | Desensamblado en `libmprctrl.so`/`libmpr.so` |
| Rango `0xc0000001..0xc0000091` en FEA | **VERIFICADO** | `libmpr.so:0x45030a..0x450312` aritmético |
| `EventSwitcher::AddCallbackFunc` copia `count*0x10` bytes | **VERIFICADO** | `libmprctrl.so:0x1c7c0..0x1c7d8` |
| `EventSwitcher::CallbackPoint` filtra `targetId`/`eventId` | **VERIFICADO** | `libmprctrl.so:0x1c8c0..0x1c8cc` |
| `EventSwitcher::Callback` invoca puntero en `entry+0x8` | **VERIFICADO** | `libmprctrl.so:0x1c876..0x1c880` |
| Literal `0xc0000004` en tabla de registro | **NO_VERIFICADO** | No encontrado en datos pasados a `AddCallbackFunc` |
| `0xc0000004` asociado a StillConverter por código | **NO_VERIFICADO** | Sin xref registro→StillConverter |
| StillConverter usa ID interno `0x4000007c` | **VERIFICADO** | `libObj.so:0x91eb60..0x91eb76` |
| Igualdad `0x4000007c` == `0xc0000004` | **NO_VERIFICADO** | Solo inferencia por nombre de log |
| StillConverter es receptor final de `CBID_ENCODE_STILL` | **INFERENCIA fuerte / NO_VERIFICADO** | Cadenas + despachador interno, sin arista registro→instancia |

---

## Conclusión

1. **El mecanismo de EventSwitcher está totalmente verificado**: registro (lista enlazada de `CallbackEntry` de 16 bytes), filtro por `targetId`/`eventId`, invocación de callback.

2. **El registro concreto para `0xc0000004` no se ha localizado**: ninguno de los 19+ sitios de llamada a `AddCallbackFunc` en `libObj.so` muestra una tabla que contenga ese valor. El valor no aparece como literal en las bibliotecas analizadas.

3. **StillConverter tiene un despachador interno verificado** que reacciona a un ID interno `0x4000007c` y emite el log `"Receive CBID_ENCODE_STILL"`, pero **la traducción numérica desde el `0xc0000004` de FEA al `0x4000007c` de StillConverter no está recuperada**.

4. **La hipótesis "StillConverter recibe CBID_ENCODE_STILL" sigue siendo INFERENCIA fuerte / NO_VERIFICADO**: apoyada por densidad de cadenas y código de despacho interno, pero sin arista estática `AddCallbackFunc(..., 0xc0000004, ..., StillConverter_method)`.

---

## Próximos pasos (para S19-08+)

- Rastrear quién llama a `AddCallbackFunc` con una tabla que incluya `eventId=0xc0000004` (buscar en todas las librerías, no solo `libObj.so`).
- Localizar la tabla de traducción `CBID_EXTERNO` → `ID_INTERNO_STILLCONVERTER` (posible en `libmpr.so` o `libmprctrl.so`).
- Identificar el objeto en `StillConverter+0x4c` (Pin) y su conexión (`ObjPin::Connect`) para seguir el flujo hacia `ObjStillRecorder` / Pool / DCF.
- Verificar el slot de vtable `+0xc` en la clase del Pin (`ObjPin::Send` vs otro método).
