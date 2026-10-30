# E26-R15 — Auditoría TPZL de Loader3, firmware personalizado 3.25 y lógica RAMCFG

Fecha: 30-10-2026. Continúa [R14](e26-r14-ramcfg-bos-analysis.md) (`b41d45ae`). **Solo análisis estático y lectura de archivos existentes.** Sin cámara, sin USB/UART, sin imágenes instalables, sin escribir NAND. Los volcados y paquetes no se tocaron.

Etiquetas: **BINARIO** = desensamblado de `bootloader.bin` (Loader3, `0xc01f0000`) · **DATOS** = leído de volcados/paquetes · **SCRIPT** = resultado de un script de este informe · **DOC** = lo dicen informes/commits del repo · **INFERENCIA** · **NO VERIFICADO** (estado físico).

Código: [`r15_tpzl_loader3.py`](../../analysis/e26-recovery/r15_tpzl_loader3.py) (validador independiente con las comprobaciones de Loader3) · [`r15-mode-table.py`](../../analysis/e26-recovery/r15-mode-table.py) (`c01f2282` sobre 55 BK4 + tabla modo→archivos) · [`tests/test_e26_r15_tpzl.py`](../../tests/test_e26_r15_tpzl.py) (5 pruebas) · salidas `r15-tpzl-audit.json`, `r15-mode-table.json`.

## 1. Resumen ejecutivo

1. **DOC. El 3.25 no es de Sony.** Es un paquete propio (E25-27, commit `71ab533d`, 28-10-2026) construido sobre el **3.21 oficial** (`firmware.tar` `97024649…`, `updater.img` `b6d51752…`). «3.25» es solo el número de versión de cabecera FDAT que exige el *guard* (solo acepta versiones mayores). De los **73 miembros** del tar solo difieren **4**: `0640_darwin/darwin_core.bin`, `0641…/darwin.sum`, `0700_part_image/dev/nflasha3` (+83 440 B) y `0701…/part_image.sum` (SCRIPT, comparación de ambos tar). `updater.img` es el oficial: **Loader2/Loader3, Backup, `partinf.conf`, kernel e initrd no cambian**.
2. **BINARIO. El lector TPZL real de Loader3 acepta el residuo de 256 B.** `c01fdd8e` calcula `residuo = offset & 0x1ff`, **solo emite un aviso** si es ≠ 0 y lee `(residuo + tamaño + 0x1ff) >> 9` sectores desde `offset >> 9`, pasando el residuo al descriptor del descompresor. Nunca aborta por desalineación. Esto resuelve el pendiente de R14/R7 «residuo sin rechazo demostrado» **a nivel de software de Loader3**.
3. **SCRIPT. Las tres imágenes pasan todas las comprobaciones de software de Loader3** (cabecera, TOC, 369 entradas, límites del dispositivo de 30 MiB). La integrada 3.25 es la única con residuo (359 de 369 entradas a 256 B). **No se demuestra incompatibilidad** (el hardware LDEC con residuo ≠ 0 y con bloques comprimidos mayores que el bloque sin comprimir sigue sin verificar; §8).
4. **BINARIO + DATOS. `c01f2282` resuelto:** solo omite una entrada RAMCFG si el elemento Backup `0xfa0033` vale 1 o 2. Vale `0x80021048` en las **55** copias BK4 → **nunca omite**. Con modo `0x1000000` Loader3 intenta cargar **los 6 archivos**; con `0x4000000`, solo `idt_cam.bin` y `av-cam.bin`.
5. **DOC. Discriminador fuerte de procedencia.** En esta misma cámara ya se instalaron con éxito, por el mismo camino (`pmca-console firmware`, CRC-32, 100 %/Done, la cámara arrancó): T024 (3.21→3.22, Darwin tipo 0) y T040 (3.23, Darwin B1a). Eran el tar oficial con **solo Darwin sustituido**; el `nflasha3` escrito era el oficial, alineado a 512 B. **El 3.25 es el primer paquete que incluyó un `nflasha3` y un `av-cam.bin` modificados.** El camino de instalación no es lo nuevo; lo nuevo es el contenido de `nflasha3`.
6. **Decisión: C** (construcción y TPZL validados frente a las comprobaciones implementadas en software; fallo físico abierto), con resultado secundario **D** (omisión RAMCFG resuelta: no hay omisión). Detalle en §16.

