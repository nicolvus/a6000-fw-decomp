# FILM-PB-1: avance parcial del productor de MPR::ER_FAILED y del 0:02 (25-11-2026)

Estado: **parcial; no cierra FILM-PB-1**. Libmpr analizada: `fw321/.../lib/libmpr.so` (SHA-256 `9a74a3bb…4c30`), REA/Ghidra, base 0. Las direcciones de este informe son de `libmpr.so`; las del traspaso son del ELF `im.elf` y difieren en +0x10000 para `MprIf::PlayMovie` (ELF `0x7229E0` ↔ libmpr `0x7329E0`).

## Hechos (REA, observados)
- `MprIf::PlayMovie` (`0x7329E0`) solo registra el log (`MprIfLog`, orden `0x4000001d`) y llama a `FeaIf::PlayMovie` (`0x45EE9C`).
- `FeaIf::PlayMovie` **no reproduce**: valida el estado de la cola (`vtable+0x18` sobre `param_1+4`; si falla devuelve 9), copia `EntryId`, `RSMPoint*` y `PlayMovieCtrl*` a un mensaje de `0x8C` bytes y lo encola con la orden `0x4000001d` (`FUN_004396d0` + `vtable+0x20`). Devuelve 0.
- Consecuencia: `PlayMovie` acepta (0) siempre que la cola acepte; el `0x1A` **se produce después, en el manejador asíncrono de la orden `0x4000001d`**, no en estas dos funciones.
- Insumo para la siguiente tarea: `FeaIf::PlayMovie` tiene 4 llamantes resueltos en `MprIf::PlayMovie` (`0x732A48` → `0x12DB00`, ver su vecino `0x12FB74`); falta localizar la tabla/despachador que asocia `0x4000001d` con su manejador.

## 0:02 (datos del MP4, medidos por Vibe y contrastados con ffprobe)
Detalle en [mp4-tiempos-vibe.md](evidence/film-pb-1-20261125/mp4-tiempos-vibe.md) (SHA-256 del vídeo confirmado).
- Ningún campo de duración (mvhd, tkhd, mdhd, elst, stts, ctts) da ~2 s en ninguna escala (90000/30000/48000); los boxes `uuid` Sony (PROF/USMT/MTDT) tampoco.
- Candidato más cercano: PTS 2,002 s del 3.er keyframe (muestra 61) truncado a 0:02. **Hipótesis débil**: otros instantes también truncan a 2; no prueba qué propiedad lee MoviePb. Falta identificarla en el firmware.

## Siguiente
1. Localizar el manejador de `0x4000001d` (tabla de órdenes del hilo de FeaCore) y desde ahí el punto que construye `0x1A`.
2. Seguir en el layout MoviePb la propiedad que alimenta el contador.
