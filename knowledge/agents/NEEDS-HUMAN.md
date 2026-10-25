# Elementos diferidos y trabajo estático restante

Actualizado el 25-10-2026. [Cola y límites vigentes](../../docs/capture/capture-static-followup-2026-10-25.md).

| Elemento | Estado y alcance |
|---|---|
| P1–P21 | Propuestas sin ejecutar. Todas diferidas por instrucción del usuario hasta completar la ingeniería inversa necesaria; no solo pendientes de autorización. P0 es preparación. |
| Apertura/análisis REA de `libObj.so` | Trabajo local. Un timeout previo no demuestra que haga falta intervención humana. Reutilizar primero evidencia exportada. |
| RecordImage `0x90b248` y RecordStill `0x908afc` | Identidades, consumidor de 25 `call_fn` y entrada estado 2/mensaje `0x10000005` conocidos. Mapeadas las 43 llamadas de RecordStill: 20 importaciones iguales y ocho parejas locales candidatas. Restan productor del mensaje, equivalencia completa y enlace con `0x40193`/YC/archivo/cortina. |
| Cola `0x40193` | Servicio `sta_tsk(0x46,descriptor)` y transporte userland→ioctl→OSAL kernel→recepción bloqueante LIRO verificados estáticamente. No exigir callback Linux específico para esta ruta. Activación efectiva no observada. [Evidencia](../../docs/capture/queue-40193-flow-2026-10-23.md). |
| Escritores de `svr_num`/`VdNum`, `S[0]` y gates | S[0] y G→S resueltos en [S205](../../docs/capture/s205-imager-s0-writer.md). Para el estado de gates se identifican Backup `0x3000b`, destino y callback de copia; tamaño/datos efectivos, productores anteriores y semántica siguen abiertos. |
| Semántica eléctrica IMX210/IMX235 | Buscar datasheets/evidencia documental. Si la evidencia estática no permite cerrar un punto, registrar el límite antes de proponer observación física. |

Ninguna prueba P1–P21 ejecutada en estos planes; S64 es un antecedente distinto.
S51 sigue A=NO, B=NO, C=NO.
