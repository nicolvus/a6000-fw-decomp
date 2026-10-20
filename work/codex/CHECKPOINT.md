# Checkpoint — S52

S52 completada: seis entregables y test aislado en `s52/`. B1 no pudo promocionarse: clase 0 A7S se escribe en destinos `+0x5c`, mientras SetExposure toma `param+9`; no hay copia demostrada. B2/B3 distinguen buffers software de hardware y conservan la frontera física. Se inició REA separado A7S conforme a política; al cierre no estaba listo (sin resultados usados como ausencia). No se modificó firmware, Ghidra ni `work/claude/`.

# Checkpoint — DFE A7S/A6000

Entregables completados en este directorio. Hallazgo principal: A7S no posee un `dfe.bin` extraído equivalente, pero su `av-cam.bin` incluye host DFE, receptor SubLVDS/MPHY y controlador IMX235. A6000 referencia `/usr/dfe/dfe.bin` y su imagen de 64 KiB tiene vectores ARM en base de análisis `0x01000000`.

TASK2 completada: validación cruzada en `crosscheck.md`. REA se usó solo en el `dfe.bin` pequeño: 83 procedimientos, vectores y arranque observados; ninguna semántica de ID de comando para lectura/disparo/VD queda afirmada. El cargador host de la ruta DFE y el consumidor final de 0x4e/0x4f siguen NO VERIFICADOS. No tratar la falta de xref directa PC-relativa como prueba de ausencia.
