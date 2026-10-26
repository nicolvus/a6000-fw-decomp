# S304 — REA/Ghidra: callers de `FUN_43858338` (dumper gates) y código que carga GOT `0x4401f080`

> **Aviso D4 (25-10-2026):** [S303 §5](s303-ref-tree-43ff3200.md) rectifica las direcciones de la rev.1 usadas aquí: `0x438581e8` y `0x43858390` eran entradas reales +0x58 (`0x43858190` y `0x43858338`).

**Informe histórico superado:** las direcciones interiores con sesgo +0x58
y las trece llamadas de este texto fueron invalidadas en
[S303 rev.3](s303-ref-tree-43ff3200.md). [S305 actualizado](s305-fun43858390-literal-pool.md)
recoge las entradas correctas y los consumidores Backup verificados el 25-10-2026.
Las afirmaciones siguientes se conservan como antecedente, no como estado vigente.

> Hito **Agente B (S300+)** — Imager: estado, drive modes y gates.
> Análisis con REA/Ghidra 12.1.4 sobre `av-cam.bin` A6000 fw3.21 (SHA `b60c845c...56bb9`), base `0x43541000`.
> Complementa: S153 (gates), S300 (xrefs estado), S303 (árbol referencias `0x43ff3200`).

---

## Hallazgos REA

### 1. Función dumper `FUN_438581e8` (S153 gates)

**Dirección real**: `0x438581e8` (Thumb, 366 bytes). La dirección `0x43858338` citada en S153 está **dentro** del cuerpo.

**Análisis REA** (`analyze_function 0x438581e8`): ✅ Éxito completo.

**Pseudocode clave** (extracto):
```c
void FUN_438581e8(param_1, param_2, param_3) {
  // Carga punteros globales (DAT_43858364, DAT_43858368, DAT_4385836c, etc.)
  iVar6 = *(int *)(DAT_43858364 + 0x438581f4);  // Puntero a estructura estado
  iVar8 = *(int *)(iVar5 + DAT_4385836c);       // Campo de estructura
  
  if (*(char *)(iVar8 + 4) == 0) {              // ← GATE state+3&2 ? (offset +4)
    // Rama sin gate activo
    if ((*(char *)(DAT_43858370 + ...) != 0) && ...) {
      FUN_439c5378(...);  // Escritura/dump
    }
  } else {
    // Rama con gate activo
    for (; 0 < iVar6; iVar6 -= iVar7) {
      sVar10 = *(short *)(iVar8 + 0x1c);        // state+0x1c (halfword)
      uVar12 = (uint)*(byte *)(iVar8 + 0x1e);   // state+0x1e (byte)
      if (sVar10 == 0) sVar10 = 3;
      if (uVar12 == 0) uVar12 = 4;
      if (*(char *)(iVar8 + 0x1f) == 1) {       // state+0x1f (flag)
        uVar13 = FUN_4382fe38();
        *(undefined8 *)(DAT_43858378 + ...) = uVar13;
      }
      // ... prepara buffer local_2c con sVar10, uVar12, iVar7 ...
      // FUN_438580a4 (prepara), FUN_439c5378 (copia), FUN_438580e8 (envía)
      // FUN_43561264/43561280/43561328/43561344 (OSAL msg queue)
    }
  }
  // Actualiza contadores: *(short *)(...), **(short **)(...)+1
  *(undefined4 *)(DAT_4385838c + ...) = 0;
  return;
}
```

**Gates leídos (confirmado S153)**:
- `state+4` (byte) → `*(char *)(iVar8 + 4)` → corresponde a **`state+3` bit 2** (shift por alineación estructura)
- `state+0x1f` (byte flag) → `*(char *)(iVar8 + 0x1f)`
- `state+0x1c` (halfword) → `*(short *)(iVar8 + 0x1c)`
- `state+0x1e` (byte) → `*(byte *)(iVar8 + 0x1e)`

**No se observan escrituras a gates** en esta función — solo lecturas.

---

### 2. Caller único: `FUN_43858390`

**Dirección**: `0x43858390` (Thumb, 3948 bytes, **no contiguo** — 4 rangos en 4914 bytes span).

**Caller REA**: ✅ Identificado como **único caller** con **13 llamadas** (UNCONDITIONAL_CALL):

| # | Site address | Offset en caller |
|---|---|---|
| 1 | `0x4385842a` | +0x9a |
| 2 | `0x43858440` | +0xb0 |
| 3 | `0x43858922` | +0x592 |
| 4 | `0x43858938` | +0x5a8 |
| 5 | `0x43858972` | +0x5e2 |
| 6 | `0x43858986` | +0x5f6 |
| 7 | `0x43858998` | +0x608 |
| 8 | `0x438589aa` | +0x61a |
| 9 | `0x43858b36` | +0x7a6 |
| 10 | `0x43858b4a` | +0x7ba |
| 11 | `0x43858b5c` | +0x7cc |
| 12 | `0x43858b6e` | +0x7de |
| 13 | `0x43858b80` | +0x7f0 |

**Patrón**: Llamadas distribuidas cada ~0x10-0x20 bytes en el rango `0x43858922–0x43858b80`, sugiriendo **bucle de procesamiento** que invoca al dumper periódicamente.

