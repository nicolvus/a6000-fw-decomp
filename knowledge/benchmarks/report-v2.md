# Benchmark v2 — verdad de referencia estructurada (Fase 12.6)

> Nota (26-10-2026): las citas `README.md:N` de este reporte son números de línea del README previo a la reorganización documental (commit `b782ebe2`, íntegro en [docs/history/README-historial-2026-10-26.md](../../docs/history/README-historial-2026-10-26.md), donde la línea N original es la N+2). No se reescriben: son instantáneas del benchmark.

Línea base PRE-rediseño conservada sin cambios en knowledge/benchmarks/baseline-2026-10-18-pre-12.6.md. Este reporte usa criterios de acierto distintos (afirmación+fuente, arista exacta, abstención correcta, cobertura de ambigüedad) y por tanto NO es comparable número-a-número con la línea base; compara la CAPACIDAD de cada método, no una métrica idéntica.

## Precision@1 por método (todas las categorías)

| Método | Aciertos | Total | Precision@1 | Latencia media (s) | Tokens aprox. medios |
|---|---:|---:|---:|---:|---:|
| ask | 8 | 17 | 0.47 | 0.0621 | 217 |
| fts5 | 8 | 17 | 0.47 | 0.0614 | 2473 |
| graph | 5 | 6 | 0.83 | 0.0440 | 1019 |
| rg | 7 | 17 | 0.41 | 0.1890 | 4420819 |

## Por categoría

