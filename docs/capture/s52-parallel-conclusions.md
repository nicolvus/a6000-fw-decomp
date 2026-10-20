# S52 — Conclusiones de la investigación paralela Claude + Codex (19-10-2026)

Agente A: Claude (Opus 5.5, effort `medium`; `work/claude/`). Agente B: Codex CLI 0.162.1, `gpt-5.6-terra`, esfuerzo `medium`
(verificado en la cabecera de `work/codex/codex-s52-*.log`). Tres rondas de B (R1 superficial, R2 dirigida, validación cruzada), dos de A
(investigación, validación cruzada). Sesiones REA separadas (`work/{claude,codex}/run/rea.sock`), ambas cerradas. Solo estático.
Binarios intactos: `analysis/s52-hashes.initial.sha256` (8/8) y manifiestos `firmware`/`silent-liro`/`ghidra-dir` OK al final.

## 1. Resumen ejecutivo

- La A7S **no suprime** el control de cortinas en LIRO: sigue enviando el paquete CAIF del evento 1 al MCU de obturador, pero **marcado
  como Silent** (bit `0x20` en `+0x12`, modo 2 en `+0xd`), con el byte de clase codificado como mecánico (3), y **deja de esperar** las
  respuestas del mecanismo (CAIF 3, bandera `0x800000`). La decisión física recaería en el MCU (INFERENCIA fuerte; parser no localizado).
- `captura+0x748` es una bandera **funcional** (esperas, eventos, temporizador), presente y **latente** en la A6000 como `+0x740`.
- La clase 0 llega a `param+9` del SetExposure IMX235 por una cadena ahora **VERIFICADA** (`0x43864c74 → 0x43f04c8c → R+0x69 → cap+0x651
  → 0x436f2938 → vtable+0x28`). La clase por sí sola **no** omite ningún envío CAIF ni MMIO (solo un mensaje interno `0x22`).
- ShutMode 0 difiere de 1/3 en bits del campo de configuración y en la función de temporización, en ambos sensores con patrones distintos;
  el efecto eléctrico sigue NO VERIFICADO. P5 sigue **NO VERIFICADO**; **S51 se mantiene**.

## 2. Diferencias nuevas descubiertas

Bits Silent del paquete CAIF (S1/S2), esperas condicionadas (S3–S7), codificación clase 0 = 3 en byte +1 (C2), omisión del mensaje
`0x22` (C1), desplazamiento +8 de la estructura de captura A7S (`+0x748`≙`+0x740`), escritura `cfg2+4|=8` en todos los ShutMode del IMX235
(corrección), campos reales de SetExposure (`0x440220ac`, `0x4401ca2e`), VD_Pre A7S guarda el tipo en `0x43eaaac0`.

## 3. Direcciones verificadas

Ver [`analysis/s52-evidence-matrix.json`](../../analysis/s52-evidence-matrix.json). Tests: `work/claude/tests/test_a7s_silent_facts.py` (11),
`test_s52_curtain_facts.py` (14), `test_s52_xcheck.py` (7), `work/codex/s52/test_s52_shutmode_facts.py` — todos OK.

## 4–7. Detalle

[Cortinas](s52-a7s-curtain-trace.md) · [Propagación de clase 0](s52-shutmode-propagation.md) ·
[IMX235/IMX210, MMIO/DFE](s52-imx210-electronic-exposure.md) · [Viabilidad](s52-a7s-a6000-feasibility.md).

## Validación cruzada y discrepancias

