# S112 — Módulo `[CAMERA_MAIN_SYNC]` (429 trazas)

**Enlace:** `analysis/s112_camera_main_sync/camera_main_sync.md`

**Resumen:** El módulo `[CAMERA_MAIN_SYNC]` del firmware A6000 fw3.21 contiene **429 trazas** que supervisan la sincronización y asignación de recursos del sensor. Las trazas se organizan en múltiples sub-bloques funcionales: `SyncResMgr` (55), control `DFS`/`DVS` (11+5), errores `APL_ERR` (17), JPEG síncrono (13), secuencias de película (9), modo HS (5), VD pre/post (5+5), gestión de carga (5), clamps (4), DMM (4), patrones de formato `%6s` (4), y 58 sub-bloques adicionales de 1–3 trazas cada uno. En la A7S fw3.20 **no hay trazas** con el prefijo `[CAMERA_MAIN_SYNC]` (0 trazas); los mismos mensajes de texto existen sin la etiqueta, lo que indica que la A7S carece de ese subsistema etiquetado aunque la funcionalidad subyacente esté presente.

**Datos clave:** rango vaddr `0x43c9b40a → 0x43cb5617`, 429 strings únicas, diferencial principal es la etiqueta de módulo `[CAMERA_MAIN_SYNC]` añadida en fw3.21 sobre código preexistente en A7S sin etiqueta.