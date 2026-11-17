# G82 — Loop Recording (estado y diseño, 17-11-2026)

Objetivo (wiki 16, Vídeo): grabación en bucle como la de Panasonic GH5: al llenarse la tarjeta o alcanzar el límite de clip, borrar lo más antiguo y seguir grabando.

## Hallazgos (VERIFICADO en `analysis/camera-extract/usr/lib/libObj.so`, `strings`)
- **No existe de fábrica**: ninguna cadena de «loop recording / overwrite / ring» en el grabador. Los «Loop» hallados son de decodificación, escalado y bucles de eventos; `InfraMovieEncoderForEncThm::SetLoopState` es del codificador de miniatura (thumbnail), no del clip.
- **Fin de grabación por tarjeta llena**: lo gobiernan `ChangeMovieMediaFullInh` / `ChangeMediaFullInh` (inhibición «media full»), el factor de espacio libre `remainSizeOnDstDisc` del modelo de contenido (ver `analysis/s87_storage/storage_filesystem.md` §3) y el límite de tiempo `PARAMID_HSMOVIE_RECTIME*` (solo HS movie). El límite de 29 min/4 GB de clip es de `ObjMedia` (ver [g79](g79-xavcs-sin-restriccion-de-tarjeta.md)).

## Diseño propuesto (NO implementado, NO verificado)
1. Cuando `ObjMedia` calcule «sin espacio» durante REC, en vez de `ChangeMovieMediaFullInh(true)` borrar el clip más antiguo de `PRIVATE/M4ROOT/CLIP` (y su entrada en el índice MP4/XML de `PRIVATE/M4ROOT`) y recalcular `remainSizeOnDstDisc`.
2. Alternativa más simple, a nivel de usuario Linux (CFW): vigilar el espacio libre y borrar el clip más antiguo cerrado antes de que llegue al umbral. No evita el corte entre clips si el límite es de tiempo.

## Por qué no se implementa ahora
- **Bloqueado por E2E-15**: el arnés aún no graba un clip (av-cam no contesta `0x3000/0x3024`), así que no se puede probar de punta a punta, y la regla del proyecto es no llevar a la cámara lo no visto en el arnés.
- La SD (G22-E-1g) está aparcada por orden del usuario; el borrado del clip antiguo y el índice dependen del sistema de ficheros emulado.

Cierre: tras E2E-15, grabar en el arnés con la cuota de la SD emulada llena y comprobar el borrado del más antiguo y la continuidad.
