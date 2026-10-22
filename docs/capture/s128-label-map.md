# S128 — el mapa de etiquetado de la fw3.21: qué módulos son nuevos y cuáles se renombraron

**Hito de la línea de ingeniería inversa general**: síntesis de todo lo medido en S106–S127 para
responder de una vez a «¿qué cambió realmente en la fw3.21 de la A6000?».

Informe: [analysis/s128_label_map/label_map.md](../../analysis/s128_label_map/label_map.md) ·
Datos: `label_map.json` · Test: `tests/test_s128_label_map.py`.

## Hallazgo central

De los **98 prefijos de módulo** con ≥ 8 cadenas:

| clase | nº | significado |
|---|---|---|
| IGUAL | 58 | la A7S usa el mismo prefijo y los textos coinciden |
| **RENOMBRADO** | **18** | la A7S **no** usa ese prefijo pero los textos coinciden: la fw3.21 **añadió la etiqueta** a mensajes que ya existían |
| PARCIAL | 2 | coincidencias parciales |
| NUEVO/PROPIO | 20 | contenido nuevo (o la A7S etiqueta con otro nombre) |

**La fw3.21 de la A6000 no reescribe el firmware: reescribe el *logging*.** Los 18 módulos
«renombrados» son `[CAMERA_MAIN_YC]` (958/968 textos comunes), `[IMAGING_CAP]` (678/697),
`[CAMERA_MAIN_SYNC]` (412/428), `[CAMERA_SA]` (228/231), `[CAMERA_MAIN]` (97/134),
`[CAMERA_MAIN_TC]` (122/125), `[IMAGING]` (115/120) y `[MOUNT_ERROR]` (78/80): en la A7S esos
mensajes existen **sin etiqueta de módulo**.

El único módulo con **cambio de contenido real y grande** es `[CAM_IMAGER]` (179 de 371 textos
comunes, 0.48): la fw3.21 reescribió la instrumentación del imager (S124) y lo amplió. Y
`[SFRS]` es al revés: la A6000 tiene 117 trazas frente a las 151 de la A7S (S116).

`[IDT_OPD]` aparece como "nuevo" solo por el etiquetado: en la A7S esos 273 mensajes son `[IDT]`
(S120).

## Abierto / NO VERIFICADO

- Para los 20 "NUEVO/PROPIO" no se ha comprobado uno por uno si el contenido es nuevo o si la
  A7S lo etiqueta con otro nombre.
- Si el conjunto de mensajes nuevos de la fw3.21 introduce alguna capacidad que la A7S no tiene
  (más allá de la instrumentación).
- Nada de esto afecta a S51.
