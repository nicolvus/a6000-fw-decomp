# S178 — censo de etiquetas A6000 fw3.21

Recuento vigente tras la auditoría del 23-10-2026.
Las listas históricas incluían etiquetas ya documentadas; la tabla siguiente usa el detalle vigente.
[Informe y evidencia individual](../../docs/capture/s178-census.md).

| magnitud | valor |
|---|---|
| etiquetas distintas `[XXX]` | **372** (techo, no número de módulos) |
| etiquetas con hito documental | **96** |
| subetiquetas documentadas | **122** |
| **pendientes reales** | **146** |
| fragmentos descartados como módulos | **8** |
| cobertura documental | **218/372** = **58.60 %** |
| etiquetas exclusivas de A6000 | **93** |
| presentes en A6000/A7S y ausentes en A6300 | **7** |

Antes: 239 pendientes; después de la auditoría: 226 pendientes + 13 fragmentos descartados; tras reclasificar 73 como sub-etiqueta de módulos ya documentados (pasada del 03-11-2026): 146 pendientes (S633 reclasifica las cinco `[STK_*]` como sub-etiquetas de `[STK]`; S631 cierra `[IMAGING_IMG]`; S632 cierra `[MODE_SNR_BUS_THROUGH]` y reclasifica `[MODE_CAP*]` como sub-etiquetas de `[IMAGING_CAP]`).
Descartar no aumenta cobertura. Se mantiene 372 como denominador histórico.
Las siete ausentes en A6300 son `[STK]`, `[STK_AUTO_SAL]`, `[STK_COLOR_SIM]`,
`[STK_C_SIM]`, `[STK_TOUCH_SIM]`, `[STK_T_SIM]` y `[OSD]`.

## Inventario reproducible

- [Lista completa, prioridad y motivo](pendientes.md): 146 abiertas y 8 descartadas.
- [Ocurrencias, direcciones y referencias por etiqueta](pendientes_auditados.json).
- [Decisiones manuales](decisiones_auditoria.json): 8 RECHAZO (los otros cinco, `[MODE_CAP*]`, pasan a sub-etiqueta de `[IMAGING_CAP]` en S632), cuatro ACEPTO como candidatas y dos NO_VERIFICADO examinadas.
- [Once referencias contrastadas con bytes y pools](evidencia_bytes.json).
- [Detalle canónico](census_detalle.json) y [resumen](census.json).

Los 8 descartes son `[D0]`–`[D7]`. Los cinco `[MODE_CAP*]`, descartados antes, son sufijos de los diagnósticos de `[IMAGING_CAP]` y pasan a sub-etiquetas (S632).
Las candidatas aceptadas `[SFR]`, `[EXL]` y `[DECMODEMGR]` siguen pendientes de decodificación (`[IMAGING_IMG]` se cerró en S631). Las otras 222 abiertas siguen NO_VERIFICADO;
220 aún no tienen examen individual de instrucciones. Ninguna se cierra por una mención documental.

Método: patrón `\[[A-Z][A-Z0-9_]{1,24}\]` sobre
`analysis/rea-independent/input/av-cam.bin`, base `0x43541000`.
El mapa `analysis/s106_imaging_cap/pic_refs_strict_global.json` aporta candidatos PIC,
no prueba de flujo. Se distinguen token y cadena contenedora. SHA-256 de entradas en el inventario.
Prioridad: captura/sensor, sincronización/visor, resto; luego cadenas contenedoras distintas
con PIC candidato descendentes, recontadas desde las ocurrencias. En 141 etiquetas el
contador difiere del histórico por incluir tokens interiores; ambas métricas se conservan.
Las cifras históricas de cadenas no equivalen a funciones demostradas.

REA primero: consulta de función agotada a los 300 s; respaldo histórico y
verificación independiente con LLVM/bytes para los casos decisivos. Un timeout no prueba ausencia.
No se alteran S51 ni las decisiones del triaje S400.

```sh
.venv/bin/python analysis/s178_census/audit_pending.py
.venv/bin/python -m pytest tests/test_s178_census.py tests/test_s178_pending_audit.py tests/test_pages_status.py -q
```

**S51 sin cambios.** Sin ejecutar firmware, cámara ni flasheo.
