# G91 — LUT `.cube` completas (17³, 33³, 65³…) en la cámara por software, sin el límite 5×9×9 del ISP (22-11-2026)

Petición: usar LUT mayores que las que admite la cámara (5×9×9). Sin cámara, sin CFW, sin tocar firmware ni `av-cam`. Código: `scripts/lut/userland/lutjpg.c` (herramienta), `scripts/lut/userland/lutdcim.sh` (lote en la cámara), `scripts/lut/lutjpg.py` (compilación, referencia, autocomprobación). Tests `tests/test_g91_lutjpg.py` (12). Contexto: [g71](g71-lut3d-formato-y-cube.md), [g89](g89-lut-sd-en-camara.md), [g90](g90-lut-interpolacion-optimizacion-geometria.md).

## 1. Por qué software y no el ISP
G90 §C (VERIFICADO en bytes): el bloque LUT del BIONZ X tiene geometría fija 5×9×9 en YCbCr (8 SRAM con 60/64 palabras usadas; cualquier eje +1 desborda). Ningún parche de `av-cam` lo amplía. La única forma de aplicar una LUT mayor es por software, y por coste solo en foto (G71 §5: vídeo/vista en vivo inviables en la CPU).

## 2. Vía elegida: proceso Linux sobre el JPEG en la SD
- **La SD es POSIX para procesos Linux**: `FuFsys /android/mnt/sdcard fuse.FuFsys rw,nosuid,nodev` (volcado `analysis/camera-dumps/20261117-traza-T2T6/sd/montajes.txt`, VERIFICADO). G89 vio solo `Fsys_*` en el proceso de la UI; este montaje FUSE (el de las apps Android) da acceso con `fopen` a `DCIM/`, sin parchear nada.
- **Sin gancho en el revelado** (LUT-B, `0x438c6f68`): sigue sin dirección/pitch/formato del búfer YC. Procesar el JPEG ya escrito evita todo eso y no puede colgar la tarea de imagen.
- **CPU de la cámara**: Cortex-A5 (`CPU part 0xc05`), `vfpv3 vfpv3d16 vfpv4`, sin NEON; 204 MB de RAM con poco libre (1–86 MB en los volcados) ⇒ binario estático y proceso por filas.

## 3. Herramienta `lutjpg`
`lutjpg [-q 1-100] LUT.cube entrada.jpg salida.jpg` (calidad por defecto 98).
- `.cube` Adobe 3D de cualquier tamaño 2…129 (`LUT_3D_SIZE`, `DOMAIN_MIN/MAX`, `TITLE`); 1D, filas incompletas o de más → código 3 sin escribir nada.
- **Interpolación tetraédrica** (la de Resolve/OCIO) en enteros: tabla u16, ejes precalculados por valor de 8 bits (índice + fracción Q16), sin desbordar 32 bits.
- libjpeg-turbo 3.1.2 (C puro, sin SIMD) por filas: memoria ≈ N³·6 B (65³ = 1,6 MB) + búferes de fila; 12,7 MB de RSS medidos en el PC con la foto de 6000×4000 (proceso dinámico; no medido en la cámara).
- Conserva tamaño, EXIF (APP1 tal cual) y el submuestreo de la entrada (4:2:2 de Sony); omite el APP2 MPF (sus desplazamientos apuntan a la vista previa añadida tras el EOI, que no se copia) y no añade JFIF si la entrada no lo tenía. Error de libjpeg → borra la salida (nunca deja un JPEG a medias); salida = entrada → código 2.
- Compilado con zig 0.17.1 (`arm-linux-musleabihf`, `-mcpu=cortex_a5-neon-d32`, estático): 410 KB, sin intérprete dinámico ni atributo NEON (test).
- `lutdcim.sh` (en la cámara, por telnet): copia `LUT/lutjpg` de la SD a `/tmp`, aplica `LUT/LUT1.cube` (o el que se pase) a todos los `DCIM/*/*.JPG` sin copia previa y escribe `LUT_OUT/<cube>/<carpeta>_<foto>.JPG`. **Los originales no se tocan** y las salidas quedan fuera de `DCIM` para no alterar la base de datos de imágenes de la cámara.

## 4. Evidencia (PC; binario ARM real bajo `qemu-arm`)
- **Exactitud**: salida del binario = referencia tetraédrica flotante (`lutjpg.tetra`) redondeada y recodificada igual: diferencia media 0,00–0,014 niveles, ≥ 99,95 % de muestras a ≤ 2 niveles (65³ película, 33³ teal & orange, 2³ inversión). Lo único que se pierde es la recompresión JPEG.
- Foto real de la cámara (`DSC03986.JPG`, 6000×4000, 4:2:2, EXIF+MPF): tamaño, EXIF y 4:2:2 conservados; sin MPF ni JFIF.
- `DOMAIN_MAX 2` correcto; `.cube` 1D/corto/vacío y JPEG no válido → sin fichero de salida.

**ISP 5×9×9 frente a software, sobre los píxeles de la misma foto** (ΔE2000 medio / p95 / máx; ISP = tabla de `sd_lut.convierte`, ajuste en ΔE de G90, trilineal):

| LUT | ISP 5×9×9 (error de la LUT) | software (error de la LUT) |
|---|---|---|
| película 33³ / 65³ | 1,35 / 2,42 / 5,6 · 1,35 / 2,46 / 6,0 | 0 |
| teal & orange 33³ | 0,30 / 0,52 / 0,8 | 0 |
| agresiva 33³ | 1,07 / 3,28 / **14,2** | 0 |

Coste propio del software = recompresión del JPEG de la cámara (identidad, 4:2:2 conservado): q95 0,86 / 2,19 (7,7 MB), **q98 0,57 / 1,62 (10,9 MB)**, q100 0,41 / 1,36 (17,7 MB); el original pesa 9,2 MB. Es ruido de compresión, no un desvío de color sistemático como el del ISP. Conclusión: con LUT suaves (teal & orange) el ISP ya es casi exacto y el software no compensa la recompresión; con LUT con curva o fuertes (película, agresiva) el software gana claramente, sobre todo en el máximo.

## 5. Corrección colateral: `cube_a6000.de2000`
ΔC usaba `C2 − C1'` en vez de `C2' − C1'`: dos colores idénticos daban ΔE ≠ 0 (hasta 0,38 en colores saturados). Corregido y con regresión (pares de Sharma, Wu y Dalal 2005, falla con el código anterior). **Las cifras de ΔE de G71, G88 y G90 están infladas** y el refinamiento entero de `lut_opt` optimizó contra la métrica errónea → pendiente LUT-DE-1. Los tests de g71/g88/g89/g90 siguen pasando con la métrica corregida.

## 6. Qué solo la cámara confirma (LUT-SW-2)
1. Que `/tmp/lutjpg` se ejecuta (binario estático musl sobre el núcleo 3.0.27) y lee/escribe en `/android/mnt/sdcard` con la cámara en modo foto.
2. Tiempo por foto de 24 Mpx (no medido; el PC con SIMD tarda 0,47 s, el Cortex-A5 sin NEON será bastante más lento) y memoria disponible.
3. Que procesar mientras se dispara no estorba la grabación de la cámara (prudencia: ejecutar con la cámara en reposo).

Fuera de alcance: vídeo y vista en vivo (solo el ISP 5×9×9); aplicar la LUT automáticamente al disparar (exigiría un hilo vigilando `DCIM`, como el de G89); recalcular la miniatura EXIF (conserva la del original).
