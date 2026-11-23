# G95 — LUT precalculada en el PC: la cámara solo valida y copia (LUT-PKG-1, 23-11-2026)

Origen: [G94](g94-lut-resolucion-entrega-fidelidad.md) §4. Sin cámara ni CFW construido. Código: `scripts/lut/lut_pkg.py` (generador y referencia), `lutsd_paquete`/`lee_paquete` en `scripts/lut/userland/lutsd.c` (hilo de la SD de [G89](g89-lut-sd-en-camara.md)). Tests: `tests/test_g95_lut_pkg.py` (3) y `tests/test_g89_lut_sd.py` adaptado.

## 1. Qué cambia
- **En el PC:** `python3 scripts/lut/lut_pkg.py ENTRADA.cube LUT1.LUT` ajusta la LUT 5×9×9 al `.cube` minimizando ΔE2000 (`cube_a6000.descompone`, 3–4 s) y la guarda ya en el formato de la ranura del blob de Backup.
- **En la SD:** el fichero se copia como `LUT/LUT<n>.LUT`, junto a los `.cube` o en su lugar.
- **En la cámara:** por cada ranura, el hilo prueba primero `X:/LUT/LUT<n>.LUT`. Si la firma, la versión, la longitud y el CRC32 cuadran, copia los 1064 B a la ranura del blob y no remuestrea nada. Si falta el fichero o no vale, sigue como hasta ahora con el `.cube`. `av-cam` no cambia: lee el mismo blob.

**Formato v1** (1080 B, little-endian):

| Desplazamiento | Campo |
|---|---|
| 0 | `A6LT` (u32) |
| 4 | versión 1 (u8) |
| 5 | 0 (u8) |
| 6 | 1064 (u16) |
| 8 | CRC32 IEEE de la carga (u32) |
| 12 | 0 (u32) |
| 16 | carga: 405 nodos × 21 bits en orden lógico (`avcam_dinamico.empaqueta_21`) |

La curva T (LUT-T-1) entrará como versión 2 cuando `av-cam` tenga su consumidor.

## 2. Evidencia (Unicorn y PC)
- `lutsd_paquete` compilado para ARM = referencia `lut_pkg.valida`: con un paquete íntegro copia la carga exacta; rechaza un fichero un byte corto o largo y uno con la firma, la versión, la longitud o la carga cambiadas (test).
- Paquete generado desde un `.cube` = tabla del ajuste en ΔE del PC, byte a byte (test).
- Hilo completo emulado: ranura 1 con un `.LUT` válido entra en el blob sin abrir ningún `.cube`; ranura 2 con el CRC roto queda inválida (test). Cada ranura prueba el `.LUT` antes que el `.cube`. Los 19 tests de G89 siguen pasando con el orden nuevo.
- **Calidad** (33³, 20 000 colores al azar, ΔE2000 medio / p95 / máx frente al `.cube`, trilineal):

| LUT | conversión en la cámara (`lutsd.c`) | paquete del PC |
|---|---|---|
| teal & orange | 0,40 / 1,43 / 4,7 | **0,07 / 0,16 / 0,9** |
| película | 1,05 / 2,42 / 8,1 | **0,79 / 1,78 / 5,1** |

- **Coste en la cámara:** lectura de 1080 B y CRC de 1064 B por ranura, una vez por inserción de tarjeta. No hay análisis de texto, remuestreo ni aritmética Q16. El código ARM crece de 3,6 a 4,2 KB.

## 3. Límites y qué confirma la cámara (LUT-SD-2)
- `lee_paquete` abre solo `X:/LUT/LUTn.LUT` (barra `/`; el nombre ya es 8.3). Si la cámara solo aceptara `\` como separador (diagnóstico pendiente de G89 §4.3), habría que probar también esa variante para el `.LUT`.
- Fin de fichero: el bucle termina con `Fsys_Read` ≤ 0, igual que el `.cube`; la semántica del 0 sigue sin confirmar.
- La vista en vivo y la foto reciben la misma tabla (G94 §3 bis), así que el paquete no cambia la fidelidad entre ambas: solo mejora el ajuste y quita trabajo a la cámara.

## 4. CFW 3.84 (23-11-2026)
Construido a petición del usuario, **sin instalar**: `python3 scripts/gui/build_cfw_objetivos.py build/cfw_lut_pkg --version 3.84 --sd-lut` (3 min). Es el CFW de objetivos con la LUT por SD de G89 más el paquete `.LUT` de este informe.
- Paquete: `build/cfw_lut_pkg/pkg-3.84/package-3.84/firmware_packed.dat`, SHA-256 `c6cbcceb7f9f749df1ce858885845c7396522645fb40e1c6f246701951a3bd8b`. `.fdat`: `39e4ecc27f9aebfde0c3ced9220c7cb1039616063db994608a7854a77af80183`. El directorio `build/` no se versiona.
- Lleva dos arreglos de G89 que la 3.83 (`build/cfw_lut_sd`, 21-11) no tenía. El primero es `DLSYM_PLT` = `0xe72e4`: con `0xe6f94` el arnés daba `pc=0` en `DT_INIT`; ahora lo cubre un test de regresión contra la relocalización `R_ARM_JUMP_SLOT` de `dlsym`. El segundo prueba 4 rutas por `.cube` (`/` o `\`, `.cube` o `.CUB`) y deja un diagnóstico en el blob, en `0x2000` y en la cabecera `[14]`, que `av-cam` ignora.
- **Verificado sobre la imagen construida:**
  - Se descomprimió `nflasha15-384.bin` (TPZL → ext2). Las cuatro bibliotecas parcheadas son idénticas byte a byte a las de `files/`. `e2fsck` solo avisa de los contadores de libres, como en las versiones anteriores.
  - `viewUnified2.so` contiene el userland completo (4216 B, con `lutsd_paquete`). En Unicorn, `DT_INIT` del fichero construido llama al `_init` original, pide `dlsym("pthread_create")` por `0xe72e4` y arranca `lutsd_hilo`.
  - Frente a la 3.83, `av-cam` solo difiere en `ZONA_B` (`0x43C1FF58…0x43C20B65`): son las tres tablas de fábrica, recalculadas con el ΔE2000 corregido de LUT-DE-1. Las cuevas no cambian.
- **Uso:** `python3 scripts/lut/lut_pkg.py mi.cube LUT1.LUT` y copiar el resultado a `LUT/` en la SD, como `LUT1.LUT`…`LUT6.LUT`. Sin `.LUT`, el `.cube` sigue funcionando.