## 2. Corrección sobre la naturaleza del 3.25

Se corrige la lectura implícita de «actualización 3.25»: **no existe `updater.img` oficial 3.25**; el repo contiene el 3.21 oficial y los paquetes propios 3.23/3.24 (E25-05) y 3.25 (E25-27). Esta sesión no busca ni inventa un 3.25 de Sony. R14 §2 ya avisaba «el repo no contiene el `updater.img` ni el `endupdate.sh` de 3.25»: es correcto porque **el updater del 3.25 es el 3.21** (hash idéntico exigido por el constructor).

## 3. Procedencia y clasificación de artefactos

| Cat. | Artefacto | SHA-256 | Estado |
|---|---|---|---|
| A | `firmware.tar` 3.21 oficial | `97024649…58d5a8` (`970246492293e9175ef67b1ad587d5289ae886d47dbd10e77637d9bee458d5a8`) | verificado en repo (constructor lo exige) |
| A | `updater.img` 3.21 | `b6d51752…2566c` | idem |
| A | `nflasha3` oficial 3.21 | `93d4a1f0…963765` | idem |
| B | `firmware_packed.fdat` / `.dat` 3.25 | `87145e1b…a8d9f` / `42c02504…f7cae` | construido offline el 28-10 (E25-27); el usuario aportó el hash del FDAT y coincide (`e26-recovery.md`) |
| B | `firmware.integrated.tar` | `440b70b1…52e1` | idem |
| **C** | **paquete efectivamente escrito en la cámara** | — | **NO DEMOSTRADO.** Sin log del actualizador ni del `pmca-console` del 3.25; solo el testimonio «100 % y Done». El hash del FDAT aportado por el usuario coincide con B, pero eso no prueba byte a byte qué se transfirió |
| D | `nflasha3.integrated.bin` | `bb9ce25a…d546c` | el mismo que va dentro de B (el tar de B contiene este archivo, SCRIPT); no es una «reconstrucción posterior distinta» |
| E | NAND histórica 3.21 (`dev_nflasha3.bin`) | `ea0a11fd…b5c6` | 20-10-2026, anterior al incidente |

**Aclaración respecto al encargo (D):** el enunciado trata `nflasha3.integrated.bin` como «reconstruido posteriormente». En el repo es el artefacto **producido por el constructor de E25-27 y empaquetado en el FDAT B**; no hay una segunda reconstrucción. Lo que sigue sin existir es C (lo escrito realmente). La imagen 4 del encargo (paquete de instalación verificado) = B, localizada y con hash; su identidad con C queda sin probar.

## 4. Matriz de componentes (Entregable A)

