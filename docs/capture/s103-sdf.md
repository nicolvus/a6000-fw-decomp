# S103 — subsistema SDF (Still DataFlow)

**Firmware:** A6000 fw3.21 | **Trazas:** 477 con prefijo `[SDF]` | **Rango vaddr:** `0x43c7785b` → `0x43c806f9`

**SDF** = *Still DataFlow* (hipótesis: no hay evidencia textual del acrónimo; sí de que es la capa de *dataflow* que ejecuta los trabajos de imagen still). Gestiona resize/rotate, JPEG encode/decode, CCNR (corner noise reduction), escena, panorama y THM. Puente entre el pipeline principal y el path PbCap (picture-before-capture) para la generación de JPEG still.

## Evidencia clave

- **Strings `[SDF]`**: primer aparición vaddr `0x43c7785c` (offset fichero `7563356`), último `MSG_ID_SDF_*` en `0x43c78350`. Módulo `0x43c7785b`-`0x43c806f9` (477 trazas A6000; 479 en A7S fw3.20).
- **Strings `[SDF_ERR]`**: vaddr `0x43c7a145` → `0x43c7eb78`. 15 mensajes de error relacionados con PTM (Picture Timing Mode): comprobación de valores "mayor/menor que 32", zonas first/second, intervalos y flags de stop/current.
- **MSG_ID_SDF_* (33 mensajes distintos)**: paint_image, copy_image, resize_rotate, resize_rotate_lowspeed, encode_jpeg, decode_jpeg, encode_jpeg_rec, decode_jpeg_rss, encode_jpeg_with_work, redeye, beauty_effect, image_effect, image_mix, split_encode, develop_resize, scn_encode, scn_encode_with_thm, ccnr_encode, ccnr_encode_with_mode, panorama_ccnr_encode, thm_copy, thm_encode, jpeg_sort, dist_encode, split_resize, face_resize, ccnr_resize, set_date_image_param, set_date_image_param_dual, dist_resize, develop_resize_apl, ptm_count.
- **Funciones clave**: `FUN_43638308` (init/start, llama a `FUN_435ab6f0` con base `0x43c77857`), `FUN_435ab6f0` (dispatcher), `FUN_4363c730` (JPEG job factory), `FUN_4363ca28` (executor dispatcher), `FUN_43639c78` (message handler). De `libObj.so`: `OBJAVBBCBASECLASS::SdfCh::resizeRotate/paintImage/copyImage`.

## Flujo principal

1. Solicitud captura still → ADF inicia pipeline SDF.
2. `ObjMsg` con `MSG_ID_SDF_*` (p. ej. `resize_rotate`, `encode_jpeg`).
3. Dispatcher SDF (`FUN_435ab6f0`) procesa el mensaje.
4. Asigna unidades DMM (`0x50b3f` STL_YCC_1920P, `0xe0b00` SDS_YCC) via MMGR.
5. Operaciones opcionales por SA (`sa_func_*`).
6. Ack devuelto con `MSG_ID_SDF_*_COMP`.

## Relaciones con otros módulos

- **SDF ↔ VDF**: `VDF::VdfToAdfYcDataSender` (0x43c86165) envía datos YC desde SDF a ADF/VDF.
- **SDF ↔ ADF**: Mensajes `MSG_ID_SDF_*`; clase C++ `OBJAVBBCBASECLASS::SdfCh*`.
- **SDF ↔ IMAGING_CAP**: Pipeline still de captura, 697 trazas.
- **SDF ↔ DMM**: Unidades `0x50b3f` y `0xe0b00` para buffers YC/SDS.
- **SDF ↔ MMGR**: Gestión de memoria `L_PRM_MMGR_UNIT_MEM_HANDLE_YCC_CAP`.
- **SDF ↔ SA**: Algunas operaciones pasan por el SA (acelerador escalar, `sa_func_*`).

## Queda sin resolver

- Significado exacto del acrónimo "SDF" (Still DataFlow es la hipótesis basada en la función, no se puede probar textualmente).
- Distinción entre las 477 y 479 trazas A6000/A7S (2 trazas adicionales en A7S).
- Mapeo completo de cada `MSG_ID_SDF_*` a su función concrete en código ensamblador.
- Verificación de que todas las direcciones de código apuntan a instrucciones Thumb válidas (próximo paso: tests).