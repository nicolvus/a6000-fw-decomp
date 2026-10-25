# Elementos diferidos y trabajo estático restante

Actualizado el 24-10-2026. [Cola y límites vigentes](../../docs/capture/repo-audit-2026-10-24.md).

| Elemento | Estado y alcance |
|---|---|
| P1–P21 | Propuestas sin ejecutar. Todas diferidas por instrucción del usuario hasta completar la ingeniería inversa necesaria; no solo pendientes de autorización. P0 es preparación. |
| Apertura/análisis REA de `libObj.so` | Trabajo local. Un timeout previo no demuestra que haga falta intervención humana. Reutilizar primero evidencia exportada. |
| RecordImage `0x90b248` y RecordStill `0x908afc` | Identidades y consumidor de 25 `call_fn` recuperados en la [auditoría de contrato](../../docs/capture/recordstill-contract-audit-2026-10-23.md). Restan activación de la entrada concreta, callees y enlace con `0x40193`; trabajo estático. |
| Cola `0x40193` | [Instalador y consumidor de arranque conocidos](../../docs/capture/queue-40193-flow-2026-10-23.md). Restan servicio indirecto `+0x3c`, callback OSAL Linux y transporte Linux↔LIRO. No está bloqueado por cámara. |
| Escritores de `svr_num`/`VdNum`, `S[0]` y gates | Procedencia no cerrada en el alcance documentado. No está demostrado que solo se pueda resolver en cámara; continuar estáticamente según la matriz S51. |
| Semántica eléctrica IMX210/IMX235 | Buscar datasheets/evidencia documental. Si la evidencia estática no permite cerrar un punto, registrar el límite antes de proponer observación física. |

Ninguna prueba P1–P21 ejecutada en estos planes; S64 es un antecedente distinto.
S51 sigue A=NO, B=NO, C=NO.