| Componente | Base original | Modificación | Artefacto | Hash | Evidencia |
|---|---|---|---|---|---|
| BIONZ (`av-cam.bin`) | 3.21 `b60c845c…56bb9` | **Demostrada:** selector `0x4384133e/42/476` + cuevas `0x43541800`, `0x43541840` (C3-B) · 111 B | `av-cam.integrated.bin` | `45a5ab35…5190e` | DOC E25-27 §2/§10; diff 111 B (R14 contó 89 B tras descomprimir `nflasha3`; la diferencia de recuento no se ha reconciliado, §13) |
| Darwin | 3.21 `5f2be06d…0bf4` | **Demostrada:** compuertas `0x20c78`/`0x1fe6c` → cueva `0x4318` + literal `0x4330` (18 B) | `darwin_core.integrated.bin` | `9771c050…fb177` | DOC E25-27 |
| Loader2 | del `updater.img` 3.21 (`loader_mpt.tar`) | **Sin cambios comprobados** | — | — | `updater.img` idéntico al oficial; `loader_writer.sh` escribe Loader3 y Loader2 solo en modo `full` |
| Loader3 | ídem | **Sin cambios comprobados** | `bootloader.bin` histórico `eb420385…` | — | idem |
| Kernel / initrd | `vmlinux.bin`, `initrd.img` del `nflasha3` 3.21 | **Sin cambios:** idénticos byte a byte (R14 §5) | — | — | DATOS |
| Backup | 11 plantillas `0110_backup` | **Sin cambios:** 73 miembros, solo 4 difieren | — | RAMCFG `01b799a4…` | SCRIPT |
| TPZL (`nflasha3`) | oficial 11 489 040 B | **Demostrada:** bloques 0, 48, 57 recomprimidos (literales, 73 984 B c/u) y alineación de 256 B → residuo 256 en 359/369 entradas | `nflasha3.integrated.bin` | `bb9ce25a…d546c` | SCRIPT (`r15-tpzl-audit.json`) |
| FDAT/DAT | oficial 3.21 | **Demostrada:** versión 3.25, CRC `6facbbf7`, DEND `fae7ef16`, `part_image.sum` `f5e75c34`/`0x00b09500` | `firmware_packed.*` | §3 | DOC |
| Menú EFCS | — | **Sin modificación de menú propia:** reutiliza el byte `+0x210` (0/1) del selector EFCS existente; no hay cambio de estructura persistente demostrado | — | — | DOC E25-27 §2 |

## 5. Reconstrucción del proceso de construcción

DOC (E25-27 §3, `scripts/e25_27/build.py`, determinista): verifica identidades → parchea `av-cam.bin` en sitio (misma cadena FAT y tamaño) → recompone **solo** los bloques TPZL 0, 48, 57 con un único segmento de literales y `ALIGN = 256` → actualiza CRC-32/tamaño en `part_image.sum` → reescribe 4 miembros del tar → empaqueta FDAT/DAT con `fwtool`. **No hay log de instalación ni manifiesto de transferencia.** Lo previsto por E25-27 se cumple en el repo; lo ejecutado en la cámara no consta.

## 6. Instalación y actualizador (Prioridad D)

SCRIPT/DOC, sobre los scripts 3.21 (que son los del 3.25 por ser el mismo `updater.img`):

- `startupdate.sh`/`us_mkfs.sh`: según `UPDATER_ACTION_MODE`, `edisx.elf /dev/nflasha partinf.conf` (tabla de particiones), `uc_mkfs.elf -m full|app` (formateo), `fmode=full` por defecto salvo `NOT_WRITE_LOADER`.
- `loader_writer.sh`: extrae `loader_mpt.tar` del updater y escribe Loader3 y Loader2 (`pformat`) en modo `full`; el código `246` es bloque defectuoso.
- `endupdate.sh`: monta `nflasha2`, copia `Backup.bin` y ejecuta `ud_keep_backup`/`ud_backup_write`.
- `partinf.conf` del 3.25 = el 3.21 (R14).

Respuestas: (1) el instalador fue `pmca-console firmware` + `updater.img` oficial (DOC T024/T040; para el 3.25 solo testimonio). (3) scripts oficiales 3.21. (4) flujo no alterado por el proyecto. (5–6) según modo: tabla de particiones, FAT de `nflasha2`, datos de `nflasha3`. (7) BOS lo reescribe `edisx` si el modo lo exige. (8) `Backup.bin` se regenera por `ud_keep_backup`. (10) **No se encontró verificación de lectura de `nflasha3` tras escribirla** (solo CRC del paquete). (11) «Done» demuestra el fin del script, no una verificación de arranque. (12) **No existen logs** del 3.25. **Límite:** no se puede afirmar qué modo (`full`/`app`) se ejecutó.

