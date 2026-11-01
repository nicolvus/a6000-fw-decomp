# E26-R45 — Firmware 3.25c (3.25 corregido), experimental y teórico

Fecha: 01-11-2026. Petición del usuario: construir la versión corregida del 3.25, corrigiendo todo lo que
bloqueó su cámara, y publicarla en GitHub como **experimental y teórica** para quien se atreva, con las
pruebas de la corrección. **Solo offline**: sin cámara, sin USB, sin firmware ejecutado en hardware.

Etiquetas: **DATOS** (paquetes reales) · **EMULACIÓN** (código real de `bootloader.bin` en Unicorn) ·
**MODELO** (LDEC de silicio sustituido por la regla de R36) · **NO VERIFICADO**.

Código: `scripts/e25_27/verify_325c.py` → [`verify-325c.json`](../../analysis/e25-27/verify-325c.json) ·
`scripts/e25_27/tpzl.py` (`_splice`) · `tests/test_e25_27_325c.py` (2) y una regresión nueva en
`tests/test_e25_27_build.py`.

## 1. Qué es

Mismo contenido funcional que el 3.25 (selector EFCS/Electronic sobre el ajuste EFCS existente, C3-B y el
Darwin condicionado de [E25-27](e25-27-construccion-firmware-integrado.md)), con la partición `nflasha3`
codificada como la de Sony. Versión de cabecera **3.25** (modelo `0x41030035`, región 0, actualizador
oficial 3.21).

| Archivo (no versionado) | SHA-256 |
|---|---|
| `analysis/e25-27/artifacts-325c/package-3.25/firmware_packed.dat` | `d64ad6e3d203dfafae020fc777ae8e9fe4a77c49f1f469cf5b907a1a6a477752` |

Construcción determinista: dos construcciones independientes dan el mismo `.dat` (DATOS).

## 2. Errores corregidos

| # | Error del 3.25 que bloqueó la cámara ([R36](e26-r36-causa-fallo-325.md)) | 3.25 | 3.25c |
|---|---|---|---|
| 1 | Bloques a 256 B: Loader3 lee sectores enteros y el residuo no llega al LDEC | 359/369 con residuo | **0/369** |
| 2 | Bloques 0/48/57 = un registro de 64 KiB (LDEC programado con 16 × 4096) | 3 bloques, 73 732 B > cota 65 800 | **16 × 4096 en los 369** |
| 3 | Relleno `0xFF` entre bloques (Sony usa `0x00`) | 4 bloques | **0** |
| 4 | **Nuevo en esta sesión:** el constructor de R36 emitía los 3 bloques como 16 registros almacenados (66 048 B = **129 sectores**). Sony nunca pasa de **126** en `nflasha3`; > 128 sectores obliga al ARM7 a partir la lectura en dos tandas (`0x1130`), ejercido por Linux en `nflasha15/16` pero **nunca por Loader3** | 145 sectores | **126 (igual que Sony)** |

Corrección del punto 4 (`tpzl._splice`, regresión escrita primero y comprobada fallando sin el cambio): en
cada bloque recompuesto se conservan los **registros comprimidos originales de Sony** de las páginas de
4096 B que no cambian y solo la página cambiada pasa a registro almacenado (forma que Sony usa). Cada bloque
tocado cambia **una sola página**: 15 de 16 registros son los bytes de Sony. Bloques resultantes: 59, 110 y
111 sectores. La imagen ocupa 11 493 888 B (Sony 11 489 040 B; partición 30 MiB).

## 3. Pruebas (30/30, `todo_ok: true`)

Ejecutadas sobre el **`.dat` final** (lo que se publica), no sobre artefactos intermedios. Controles
negativos: el `.dat` 3.25 que bloqueó la cámara (`42c02504…`) y el 3.21 de Sony.

| Grupo | Comprobación | Resultado |
|---|---|---|
| Contenedor | Descifrado independiente (auditor E25-06, no fwtool) = FDAT; sumas de 16 bits, bandera y longitudes de bloque; DEND; CRC de cabecera; versión, modelo, región; `updater.img` oficial 3.21 | OK (y fwtool lo reextrae byte a byte en `build.package`) |
| tar | Frente al 3.21: solo `darwin_core.bin`, `darwin.sum`, `dev/nflasha3`, `part_image.sum`. Frente al 3.25 que bloqueó: **solo `dev/nflasha3` y `part_image.sum`** (BIONZ y Darwin idénticos) | OK |
| tar | `part_image.sum` verifica `dev/nflasha3` (CRC-32 y tamaño, lo que relee el actualizador) | OK |
| `nflasha3` | Residuo 0, 16 × 4096 y cota de Sony en los 369 (`hardware_violations`); relleno `0x00`; bloques contiguos; 369 bloques; ≤ 126 sectores; cabe en la partición | OK (3.25: 365 violaciones) |
| `nflasha3` | Bloques no recompuestos idénticos a los de Sony (366/369); 15/16 registros de Sony en cada uno de los 3 recompuestos | OK |
| Contenido | FAT descomprimida = la del 3.25 previsto; los **89 B** distintos de Sony están todos dentro de `AV-CAM.BIN`; devolver `AV-CAM.BIN` original reproduce el 3.21 exacto | OK |
| Emulación | Loader3 (`c01fe4ec`, `c01fdd8e`) y ARM7 (`0x3f4`) reales + LDEC modelado sobre los 369 bloques | **3.25c: 0 fallos, 0 avisos de residuo** · Sony: 0 · 3.25: 361 fallos desde el bloque 0 |
| Suite | `pytest` E25-27 + 3.25c + E26 R37–R39: 40 pasan; `ruff` limpio; `mypy` sin avisos nuevos | OK |

## 4. Lo que estas pruebas NO demuestran (por eso es teórico)

- **Nunca se ha instalado ni arrancado en una cámara.** La única cámara de pruebas está bloqueada por el 3.25.
- El LDEC es silicio y se **modela** (R36/R39). La confirmación física del −302 (UART/LED) no existe.
- El código nuevo de BIONZ (selector, C3-B) y de Darwin (cueva `0x4318`) **nunca se ha ejecutado** en hardware:
  solo emulación (E25-24b…E25-27). Un fallo ahí podría colgar la cámara después de arrancar.
- Tras instalarlo, la cámara queda en versión 3.25: el 3.24 ya no se acepta y para volver al firmware de Sony
  hace falta el paquete **3.26** (contenido oficial, R37/R38), también nunca instalado.
- Si el arranque falla, **no hay recuperación conocida sin abrir la cámara** (R33, R37–R44).

## 5. Publicación

Release de GitHub `fw-3.25c-experimental`, marcado como *pre-release*, con el `.dat` 3.25c, el 3.26 de vuelta
atrás (`c730f8e2…`), `SHA256SUMS.txt` y `verify-325c.json`. Los binarios no entran en el árbol de git.
