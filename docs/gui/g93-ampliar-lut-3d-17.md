# G93 — ¿Se puede ampliar la LUT 3D del BIONZ X de 5×9×9 a 17³? (23-11-2026)

Petición: ampliar de verdad la rejilla 5×9×9 (no solo añadir la curva 1D de G92) a algo como 17×17×17. Solo estático (REA compartida + Capstone sobre `av-cam` de A6000 fw3.21, A7S fw3.20 y A6300 fw2.01); sin cámara ni CFW. Test: `tests/test_g93_lut_geometria.py` (3). Contexto: [g90 §C](g90-lut-interpolacion-optimizacion-geometria.md), [g91](g91-lut-completa-por-software.md), [g92](g92-auditoria-cadena-color-lut-general.md).

## 1. Conclusión
**No hay manera de que el procesador aplique una LUT de 17³ (ni de 9³).** La rejilla no es una elección del firmware que se pueda parchear, sino del bloque de hardware: las SRAM no tienen sitio y el mismo diseño se repite sin cambios en tres modelos. Las LUT de 17³ o mayores solo se pueden aplicar fuera del ISP: en foto por software dentro de la cámara (G91, hecho) y en vídeo en postproducción.

## 2. Evidencia (VERIFICADO en bytes salvo lo marcado)
1. **Capacidad.** La escritura al HW (`0x43b67918`, 8 casos fijos) usa bancos a `+0x17000` (paso `0x200` ⇒ ≤128 palabras), `+0x17200…0x17700` (paso `0x100` ⇒ ≤64) y `+0x17800` (≤512 hasta el final del IP). Los vértices se reparten por paridad de (j, a, b) para leer los 8 de una celda a la vez (G90). Palabras necesarias en el banco más lleno: 5×9×9 = 75 (cabe); 6×9×9 o 5×10×10 desbordan uno de 64; **9³ pide 100 en un banco de 64** y **17³ pide 729 en el banco 0** y 4913 en total, frente a 1024 palabras de toda la ventana (test). Ni cambiando el reparto cabe.
2. **Geometría fija en todo el código.** `Create3DLUT` (`0x437a1d7c`) recorre bucles fijos `9 × 9 × 5`; la copia es de `0x654` B fijos; el escritor tiene 8 tamaños constantes. Los 18 registros de control (`+0x15c100…0x144`) son de 1 bit o de 6 bits: ninguno puede codificar el tamaño de la rejilla (G90).
3. **Mismo bloque en A7S y A6300.** La permutación de 405 nodos (810 B, `0x43bef2ac`) y el escritor completo (0x6a B con sus constantes) están idénticos byte a byte en `av-cam-a7s.bin` (`0x43b61eba`) y en `av-cam-a6300.bin` (`0x43c2be20`) (test). Es el diseño del IP de la familia BIONZ X, no un recorte de la A6000.
4. **`BlkOfs Cr/Cb` no es geometría.** El único parámetro con nombre de bloque (`Create3DLUT … BlkOfs Cr:%X, Cb:%X`, solo en la A6000) suma un desplazamiento de croma, sacado de la tabla `+0x5c0`, a los nodos centrales (a = b = 4) de los dos planos de Y más oscuros. Es una corrección del color de los negros, no un desplazamiento ni un cambio de escala de la rejilla.
5. **No hay otra LUT 3D grande en `av-cam` de la A6000.** Revisadas las cadenas `lut` y `RgbPath`: `hndl_for_rdm_lut` (`0x439d0138`, CAMERA_SA) es un búfer más entre 18 asignados; `SetRgbPathEo` solo elige entre visor y pantalla. La A6300 tiene un comando que la A6000 no tiene, `VdfDisplayCmdSetMonitorLut` (vtable `0x441883f8`, parámetro de 1 byte): elige una LUT de monitor fija (asistente de gamma) y solo afecta a la pantalla, no a la grabación. Su forma (1D o 3D) no se ha estudiado.

**Límite:** la parte del IP en `+0x11000…+0x16FFF` no la escribe el firmware y no se sabe qué hay. Aunque hubiera SRAM, el generador de direcciones del HW está pensado para 5×9×9 y ningún registro lo cambia. Solo una prueba en la cámara lo descartaría del todo, y no compensa.

## 3. Qué sí da una LUT completa
| Vía | Alcance | Estado |
|---|---|---|
| `.cube` completo por software sobre el JPEG (2…129³, tetraédrica) | foto | G91 hecho offline · LUT-SW-2 (cámara) |
| Curva 1D tras la gamma + 5×9×9 (shaper) | vídeo, vista en vivo y foto | G92 verificado en Unicorn · LUT-T-1 |
| `.cube` en postproducción | vídeo | fuera de la cámara |
| LUT de monitor (`SetMonitorLut`) | solo pantalla | no existe en la A6000 |

La ganancia de la curva 1D frente a 5×9×9 sola está medida en G92 §4 (película 0,79 → 0,19 ΔE medio). Es lo máximo que se acerca a 17³ con el hardware de la A6000.
