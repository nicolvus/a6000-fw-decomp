# S382 — Quién llama a RecordStill::Execute (0x90b248) en libObj.so A6000 fw3.21

## 1. Resumen

**RecordStill::Execute** está en `0x0090b248` (Thumb-2). Se encontró **1 llamador directo BL**:

| Llamador (BL) | Dirección | Notas |
|---|---|---|
| Función desconocida | `0x007484dc` | Único llamador directo de `RecordStill::Execute` |

Además, se encontraron **dos sitios dentro de funciones que contienen `bl #0x90b248`**:

| Dirección | Función contenedora | Llamador de la función contenedora |
|---|---|---|
| `0x0090de2e` | `0x0090de2c` (Thumb-2) | `0x00755af8` |
| `0x91634e` | `0x0091631e` (Thumb-2) | Ningún llamador BL directo encontrado |

## 2. Detalles de los llamadores

### 0x7484dc → RecordStill::Execute (0x90b248)

Llamador directo único. No tiene llamadores BL propios (función hoja o llamada indirecta). Contexto:

```
0x007484dc: bl         #0x90b248   ← llama a RecordStill::Execute
```

### 0x90de2e → RecordStill::Execute (dentro de 0x90de2c)

Función contenedora `0x0090de2c` (Thumb-2), llamada desde `0x00755af8`. Cuerpo:

```
0x0090de2c: mov        r1, r6          ← argumento r1 = r6
0x0090de2e: bl         #0x90b248       ← llama a RecordStill::Execute (r0=r4, r1=r6)
0x0090de32: b          #0x90e022
```

La función 0x90de2c recibe `r4` y `r6` como argumentos y los pasa a RecordStill::Execute. `r4` es probablemente el objeto `this` (ObjStillRecorder*), `r6` es el ObjMsg*.

### 0x91634e → RecordStill::Execute (dentro de 0x91631e)

Función contenedora `0x0091631e` (Thumb-2), **sin llamador BL directo** (llamada vía puntero de función/vtable). Cuerpo:

```
0x0091634a: mov        r0, r4          ← r0 = r4 (objeto)
0x0091634c: mov        r1, r6          ← r1 = r6 (mensaje)
0x0091634e: bl         #0x90b248       ← llama a RecordStill::Execute
0x00916352: b          #0x9163f0
```

## 3. Argumentos de RecordStill::Execute

En ambos sitios llamadores, el patrón de argumentos es consistente:
- `r0` = puntero al objeto (`this`, tipo `ObjStillRecorder*` o similar)
- `r1` = puntero al `ObjMsg*` recibido

Esto concuerda con el prólogo de RecordStill::Execute:
```
0x0090b248: push.w   {r4, r5, r6, r7, r8, sb, sl, fp, lr}
0x0090b250: sub.w    sp, sp, #0xb00
0x0090b252: mov      r8, r1            ← r8 = ObjMsg* (r1 del caller)
0x0090b25a: mov      r4, r0            ← r4 = this (r0 del caller)
```

## 4. Método de búsqueda

Script de decodificación BL/BLX puro (sin REA):
- Desensamblado completo de `.text` (11.4 MB) con capstone
- Decodificación manual de `imm24` de instrucciones `BL`/`BLX` Thumb-2
- Barrido de 4 396 498 instrucciones, 284 198 targets únicos de BL/BLX

## 5. Estado de A7S (pendiente de reconciliar, ver S385)

En A7S fw3.20:
- `movw #0x100f`: **0 sitios** en `.text` (vs 1 en A6000 en 0x90b2a4)
- `movt #0x0001` (parte alta de 0x100f): **0 sitios**
- RecordStill::Execute: **no localizado** en A7S
- Requiere búsqueda por patrón de cuerpo de función o por xrefs entrantes

---

**Tests:** `analysis/s380_libobj_map/tests/test_s382_recordstill_callers.py` (ver abajo).
**Evidencia:** capstone desensamblado directo de las direcciones citadas.