| Tema | A (Claude) | B (Codex) | Resolución |
|---|---|---|---|
| Destino de la clase | `G=0x43f06bc8+0x5c` | R1: `0x43f06d5c..98` | B se corrigió en R2 (PC mal aplicado); coordinador confirma por literal |
| Clase → `param+9` | VERIFICADO | PARCIAL: identidad de registro no demostrada | **Coordinador:** ambos sitios llaman `0x43861f58(cap+0x1c0, cap+0x1b8)`, que devuelve uno de dos buffers estáticos (`0x43eb7f0c`/`0x43f0552c`) → VERIFICADO estructural, INFERENCIA solo en estabilidad del estado |
| Rango IMX210 modo 3 | `0x436d717a..71a8` | `0x436d7114..78` | B REFUTADO (es el modo 2) |
| «SHR no cambia el patrón» | artefacto del arnés | afirmado | A: el prólogo escribe SHR en ~12 campos; B corregido |
| `cfg2+4|=8` | solo clase 0 (tabla previa) | omitido | todos los modos 0/1/3/4 (A corrige su propia tabla) |
| `+0x748` ≙ `+0x740`, escritor único | VERIFICADO | PARCIAL (no reprodujo recuentos) | se mantiene VERIFICADO en escritor/offset; recuentos INFERENCIA |
| `0xf2910048` genérico | ~150 llamadores | PARCIAL | helper GPIO genérico CONFIRMADO; recuento no reproducido |
| Error histórico `0x43826dc0` | — | no repetido | OK |

## 9. Hipótesis (definiciones del encargo S52)

| H | Estado | A favor | En contra / incógnitas | Confianza | Próxima comprobación |
|---|---|---|---|---|---|
| H52-1 `+0x748` controla una decisión funcional de captura silenciosa | **VERIFICADO** (software) | S3–S7 condicionados; escrito solo si tipo 2 | efecto mecánico; inicialización del campo | alta | constructor/reset de captura |
| H52-2 clase 0 omite una operación mecánica ejecutada con 1/3 | **NO VERIFICADO** (desfavorable) | omite el mensaje `0x22` (C1) | C1 sin receptor conocido; byte +1 = clase 3; ningún CAIF/MMIO omitido | media | receptor de `0x437c3114(0xa..0x12)` |
| H52-3 clase 0 llega a ShutMode | **VERIFICADO** (estático) | cadena completa por instrucciones | estabilidad del selector, condición `0x4386216e` | alta | emulación de `0x43862158` con estado realista |
| H52-4 IMX235 usa secuencia electrónica específica en Silent | **INFERENCIA** | modos `0x4e/0x4f` (48 campos), ShutMode 0, esperas mecánicas omitidas | ningún campo clasificado; bits sin semántica | media | consumidores de la matriz; datasheet |
| H52-5 IMX210 posee mecanismos para exposición electrónica completa | **NO VERIFICADO** | ShutMode 0 y lectura completa `0x0b/0x2f` existen | bits distintos al IMX235; sin `0x4e/0x4f`; sin ruta que use 0 | baja | datasheet / traza pasiva autorizada |
| H52-6 cortinas y lectura electrónica son decisiones independientes coordinadas | **INFERENCIA fuerte** | ramas paralelas desde `cap+0x78c`; drive_mode no toca paquete ni esperas | cobertura parcial del constructor del paquete | media-alta | recorrer callees de `0x43862e24` |
| H52-7 la ausencia en A6000 es de configuración/controlador, no física | **HIPÓTESIS** («código existente activable»: **DESCARTADO**) | todas las piezas LIRO que faltan son software; Darwin con mismos tipos | MCU Darwin y sensor no demostrados capaces | baja | parser CAIF Darwin A6000 |

Nota: los agentes usaron etiquetas propias distintas en H52-2/4/6 (p. ej. Claude «H52-6 = lógica latente», Codex «H52-4 = clase 0 inhibe
cortina»); esta tabla re-evalúa con el texto del encargo.

## 10. Límites

Sin ejecución ni cámara; índices de referencias heurísticos (REA no reconoce varias funciones Thumb: ausencia ≠ inexistencia); parser CAIF
de Darwin no localizado en ninguna ROM; contrato de aplicadores IMX y transporte serie sin recuperar; valores iniciales de RAM tomados del
fichero; tareas asíncronas: la cronología S3–S7 no es temporal.

## 11. Experimentos siguientes

Ver [viabilidad § Experimentos](s52-a7s-a6000-feasibility.md). Prioridad 1: parser CAIF en `darwin_core.bin` (A7S vs A6000) y tratamiento del bit `0x20`.
