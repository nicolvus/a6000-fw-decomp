# LÍNEA B — Compatibilidad SFRA <-> MPR (CRÍTICA)
Objetivo: ¿puede un JPEG READY de SFRA entregarse a MPR como mainJpg?
Tareas: B-01 comparar descriptores: buffers READY/GET_JPEG de SFRA (analysis/ghidra/sfra-*, sdf-*, ddl-jpeg-*) frente a (memHandle, offset, size) de StillInfo.jpg_info. B-02 dominio DMM/SDS de handles: quién crea, quién resuelve, si el handle SFRA es válido en libmpr. B-03 propiedad y ciclo de vida (liberación, ring, coherencia de caché) tanto en LIRO como en libInfraStreamingServer (GetLiveViewJpeg/MmapLiveViewJpeg). B-04 qué EXIF/screennail/thumb produce ISS/SFRA por fotograma. B-05 si no son compatibles: copia/conversión mínima concreta (teórica).
Salidas: docs/capture/sfra-mpr-buffer-bridge.md (comparación de estructuras, mapa de propiedad, propuesta teórica).
Aceptación: demostrar compatibilidad de descriptores o una copia/conversión concreta. Coordina con A leyendo sólo su analysis/stillinfo-layout.json cuando exista (no lo edites).