## 7. Auditoría del lector TPZL de Loader3 (Prioridad B)

**BINARIO.** Cadena (nombres por función, direcciones reales):

| Función | Papel | Evidencia |
|---|---|---|
| `c01f4690` | lector de sectores FAT: `r0 = c01f2c2a(...)`; si ≠ 0 devuelve `−302` (`0xfffffece + 4`) | `c01f469a`–`c01f46a4` |
| `c01f2c2a` | si el tipo de dispositivo `[tabla+8]==3` (TPZL): `c01f9a66(2, dev)` busca el dispositivo registrado, `c01f9a90` lo abre (llama a `ops[0]`), `c01f9bd0` lee; `r0 ≤ 0` → `−5` | `c01f2c3e`–`c01f2c88` |
| `c01f9bd0`/`c01f9b10` | comprueba que `offset & (align−1) == 0` con `align = dev[0x20]` (alineación **de la petición lógica**, no del contenedor); error `−0x16` | `c01f9b18`–`c01f9b3c` |
| `c01fe4ec` | **registro TPZL**: lee 0x18 B; exige magic `TPZL` (`0x4c5a5054`), `u32@4 ≤ 0x11`, `u32@8` y `u32@0xc` ≠ 0 y `(a|b)&3 == 0`; reserva el TOC, lo lee, `entradas = tamaño >> 3` | `c01fe4fa`–`c01fe55c` |
| `c01fe006` | petición: índice de bloque `< entradas` (`c01fe03a`); llama a `c01fdd8e` por bloque | `c01fe05c`–`c01fe060` |
| `c01fdd8e` | por bloque: `offset = TOC[i]`, `tamaño = TOC[i+4]`; `residuo = offset & 0x1ff`; ≠ 0 → solo **aviso** (`c020bd24`); `sector = base + (offset>>9)`; `n = (residuo + tamaño + 0x1ff)>>9`; construye descriptores NAND con `c01fdbe0` | `c01fddf6`–`c01fde34` |
| `c01fdf26`/`c01fdf5a` | segundo recorrido sobre el TOC con el mismo aviso (`c01fdf70`–`c01fdf78`) y misma fórmula | `c01fdf6c`–`c01fdf90` |

**Hechos:** (a) no hay rama que aborte por residuo ≠ 0; (b) el residuo se transmite al descriptor del descompresor (`[sp+0xc]`); (c) la capacidad de descriptores por llamada (`c01fe632`: `1 + (2·X + 0x3fff7)/P`) cubre ≥ 256 KiB, muy por encima de los 145 sectores (72,5 KiB) de la imagen 3.25; (d) la cadena de texto del aviso está fuera del prefijo de 43 páginas de INFO 5 (`0xc020e86c`): **el texto exacto no es legible**.

**Límites (INFERENCIA/NO VERIFICADO):** el tamaño de página `P` y el comportamiento del hardware LDEC con residuo ≠ 0 o con entrada mayor que la salida no se pueden resolver estáticamente; `c01f9a90`/`ops` son llamadas indirectas.

## 8. Residuo de 256 B (Prioridad B.2)

SCRIPT/DATOS (`r15-tpzl-audit.json` y `compare_tpzl.py`):

