# Benchmark de recuperación — Sony A6000 (generado, no editar a mano)

Verdad de referencia fijada MANUALMENTE antes de ejecutar este script (ver `note` de cada consulta en `scripts/knowledge/benchmark.py`), no generada por el propio sistema. `approx_tokens_estimate` = caracteres/4, SIEMPRE una aproximación: no hay tokenizador real disponible en este entorno.

| Consulta | Método | Latencia (s) | Líneas | Chars | Tokens (aprox.) | Acierto |
|---|---|---:|---:|---:|---:|---|
| setimagewrited-addr | rg_crudo | 0.0946 | 322 | 360448 | 90112 | ✓ |
| setimagewrited-addr | search_exact | 0.1232 | 52 | 62574 | 15644 | ✓ |
| setimagewrited-addr | ask | 0.1013 | 5 | 367 | 92 | ✓ |
| setimagewrited-code | rg_crudo | 0.1206 | 1287 | 6043816 | 1510954 | ✓ |
| setimagewrited-code | search_exact | 0.147 | 52 | 198831 | 49708 | ✓ |
| setimagewrited-code | ask | 0.1535 | 9 | 1138 | 284 | ✓ |
| gpio-curtain | rg_crudo_todas_palabras | 0.2634 | 83965 | 17913478 | 4478370 | ✓ |
| gpio-curtain | search_text_fts5 | 0.0387 | 40 | 2572 | 643 | ✓ |
| gpio-curtain | ask | 0.0607 | 14 | 978 | 244 | ✓ |
| efcs-selector | rg_crudo_todas_palabras | 0.6851 | 13987 | 92100593 | 23025148 | ✓ |
| efcs-selector | search_text_fts5 | 0.0494 | 39 | 2490 | 622 | ✓ |
| efcs-selector | ask | 0.0378 | 18 | 1036 | 259 | ✓ |
| darwin-rom-base | rg_crudo_todas_palabras | 0.8963 | 335650 | 191766895 | 47941724 | ✓ |
| darwin-rom-base | search_text_fts5 | 0.0398 | 45 | 2746 | 686 | ✓ |
| darwin-rom-base | ask | 0.0458 | 15 | 863 | 216 | ✓ |
| a6300-comparison | rg_crudo_todas_palabras | 0.3015 | 21437 | 23194468 | 5798617 | ✓ |
| a6300-comparison | search_text_fts5 | 0.0391 | 43 | 2366 | 592 | ✓ |
| a6300-comparison | ask | 0.0388 | 18 | 1011 | 253 | ✓ |
| s27-correction | search_graph | 0.0365 | 15 | 928 | 232 | ✓ |
| s27-correction | search_claim | 0.0369 | 16 | 1105 | 276 | ✓ |
| s27-correction | ask | 0.0366 | 13 | 868 | 217 | ✓ |

Aciertos: 21/21 comparaciones método×consulta.
