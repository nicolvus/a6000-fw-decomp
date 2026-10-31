# E26-R36 — Por qué falló el 3.25 si el 3.23 se instaló bien

Fecha: 31-10-2026. Continúa [R15](e26-r15-tpzl-custom-fw325.md)–[R17](e26-r17-arm7-ldec-segment-analysis.md) y [R30](e26-r30-updater-done-boundary.md). **Solo análisis offline** de archivos, binarios y fuentes GPL de Sony. Sin cámara, sin USB/UART, sin escribir NAND. Pedido del usuario: verificar de inicio a fin, dos veces, por qué falló el 3.25 viniendo del 3.23.

Etiquetas: **BINARIO** = desensamblado (Capstone) de `bootloader.bin` (Loader3 en `0x22800`, BossFirm ARM7 en `0x18800`) · **DATOS** = leído de paquetes e imágenes · **FUENTE** = código GPL de Sony en `analysis/session18/main/sony-oss-extracted/linux` · **INFERENCIA** · **NO VERIFICADO**.

Código: [`r36_ldec_records.py`](../../analysis/e26-recovery/r36_ldec_records.py) → [`r36-ldec-records.json`](../../analysis/e26-recovery/r36-ldec-records.json) (dos parsers independientes que deben coincidir) · `scripts/e25_27/tpzl.py` (`hardware_violations`, codificador corregido) · `tests/test_e25_27_build.py` (2 pruebas nuevas y una aserción en la construcción completa).

## 1. Respuesta

El 3.23 y el 3.25 pasaron por el mismo camino (mismo actualizador 3.21, mismo Loader2/Loader3, mismo flujo `pmca-console`). **La única diferencia que Loader3 lee es `nflasha3`.** El 3.23 llevaba la de Sony; el 3.25 llevaba una reconstruida por `scripts/e25_27/tpzl.py` con dos defectos de formato que el software de verificación aceptaba y la ruta hardware de Loader3 no puede leer:

1. **Bloques desalineados (359 de 369).** El constructor alineaba a 256 B. Loader3 lee sectores enteros desde `offset >> 9` y el desplazamiento dentro del sector (256 B) **no llega al descompresor**: solo genera un aviso. El LDEC recibe 256 B del bloque anterior antes del inicio real del bloque.
2. **Bloques 0, 48 y 57 con un solo registro de 64 KiB.** El LDEC se programa con `bloque >> 12 = 16` registros de 4096 B; el constructor emitía un único flujo de literales de 65 536 B y 73 732 B, por encima de la cota de Sony para un bloque (16 × 4112 + 8 = 65 800 B).

La primera lectura de la partición 3 en el arranque (sector de arranque FAT, bloque 0) cae en el defecto 2. La primera lectura del RAMCFG (`\sabin`, bloque 240) cae en el defecto 1. Cualquier fallo de esa lectura sale de Loader3 como **−302** (`c01f2c2a` → `c01f4690`), que es exactamente el patrón observado de 3 pulsos lentos y 2 rápidos ([R13](e26-r13-led-error-provenance.md), [R14](e26-r14-ramcfg-bos-analysis.md)).

**Clasificación:** causa identificada offline (BINARIO + DATOS + FUENTE). Falta solo la confirmación física (log UART `LD3_E`/`FAT_E`), que no está autorizada. **[R39: reproducida en emulación con el código real de Loader3 y ARM7 y el LDEC modelado; 361/369 bloques fallan, Sony y la corregida 0 ([R39](e26-r39-estatico-profundo.md) §2). La UART está silenciada (R37).]**

## 2. Comparación de paquetes (verificada dos veces)

Descifrado de los `.dat` realmente instalados con el auditor de E25-06 (AES de `cryptography`) y comparación con su FDAT plano; luego, tar miembro a miembro (parser ustar propio). Repetido con `fwtool` para el 3.21.

| Paquete | `.dat` | Descifrado = FDAT plano | Miembros distintos frente al 3.21 |
|---|---|---|---|
| 3.23 (T040, arrancó) | `4c21353d…` | sí (DEND y CRC correctos) | `darwin_core.bin`, `darwin.sum` |
| 3.25 (bloqueó) | `42c02504…` | sí | `darwin_core.bin`, `darwin.sum`, **`dev/nflasha3`**, **`part_image.sum`** |

