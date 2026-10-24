# S178 — censo de etiquetas y auditoría de candidatas

Revisión del 23-10-2026. Corrige los recuentos históricos de este informe:
58 hitos + 38 subetiquetas y 276 pendientes estaban desactualizados.
El detalle al empezar contenía 94 hitos + 39 subetiquetas y 239 pendientes,
coincidiendo con la [auditoría vigente](../auditoria-2026-10-23.md), fila del censo.
La cobertura es documental; no demuestra funciones ni equivalencia entre modelos.

| Magnitud | Antes | Después |
|---|---:|---:|
| Tokens distintos `[XXX]` A6000 fw3.21 | 372 | 372 |
| Con hito documental | 94 | 94 |
| Subetiquetas documentadas | 39 | 39 |
| Cobertura documental | 133/372 (35.75 %) | 133/372 (35.75 %) |
| Pendientes de investigación | 239 | 226 |
| Fragmentos descartados como módulos | 0 | 13 |

**133 + 226 + 13 = 372**. Descartar no aumenta cobertura.
372 es el denominador histórico de tokens, no un número demostrado de módulos.
Las 93 etiquetas exclusivas de A6000 y las siete ausentes en A6300 no cambian.

## Decisiones y pruebas

| Veredicto | Etiquetas | Evidencia exacta |
|---|---|---|
| RECHAZO | `[MODE_CAP]`, `[MODE_CAP_DRP]`, `[MODE_CAP_PREREVIEW]`, `[MODE_CAP_SNR]`, `[MODE_CAP_SNR_PREREVIEW]` | Sufijos de diagnósticos `[IMAGING_CAP]: CamCore … Error!`; cadenas `0x43cada50`, `0x43cad970`, `0x43cad9df`, `0x43cadab6`, `0x43cadb9d`; ADD PC `0x437f5d48`, `0x437f5c32`, `0x437f5cb8`, `0x437f5f20`, `0x437f61d2`. |
| RECHAZO | `[D0]`–`[D7]` | Campos `:%04x` de `[CAM_UTIL_ADJ]`; cadenas `0x43ccde70` / `0x43ccdeae`; ADD PC `0x43900abc` / `0x43900ae2`. |
| ACEPTO como candidatas; siguen pendientes | `[IMAGING_IMG]`, `[SFR]`, `[EXL]`, `[DECMODEMGR]` | Prefijos de trazas con referencias verificadas: `0x43cb4355` ← `0x4381bac8`; `0x43ce757f` ← `0x439a63aa`; `0x43c911ab` ← `0x436c95cc`; `0x43c45f77` ← `0x435c9186`. No se demuestra un módulo funcional completo. |
| NO_VERIFICADO tras examen | `[NULL]`, `[HW]` | Marcadores anidados en `[ACCY]`, cadenas `0x43c25b20` / `0x43c24cac`; no se distingue categoría de logger, campo o submódulo. |

Fuentes: [decisiones individuales](../../analysis/s178_census/decisiones_auditoria.json),
[bytes LDR/ADD y pools](../../analysis/s178_census/evidencia_bytes.json) y
[ocurrencias y referencias completas](../../analysis/s178_census/pendientes_auditados.json).
Cada ocurrencia conserva dirección del token, cadena contenedora, offset, texto hasta NUL
y referencias PIC candidatas. SHA-256 de entradas en el inventario.
Los ceros históricos de cadenas referenciadas de los sufijos no significan ausencia
de referencias a su cadena contenedora.

## Cola abierta y límites

La [lista explícita](../../analysis/s178_census/pendientes.md) incluye las 226 pendientes,
las 13 descartadas y su motivo. De las abiertas, cuatro se aceptan como candidatas y
222 siguen NO_VERIFICADO: dos examinadas y 220 sin revisión individual de instrucciones.
Ninguna se promueve por aparecer en otro informe. `[SFR]` no se equipara a `[SFRA]`/`[SFRS]`.

Orden reproducible: captura/sensor, sincronización/visor, resto; dentro de cada grupo,
cadenas contenedoras distintas con PIC candidato, recontadas, descendentes y etiqueta.
141 etiquetas difieren del contador histórico de cadenas que empiezan con el token:
por ejemplo `[SFR]` tiene 16 contenedoras con PIC candidato frente a 15 del censo,
y los cinco sufijos de modo tienen una cada uno frente a cero. Ambas métricas se
conservan separadas; estas diferencias no cambian cobertura ni prueban módulos.
Es una prioridad léxica manual, no una
relación funcional demostrada con el obturador. `[IMAGING_IMG]`, `[EXL]` y `[SFR]`
preceden a `[DECMODEMGR]` (30 cadenas históricas).

REA primero: `analyze_function(0x437f5d48)` sobre el original agotó el límite MCP de 300 s.
Un timeout no prueba ausencia de función. El contraste decisivo usa Thumb de LLVM y bytes:
`cadena = (word_pool + ADD_PC + 4) & 0xffffffff`. El respaldo histórico se conserva aparte;
límites inferidos y pseudocódigo no sustituyen las instrucciones.
El [respaldo Ghidra de solo lectura](../../analysis/s178_census/funciones_historicas.json)
recupera los contenedores `0x437f5a04` (cinco sufijos de modo), `0x43900a24`
(campos D0–D7), `0x4381ba9c` (traza Image::Clone), `0x436c95b4` (traza EXL) y
`0x435c9124` (SetState). El sitio `0x439a63aa` de `[SFR]` no tiene función
existente en ese proyecto; no se sembró una entrada arbitraria.
[Registro de intento REA y consultas de respaldo](../../analysis/s178_census/rea_intento.json).
Las [instrucciones LLVM](../../analysis/s178_census/llvm_instrucciones.json) conservan
los comandos y offsets; se suma `0x43541000` para obtener direcciones virtuales.
La sección `.text` de la vista ELF se comparó completa y es idéntica al original.
El [contexto S400](../../analysis/s400_open_questions_triage/README.md) se consultó para
separar cobertura, clasificación y relaciones documentales; no se rehízo su triaje.

**S51 sin cambios.** Sin ejecutar firmware, cámara ni flasheo. La ausencia de una ruta
de obturador completamente electrónico sigue NO_VERIFICADO para estas candidatas.

```sh
.venv/bin/python analysis/s178_census/audit_pending.py
.venv/bin/python -m pytest tests/test_s178_census.py tests/test_s178_pending_audit.py tests/test_pages_status.py -q
```

El generador no cambia decisiones ni cobertura: regenera inventario y lista desde
los bytes, el mapa PIC histórico, el detalle y las decisiones revisadas.

## Validación final — 24-10-2026

- **95 pruebas pasan**: censo, inventario, bytes/pools, Pages y conocimiento, incluido MCP.
  El transporte de la prueba MCP se ejecutó fuera del aislamiento tras bloquearse dentro.
- Ruff/Mypy sin avisos nuevos. Se mantienen el SIM115 previo del test histórico y
  seis diagnósticos previos de Mypy en el cierre de `build_pages_status.py`; no se alteraron esas líneas.
  Los Python nuevos y los demás archivos comprobados pasan sin avisos.
- Mantenimiento completo del conocimiento: **1460 entidades y 3071 relaciones**
  en ambas reconstrucciones; derivados regenerados. Ninguna decisión S400 modificada.
- SHA-256 de firmware, `silent-liro` y directorio Ghidra coinciden con sus manifiestos finales.
  La vista ELF usada por LLVM contiene exactamente los bytes del original.

**VEREDICTO: APROBADO.** Se aprueba el inventario y los cambios respaldados;
las 226 investigaciones abiertas conservan sus límites explícitos.