1. **Ubicación:** no es relleno entre bloques. Los bloques están contiguos (`off[i+1] = off[i] + size[i]`); el residuo es la posición de inicio dentro del sector. Los bloques 0, 48 y 57 crecen +47 872 B, +17 664 B y +17 664 B (múltiplos **impares** de 256 B); cada uno invierte la paridad: bloques 1–48 → 256, 49–57 → 0, 58–368 → 256. Total 359 con 256 y 10 con 0.
2. **Pertenencia:** el residuo no es un campo; es el desplazamiento de bloques comprimidos válidos. **Declarado:** incluido en el `tamaño` + el cálculo de sectores de Loader3.
3. **¿Loader3 lo lee?** Sí, lo trata (§7). **¿Altera límites?** Añade un sector por bloque desalineado (116 vs 115, etc.); el máximo pasa de 126 a 145 sectores. El último bloque termina a 256 B en un sector y lee 6 sectores (hasta `11 572 736`); el oficial también lee más allá del final del archivo (TOC termina en `11 489 280` > `11 489 040`), de modo que **ambas** imágenes dependen de bytes posteriores al archivo en la partición (el volcado histórico los muestra `0xFF` hasta 30 MiB).
4. **Diferencias frente a las originales que sí son atípicas** (DATOS): (i) alineación de bloques a 256 B (Sony: 512 B); (ii) tres bloques con **73 984 B comprimidos, mayores que los 65 536 B que producen**; el mayor bloque oficial es 64 512 B; (iii) relleno entre bloques `0xFF` (oficial `0x00`). Ninguna es una violación de las comprobaciones de software; cualquiera podría importar al hardware LDEC. **No se cataloga como corrupción.**

## 9. Comparación independiente de imágenes (Prioridad C)

| Medida | Cámara 3.21 (E) | Oficial 3.21 (A) | Integrada 3.25 (B/D) |
|---|---|---|---|
| Tamaño | 31 457 280 (30 MiB con `0xFF`) | 11 489 040 | 11 572 480 |
| Cabecera (`TPZL`, shift 16, TOC `0x18`) / entradas | ok / 369 | ok / 369 | ok / 369 |
| Bytes descomprimidos | 24 182 784 | 24 182 784 | 24 182 784 |
| Residuos por entrada | {0: 369} | {0: 369} | {0: 10, 256: 359} |
| Máx. sectores por bloque | 126 | 126 | 145 |
| Comprobaciones Loader3 (validador R15) | **pasa** | **pasa** | **pasa**, con aviso de residuo |
| Contenido FAT / RAMCFG | R14 | R14 | R14 (89 B de `av-cam` difieren) |

Equivalencia con el parser existente: el validador R15 (independiente de `scripts.e25_27.tpzl`) coincide en cabecera, número de entradas y residuos con `compare_tpzl.py` (369; 0:10/256:359). Casos sintéticos (5 pruebas): magic erróneo, shift > `0x11`, TOC no múltiplo de 4, lectura fuera del dispositivo y residuo 256 → rechazo o aviso según el binario.

## 10. `c01f2282` y `c01f16b0` (Prioridad E)

BINARIO + DATOS:

- `c01f16b0` lee el elemento Backup `0xfa007f − 0x4c = 0xfa0033` con `c01f498c`; devuelve su u32 (0 si falta, con log).
- `c01f2282`: `v = c01f16b0()`; **solo si `v ∈ {1,2}`** y `[0xc00e0004] ≠ 6` consulta `c01f5f18()` (`= [0xc00e0060+0x24]`); si ≠ 0 devuelve 1 («omitir», `CFG:skip`); en cualquier otro caso 0.
- `[0xc00e0060+0x24]` lo inicializa `c01f61a0`: a 1 si el byte `+0xd` del elemento `0x280005` vale 1, o según el tipo de producto `[0xc00e0060+0x34]` (5/4/7). En los 11 BK4 con `backup_flash.bin` vale 0.
- Llamadores: `c01f307c` (RAMCFG) y `c01f7752` (otra ruta, no analizada).
- **DATOS:** `0xfa0033 = 0x80021048` en las **55** copias → `c01f2282 = 0` siempre.

### Tabla de selección (Entregable E)

