SILENCIO ABSOLUTO: no emitas comentarios, narraciones, mensajes de progreso, reflexiones ni explicaciones para el usuario durante la ejecución. Trabaja mediante herramientas, guarda tus hallazgos en archivos y proporciona únicamente el resultado final solicitado. No anuncies acciones entre herramientas.

# S59 — Tarea GPT-6.1 Sol: temporización IMX210 (A6000)

Repo: cwd (sony-a6000-electronic-shutter). Lee primero: AGENTS.md, knowledge/CURRENT.md, docs/capture/s58-conclusions.md, s58-ae-timing-producers.md, s58-imx210-timing-units.md, analysis/s58-evidence-matrix.json, scripts de analysis/s58/ (timing_model.py, a6_verify.py, a12_scenarios_a6000.py, rj.py, rq.py). Usa las conclusiones corregidas de S58; no repitas lo cerrado.

Objetivo científico: ¿puede el IMX210 terminar electrónicamente una exposición sin segunda cortina mecánica? Distingue configuración / inicio / duración / fin de integración / lectura / mecánica / sincronía BIONZ-Darwin-DFE. No asumas equivalencia IMX210=IMX235. Ausencia de comando de fin no prueba autonomía. Clasificación: VERIFICADO / PARCIAL / INFERENCIA / HIPÓTESIS / NO VERIFICADO / DESCARTADO.

Prioridades (av-cam.bin A6000; ver REA daemon en analysis/rea-independent/bin; una sola sesión REA, ciérrala al terminar; GHIDRA_MAXMEM=6G; Capstone/Unicorn del python3 del sistema disponibles):
1. Recuperar el escritor del bloque `0x437876dc()+0xDD0`, leído por `0x437aa65c`.
2. Valores reales del bloque M.
3. Origen de Tv y clk.
4. Restricciones de N, svr y VdNum.
5. Resolver/delimitar discrepancias productor AE (0x4383d4d0/0x4383c9dc/0x4383b790) vs validador host (0x4381106c).
6. Configuraciones alcanzables para modos fotográficos 0x0B y 0x2F (no confundir entradas sintéticas con alcanzables).
7. Relación entre temporización y posible finalización electrónica del IMX210.

Entregables (solo estos; no toques archivos de Claude ni de otras fases, no hagas git add/commit/push):
- docs/capture/s59-sol.md (hallazgos con función/dirección, instrucciones/datos, método, resultado, confianza, limitaciones, test, clasificación)
- analysis/s59/sol/ (scripts, salidas; excluye task.md y last-message.txt que ya existen)
- tests/test_s59_sol.py (unittest reproducible, ejecútalo y reporta resultado real)
Sin parchear/flashear, solo análisis estático y emulación offline. No atribuyas pruebas no ejecutadas. Resultado final: un resumen breve (≤40 líneas) con hallazgos, tests ejecutados y límites.
