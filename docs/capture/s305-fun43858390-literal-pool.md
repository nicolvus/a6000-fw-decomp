# S305 — Análisis de `FUN_43858390` (caller dumper) y búsqueda literal pool `0x4401f080`

> Hito **Agente B (S300+)** — Imager: estado, drive modes y gates.
> Continuación de S304. Análisis REA/Ghidra de `av-cam.bin` A6000 fw3.21.

---

## 1. Función `FUN_43858390` — caller principal del dumper

**Dirección**: `0x43858390` (Thumb, 3948 bytes, **no contiguo** — 4 rangos: `0x43858390–0x438583a5`, `0x438583b0–0x43858f03`, `0x4385922c–0x438594e3`, `0x43859578–0x438596c1`; span 4914 bytes).

**Prologue**: `push {r0,r1,r2,r4,r5,r6,r7,r8,r9,r10,r11,lr}` (Thumb, 12 registros en total, incluido lr).

**Patrón de llamadas al dumper** (13 sites en rango `0x43858922–0x43858b80`):
- Trece sitios estáticos de llamada a `FUN_438581e8`.
- Preparación de argumentos antes de esas llamadas; flujo completo pendiente.
- No son trece iteraciones observadas: no se ejecutó el firmware ni se demostró aquí un bucle.

**Función no analizada completamente** por REA (pseudocode excede buffer). Pendiente análisis por tramos.

---

## 2. Búsqueda literal pool GOT `0x4401f080`

**Objetivo**: Encontrar código que carga la tabla `0x43ff3200` vía GOT slot `0x4401f080`.

**Método**: Búsqueda de literal `0x4401f080` en binario + análisis de LDR literal cercanos.

**Resultado**:
- Literal `0x4401f080` aparece **1 vez** en `0x4401f080` (el GOT slot mismo)
- **0 referencias directas** al GOT slot detectadas por REA
- Acceso es vía **PC-relative LDR literal pool** (Thumb `ldr rX, [pc, #imm]`)

**Búsqueda de LDR literal pools candidatos**:
```python
# Buscar patrón Thumb LDR literal: 0x4800-0x4BFF (ldr rX, [pc, #imm])
# seguido de literal pool con 0x4401f080
```

**Pendiente**: Análisis Ghidra headless con script `findReferencesTo(DAT_4401f080)` o búsqueda manual de literal pools en regiones de código que usan la tabla `0x43ff3200`.

---

## 3. Próximos pasos (S306+)

| Acción | Herramienta | Objetivo |
|---|---|---|
| Analizar `FUN_43858390` por tramos (0x43858390, 0x438583b0, 0x4385922c, 0x43859578) | REA `analyze_function` con `file-offset` | Entender bucle principal, qué estructura procesa, origen de argumentos al dumper |
| Ghidra headless `findReferencesTo(DAT_4401f080)` | Ghidra headless + script | Encontrar todo código que referencia GOT slot tabla `0x43ff3200` |
| Xrefs a `state+3` (`0x43f72d05`) / `state+6` (`0x43f72d08`) | REA `xrefs` + análisis stores | Identificar escritores de gates |
| Análisis `FUN_438580a4` / `FUN_438580e8` / `FUN_439c5378` | REA `analyze_function` | Entender preparación/envío del dump |

---

## 4. Bloqueadores actuales

| Bloqueador | Causa | Mitigación |
|---|---|---|
| `FUN_43858390` demasiado grande para REA buffer | 3948 bytes, no contiguo | Analizar por tramos con `file-offset` o Ghidra headless |
| REA no expone xrefs a GOT slots / literal pools | Limitación reference manager | Usar Ghidra headless `findReferencesTo` |
| Writers gates `state+3`/`state+6` no identificados | Solo dumper (lector) analizado | Buscar STORE a `0x43f72d05`/`0x43f72d08` + análisis dinámico |

---

## 5. Esquemas de tests pendientes para S305 (no ejecutables)

```python
def test_fun_43858390_calls_dumper_13_times():
    """Verificar 13 callsites en FUN_43858390."""
    # Requiere REA analyze_function por tramos
    pass

def test_got_0x4401f080_literal_pool():
    """Verificar que GOT slot se accede vía LDR literal pool."""
    # Buscar LDR literal con target 0x4401f080 en contexto
    pass

def test_fun_43858390_loop_structure():
    """Resolver flujo de control; 13 sitios de llamada no prueban 13 iteraciones."""
    pass
```

---

## 6. Resumen estado S304/S305

| Item | Estado |
|---|---|
| Dumper `FUN_438581e8` analizado | ✅ COMPLETO |
| Callers dumper (1 caller, 13 sites) | ✅ VERIFICADO |
| Caller `FUN_43858390` analizado | 🔄 EN PROGRESO (parcial) |
| GOT `0x4401f080` literal pool | 🔄 PENDIENTE (Ghidra headless requerido) |
| Writers gates `state+3`/`state+6` | ❌ NO_VERIFICADO |

---

## 7. Artefactos

- `docs/capture/s304-rea-dumper-callers.md` — S304 completo
- `docs/capture/s305-fun43858390-literal-pool.md` — este informe (S305)

---

## 7. Veredicto

**S305 EN PROGRESO**: Análisis de `FUN_43858390` y búsqueda literal pool requieren Ghidra headless para completarse. REA buffer limitado impide análisis completo de función grande no contigua.

**Recomendación**: Usar Ghidra headless con scripts para:
1. `findReferencesTo(DAT_4401f080)` → localizar código que usa tabla `0x43ff3200`
2. Analizar `FUN_43858390` completa → entender bucle principal de captura
3. `findReferencesTo(0x43f72d05)` / `0x43f72d08` → encontrar escritores gates