| Modo | Archivo | ¿Se intenta cargar? | Condición | Evidencia |
|---|---|---|---|---|
| `0x1000000` (normal / HotOFF) | `\sabin\idt_cam.bin`, `\sabin\sa_dfdet.bin`, `\av-cam.bin`, `\kemco.txt`, `\initrd.img`, `\vmlinux.bin` | **Sí, los 6** (en orden) | `(modo&0xf00000)==(flags&0xf00000)`, `flags&(modo&0xf000000)≠0`; `c01f2282 = 0` | `c01f304c`–`c01f307a`; `r15-mode-table.json` |
| `0x4000000` (arranque 0xa/0xb / Normal load OFF) | `idt_cam.bin`, `av-cam.bin` | Sí; los otros 4 no | idem | idem |
| `0x2000000` (modo 2) | ninguno | No | ningún `flags` lo incluye | idem |
| Early load (bit 20) | ninguno | No | `flags` sin bits 20–23 | idem |

El modo que usa el arranque normal sigue siendo `0x1000000` (R14); el caso `c01f7752` queda como llamada indirecta no resuelta. **Todos los archivos del modo normal son obligatorios**: ninguno se omite por `c01f2282`.

## 11. Relación Silent Shooter/EFCS con el arranque temprano (Prioridad F)

1. La modificación vive en `av-cam.bin` (BIONZ, cuevas en `0x43541800/0x43541840`) y en `darwin_core.bin` (MCU). Se carga como archivo FAT de `nflasha3` por Loader3 y **se ejecuta después**; Loader3 lo lee sin interpretarlo.
2. No se alteró: Loader2/3, `partinf.conf`, RAMCFG, kernel, initrd, `Backup`, `kemco.txt`, ni encabezados leídos por Loader3. `av-cam.bin` conserva el tamaño (11 427 236 B) y la cadena FAT.
3. **Cadena hacia −302: no hay ruta demostrada** desde el contenido del selector/EFCS hasta un `−302`. Hay una ruta **del contenedor** (reescritura de `nflasha3`) que sí es nueva respecto a T024/T040 y que, si falla al leerse, daría `−302` vía `c01f4690`.
4. Distinción: error de construcción/empaquetado (no demostrado); de escritura (no verificable); de lectura de arranque (hipótesis H3); funcional del código personalizado (solo aplicable **después** de cargar `av-cam.bin`, fuera de `−302`).

## 12. Matriz de hipótesis

| H | Condición necesaria | A favor | En contra | −302 alcanzable | Offline | Incertidumbre | Próxima comprobación |
|---|---|---|---|---|---|---|---|
| H1 BOS | firma sector 0 ≠ `8246` | `edisx` puede reescribir | `partinf.conf` = 3.21; T024/T040 pasaron por el mismo flujo | sí | BOS histórico válido | estado físico | confirmar `edisx`/modo en logs (no existen) |
| H2 Backup/`nflasha2` | fallo de lectura/montaje | `ud_keep_backup` reescribe `Backup.bin` | RAMCFG igual en 55 copias; mismo flujo ya probado | sí (`c01f4690`) | copias válidas | `Backup.bin` real posterior no disponible | ninguna offline |
| **H3 TPZL/`nflasha3`** | LDEC/NAND no acepta residuo 256 o entrada > salida | **único cambio de contenido nuevo en un `nflasha3`**; atipicidades §8.4; −302 por `c01f4690` | Loader3 trata el residuo sin abortar; imágenes pasan | sí | pasa software | **hardware LDEC no verificado** | caso del decompresor LDEC de `lld.ko`/ARM7 con residuo ≠ 0 (§14) |
| H4 RAMCFG | entrada omitida/errónea | — | `c01f2282` nunca omite; 6 archivos presentes | sí (archivo ausente) | todos presentes en las 3 imágenes | ninguna adicional | — (cerrada offline) |
| H5 Proceso de actualización | escritura incompleta | «Done» sin verificación de lectura | mismo camino T024/T040 exitoso | indirecto | sin logs | modo `full`/`app` desconocido | sin logs: ninguna |
| H6 Código personalizado | ejecutado antes del fallo | — | se carga y ejecuta después de Loader3; sin ruta a `−302` | no | emulación E25-27 | solo aplicable post-carga | requiere hardware |

