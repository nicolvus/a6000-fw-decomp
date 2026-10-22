# S108 — Módulo [CAMERA_SA] (231 trazas)

**Enlace:** `analysis/s108_camera_sa/camera_sa.md`

**Resumen:** El módulo `[CAMERA_SA]` del firmware A6000 fw3.21 contiene 231 trazas que supervisan el acelerador escalar (SA) de la cámara. Las trazas se organizan en 13 sub-bloques funcionales: Módulo APL (27), Gestión de Memoria (20), Errores GetAddr (35), Alineación de Parámetros (29), Parámetros Inválidos (2), Paso de Mensajes (18), Parámetros Yc DUALREC (14), Cierre de Handles de Imagen (4), Cierre de Handles WorkMemArea (3), Cierre de Handles Genéricos (13), Referencias API SA (8), Errores Especiales (4) y Códigos de Error (3). En A7S fw3.20 no existe el prefijo `[CAMERA_SA]` (0 trazas), siendo los mensajes equivalentes sin etiqueta.

**Datos clave:** rango vaddr `0x43cc5286 → 0x43cef0d8`, 231 strings únicas, diferencial principal es la etiqueta de módulo añadida en fw3.21 sobre código preexistente en A7S sin etiqueta.
