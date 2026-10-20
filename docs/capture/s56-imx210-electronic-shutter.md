# S56-C — Integración electrónica del IMX210 (20-10-2026)

## Secuencia (categorías analíticas, solo lo que el firmware muestra)
Preparación de registros (SetExposure/SetRead/SetMode → sombra) → pulso SSB → Execute: lote de 119 sincronizado (`SyncMode 2`) + 8 inmediatos → lectura. En `StartExposure` (`0x438c828c`, evento 0xe): `SetExposure → SetRead → SSB → Execute(1)` solo `si [cap+0x4b9c]==0`; si no, `Execute(0)` (reinicia el P2S sin datos). Además envía a Darwin `msg 0x107` con `[cap+0x56c]` (tiempo de exposición) y `[cap+0x570]` (espera derivada de `[O+0x3a0]` ms): el tiempo mecánico lo gobierna esa ruta, no el lote de registros (INFERENCIA).

## ShutMode (C.2) — emulado
| ShutMode | ID1 | extra |
|---|---|---|
| 0 | 0x40 | — |
| 1 | 0xC4 | — |
| 2 | 0x94 | carga 0x100/0x101 desde el argumento |
| 3 | 0xD4 | — |
| 4 | 0xC0 | — |
svd/shd/spl (IDs 3–8) no dependen de ShutMode; sí se recalcula `[O+0x3a0]` (ms+1). **H56-3 PARCIAL:** ShutMode modifica bits de ID1 y 0x100/0x101; ShutMode 0 no equivale a obturación electrónica (sin semántica de bits). Ningún ShutMode escribe un registro «fin de exposición» identificable.

## Resolución completa y EFCS (C.3/C.4)
Los modos 0x0b/0x2f usan el mismo SetExposure/Execute que el resto (no hay rama por modo salvo la tabla de lectura `0x436d79c4`); por tanto los registros de tiempo (3–8) existen también a resolución completa, pero **no hay evidencia de qué fija el fin de integración** (lectura por filas del sensor vs. cortina). El tiempo real del usuario llega al `ExpRsvParam` por banco (`0x43849fb8`←fuente `0x43eb35d0`, rellenada fuera de lo rastreado): eslabón no recuperado. No se encontró cadena EFCS en el sensor distinta de las anteriores.
`CIS0_SHT_RST→XPI` (esquema) es una línea discreta sensor←BIONZ; ningún texto ni escritura del firmware la nombra (S56-E).

## Clasificación C.5
**Fin electrónico de integración a resolución completa: NO VERIFICADA.** Ni demostrada ni refutada en la ruta convencional (registros). Eslabón exacto que falta: semántica de ID1/3–8/0x100–0x101 del IMX210 en lectura completa y de `XPI`; vía de resolución: datasheet o traza pasiva CIS0 + XPI + VD (formato ya decodificable).