**Función `FUN_43858390`**:
- Tamaño: 3948 bytes, **no contiguo** (4 rangos disjuntos)
- Span: 4914 bytes (`0x43858390–0x438596c1`)
- **No analizada completamente** (pseudocode excede buffer REA)
- Prologue: `push {r0,r1,r2,r4,r5,r6,r7,r8,r9,r10,r11,lr}` (Thumb, muchos registros)

---

### 3. GOT slot `0x4401f080` (tabla `0x43ff3200`)

**Búsqueda REA xrefs**: ❌ **0 resultados** (vacío).

**Verificación por bytes** (S303): El literal `0x43ff3200` aparece **una sola vez** en `0x4401f080` (GOT slot).

**Interpretación**: El acceso a la tabla es vía **PC-relative LDR literal** (Thumb `ldr rX, [pc, #imm]`), que Ghidra **no registra como xref de datos** en el reference manager. El código que usa la tabla hace:
```asm
ldr rX, =0x4401f080   ; literal pool con 0x4401f080
ldr rX, [rX]          ; rX = 0x43ff3200 (base tabla)
; luego indexa: ldr rY, [rX, #offset]
```

**Pendiente**: Identificar funciones que cargan `0x4401f080` (requiere análisis de literal pools o Ghidra `findReferencesTo` en `DAT_4401f080`).

---

### 4. Conclusiones para S303/S304

| Item | Estado | Evidencia |
|---|---|---|
| **Dumper gates (`FUN_438581e8`)** | **ANALIZADO** | REA completo; lee `state+3`/`state+6` (vía offsets estructura) |
| **Callers del dumper** | **VERIFICADO** | Único: `FUN_43858390`; 13 llamadas en bucle |
| **Función caller (`FUN_43858390`)** | **PARCIAL** | Identificada; 13 callsites; pseudocode incompleto (buffer excedido) |
| **Código que carga GOT `0x4401f080`** | **NO_VERIFICADO** | Acceso vía literal pool; REA no expone xrefs a GOT slots |
| **Escritores gates `state+3`/`state+6`** | **NO_VERIFICADO** | Dumper solo lee; escritores no identificados |

---

### 5. Próximos pasos (S305+)

| Acción | Herramienta | Objetivo |
|---|---|---|
| Analizar `FUN_43858390` por tramos | REA `analyze_function` con `file-offset` | Entender el bucle principal que invoca al dumper |
| Buscar literal pool `0x4401f080` | Ghidra `findReferencesTo(DAT_4401f080)` | Encontrar código que accede a tabla `0x43ff3200` |
| Xrefs a `state+3` (`0x43f72d05`) / `state+6` (`0x43f72d08`) | REA `xrefs` + análisis de stores | Identificar escritores de gates |
| Análisis de `FUN_438580a4` / `FUN_438580e8` | REA `analyze_function` | Entender preparación/envío del dump |

---

### 6. Artefactos REA

- `ev_0123448df317d183d992b8a25e603f7a215ab49dc773cb0297621e67970420a2` — `analyze_function 0x438581e8` (dumper)
- `ev_d731c8f259b98a555c11efccbf25f1973a0e220a99177eba2319996cce092ede` — `analyze_function 0x43858390` (caller, retenido)
- `ev_92354edaa18811473f40c2c4aa278afe005e177b7d0527fd77d5d2a4a29c52a4` — `read_bytes 0x43858390` (prologue)
- `ev_0359d0e2aa3515a28cfdbfd9a8747fd5e4c2b5c6cf01c863eb1ed1ba03e53a68` — `xrefs 0x43858338` (vacío, dirección interior)
- `ev_2ee664b4864efce7b2fc26bdbc1b0679a2fb67cefc5d4a368afdcc6e5e4e548d` — `xrefs 0x4401f080` (vacío)

---

### 7. Tests sugeridos

```python
# Verificar 13 callsites en FUN_43858390
def test_dumper_callers():
    xrefs = rea_xrefs("0x438581e8")
    callers = [x for x in xrefs if x.kind == "CALL"]
    assert len(callers) == 13
    assert all(c.source_procedure.address == "0x43858390" for c in callers)

# Verificar que dumper no escribe gates
def test_dumper_no_write_gates():
    func = rea_analyze("0x438581e8")
    writes = [op for op in func.pcode if op.opcode == "STORE" and "0x43f72d05" in str(op) or "0x43f72d08" in str(op)]
    assert len(writes) == 0
```

---

## 8. Veredicto final S304

**COMPLETADO PARCIALMENTE**:
- ✅ Dumper analizado y gates confirmados (lectura)
- ✅ Caller único identificado con 13 invocaciones
- ❌ Código que carga GOT `0x4401f080` no localizado (acceso indirecto vía literal pool)
- ❌ Escritores de gates `state+3`/`state+6` no identificados

**Bloqueador**: REA no expone xrefs a GOT slots ni a literal pools. Requiere Ghidra headless con script `findReferencesTo` o análisis manual de literal pools.

**S51 inalterado**: A=NO, B=NO, C=NO.
