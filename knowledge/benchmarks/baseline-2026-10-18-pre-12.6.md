# Benchmark de recuperación — Sony A6000 (generado, no editar a mano)

Verdad de referencia fijada MANUALMENTE antes de ejecutar este script (ver `note` de cada consulta en `scripts/knowledge/benchmark.py`), no generada por el propio sistema. `approx_tokens_estimate` = caracteres/4, SIEMPRE una aproximación: no hay tokenizador real disponible en este entorno.

| Consulta | Método | Latencia (s) | Líneas | Chars | Tokens (aprox.) | Acierto |
|---|---|---:|---:|---:|---:|---|
| setimagewrited-addr | rg_crudo | 0.734 | 322 | 360448 | 90112 | ✓ |
| setimagewrited-addr | search_exact | 0.1057 | 52 | 62574 | 15644 | ✓ |
| setimagewrited-addr | ask | 0.0928 | 8 | 856 | 214 | ✓ |
| setimagewrited-code | rg_crudo | 0.3417 | 1287 | 6043816 | 1510954 | ✓ |
| setimagewrited-code | search_exact | 0.0976 | 52 | 133948 | 33487 | ✓ |
| setimagewrited-code | ask | 0.0921 | 5 | 742 | 186 | ✓ |
| gpio-curtain | rg_crudo_todas_palabras | 0.3273 | 83987 | 17917463 | 4479366 | ✓ |
| gpio-curtain | search_text_fts5 | 0.0677 | 40 | 2572 | 643 | ✓ |
| gpio-curtain | ask | 0.0613 | 14 | 978 | 244 | ✓ |
| efcs-selector | rg_crudo_todas_palabras | 0.6824 | 14075 | 92110936 | 23027734 | ✓ |
| efcs-selector | search_text_fts5 | 0.0435 | 39 | 2490 | 622 | ✓ |
| efcs-selector | ask | 0.0388 | 18 | 1036 | 259 | ✓ |
| darwin-rom-base | rg_crudo_todas_palabras | 1.1664 | 335993 | 191808528 | 47952132 | ✓ |
| darwin-rom-base | search_text_fts5 | 0.0662 | 45 | 2746 | 686 | ✓ |
| darwin-rom-base | ask | 0.0624 | 15 | 863 | 216 | ✓ |
| a6300-comparison | rg_crudo_todas_palabras | 0.1904 | 21732 | 23231141 | 5807785 | ✓ |
| a6300-comparison | search_text_fts5 | 0.0663 | 43 | 2366 | 592 | ✓ |
| a6300-comparison | ask | 0.0625 | 18 | 1011 | 253 | ✓ |
| s27-correction | search_graph | 0.059 | 15 | 928 | 232 | ✓ |
| s27-correction | search_claim | 0.059 | 16 | 1105 | 276 | ✓ |
| s27-correction | ask | 0.0602 | 13 | 868 | 217 | ✓ |

Aciertos: 21/21 comparaciones método×consulta.
