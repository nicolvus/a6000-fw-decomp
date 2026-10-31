# E26-R28 — Búsqueda externa de TPZL con 1 segmento o residuo ≠ 0 (30-10-2026)

Ejecuta la Prioridad E que R17 había dejado sin hacer: búsqueda documental pública de muestras TPZL de Sony con un solo segmento de 64 KiB o residuo distinto de 0, en otros modelos (α7/α7 II/α5100/α6300) y en las herramientas de la comunidad (`fwtool`, Sony-PMCA-RE).

## Método

- `WebSearch` (modo estándar): «Sony TPZL firmware compression format», «Sony camera firmware TPZL segment 64KiB fwtool github», «TPZL magic bytes firmware», búsqueda de código en GitHub.
- `gh search code "TPZL"` (GitHub, sin filtro de repositorio): búsqueda literal de la cadena.
- `gh api search/code` acotada a `repo:ma1co/Sony-PMCA-RE` (el proyecto de referencia de la comunidad, confirmado existente y activo) con los términos `TPZL`, `loader3`, `compress`.
- `gh search repos` para «fwtool sony» y «sony-pmca», para verificar qué proyectos públicos existen y qué capa de firmware cubren.

## Resultado: NEGATIVO, sin muestras ni documentación pública

1. **Ninguna mención de «TPZL» en ningún resultado relevante.** Todas las coincidencias de `gh search code "TPZL"` son azarosas (subcadenas dentro de `TPZLine`, `tpzl` de un puzle de Advent of Code 2022, URLs acortadas) — ninguna es firmware ni de Sony.
2. **`ma1co/Sony-PMCA-RE`** (el proyecto de referencia de la comunidad para ingeniería inversa de cámaras Sony, confirmado activo) **no contiene ninguna referencia a `TPZL`, `loader3` ni a compresión de bloques** (0 resultados en los tres términos). Opera en la capa de empaquetado del actualizador (formato `FDAT`/`Msfirm`/`DSLR`/`ASH`), no en el BootROM/Loader2/Loader3 que este repositorio reconstruyó.
3. **`fwtool.py` (la herramienta pública más citada)** solo desempaqueta esos mismos formatos de actualizador; ningún issue ni fork menciona TPZL o el formato interno de segmentos.
4. **Ningún otro proyecto público** (PSP `KL4E`/`KL3E`, `LZR`, formatos de otros fabricantes) usa el nombre TPZL ni coincide con la estructura de segmentos de 64 KiB documentada en R16/R17.

## Conclusión

**`TPZL` no tiene documentación, muestras ni discusión pública conocida fuera de este repositorio.** Es, hasta donde la búsqueda pública permite afirmar, un formato interno de Sony sin exposición en la comunidad de ingeniería inversa de cámaras (que se centra en el actualizador, no en el cargador de arranque). No se puede construir la tabla de muestras con SHA-256/modelo/distribución de segmentos que pedía el criterio de cierre original, porque **no existen muestras públicas** con las que construirla.

## Cierre del pendiente

`E26-R17-TPZL-1SEG` — **CERRADO (resultado negativo, documentado)**: la búsqueda se hizo y no encontró nada; no es una omisión silenciosa. El corpus de R16 (6 imágenes propias, ≈6200 bloques, siempre 16×4 KiB, residuo 0) sigue siendo el único disponible para este modelo.

## Límites

- `WebSearch` no indexa bien el código fuente de GitHub; se complementó con `gh search code`/`gh api search/code`, que sí lo hace.
- No se buscó en foros especializados fuera de GitHub (p. ej. dpreview, eoshd, foros en japonés) ni en patentes de Sony con otros términos técnicos (compresión de firmware, actualizador de cámara) que pudieran nombrar el formato de otra manera.
- Resultado negativo de una búsqueda pública no prueba que el formato no esté documentado en ningún sitio privado o de pago (manuales de servicio Sony internos, por ejemplo).
