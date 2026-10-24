# S382 — Llamadores de RecordImage (0x90b248), antigua etiqueta RecordStill::Execute

## 1. Resumen

**Corrección de contrato (23-10-2026):** `0x0090b248` se identifica internamente como **RecordImage**, no se ha demostrado el nombre C++ `RecordStill::Execute`. Ver [comparación completa de contratos y bytes](recordstill-contract-audit-2026-10-23.md). `0x7484dc` y `0x755af8` eran falsos llamadores por recalcular el destino absoluto que entrega Capstone.

| Llamador (BL) | Dirección | Notas |
|---|---|---|
| BLX a PLT `0x000e16b4` | `0x007484dc` | Retirado: no llama a `RecordStill::Execute` |

Además, se encontraron **dos sitios dentro de funciones que contienen `bl #0x90b248`**:

| Dirección | Función contenedora | Llamador de la función contenedora |
|---|---|---|
| `0x0090de2e` | `0x90d7e8..0x90e148` (unwind + prólogo) | 25 punteros Thumb consumidos por `StateMgr::CallFunc` |
| `0x91634e` | `0x9162d0..0x91647c` (unwind + prólogo) | NO_VERIFICADO; `0x91631e` es tabla TBB |

## 2. Detalles de los llamadores

### 0x7484dc → RecordStill::Execute (0x90b248)

Resultado real de los bytes `99 f5 ea e0`:

```
0x007484dc: blx        #0xe16b4    ← PLT, no RecordStill::Execute
```

### 0x90de2e → RecordImage (dentro de 0x90d7e8)

Bloque `0x0090de2c` (Thumb-2). `0x755af8` contiene `86 f5 4e e3`, un `blx #0xdc198` a PLT, no una llamada a este bloque. Cuerpo local:

```
0x0090de2c: mov        r1, r6          ← argumento r1 = r6
0x0090de2e: bl         #0x90b248       ← RecordImage (r0=r4, r1=r6)
0x0090de32: b          #0x90e022
```

La entrada `0x90d7e8` preserva `r0` en `r6` y `r1` en `r4`; consulta `GetMessageId(r6)`. `0x90de2a` prepara `r0=r4`; `0x90de2c` prepara `r1=r6`. Objeto y mensaje son tipos inferidos del uso. El bloque no es el comienzo de función.

### 0x91634e → RecordImage (dentro de 0x9162d0)

Entrada `0x9162d0` corroborada por prólogo y `.ARM.exidx`. Preserva `r0` en `r4`, `r1` en `r6`. `0x916316` es TBB; `0x91631e` pertenece a su tabla de 13 bytes, no es código. El caso `GetMessageId == 0x10000005` conduce al bloque:

```
0x0091634a: mov        r0, r4          ← r0 = r4 (objeto)
0x0091634c: mov        r1, r6          ← r1 = r6 (mensaje)
0x0091634e: bl         #0x90b248       ← RecordImage
0x00916352: b          #0x9163f0
```

## 3. Argumentos de RecordImage

En ambos sitios llamadores, el patrón de argumentos es consistente:
- `r0` = puntero al objeto (`this`, tipo `ObjStillRecorder*` o similar)
- `r1` = puntero al `ObjMsg*` recibido

Esto concuerda con el prólogo de RecordImage:
```
0x0090b248: push.w   {r4, r5, r6, r7, r8, sb, sl, fp, lr}
0x0090b24c: sub.w    sp, sp, #0xb00
0x0090b250: sub      sp, #4
0x0090b252: mov      r8, r1            ← r8 = ObjMsg* (r1 del caller)
0x0090b25a: mov      r4, r0            ← r4 = this (r0 del caller)
```

## 4. Método de búsqueda

La auditoría contrasta Capstone con LLVM y bytes. Los operandos inmediatos BL/BLX ya son direcciones absolutas: **no** aplicar `address + 4 + imm * 2`. Los límites proceden de PREL31, prólogos y flujo local, no de las ventanas aisladas. La exhaustividad de llamadas sigue sin demostrarse.

Hay 25 punteros `0x90d7e9` en `.data.rel.ro`, VA `0x101ef18..0x101f158`, stride `0x18`, con relocaciones R_ARM_RELATIVE. Son el campo `call_fn` de 25 filas `StateMgr::_FuncEntry` iniciadas en `0x101ef0c`. `ObjStillRecorder` registra esas filas mediante `StateMgr::AddEntry`; su manejador llama a `ChangeState` y `StateMgr::CallFunc` lee `fila+0xc` antes de `blx r3` en `libmprctrl.so:0x1cef2`. La fila 22 exige estado 2 e ID `0x10000005`; su activación runtime sigue NO_VERIFICADO. Detalle y prueba: [auditoría de contrato](recordstill-contract-audit-2026-10-23.md). Los negativos de palabras `0x90b248/249` y `0x9162d0/d1` en PT_LOAD no prueban ausencia de despacho indirecto.

## 5. A7S: comparación reconciliada

La candidata A7S `0x847e1c..0x84814c` es RecordStill, con cinco entradas ABI; su pareja estructural A6000 es `0x908afc..0x908e2c`. RecordImage A6000 `0x90b248..0x90c088` tiene pareja A7S `0x84a568..0x84b3a8`, que sí contiene `movw r1,#0x100f` en `0x84a5c4`. En ambos modelos RecordImage llama al helper RecordStill. Equivalencia de todos los callees y ejecución física NO_VERIFICADO. Ver [S385](s385-libobj-a6000-vs-a7s-diff.md).

---

**Tests:** `analysis/s380_libobj_map/tests/test_s382_recordstill_callers.py` (ver abajo).
**Evidencia:** capstone desensamblado directo de las direcciones citadas.
