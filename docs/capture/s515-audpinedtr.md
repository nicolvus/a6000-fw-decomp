# S515 — subetiqueta `[AUDPINEDTR]` (dataflow infra sender, línea general)

## Alcance

Decodificación de la subetiqueta `[AUDPINEDTR]` del `av-cam.bin` A6000 fw3.21, comparada con A7S fw3.20 y A6300 fw2.01.

## VERIFICADO

- **Volumen de trazas:** A6000 = 34 cadenas `[AUDPINEDTR]`; A7S = 34; A6300 = 79.
  Fuente: `strings | grep -c '\[AUDPINEDTR\]'`.
- **Inventario REA:** 34 cadenas (`analysis/s515_audpinedtr/ad_strings.json`).
- **Referencias de código:** por determinar (pendiente de xrefs REA).
- **Subsistemas inferidos (VERIFICADO por texto):** *Dataflow Infra Sender*:
  - `DataflowInfraSender::SendASync`, `dmm_share`, `dmm_free`, `Dmac Open/Start`, `dmm_alloc`, `SendPinData`, `SendMuteData`, `Initialize`, `Finalize`, `CopyNum`, `Set Audio Info`, `Pin Proc Err`, `Iterator Full`, `Bad Arg`, `Software Bug`.
  - Manejo de buffer de audio LPCM (Main/Sub), DMM (shared memory), DMAC transfers, pin-based data delivery.
- **Comparación:** A6000 y A7S idénticas (34/34); A6300 tiene más (79, superset).
  Ver `analysis/s515_audpinedtr/ad_compare.json`.

## INFERENCIA

- `[AUDPINEDTR]` = módulo de **envío de infraestructura de datos de audio** (Dataflow Infra Sender), parte del pipeline de audio/vídeo, no relacionado con el obturador electrónico.
- Maneja transferencias DMA de buffers de audio LPCM entre memoria compartida (DMM) y pines de datos (SendPinData/SendMuteData).

## NO VERIFICADO

- Referencias de código exactas (xrefs).
- Funciones contenedoras y sus direcciones.

## Artefactos pendientes

- `analysis/s515_audpinedtr/ad_strings.json` (34 cadenas REA)
- `analysis/s515_audpinedtr/ad_xrefs.json` (xrefs REA)
- `analysis/s515_audpinedtr/ad_functions.json` (funciones contenedoras)
- `analysis/s515_audpinedtr/ad_compare.json` (comparación A6000/A7S/A6300)

## Límite

Análisis estático sobre `av-cam.bin`; sin ejecución. Módulo ajeno al obturador.