| Categoría | Método | Consulta | Acierto | Latencia (s) | Chars | RSS Δ (KB) |
|---|---|---|---|---:|---:|---:|
| exact | rg | exact-setimagewrited-addr | ✓ | 0.1495 | 360557 | 124204 |
| exact | fts5 | exact-setimagewrited-addr | ✓ | 0.1086 | 62574 | 0 |
| exact | ask | exact-setimagewrited-addr | ✗ | 0.1253 | 282 | 0 |
| exact | rg | exact-osal-0x50004 | ✓ | 0.1207 | 78173 | 32652 |
| exact | fts5 | exact-osal-0x50004 | ✓ | 0.0955 | 72519 | 0 |
| exact | ask | exact-osal-0x50004 | ✓ | 0.0946 | 450 | 0 |
| conceptual | rg | concept-darwin-rom-base | ✗ | 0.1354 | 258 | 0 |
| conceptual | fts5 | concept-darwin-rom-base | ✓ | 0.0636 | 2746 | 0 |
| conceptual | ask | concept-darwin-rom-base | ✓ | 0.0634 | 863 | 0 |
| conceptual | rg | concept-gpio-curtain | ✗ | 0.1238 | 134 | 0 |
| conceptual | fts5 | concept-gpio-curtain | ✓ | 0.0614 | 2489 | 0 |
| conceptual | ask | concept-gpio-curtain | ✓ | 0.0627 | 976 | 0 |
| conceptual | rg | concept-imx210-vs-imx284 | ✗ | 0.1025 | 132 | 0 |
| conceptual | fts5 | concept-imx210-vs-imx284 | ✗ | 0.0644 | 2679 | 0 |
| conceptual | ask | concept-imx210-vs-imx284 | ✗ | 0.0641 | 1017 | 0 |
| historical | rg | hist-s27-corrects | ✓ | 0.1208 | 3271 | 6440 |
| historical | fts5 | hist-s27-corrects | ✓ | 0.0698 | 2541 | 0 |
| historical | graph | hist-s27-corrects | ✓ | 0.0583 | 928 | 0 |
| historical | ask | hist-s27-corrects | ✓ | 0.0597 | 868 | 0 |
| historical | rg | hist-s29-setimagewrited-code | ✗ | 0.117 | 137 | 0 |
| historical | fts5 | hist-s29-setimagewrited-code | ✓ | 0.0624 | 2628 | 0 |
| historical | ask | hist-s29-setimagewrited-code | ✓ | 0.0621 | 1112 | 0 |
| relational | rg | rel-osal-callback | ✓ | 0.1244 | 155 | 0 |
| relational | fts5 | rel-osal-callback | ✗ | 0.0397 | 2361 | 0 |
| relational | graph | rel-osal-callback | ✓ | 0.0353 | 298 | 0 |
| relational | ask | rel-osal-callback | ✗ | 0.0404 | 1031 | 0 |
| relational | rg | rel-ghidra-one-hop | ✓ | 0.1115 | 145 | 0 |
| relational | fts5 | rel-ghidra-one-hop | ✗ | 0.0407 | 3000 | 0 |
| relational | graph | rel-ghidra-one-hop | ✓ | 0.0365 | 13538 | 0 |
| relational | ask | rel-ghidra-one-hop | ✗ | 0.0418 | 1015 | 0 |
| multietapa | rg | multi-ghidra-two-hop-chain | ✗ | 0.1352 | 119 | 0 |
| multietapa | fts5 | multi-ghidra-two-hop-chain | ✗ | 0.0397 | 2658 | 0 |
| multietapa | graph | multi-ghidra-two-hop-chain | ✗ | 0.0369 | 9379 | 0 |
| multietapa | ask | multi-ghidra-two-hop-chain | ✗ | 0.0408 | 889 | 0 |
| multietapa | rg | multi-encodestill-chain-no-coverage | ✗ | 0.0991 | 143 | 0 |
| multietapa | fts5 | multi-encodestill-chain-no-coverage | ✗ | 0.0393 | 2733 | 0 |
| multietapa | graph | multi-encodestill-chain-no-coverage | ✓ | 0.0365 | 153 | 0 |
| multietapa | ask | multi-encodestill-chain-no-coverage | ✗ | 0.0406 | 940 | 0 |
| negative | rg | neg-fabricated-function-address | ✗ | 0.1116 | 1308 | 0 |
| negative | fts5 | neg-fabricated-function-address | ✗ | 0.0879 | 27 | 0 |
| negative | ask | neg-fabricated-function-address | ✓ | 0.0907 | 63 | 0 |
| negative | rg | neg-disconnected-trace-node | ✗ | 0.139 | 146 | 0 |
| negative | fts5 | neg-disconnected-trace-node | ✗ | 0.1176 | 27 | 0 |
| negative | graph | neg-disconnected-trace-node | ✓ | 0.0603 | 168 | 0 |
| negative | ask | neg-disconnected-trace-node | ✗ | 0.0633 | 1137 | 0 |
| ambiguous | rg | ambig-generic-callback-term | ✓ | 0.6073 | 136678556 | 96868 |
| ambiguous | fts5 | ambig-generic-callback-term | ✓ | 0.0378 | 2497 | 1900512 |
| ambiguous | ask | ambig-generic-callback-term | ✓ | 0.069 | 1049 | 0 |
| ambiguous | rg | ambig-generic-init-term | ✓ | 0.7601 | 163492184 | 0 |
| ambiguous | fts5 | ambig-generic-init-term | ✓ | 0.0377 | 2526 | 493252 |
| ambiguous | ask | ambig-generic-init-term | ✓ | 0.0593 | 1073 | 0 |
| partial | rg | partial-caution-config-empty | ✗ | 0.1078 | 148 | 0 |
| partial | fts5 | partial-caution-config-empty | ✗ | 0.0381 | 1704 | 0 |
| partial | ask | partial-caution-config-empty | ✗ | 0.0384 | 918 | 0 |
| partial | rg | partial-xref-family-no-binary-id | ✗ | 0.1477 | 137 | 0 |
| partial | fts5 | partial-xref-family-no-binary-id | ✗ | 0.0389 | 2425 | 0 |
| partial | ask | partial-xref-family-no-binary-id | ✗ | 0.0399 | 1109 | 0 |

## Limitaciones conocidas del criterio de puntuación (no ajustadas a propósito)