El `nflasha3` dentro del 3.25 instalado es byte a byte el artefacto auditado (`bb9ce25a…`). R30 ya había mostrado que el actualizador relee `/dev/nflasha3` y comprueba su CRC antes de Done: la cámara tiene exactamente esa imagen.

**Darwin no explica −302:** Loader3 no lee Darwin y el LED lo genera Loader3 en BIONZ, que por tanto arrancó. El cambio de Darwin del 3.25 (cueva `0x4318`) sigue sin probarse, pero solo podría actuar después.

## 3. Lo que exige la ruta hardware (BINARIO, releído en esta sesión)

| Paso | Instrucciones | Qué se comprueba |
|---|---|---|
| Petición de bloque | `c01fdd8e`: `c01fddf6 ubfx r0,sb,#0,#9` (residuo) → solo `bl 0xc020bd24` (aviso) y `[sp+0xc]`; `c01fde20 add r2,r1,sb,lsr #9` (sector inicial = `off>>9`); `c01fde28 lsrs r3,r0,#9` (nº de sectores) → `c01fdbe0` | La lista de transferencia es de **sectores enteros**; el residuo no entra en ella |
| Trabajo | `c01fde0a lsrs r0,r7,#0xc` → `+0xc = bloque>>12 = 16`; `+0x10 = [r5]` (búfer destino) | Formato `{n, lista, residuo, registros, destino, tamaño}` |
| Copia al ARM7 | `c01fccd2`: `movs r2,#0x18` + `blx memcpy` y la lista detrás | Se copia, nada más |
| ARM7 op 0 | `0x1338` lee `[r7]` y `[r7,#4]`; `0x3f4`: `ldr r3,[r0,#0xc]` → `str r3,[r1,#0xc]` y `ldr r0,[r0,#0x10]` → `str r0,[r1,#0x10]` | El LDEC recibe registros y destino. **`+8` (residuo) no se lee** |
| Reintento | `c01fdf26`/`c01fdf5a`: mismo `off>>9`, residuo solo para el aviso | Tampoco hay ajuste por bytes |

Linux usa el LDEC igual: `ldec.ko` `boss_hw_ldec_set(registros, destino)` escribe `+0xc` y `+0x10` y alimenta la entrada por DMA (`ldec_ioctl`, `0x63c`). Su estado: 1 = éxito, 4 → −EIO, otro → −13 (`boss_hw_ldec_process`, `0xc24`–`0xc44`).

**Consecuencia:** en un bloque con residuo 256, el flujo que entra en el LDEC empieza 256 B antes del primer registro. El LDEC no recibe ningún dato que le permita saltarlos. R16/R17 dejaron «qué hace el silicio con el residuo» como indecidible; lo decisivo es que **el residuo nunca llega al silicio**.

## 4. Formato de Sony (DATOS + FUENTE)

| Comprobación | Resultado |
|---|---|
| Corpus: 16 imágenes TPZL de Sony (A6000 3.21, α7S 3.20, α6300 2.01, volcados de esta cámara) | **19 489 bloques y 311 824 registros**: todos los bloques son 16 registros de 4096 B y todos los offsets tienen residuo 0. Dos parsers independientes coinciden |
| Registro almacenado de Sony | `0F 00 <u16 4096> + 4096 B`; 4556 en `nflasha15` y 162 bloques hechos solo de ellos (129 sectores), que Linux lee en cada arranque de esta cámara |
| TOC de Sony | bloques contiguos, tamaños múltiplo de 512, relleno `0x00` |
| Cota de tamaño (`cmpr.c`, `cmpr_demand_wlen`) | `bloques × ((bloque/4096) × 4112 + 8)`: el formato es por unidades de 4096 B y un bloque de 64 KiB no pasa de 65 800 B |
| 3.25 instalado | residuo 256 en 359 bloques; bloques 0/48/57 = 1 registro de 65 536 B y 73 732 B; relleno `0xFF` en 4 bloques |

## 5. Qué lee el arranque (DATOS, `fwtool` + FAT12 recorrida a mano)

| Lectura de Loader3 | Bloques | Con residuo 256 | De 1 registro | 3.21 oficial |
|---|---:|---:|---|---|
| Sector de arranque, FAT y raíz | 1 (bloque 0) | 0 | **0** | sin anomalías |
| `\sabin` (primera entrada RAMCFG) | 1 (240) | **1** | — | sin anomalías |
| `\sabin\idt_cam.bin` | 4 | 4 | — | sin anomalías |
| `\sabin\sa_dfdet.bin` | 4 | 4 | — | sin anomalías |
| `\av-cam.bin` | 176 | 166 | 0, 48, 57 | sin anomalías |
| `\initrd.img` | 63 | 63 | — | sin anomalías |
| `\vmlinux.bin` | 55 | 55 | — | sin anomalías |

