# S178 — censo de etiquetas A6000 fw3.21

Recuento vigente tras la auditoría del 23-10-2026.
Las listas históricas incluían etiquetas ya documentadas; la tabla siguiente usa el detalle vigente.
[Informe y evidencia individual](../../docs/capture/s178-census.md).

| magnitud | valor |
|---|---|
| etiquetas distintas `[XXX]` | **372** (techo, no número de módulos) |
| etiquetas con hito documental | **242** |
| subetiquetas documentadas | **130** |
| **pendientes reales** | **0** |
| fragmentos descartados como módulos | **0** |
| cobertura documental | **372/372** = **100.00 %** |
| etiquetas exclusivas de A6000 | **93** |
| presentes en A6000/A7S y ausentes en A6300 | **7** |

Antes: 239 pendientes; después de la auditoría: 226 pendientes + 13 fragmentos descartados; tras reclasificar 73 como sub-etiqueta de módulos ya documentados (pasada del 03-11-2026): 0 pendientes (S634 documenta con medidas las 146 restantes, familia OTROS; S633 reclasifica las cinco `[STK_*]` como sub-etiquetas de `[STK]`; S631 cierra `[IMAGING_IMG]`; S632 cierra `[MODE_SNR_BUS_THROUGH]` y reclasifica `[MODE_CAP*]` como sub-etiquetas de `[IMAGING_CAP]`).
Descartar no aumenta cobertura. Se mantiene 372 como denominador histórico.
Las siete ausentes en A6300 son `[STK]`, `[STK_AUTO_SAL]`, `[STK_COLOR_SIM]`,
`[STK_C_SIM]`, `[STK_TOUCH_SIM]`, `[STK_T_SIM]` y `[OSD]`.

## Inventario reproducible

- [Lista completa, prioridad y motivo](pendientes.md): 0 abiertas y 0 descartadas.
- [Ocurrencias, direcciones y referencias por etiqueta](pendientes_auditados.json).
- [Decisiones manuales](decisiones_auditoria.json): 8 RECHAZO (los otros cinco, `[MODE_CAP*]`, pasan a sub-etiqueta de `[IMAGING_CAP]` en S632), cuatro ACEPTO como candidatas y dos NO_VERIFICADO examinadas.
- [Once referencias contrastadas con bytes y pools](evidencia_bytes.json).
- [Detalle canónico](census_detalle.json) y [resumen](census.json).

Los ocho `[D0]`–`[D7]`, descartados antes, son campos de dos trazas de `[CAM_UTIL_ADJ]` y pasan a sub-etiquetas (S636); ya no queda ningún descarte. Los cinco `[MODE_CAP*]`, descartados antes, son sufijos de los diagnósticos de `[IMAGING_CAP]` y pasan a sub-etiquetas (S632).
Las 146 etiquetas que seguían pendientes pasan a hito con S634: medidas de cadenas, sitios, funciones, referencias y alcance al obturador; sin atribuir significado ni módulo. «Documentada» no implica decodificada: la semántica de cada módulo sigue sin afirmarse. Ninguna se cierra por una mención documental sin medida.

**S51 sin cambios.** Sin ejecutar firmware, cámara ni flasheo.