Orden por sustento: **H3 > H5 > H1/H2 > H4 (descartada como causa de omisión) > H6** (solo si el LED fuese de otra etapa; ver límite de R13: el −302 es compatible, no confirmado).

## 13. Pruebas ejecutadas

- `pytest tests/test_e26_r15_tpzl.py tests/test_e26_r14_ramcfg_bos.py tests/test_e26_tpzl.py`: **14 pasan**.
- `ruff check` / `ruff format --check` sobre los archivos nuevos: sin avisos (el repo tiene 22 avisos Ruff previos en `analysis/e26-recovery/`, no tocados). `mypy r15_tpzl_loader3.py`: sin avisos.
- Pendiente sin reconciliar: R14 cita 89 B de diferencia en `av-cam.bin`; E25-27 cita 111 B de diff BIONZ (20+58+rama/store). No se reanalizó; es discrepancia de recuento, no de contenido.

## 14. Matriz de evidencia y límites

| Afirmación | Tipo | Límite |
|---|---|---|
| 4/73 miembros difieren | SCRIPT | solo el paquete B |
| Loader3 tolera residuo | BINARIO | hardware LDEC no probado |
| `c01f2282` no omite | BINARIO + DATOS (55 BK4) | `Backup.bin` real posterior |
| T024/T040 exitosos con `nflasha3` oficial | DOC | el 3.25 puede haber usado otro modo |
| Qué se escribió en 3.25 (C) | **sin evidencia** | no hay logs |
| Texto de aviso de residuo | no legible | fuera del prefijo de 43 páginas |

## 15. Respuestas de cierre

**Q1.** SÍ: base 3.21 oficial + selector/C3-B/Darwin propios (E25-27, `71ab533d`). **Q2.** NO (inferido: BIONZ 111 B, Darwin 18 B, `nflasha3`; sin prueba de que no haya más, aunque 69 de 73 miembros son idénticos). **Q3.** NO: B localizado; C no. **Q4.** NO demostrable; solo el hash FDAT coincide con el aportado. **Q5.** SÍ (E25-27 más este informe). **Q6.** PARCIAL: registro, petición, residuo y cálculo de sectores sí; el hardware LDEC no. **Q7.** SÍ: desplazamiento de bloques contiguos, no relleno. **Q8.** SÍ (software de Loader3). **Q9.** NO demostrada; la atipicidad §8.4 queda como hipótesis. **Q10.** Parcial: flujo oficial 3.21, modo ejecutado no probado. **Q11.** SÍ: no omite. **Q12.** Tabla §10. **Q13.** NO hay evidencia de que lo afecten. **Q14.** H4 descartada como causa de omisión; H3 mejor sustentada (sin prueba). **Q15.** Análisis del decompresor LDEC (ARM7/`lld.ko`) con residuo y entrada > salida; ver qué hace `c01f7752`; reconciliar 89/111 B. **Q16.** Ver §17.

## 16. Decisión

**C — Construcción y TPZL validados** frente a las comprobaciones implementadas en software; el fallo físico sigue abierto. Resultado secundario **D** (RAMCFG: no hay omisión; 6 archivos en modo normal). No se declara A ni B: no hay incompatibilidad demostrada y la cámara no se ha tocado.

## 17. Recomendación para R16

Auditar la **ruta hardware de descompresión** (`lld.ko` `0x10e0c` → `boss_hw_arm7_comm_set_firmware_api_param` op `0x2800`; ARM7) buscando: (1) restricción de residuo ≠ 0; (2) límite de entrada ≥ 64 KiB. Si esa ruta acepta ambos, la causa más probable pasa a H5/H1 y exige evidencia física. Este informe no sustituye pruebas sobre la cámara; las pruebas sobre archivos no demuestran recuperación.
