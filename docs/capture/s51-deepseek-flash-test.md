# S51 — Prueba real de DeepSeek-V4.1-Flash-1017 como investigador autónomo

Presupuesto autorizado: USD 1.00. Gasto real observado: **USD 0.01** (saldo $2.00 → $1.99).
Ejecutado 2026-10-19. Evidencia: `analysis/s51/deepseek/` (scripts, `balance_log.txt`, `phase1_result.json`).

## 1. Rendimiento técnico

- **Modelo efectivo:** `deepseek-flash` (DeepSeek-V4.1-Flash-1017), confirmado en el campo `"model"` de cada
  respuesta de la API (`analysis/s51/deepseek/phase1_result.json`, prueba directa en
  `scripts/s51/test_api_call.fish`). No se usó `deepseek-v4-pro` en ningún momento.
- **Cliente agente:** Claude Code en modo no interactivo (`claude -p ... --bare`), apuntado al endpoint
  Anthropic-compatible (`https://api.deepseek.com/anthropic`), con `--mcp-config` restringido a los MCP
  del proyecto (`rea`, `sony-a6000-knowledge`) y `--permission-mode bypassPermissions` (sin ello, el modo
  `--print` deniega automáticamente cualquier tool call).
- **MCP realmente invocados:** sí se invocó REA (confirmado por el log de la sesión fallida: 13 turnos,
  llamadas a tools antes del aborto). No se puede confirmar si llegó a completar una consulta útil al MCP
  de conocimiento antes del aborto — el resultado no incluye las respuestas intermedias de las tools.
- **Funciones analizadas:** ninguna de forma utilizable por el propio DeepSeek — la sesión abortó con
  `"api_error":"autocompact_thrashing"` antes de producir una respuesta final.
- **Causa raíz identificada (verificada después, por mí/Claude directamente):** `mcp__rea__analyze_function`
  sobre `DmmCloseAndFree` devuelve ~268.000 caracteres de una sola vez (pseudocódigo + ensamblador + xrefs
  completos sin filtrar). Ese volumen, repetido en más de una tool call, llenó la ventana de contexto,
  forzó compactación, se volvió a llenar en ≤3 turnos, y el harness cortó la sesión (`rapid_refill_breaker`).
  Esto no es un fallo de DeepSeek entendiendo la tarea; es una incompatibilidad entre el tamaño de las
  respuestas de REA sin acotar y la disciplina de contexto necesaria para absorberlas.
- **Validación directa (bypaseando el problema):** usé REA yo mismo con `jq` para extraer solo
  `pseudocode`/`assembly`/`callers`/`callees` en vez de volcar el JSON completo. Resultado para
  `DmmAccess::DmmCloseAndFree` (Ghidra `0x2afe8`, thunk `0x1fdf4`): coincide exactamente con
  [S37](s37-libmprctrl-dmm-extents.md) — mismo thunk, mismo callee `MprCtrlLog::SetUnitHandleLog`
  (`0x1ee80`→`0x23db2`), mismo salto final `b.w 0x1fca0`. **Coincidencia total con evidencia histórica,
  sin hallazgos nuevos** (la función ya estaba completamente documentada en S37/S30).
- **Errores/alucinaciones detectadas:** ninguna alucinación — DeepSeek no llegó a emitir una respuesta
  final citable. El único error es el de infraestructura (thrashing) ya descrito.