- **partial**: el acierto exige salida VACÍA. Un método que devuelve texto no distingue aquí entre 'afirmé una relación falsa' y 'listé archivos reales sin resolver ninguna relación concreta' (p. ej. rg encontrando literalmente la cadena 'CautionConfig' en archivos que existen). Es un criterio conservador que probablemente subestima el acierto real de rg/fts5 en esta categoría; no se relajó para no ajustar el benchmark en busca de resultados favorables.
- **rg sin presupuesto**: en consultas genéricas ('callback', 'init') ripgrep recorre TODO el repositorio (incluye analysis/, binarios de evidencia, logs) sin ningún recorte, generando decenas de millones de caracteres. Esto es intencional (mide el costo real de 'sin motor'), no un error de medición; infla fuertemente el promedio de tokens estimados de la fila 'rg' en la tabla de Precision@1 — leer esa fila junto con la tabla por categoría, no aislada.
- **memoria (RSS Δ)**: aproximada por diferencia de resource.getrusage(RUSAGE_CHILDREN).ru_maxrss entre llamadas sucesivas; es un pico ACUMULADO entre procesos hijo del mismo padre, puede mostrar 0 si una llamada previa ya alcanzó un pico mayor que la actual. No es una medición aislada por proceso.
- **tokens**: SIEMPRE una estimación (caracteres/4). No hay tokenizador real ni reporte de uso de un agente real disponible en este entorno; estos números NO deben citarse como ahorro de tokens real de Claude Code o Codex.

## Notas de verdad de referencia

- **exact-setimagewrited-addr** (exact/WriteStill): docs/capture/pool-write-completion.md:27, verificado manualmente antes de este benchmark
- **exact-osal-0x50004** (exact/OSAL): README.md:93 y docs/capture/s28-osal-pin-contract-closure.md; 0x50004 es un identificador de mensaje OSAL, NO una dirección de función
- **concept-darwin-rom-base** (conceptual/Darwin): docs/STATE.md:20, 'La base es 0x4200, NO 0'; 0x4200 es una base ROM, NO una dirección de función
- **concept-gpio-curtain** (conceptual/GPIO): docs/capture/fm3-gpio-shutter-mapping.md, verificado manualmente
- **concept-imx210-vs-imx284** (conceptual/IMX210): README.md:39, '0x4e de IMX284 es rechazado por el controlador IMX210 de A6000'
- **hist-s27-corrects** (historical/general): docs/capture/README.md:16 corrige S27, verificado manualmente en Fase 3
- **hist-s29-setimagewrited-code** (historical/WriteStill): README.md:91, corrección de S29: SetImageWrited es 0x1007, no 0x1009 (verificada manualmente)
- **rel-osal-callback** (relational/OSAL): relación CALLS real extraída de evidencia REA (Fase 12.4.B); no existe en ningún documento Markdown, solo en el grafo
- **rel-ghidra-one-hop** (relational/general): relación CALLS real extraída de pseudocódigo Ghidra (Fase 12.4.B); solo existe en el grafo
- **multi-ghidra-two-hop-chain** (multietapa/general): cadena real de 2 saltos (FUN_43792a0c -> FUN_43804c5c -> FUN_43b00d06); no reconstruible con un solo grep ni con un único resultado FTS5
- **multi-encodestill-chain-no-coverage** (multietapa/EncodeStill): CONTEXT.md:26 documenta esta cadena como hallazgo manual de la investigación, pero NINGUNA de esas direcciones es una entidad Function en el grafo (no analizada por Ghidra/REA en el corpus actual): el grafo debe abstenerse, no inventar la ruta
- **neg-fabricated-function-address** (negative/general): 0x50004 es un identificador de mensaje OSAL, no una dirección Ghidra: 'FUN_50004' no debe existir como función en ningún método
- **neg-disconnected-trace-node** (negative/general): un id de nodo que no existe en el grafo debe reportar ausencia de relaciones, nunca inventar un salto
- **ambig-generic-callback-term** (ambiguous/general): 'callback' aparece en documentos de varios subsistemas no relacionados (OSAL, CAIF, Darwin); un método correcto debe exponer varias fuentes candidatas, no colapsar a una sola 'la' respuesta
- **ambig-generic-init-term** (ambiguous/general): 'init' es genérico y aparece en múltiples binarios/documentos sin relación entre sí
- **partial-caution-config-empty** (partial/general): familia REA CautionConfig (12+12 archivos, catalogada en knowledge/catalog/JSON-CATALOG.md): workflow_entries/entries están vacíos en el corpus real; no se construyó extractor porque no hay relación verificable que extraer, y ningún método debe inventar una
- **partial-xref-family-no-binary-id** (partial/general): familia Ghidra de 61 archivos con xrefs reales pero SIN binary_sha256 (hallazgo de inventory_json.py, Fase 12.4.A): la identidad del binario no puede verificarse, así que no se incorporó al grafo; una consulta sobre ella debe devolver 'sin ruta verificable', no una relación fabricada
