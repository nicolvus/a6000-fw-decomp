# S382 — Quién llama a RecordStill::Execute (0x90b248) en libObj.so A6000 fw3.21

## 1. Resumen

**RecordStill::Execute** está en `0x0090b248` (Thumb-2). Corrección de auditoría (23-10-2026): `0x7484dc` y `0x755af8` eran falsos llamadores por recalcular el destino absoluto que entrega Capstone.

| Llamador (BL) | Dirección | Notas |
|---|---|---|
| BLX a PLT `0x000e16b4` | `0x007484dc` | Retirado: no llama a `RecordStill::Execute` |

Además, se encontraron **dos sitios dentro de funciones que contienen `bl #0x90b248`**:

| Dirección | Función contenedora | Llamador de la función contenedora |
|---|---|---|
| `0x0090de2e` | Límite de función NO_VERIFICADO; `0x0090de2c` es un bloque | NO_VERIFICADO; `0x755af8` no llama aquí |
| `0x91634e` | Límite de función `0x0091631e` NO_VERIFICADO | NO_VERIFICADO; no se demuestra despacho indirecto |

## 2. Detalles de los llamadores

### 0x7484dc → RecordStill::Execute (0x90b248)

Resultado real de los bytes `99 f5 ea e0`:

```
0x007484dc: blx        #0xe16b4    ← PLT, no RecordStill::Execute
```

### 0x90de2e → RecordStill::Execute (dentro de 0x90de2c)

Bloque `0x0090de2c` (Thumb-2). `0x755af8` contiene `86 f5 4e e3`, un `blx #0xdc198` a PLT, no una llamada a este bloque. Cuerpo local:

```
0x0090de2c: mov        r1, r6          ← argumento r1 = r6
0x0090de2e: bl         #0x90b248       ← llama a RecordStill::Execute (r0=r4, r1=r6)
0x0090de32: b          #0x90e022
```

El bloque mueve `r6` a `r1`; los tipos de `r0` y `r1` son inferencias. Un bloque no demuestra el comienzo de una función ni su convención de llamada.

### 0x91634e → RecordStill::Execute (dentro de 0x91631e)

Bloque dentro de la candidata `0x0091631e` (Thumb-2). Su entrada y despacho vía puntero/vtable siguen **NO_VERIFICADO**. Cuerpo:

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
0x0090b24c: sub.w    sp, sp, #0xb00
0x0090b250: sub      sp, #4
0x0090b252: mov      r8, r1            ← r8 = ObjMsg* (r1 del caller)
0x0090b25a: mov      r4, r0            ← r4 = this (r0 del caller)
```

## 4. Método de búsqueda

La auditoría decodifica ventanas exactas con Capstone y contrasta los bytes. Sus operandos inmediatos BL/BLX ya son direcciones absolutas: **no** aplicar `address + 4 + imm * 2`. Se retiran las cifras históricas del barrido porque procedían del cálculo erróneo. Los dos sitios BL quedan confirmados; la exhaustividad y los límites de sus funciones no quedan demostrados por estas ventanas.

## 5. Estado de A7S (pendiente de reconciliar, ver S385)

En A7S fw3.20:
- `movw #0x100f`: **0 sitios** en `.text` (vs 1 en A6000 en 0x90b2a4)
- `movt #0x0001` no es la parte alta de `0x100f` (es cero); ese patrón no identifica esta función.
- RecordStill::Execute: **no localizado** en A7S
- Requiere referencias PC-relativas a sus cadenas y recuperación de la función; ver S385. La ausencia de prólogo no prueba ausencia de función.

---

**Tests:** `analysis/s380_libobj_map/tests/test_s382_recordstill_callers.py` (ver abajo).
**Evidencia:** capstone desensamblado directo de las direcciones citadas.