No hay ninguna ruta de arranque normal que llegue al kernel sin leer bloques defectuosos.

## 6. Por qué no lo detectaron las comprobaciones offline

`tpzl.py` y `fwtool` descomprimen por software: concatenan registros sin mirar su tamaño ni la alineación, así que el 3.25 «se descomprimía igual». El constructor verificaba su salida con su propio decodificador (comprobación circular). Ningún verificador del proyecto modelaba la ruta Loader3 → ARM7 → LDEC.

## 7. Corrección del constructor

- `scripts/e25_27/tpzl.py`: `ALIGN = 512`, bloques recompuestos como 16 registros almacenados de 4096 B (la forma de Sony), relleno `0x00`, y `hardware_violations()` (residuo, 16 × 4096, cota de Sony). `rebuild` se niega a devolver una partición con violaciones.
- Regresión escrita primero: falló con el codificador anterior y pasa con el nuevo. `hardware_violations` acepta el `nflasha3` oficial y marca en el 3.25 instalado 359 residuos y 3 bloques de un registro.
- Construcción completa en un directorio temporal (no se tocó `analysis/e25-27/artifacts/`): residuo 0 en 369/369, 16 × 4096 en todos, máximo 129 sectores (igual que Sony), mismo contenido FAT que el 3.25 (89 B distintos del 3.21) y mismos `av-cam`/Darwin.
- **La recomendación 2 del README («alinear a 512») no bastaba**: la variante de `compare_tpzl.py` alineada a 512 sigue teniendo 3 bloques de un registro de 73 732 B (6 violaciones).

Que la imagen corregida cumpla el formato de Sony **no prueba** que arranque ni que el código nuevo de BIONZ/Darwin funcione. No se ha construido ningún paquete instalable y nada se ha instalado.

## 8. Correcciones trazables (no se alteran los informes previos)

- **R16 §6** («73 984 B no es un límite demostrado»): sigue sin demostrarse un límite del hardware, pero el bloque supera la cota del propio formato de Sony (`cmpr.c`: 65 800 B).
- **R17 §1.4 y decisión C** («no se prueba qué hace el silicio con los primeros 256 B»): el residuo no llega al LDEC por ninguna instrucción de Loader3 ni del ARM7, así que el silicio recibe el flujo desde el inicio del sector.
- **README § «Qué falló en el 3.25», punto 2:** alinear a 512 es necesario pero no suficiente.
- **E25-27 §3:** «segmento de literales … alineado a 256 B» describe el artefacto instalado; el constructor actual ya no produce ese formato.

## 9. Verificaciones ejecutadas

| Comprobación | Veces | Resultado |
|---|---|---|
| `.dat` 3.23/3.25 descifrados = FDAT plano; diff de miembros | 2 (`fwtool` en el 3.21 y auditor E25-06) | 2 y 4 miembros |
| Auditoría de registros del corpus y del 3.25 | 2 (parser propio y `hardware_violations`; script ejecutado dos veces) | coinciden |
| Desensamblado `c01fdd8e`, `c01fccd2`, `c01fdf26`, ARM7 `0x1338`/`0x3f4`, `ldec.ko` | 1 propio + R16/R17 | coincide con R16/R17 |
| Mapa de lecturas de arranque | 2 (3.25 y 3.21 como control) | §5 |
| `pytest` E25-27 y E26 R13–R17 | 49 pasan | — |
| `ruff check`, `mypy` en los archivos tocados | sin avisos nuevos | `tpzl.py` ya no estaba formateado con `ruff format` antes; no se reformateó |

## 10. Lo que sigue abierto

- Confirmación física (UART pasiva de Loader3: `LD3_E`, `FAT_E`, `CFG_E` y el aviso de residuo). Requiere autorización (`E26-R12-UART-FISICO`).
- La recuperación no cambia: restaurar `nflasha3` desde `dev_nflasha3.bin` ([R30](e26-r30-updater-done-boundary.md)); la vía de escritura sigue siendo física ([R33](e26-r33-veracidad-clave-nflasha0.md)).
- El Darwin del 3.25 y el código nuevo de BIONZ no se han ejecutado nunca.
