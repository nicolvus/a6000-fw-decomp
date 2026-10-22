# S179 — `[CAM_SCALAR]`: la capa HAPI de imagen de la cámara (etiqueta nueva de la fw3.21)

**34 trazas · 47 sitios (regla PIC estricta) · 14 funciones emisoras · 0 llamadas al acelerador SA.** Detalle: `analysis/s179_cam_scalar/cam_scalar.md` / `.json`.

## Qué es
`[CAM_SCALAR]` **no es un módulo de código con nombre propio**: es una **etiqueta de traza** que la fw3.21 de la A6000 antepone a 34 mensajes de la **capa de la cámara que atiende las peticiones HAPI de imagen** («HAPI Manager» + filtros HAPI del pipeline TBOX): recepción OSAL, despacho por `MSG_ID` `0x5001`–`0x5017`, validación de imágenes, handles DMM (`YCC_FULL`, `RAW_FULL`), buffers YC/SDS-YC, clonado/parseo/inserción/extracción de imágenes, *develop* RAW→YC y parámetros de secuencia.
**La sigla NO tiene base textual** (34 apariciones = 34 trazas; `CamScalar`/`cam_scalar` = 0) → **se deja sin desarrollar**.

## Hipótesis del enunciado: REFUTADA
«[CAM_SCALAR] = la capa de cámara que usa el acelerador escalar SA» **no se sostiene**: las 14 funciones emisoras hacen **0 llamadas** a `NS_SCALAR_INFRA` (`0x43990000`–`0x439c0000`, donde vive `[SAD]`/S167, `[SFRA]`, `[SFRS]`); en la banda `0x439xxxxx` sólo están el logger global `0x43902718` y el emisor de respuestas `0x43901a8c`. El código no referencia ninguna cadena `sa_func_*`; todas las `SCALAR`/`Scalar` de la A6000 (88 + 261) son de `NS_SCALAR_INFRA`.

## Las 34 trazas (vaddr → texto corto; sitio y función en `cam_scalar.md`)
```
0x43cb045a HAPI Manager:Recieve error   0x43cb0483 Message size 0   0x43cb04ad Empty Message   0x43cb0661 Unknown MSG_ID
0x43cb04d6 req_sequence_create_stream   0x43cb0515 req_tool_get_image_info   0x43cb0551 req_filter_develop
0x43cb0588 %s: input image and sdsYC invalid (3)   0x43cb05bc %s: copyStdYc error (3)   0x43cb05df %s: warning. NR Level OFF
0x43cb0607 %s: input image is invalid (6)   0x43cb0631 %s: input stdYcHandle is invalid   0x43cb06f4 %s: unsupported format (3)
0x43cb0726 %s: YC(develop) DMM allocation error   0x43cb076c %s: SdsYc error (3)   0x43cb07f1 %s: dmm_handle[YCC_FULL] error (2)
0x43cb0829 %s: Alloc SDS YC error   0x43cb084e %s fatal   0x43cb0865 %s: No YCC_FULL handle   0x43cb088a %s: No RAW_FULL handle
0x43cb08af %s: dmm_handle[%d] error (2)   0x43cb08d6 %s: ShareCheck error   0x43cb08f9 %s: p_newparam error   0x43cb091c %s: outImage error
0x43cb093d %s: dmm_handle[%d] Share (2)   0x43cb096a %s: Share error   0x43cb0a03 %s: ExposureCount inválido   0x43cb0a3f %s: RecordCount inválido
0x43cb0a79 %s: CapMode is not CAP_SINGLE   0x43cb0b5e %s: input image is null.   0x43cb0aa5 Open Error ← MUERTA
0x43cb0abe %s: AllocNewWait error ← MUERTA   0x43cb0ae3 %s: %d Free error ← MUERTA   0x43cc679a RecordCount Unmatch! : remain %d
```

## Hallazgos con dirección
- **«Se reescribe el logging» (S128/S130)**: en las **34/34** cadenas los bytes en `vaddr+14` son el literal **sin** el prefijo `"[CAM_SCALAR]: "` (14 B exactos) y ese texto **sigue referenciado** por el logger global. La fw3.21 **duplica** la traza: la nueva (`bl` al logger de módulo `0x4380a5d0`, **id de módulo 5**, **nivel 6**, flag 1) y la vieja (`bl 0x43902718` → `vaddr+14`), intacta. Ejemplo `0x4380a872` (A6000) vs `0x4382d4c6` (A7S, una sola llamada al logger `0x438f7114`).
- **Despachador HAPI** `0x4380a688`: `sub.w r3,r3,#0x5000` + `subs #1` + `cmp #0x16` + `tbh` de **23 entradas** (base `0x4380a72c`) → `MSG_ID` **`0x5001`–`0x5017`**.
- **`SetSpecialSequence`** `0x4380c344`: `ExposureCount` (`p[4]`) = **1**, `RecordCount` (`p[5]`) **≤ 5**, `CapMode` = **`CAP_SINGLE`**. Handles DMM: `DMM_HANDLE_YCC_FULL` (`0x43cb080e`), `YCC_FULL`, `RAW_FULL`, `CheckDMMforClone` (`0x43cb09cc`).
- **Ficheros**: `HAPI_Filter_TBOX.cpp` (`0x43cb07b7`, ref. `0x4380b79a`, línea 99), `CS_Command.cpp` (`0x43cb0b85`, ref. `0x4380c80e`, línea 112), `ImageParamCapture_SyncBranch.cpp` (`0x43cc6779`, ref. `0x438bbc50`).
- **94/94 pares PIC verificados a mano** (47 nuevos + 47 gemelos), 0 fallos, 0 reuso de registro; el escaneo local reproduce el mapa global (17 525 destinos) con **0 discrepancias**; **0** punteros absolutos de 4 B.

## Diferencial
| | A6000 fw3.21 | A7S fw3.20 | A6300 fw2.01 |
|---|---|---|---|
| token `[CAM_SCALAR]` / núcleo sin prefijo | **34** / — | **0** / **34/34** | **0** / **34/34** |
| gemelo exacto en `+14` | **34/34** | — | — |
| código equivalente | `0x4380a688`–`0x4380c6f4` | `0x4382d49c`–`0x4382e…` | `0x438c8d…`–`0x438ca…` |
| `HAPI_Filter_TBOX.cpp`/`CS_Command.cpp` | sí / sí | sí / sí | sí / sí |

→ **Cambio de *logging*, no de código**: misma tabla de `MSG_ID`, mismos ficheros, mismos nombres de método (`req_*`, `Start_*`, `Check*`) y mismos mensajes. La A6300 cambia dos textos (`%s: Develop(RAW->YC) fail.`, `%s: invalid parameter on simple develop.`) y `req_image_clone`→`req_yc_image_parse`.

## Línea del obturador: NEGATIVO ACOTADO
0 coincidencias de `shutter`/`silent`/`curtain`/`electro`/`mech`/`obtur`/`sensor`/`readout`/`shut`/`svd`/`shd`/`spl`/`frame`/`imager`/`drive`/`brack`/`sweep`/`still`/`movie`/`focus`/`iso`/`apert`/`sync`/`vsync`/`scan`. Lo único de nivel captura son `ExposureCount`, `RecordCount` y `CapMode` (`CAP_SINGLE`): **parámetros de secuencia**, no del obturador; el «develop» es la conversión software RAW→YC. → **S51 (A/B/C = NO) se mantiene.**