- **Limitaciones:** no se pudo evaluar la calidad de razonamiento de DeepSeek sobre evidencia REA real,
  porque la sesión nunca llegó a sintetizar una respuesta. La prueba de fase 1 (tal como se diseñó, pidiendo
  a DeepSeek que decompile y compare libremente) no es repetible sin antes acotar el tamaño de las
  respuestas de REA (p. ej. instruir explícitamente "no vuelques el JSON completo, pide solo pseudocódigo y
  resume").

## 2. Investigación S51 (continuación de S50)

No se ejecutó una segunda fase de investigación nueva de fondo físico (rutas de configuración del sensor /
exposición electrónica) dentro de esta prueba: el presupuesto de tiempo se usó en diagnosticar y validar la
integración DeepSeek+REA (fase 1), y el estado de conocimiento existente (`get_current_state`,
`get_open_questions`) confirma que S46–S50 ya dejaron las preguntas A/B abiertas como NO_VERIFICADO/
CONFLICTO_PENDIENTE (p. ej. escritor de `0x43e16d2c` sin recuperar, integración y supresión de cortinas
NO_VERIFICADO). Repetir esas búsquedas en esta sesión habría violado la restricción explícita de S51 de no
repetir trabajo ya hecho en S49/S50 sin una REA nueva y acotada que esta prueba no llegó a ejecutar.

**A. ¿Se identificó una ruta demostrada de exposición totalmente electrónica?** NO.
**B. ¿Existe evidencia suficiente para diseñar ahora un parche funcional?** NO.
**C. ¿Se demostró imposibilidad física del sensor?** NO.

Ninguna de las tres respuestas cambia respecto al cierre de S50: sigue sin demostrarse ni la capacidad ni
la imposibilidad de una captura completamente electrónica a resolución completa.

## 3. Evaluación económica

| Intento | Saldo inicial | Saldo final | Gasto observado |
|---|---|---|---|
| Fase 1 (sesión completa, thrashing) | $2.00 | $1.99 | **$0.01** (entre $0.005 y $0.015 por redondeo a centavos) |

Tokens reales reportados por la API en esa sesión (campo `modelUsage.deepseek-flash` del resultado):
entrada sin caché 305.773, entrada con caché (`cacheReadInputTokens`) 1.521.152, salida 21.100.
Hora de la corrida: ~20:04 UTC del 19/10 (martes) → fuera de las franjas peak de DeepSeek
(01:00–04:00 y 06:00–10:00 UTC, lun–vie), por lo tanto tarifa **off-peak**: entrada sin caché $0.15/1M,
entrada con caché $0.003/1M, salida $0.6/1M.

Costo calculado aplicando esa tarifa a esos tokens:
`305.773×0.15 + 1.521.152×0.003 + 21.100×0.6` (todo ÷1M) ≈ **$0.063**.

**Verificación cruzada:** el dashboard de uso de la propia cuenta DeepSeek (2026-10-19) reporta
1.848.073 tokens totales — 1.521.152 de entrada con acierto de caché, 305.811 de entrada sin caché,
21.110 de salida — prácticamente idénticos a los de `modelUsage` (diferencia de <0,1%, atribuible a un
turno adicional de diagnóstico). Esto descarta que la discrepancia de costo se deba a un conteo erróneo
de tokens por parte de Claude Code: los tokens son reales y confirmados por DeepSeek.

**Discrepancia de costo sin explicar:** el costo calculado por tarifa publicada sobre esos tokens reales
(~$0.063) sigue siendo más de 4× el gasto real por saldo (~$0.01). Con los tokens ya verificados, las
hipótesis que quedan son: (a) alguna promoción/descuento activo en la cuenta no reflejado en la tabla de
precios pública, (b) una tarifa horaria distinta a la asumida (aunque la corrida fue ~20:04 UTC, fuera de
los rangos peak publicados), o (c) una franja de precios introductoria para el modelo recién lanzado. No
tengo forma de confirmar cuál aplica sin acceso a la facturación detallada de la cuenta. El campo
`total_cost_usd` que el propio JSON de Claude Code reporta ($1.95, `costBasis:"unknown"`) sigue siendo
el más alejado de los tres: usa la tabla de precios de Anthropic, no la de DeepSeek, y debe descartarse
por completo.

No se reutilizó el saldo para una segunda fase porque la condición de bloqueo técnico (DeepSeek
+ Claude Code no pudo completar una tarea real de RE sin ajuste previo del prompt) ya es una conclusión
decisiva sobre la integración tal como está probada, y el presupuesto restante ($0.98) se dejó intacto
en vez de gastarlo en reintentos no planeados por S51 §7 ("no consumas el presupuesto en intentos
repetitivos de configuración").

- Total tokens de entrada: 305.773 (sin caché) + 1.521.152 (caché) = 1.826.925
- Total tokens de salida: 21.100
- Número de peticiones: 1 sesión multi-turno (13 turnos internos), más 2 llamadas de diagnóstico triviales
  (balance, prueba de 10 tokens) con costo despreciable.
- Tiempo total: ~2 minutos (sesión fase 1) + diagnóstico.
- Funciones investigadas con éxito: 1 (`DmmAccess::DmmCloseAndFree`), validada por mí directamente, no por
  DeepSeek.
- Hallazgos realmente nuevos: ninguno (coincide con S37).

## 4. Comparación

- **Eficiencia económica:** el gasto real fue mínimo ($0.01 de $1.00), pero porque la sesión abortó, no
  porque haya sido una investigación barata y productiva. No es una base válida para proyectar costo por
  hallazgo.
- **Precisión:** no evaluable — DeepSeek no llegó a emitir una conclusión propia verificable en esta prueba.
- **Capacidad de usar REA autónomamente:** parcial. Sí invocó las tools (no fue un fallo de conectividad
  MCP), pero no sobrevivió al tamaño de sus propias respuestas sin instrucciones explícitas de acotar
  consultas — algo que S51 §7 ya anticipaba como riesgo ("no vuelques miles de líneas... si puedes guardar
  evidencia y consultar rangos relevantes") pero que el prompt de fase 1 no impuso con suficiente fuerza.
- **¿Reemplaza o complementa a Claude/Codex?** Con esta evidencia, no: en su configuración actual (prompt
  libre + REA sin acotar), DeepSeek Flash vía Claude Code no completó ni una validación simple. Sería
  necesario un prompt que fuerce consultas REA pequeñas (como las que yo usé manualmente con `jq`) antes de
  repetir la prueba. No se dispone de datos para comparar contra el costo de las suscripciones de Claude
  Pro/Codex (esa comparación no se intentó, siguiendo la instrucción de no inventarla).

## 5. Condición de finalización aplicada

Se cerró la prueba por la condición 4 de S51 §10: *"DeepSeek demuestra ser incompatible con las
herramientas necesarias"* — en su forma concreta de no sobrevivir al volumen de las respuestas de REA sin
acotar —, no por agotamiento de presupuesto (quedó $0.98 de margen sin usar).
