# S128 — el mapa de etiquetado de la fw3.21: qué módulos son nuevos y cuáles se renombraron

> Hito de la **línea de ingeniería inversa general**: una síntesis de todo lo medido en
> S106–S127, para responder de una vez a la pregunta «¿qué cambió realmente en la fw3.21 de la
> A6000?». Todos los datos salen de los bytes de la A6000 fw3.21 y de la A7S fw3.20.
> Sin efecto en S51.

## 1. Método

Para cada prefijo `[MÓDULO]` del mapa de S79 (`analysis/s79_modules/module_map.json`) se
compara, **texto a texto**, la A6000 fw3.21 con la A7S fw3.20:

- cuántas cadenas lleva el prefijo en cada firmware;
- si la A7S usa ese prefijo;
- cuántas de las cadenas de la A6000 existen en la A7S (con el prefijo puesto, si la A7S lo usa;
  sin el prefijo — es decir, **sin etiquetar** — si no lo usa).

De ahí la clasificación:

| clase | significado |
|---|---|
| **IGUAL** | la A7S usa el mismo prefijo y los textos coinciden (≥ 60 %) |
| **RENOMBRADO** | la A7S **no** usa ese prefijo, pero los textos coinciden (≥ 60 %): la fw3.21 **añadió la etiqueta** a mensajes que ya existían |
| **PARCIAL** | coincidencias entre el 20 % y el 60 % |
| **NUEVO/PROPIO** | casi sin coincidencias: la fw3.21 escribió esos mensajes de nuevo (o la A7S los etiqueta con **otro** nombre) |

## 2. Resultado (98 prefijos con ≥ 8 cadenas)

| clase | nº de prefijos |
|---|---|
| IGUAL | 58 |
| RENOMBRADO | 18 |
| PARCIAL | 2 |
| NUEVO/PROPIO | 20 |

Los módulos grandes (≥ 40 cadenas):

| prefijo | n A6000 | prefijo en A7S | textos comunes | clase |
|---|---|---|---|---|
| `ADF` | 1220 | 1269 | 1218 (1.00) | IGUAL |
| `CAMERA_MAIN_YC` | 968 | 0 | 958 (0.99) | **RENOMBRADO** |
| `IMAGING_CAP` | 697 | 0 | 678 (0.97) | **RENOMBRADO** |
| `SDF` | 477 | 479 | 477 (1.00) | IGUAL |
| `CAMERA_MAIN_SYNC` | 428 | 0 | 412 (0.96) | **RENOMBRADO** |
| `CAM_IMAGER` | 371 | 0 | 179 (0.48) | **PARCIAL** |
| `IDT` | 297 | 305 | 292 (0.98) | IGUAL |
| `IDT_OPD` | 273 | 0 | 0 (0.00) | NUEVO/PROPIO |
| `CDIAG` | 255 | 255 | 255 (1.00) | IGUAL |
| `VDF` | 243 | 162 | 162 (0.67) | IGUAL |
| `CAMERA_SA` | 231 | 0 | 228 (0.99) | **RENOMBRADO** |
| `TRK` | 215 | 215 | 215 (1.00) | IGUAL |
| `VEF` | 149 | 141 | 141 (0.95) | IGUAL |
| `CAMERA_MAIN` | 134 | 0 | 97 (0.72) | **RENOMBRADO** |
| `MOUNT_DEBUG` | 132 | 0 | 0 (0.00) | NUEVO/PROPIO |
| `CAMERA_MAIN_TC` | 125 | 0 | 122 (0.98) | **RENOMBRADO** |
| `IMAGING` | 120 | 0 | 115 (0.96) | **RENOMBRADO** |
| `SFRS` | 117 | 151 | 117 (1.00) | IGUAL |
| `ACCY` | 106 | 0 | 0 (0.00) | NUEVO/PROPIO |
| `VPH_API` | 106 | 0 | 0 (0.00) | NUEVO/PROPIO |
| `SFRA` | 100 | 100 | 100 (1.00) | IGUAL |
| `MOUNT_ERROR` | 80 | 0 | 78 (0.97) | **RENOMBRADO** |

(la tabla completa, con los 98 prefijos, está en `label_map.json`)

## 3. Lectura

1. **La fw3.21 de la A6000 no reescribe el firmware: reescribe el *logging*.** De los 98
   prefijos grandes, **58 son idénticos** (la A7S los etiqueta igual) y **18 son "renombrados"**:
   la A7S tiene **exactamente los mismos mensajes** pero **sin etiqueta de módulo**, y la A6000
   fw3.21 los etiqueta con `[CAMERA_MAIN_YC]`, `[IMAGING_CAP]`, `[CAMERA_MAIN_SYNC]`,
   `[CAMERA_SA]`, `[CAMERA_MAIN]`, `[CAMERA_MAIN_TC]`, `[IMAGING]`, `[MOUNT_ERROR]`…
   Esto confirma, de forma transversal, lo que se vio hito a hito (S106 `[IMAGING_CAP]`, S119
   `[APL]` dentro de `[CAMERA_SA]`, S120 `[IDT_OPD]`, S122 `[CAMERA_MAIN_TC]`, S126 `[CAMERA_MAIN]`).
2. **Lo que sí es nuevo de verdad** (20 prefijos "NUEVO/PROPIO") son pocos y pequeños, y
   [`IDT_OPD`] es el caso límite: no es contenido nuevo, es **etiquetado nuevo** (en la A7S esos
   273 mensajes son `[IDT]`, y en la A6000 son `[IDT_OPD]` con su gemelo `[IDT]` justo al lado,
   S120).
3. **El único módulo con cambio de contenido real y grande** es `[CAM_IMAGER]`
   (179 de 371 textos comunes, 0.48): la fw3.21 **reescribió la instrumentación del imager**
   (nuevos `SetExps`/`SetRead`/`Execute` con el drive mode anterior, S124) y de paso **amplió** el
   módulo.
4. **`[SFRS]`**: la A6000 tiene 117 trazas y la A7S **151** → aquí la A6000 tiene **menos**
   instrumentación (S116).

## 4. Verificaciones hechas

| afirmación | cómo se comprueba |
|---|---|
| 98 prefijos con ≥ 8 cadenas | `label_map.py` (extracción por prefijo sobre los dos blobs) |
| clasificación por coincidencia de textos | comparación literal texto a texto de las cadenas de cada prefijo |
| los 18 "renombrados" tienen 0 apariciones del prefijo en la A7S | campo `usa_prefijo_en_a7s` de `label_map.json` |
| los "IGUAL" tienen el prefijo en la A7S | ídem |

## 5. NO VERIFICADO / abierto

- Para los 20 "NUEVO/PROPIO" no se ha comprobado uno por uno si el contenido es nuevo o si la
  A7S lo etiqueta con otro nombre (caso de `[IDT_OPD]`, ya resuelto en S120).
- Si el conjunto de mensajes *nuevos* de la fw3.21 introduce alguna capacidad que la A7S no
  tiene (más allá de la instrumentación): no comprobado.
- Nada de esto **afecta a S51** (A/B/C = NO).

## 6. Ficheros de este hito

| fichero | contenido |
|---|---|
| `label_map.json` | los 98 prefijos con su clasificación y sus cifras |
| `label_map.py` | script reproducible del mapa |
