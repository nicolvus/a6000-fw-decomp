# E26-R16 — Auditoría de la ruta LDEC/BOSS/ARM7 del TPZL personalizado 3.25

Fecha: 30-10-2026. Continúa [R15](e26-r15-tpzl-custom-fw325.md) (`e5368824`, presente en `main`). **Solo análisis estático y lectura de archivos existentes.** Sin cámara, sin USB/UART, sin imágenes instaladoras, sin escribir NAND. `camera-dumps` y `exp2-session-log.jsonl` no se tocaron.

Etiquetas: **BINARIO** = desensamblado de `bootloader.bin` (Loader3 `0xc01f0000`, prefijo de 43 páginas; BossFirm = `bootloader.bin[0x18800:+0x3800]`, SHA `b70a89a0…`) · **DATOS** = leído de imágenes · **SCRIPT** = salida de un script de este informe · **INFERENCIA** · **NO VERIFICADO**.

Código: [`r16_dis.py`](../../analysis/e26-recovery/r16_dis.py), [`r16_xref.py`](../../analysis/e26-recovery/r16_xref.py), [`r16_callgraph.py`](../../analysis/e26-recovery/r16_callgraph.py) (Loader3), [`r16_arm7.py`](../../analysis/e26-recovery/r16_arm7.py) (BossFirm) · [`r16_lz_features.py`](../../analysis/e26-recovery/r16_lz_features.py) → `r16-lz-features.json`, `r16-segment-structure.json` · [`r16_tpzl_corpus.py`](../../analysis/e26-recovery/r16_tpzl_corpus.py) → `r16-tpzl-corpus.json` · [`r16_avcam_reconcile.py`](../../analysis/e26-recovery/r16_avcam_reconcile.py) → `r16-avcam-reconcile.json` · [`tests/test_e26_r16_ldec.py`](../../tests/test_e26_r16_ldec.py) (6 pruebas; las que leen firmware se omiten si falta).

## 1. Resumen ejecutivo

1. **BINARIO. El descompresor TPZL de Loader3 no es software de Loader3.** El prefijo analizable no contiene decodificador LZ (ningún literal `0xf29030xx`, ninguna tabla de longitudes 3..16/32/64). `c01fdd8e` arma un *trabajo* y lo envía por `c01fce8c` a la pila MuMin enlazada en Loader3 (cadenas «mumin ldec error», «ldec tulist initilization failed»), que escribe en la SRAM del ARM7 (`+0x3f40`). El ARM7 (BossFirm) programa el LDEC (`0xf2903000`). Es la misma cadena que usa Linux.
2. **DATOS (nuevo, discriminante).** En las **6 imágenes TPZL de Sony** disponibles (3.21 oficial, α7S 3.20, α6300 2.01, y `nflasha7`/`nflasha15` volcadas de esta cámara el 20-10) **todos** los bloques (≈ 6 200) constan de **exactamente 16 segmentos LZ/raw de 4096 B de salida**, cada uno con su terminador. Loader3 pasa al ARM7 `tamaño_bloque >> 12 = 16` y el ARM7 lo escribe en el registro LDEC `0xf290300c`. **Los bloques 0, 48 y 57 del 3.25 son el único caso del corpus con 1 segmento de 65 536 B.** Es una diferencia real y universal, no explicada en R15. **No se demuestra** que el LDEC la rechace (semántica del registro desconocida).
3. **DATOS + BINARIO. 73 984 B no es un límite demostrado.** Las propias imágenes de Sony contienen bloques de **129 sectores** (raw, 66 048 B; 162 y 68 en `nflasha15/16` de la cámara), que Linux lee por el mismo ARM7. El ARM7 trocea por lotes de `0x80` unidades (`0x1130`); 145 sectores requiere un único envolvimiento, como 129. El mayor bloque con residuo ≠ 0 o > 129 sectores **no existe en el corpus de Sony**.
4. **BINARIO. Residuo:** sin consumidor encontrado en el ARM7 analizado, y sin ninguna rama de rechazo. No se prueba que se descarte (límite §5).
5. **BINARIO. −302 es un colector:** `c01f4690` convierte *cualquier* error no nulo de `c01f2c2a` en −302. No se prueba un fallo LDEC real en la cámara.
6. **BINARIO. `c01f7752` resuelto:** no carga archivos; solo conmuta el bit 2 de un byte de configuración. Sus errores son −205/−206/3, nunca −302.
7. **DATOS. 89/111 conciliado:** 89 B BIONZ (28 selector + 61 C3-B, todos dentro de los parches; 92 B escritos, 3 sin cambio de valor) **+ 22 B Darwin** = 111. E25-27 §ejecutivo rotula 111 como «BIONZ»: era el total del manifiesto.
8. **Tests de conocimiento:** los 2 fallos se reproducen en una línea base limpia desde `a8a182c9` (R7); R15 no los introdujo (§12).
9. **Decisión: C** — diferencia real entre artefactos (estructura de segmentos del TPZL 3.25) no explicada por R15; **no A**: no hay rechazo demostrado.

## 2. Estado heredado de R15

R15: Loader3 acepta residuo ≠ 0 (aviso), las tres imágenes pasan las comprobaciones de software; el 3.25 es el 3.21 + `nflasha3`/`darwin` propios; lo escrito en la cámara (C) y su estado actual son desconocidos. Se mantiene todo. Correcciones a R15: (i) Darwin difiere en **22 B**, no 18; (ii) «111 B de BIONZ» → 89 B (§11).

## 3. Arquitectura LDEC / BOSS / ARM7

| Capa | Función / dirección | Qué hace | Tipo |
|---|---|---|---|
| Lectura FAT | `c01f4690`→`c01f2c2a` | tipo 3 (TPZL): `c01f9a66/90` abre; `c01f9bd0`→`c01f9b10` | BINARIO (R15) |
| Dispositivo TPZL | `c01fe118` → `c01fe006` | `c01fe118` **reintenta 4 veces** (r4 = 3..0, `c01fe12c`–`c01fe14a`); `c01fe006` pide cada bloque | BINARIO |
| Petición de bloque | `c01fdd8e` | caché por bloque; calcula residuo/sectores; `c01fdbe0` arma lista; `c01fce8c` envía | BINARIO |
| Lista de transferencia | `c01fdbe0` | divide `[sector, sector+n)` en entradas de 12 B `{ptr, inicio, nº sectores}` por página NAND | BINARIO |
| Cola/envío | `c01fce8c`→`c01fccd2` | copia el trabajo (0x18 B) a un buffer alineado a 32 B; `c01fc4f8` guarda el puntero en SRAM `+0x3f40+0x24` | BINARIO |
| Espera | `c01fcf70` (máscara `0x3000000`) | códigos −0x20005 / −0x20006 / −0x20001 | BINARIO |
| ARM7 despacho | tabla `0x379c`, `0x0ec8` | índice 0 → `0x1338` (solicitud LDEC) | R7b |
| ARM7 LDEC | `0x1338`, `0x3f4`, `0x1130`, `0x1688`, `0x1738` | ver §6–7 | BINARIO |
| Registros | `0xf2903000` (+0x0c, +0x10, +0x28..+0x30), tulist `+0x2068` | escritos por el ARM7 | BINARIO |

**Separación del comando `0x2800`.** `lld.ko` `boss_hw_arm7_comm_set_firmware_api_param(…,0x2800)` y `c003333a(6,0x2800,…)` de Loader2 pertenecen a la lectura NAND/firmware **antes de Linux** (R7b). La ruta de este informe es otra: `c01fdd8e`/`c01fbd78` → `c01fce8c` → SRAM `+0x3f40`, op índice 0. **No hay referencia cruzada verificada entre ambas**; `0x2800` se excluye del grafo de descompresión. (Que ambas viajen por el mismo buzón SRAM `+0x3f40` no las identifica.)

## 4. Grafo de datos (solicitud → bytes descomprimidos)

```
c01f2c2a ─ c01f9bd0/c01f9b10 (alineación lógica dev[0x20]) ─ ops[] ─ c01fe118 (4 intentos)
  └ c01fe006(bloque i < entradas)
      └ c01fdd8e: off=TOC[i], tam=TOC[i+4], res=off&0x1ff, sect0=base+(off>>9), n=(res+tam+0x1ff)>>9
          ├ c01fdbe0 → lista {ptr,inicio,n} (12 B/entrada)
          └ trabajo = {cuenta, lista, res, tam_bloque>>12, dev, tam_bloque}  (0x18 B)  → c01fce8c
c01fccd2: copia → SRAM ARM7 +0x3f40 (puntero a trabajo en +0x3f54)
ARM7 0x1338: r7=trabajo; 0x3f4: [0xf290300c]=trabajo+0xc (=16), [0xf2903010]=trabajo+0x10
             por entrada → 0x1130 (lotes de ≤0x80) → 0x1688/0x1738 → tulist (0xf2903000+0x2068)
LDEC → buffer destino → c01fe598/c01fdf26 (consolidación) → bytes al lector FAT
```

BINARIO: `c01fddf6`–`c01fde4a` (campos del trabajo), `c01fccd2` `movs r2,#0x18`, ARM7 `0x3f4` `ldr r3,[r0,#0xc]`/`ldr r0,[r0,#0x10]`. `c01fbd78` (lectura MuMin genérica) construye el **mismo** trabajo con residuo **0** fijo (`strd r8,r1,[sp,#0xc]`, r8 = 0). El camino con residuo solo existe para TPZL.

## 5. Seguimiento del residuo de 256 B

| Etapa | Función | Campo | L/E | Transformación | Evidencia |
|---|---|---|---|---|---|
| 1 | `c01fdd8e` | TOC offset | L | `res = off & 0x1ff` (`ubfx r0,sb,#0,#9`, `c01fddf6`) | BINARIO |
| 2 | ídem | `[sp]`,`[sp+0xc]` | E | aviso si ≠ 0 (`c01fde00`); `[sp+0xc]` = trabajo+8 | BINARIO |
| 3 | ídem | sectores | — | `n=(res+tam+0x1ff)>>9`, `sect0=base+(off>>9)` → lista | BINARIO |
| 4 | `c01fdf26/5a` | TOC | L | segundo recorrido, mismo aviso y fórmula | BINARIO |
| 5 | `c01fccd2` | trabajo+8 | L/E | copiado con los 0x18 B al buffer del ARM7 | BINARIO |
| 6 | ARM7 `0x1338`/`0x3f4` | trabajo+0,+4,+0xc,+0x10 | L | **+8 no se lee** | BINARIO |
| 7 | ARM7 `0x1130`/`0x1688`/`0x1738` | entradas de 12 B; geometría `dev[+8]/[+0x18]` | L | trabajan en sectores completos; sin acceso a trabajo+8 | BINARIO |
| 8 | LDEC (`0xf2903000`) | — | — | **NO VERIFICADO** | — |

Respuestas: (1) trabajo+8; (2) en Loader3 solo el aviso y la copia; (3–4) copiado, no consumido en las funciones analizadas; (5) el desplazamiento sí se refleja en el *inicio y número de sectores* (sector de inicio = `off>>9`; un sector extra); no hay DMA con el residuo en bytes visible; (6–7) sin máscara ni descarte de bytes iniciales visible; (8) la longitud efectiva enviada es `n·512`, incluye `res`; (9) **no se encontró** rama de error por desalineación. **Límite honesto:** no se rastreó *todo* el ARM7 en busca de lectores indirectos de trabajo+8 (el escaneo por patrón `mov rX,#0x3f40` no encontró candidatos; la verificación completa necesita desensamblado total con flujo de datos). Si los primeros `res` bytes se ignoran, el LDEC leería el flujo desde el *inicio del sector*, es decir, con 256 B de datos del bloque anterior delante: **de ser así, TODOS los bloques con residuo ≠ 0 se corromperían** — el residuo existe en el diseño de Sony y Loader3 lo avisa, lo que sugiere que el hardware lo contempla, pero el corpus de Sony tiene residuo 0 en el 100 % de las entradas.

## 6. Límites de entrada y salida

| Propiedad | Evidencia | Valor |
|---|---|---|
| Salida por trabajo | trabajo+0xc = `(1<<shift)>>12`; shift ≤ 0x11 (`c01fe518`) | 16 (shift 16); máx. 32 |
| Unidades por lote | ARM7 `0x1130`: `cmp r0,#0x80` | **0x80** entradas/sectores por lote; al llenarlo reinicia `[r5+8]`, `[r5+0xc]` (= tulist `+0x2068`) y sigue (`0x12e8`–`0x1320`) |
| Capacidad de descriptores | `c01fe632` | ≥ 256 KiB (R15) |
| Entrada máxima | ningún campo de 16 bits hallado en `c01fdbe0`/`0x1130` | no se halló límite de 64 KiB |
| Corpus Sony | `r16-tpzl-corpus.json` | máx. 129 sectores (66 048 B), 162 y 68 bloques > 128 en `nflasha15/16` |
| 3.25 integrado | idem | 145 sectores (73 984 B), 3 bloques > 128 |

INFERENCIA: 129 y 145 sectores atraviesan la misma lógica de envolvimiento (128 + resto). Linux ejecuta el caso 129 en esta cámara (lectura de `nflasha15/16`), por lo que el envolvimiento está ejercido en hardware real; 145 solo exige un resto mayor (17 frente a 1). **NO VERIFICADO:** que el LDEC drene el tulist antes de la reutilización (`0x1130` no espera; las llamadas `0x81c/0x784/0x8ac` no se trazaron).

## 7. Comparación a nivel de trabajo (bloque 0)

| Propiedad | Sony 3.21 | Integrado 3.25 |
|---|---|---|
| Longitud comprimida | 26 015 B (bloque 0) | 73 984 B (alineada; 73 732 de datos) |
| Longitud descomprimida | 65 536 | 65 536 |
| Residuo | 0 | 256 |
| Sectores solicitados | 51 | 145 |
| Segmentos por bloque (trabajo+0xc = 16) | **16 × 4096 B** | **1 × 65 536 B** |
| Terminadores `bd==0` | 16 | 1 |
| Grupos `flags==0` (8 literales) | 1 337 | 8 192 |
| Tamaño de descriptor | 12 B/entrada, ≥ 1 por página | ídem |
| Límite documentado | ninguno hallado; lote 0x80 | ídem |
| Resultado estático | pasa | pasa |

DATOS (`r16-lz-features.json`, `r16-segment-structure.json`): en Sony, 319 103 grupos `flags==0` y 5 851 segmentos LZ (más 53 raw) en 369 bloques; los bloques 0/48/57 reconstruidos son los **únicos** con `segmentos ≠ 16`. Los 366 restantes del 3.25 son idénticos a los oficiales. **Condiciones verificables que distinguen las imágenes:** (a) residuo 256; (b) 145 sectores; (c) **estructura de 1 segmento frente a 16**. Solo (c) contradice una propiedad **uniforme** del corpus y coincide con un parámetro que el ARM7 escribe en hardware.

Pregunta abierta de (c): el LDEC podría contar terminadores/segmentos de 4 KiB (16 = `trabajo+0xc`) o limitarse a decodificar hasta producir los bytes; ninguna fuente disponible (sin datasheet) lo decide. Un único segmento válido para el decodificador de software (`fwtool`, `tpzl.py`) y para Loader3 no prueba nada sobre el LDEC.

## 8. Propagación de errores hasta −302

| Etapa | Salida | Evidencia |
|---|---|---|
| `c01fdbe0` sin lista / `c01ffb6a` ≠ 0 | −1 | `c01fdc2c`, `c01fdf18` |
| `c01fce8c` | −0x20001 (sin memoria/estado), otro ≠ 0 | `c01fce8c`, `c01fcf0c` |
| `c01fcf70` (espera, máscara `0x3000000`) | −0x20005, −0x20006, ≥ 0 | `c01fe0b6`–`c01fe0d6` |
| `c01fe006` | `sxtb(r7)`; si −0x20006 llama a `c01fdf26` y al final `c01fe4cc` (aviso) | `c01fe0c8`–`c01fe0ea`, `c01fe114` |
| `c01fe118` | **4 intentos**; devuelve el último ≠ 0 | `c01fe12c`–`c01fe14e` |
| `c01f9b10` | −0x16 si `offset & (align−1)` | `c01f9b2a`–`c01f9b3c` |
| `c01f2c2a` | ≤ 0 → −5; fallo de apertura → ese código | `c01f2c84`–`c01f2c88` |
| `c01f4690` | **cualquier ≠ 0 → −302** | `c01f469e`–`c01f46a4` |

Hechos: se reintenta (4 intentos) y no se sustituye el bloque; no hay información parcial utilizable (el éxito exige longitud > 0, `c01f2c84`); `−302` pierde la causa. Un bloque estructuralmente válido **sí puede** fallar por parámetros de hardware (estados −0x2000x del ARM7 llegan por `c01fcf70`). **Ruta verificada por software:** cualquier fallo del contenedor → −302. **Dependiente de hardware:** si el LDEC produce ese fallo con el TPZL 3.25. Sin evidencia de ejecución real, **no se afirma** que la cámara sufriera un error LDEC. El patrón LED sigue siendo compatible con −302, no confirmado (R13).

## 9. `c01f7752`

BINARIO: es la 2.ª instrucción de `c01f7746`: si `c01f159a() ≠ 0` (modo actualizador/variable de arranque) devuelve 0; si no, `skip = c01f2282()` y tail-call a `c01f7652(r0=[lit], r1=[lit], skip)`. `c01f7652` realiza configuración de hardware/energía (mensajes `c01f3670`, escrituras con `c01f3708(7,…)`, `0x290`, `c01f7784`) y **solo usa `skip` para fijar/borrar el bit 2 de un byte de configuración** (`c01f771a`–`c01f7726`). `c01f7746` se invoca desde `c01f59ae` (`c01f5a02`), que despacha por tipo de producto `[0xc00e0060+0x34]` (5, 4 o 7); sus errores se devuelven como −205/−206 (`c01f59ba`, `c01f5a26`) o código 3.
Comparación con `c01f307c`: allí `c01f2282` **omite** una entrada RAMCFG (archivo); aquí solo modifica un bit. Con `c01f2282 = 0` (55/55 BK4) el bit 2 queda borrado. **No carga archivos ni produce −302.** Dependencia RAMCFG: solo por `c01f2282`/Backup `0xfa0033`.

## 10. Hardware: lo que sigue sin comprobarse

Registros LDEC (0x0c = nº de segmentos de 4 KiB, 0x10 = campo no identificado, 0x28/0x2c/0x30 = constantes 0x7b/4/0x7b), semántica del terminador por segmento, reutilización del tulist, tratamiento del residuo en silicio. No hay datasheet; la búsqueda documental pública no se ejecutó (sin acceso a fuentes técnicas verificables en el repo; el dato público conocido de la serie —fwtool/LZPT— describe el formato, no el LDEC) y no se extrapola a otras generaciones BIONZ.

## 11. Conciliación 89/111 B (`av-cam.bin`)

SHA-256: original `b60c845c…56bb9`; integrado (E25-27) y extraído de `nflasha3.integrated.bin` y del `firmware.integrated.tar`: **`45a5ab35…5190e`** (idénticos, 11 427 236 B). `nflasha3` del artefacto y del tar: `bb9ce25a…d546c` (idénticos).

| Offset | Longitud parcheada | Bytes distintos | Componente | Evidencia |
|---|---|---|---|---|
| `0x30033e` | 4 | 4 | selector `bne.w`→NOP | SCRIPT |
| `0x300342` | 4 | 3 | selector `bl` cueva (1 byte coincide) | SCRIPT |
| `0x300476` | 2 | 2 | selector store→NOP | SCRIPT |
| `0x000800` | 20 | 19 | cueva selector | SCRIPT |
| `0x3872fe` | 4 | 4 | C3-B gancho `bl` | SCRIPT |
| `0x000840` | 58 | 57 | cueva C3-B | SCRIPT |
| **BIONZ** | **92** | **89** | — | 7 intervalos contiguos |
| Darwin | — | **22** | `darwin_core` | SCRIPT |

El manifiesto E25-27 (`diff_count`): selector 28, C3-B 61, Darwin 22, total **111** = 28 + 61 + 22. Es decir, **R14 tenía razón (89 B BIONZ)** y E25-27 sumaba Darwin; no hay diferencia sin explicar. Explicación de «escritos 92 / distintos 89»: tres bytes parcheados coinciden con el valor original (0 en la cueva, un byte de `bl`).

## 12. Auditoría de `tests/knowledge`

- Nombres: `test_every_open_question_is_triaged` y `test_current_index_matches_full_citations_contexts_and_relation_types` (`tests/knowledge/test_open_questions_triage.py`).
- Causa: `analysis/s400_open_questions_triage/triage.json` (último cambio `a432e3ee`, R7b) no contiene las filas de `docs/PENDIENTES.md`/`OPEN-QUESTIONS.md` añadidas después (CORRECTS/«pendiente» de R8–R15).
- Línea base reproducible: *worktree* limpios en cada commit de `a432e3ee..e5368824`: el fallo aparece en **`a8a182c9` (R7 completo)** y se mantiene hasta `e5368824`. R15 no lo introdujo; la deriva se acumula desde R7.
- Entorno: con el Python del sistema falla la recolección (`ModuleNotFoundError: mcp`); con `.venv/bin/python`, **77 pasan, 2 fallan**. En un *worktree* limpio fallan además 2 por datos no versionados (`test_s32_rectification_uses_original_firmware_bytes` necesita `firmware/…/av-cam.bin`; `test_call_tool_with_invalid_input_does_not_crash_server` necesita `.knowledge-cache` sqlite).
- Corrección aplicada: `extend_triage.py` añadió las filas nuevas a `triage.json` (como `VIGENTE`, pendientes de revisión manual); los tests no se modificaron; `tests/knowledge`: 79 pasan.

## 13. Pruebas y evidencia de binario

`pytest tests/test_e26_r16_ldec.py tests/test_e26_r15_tpzl.py tests/test_e26_r14_ramcfg_bos.py tests/test_e26_tpzl.py`: 20 pasan. Ruff y mypy sobre los archivos nuevos: sin avisos. **SINTÉTICO:** `test_synthetic_segment_walk` (bloques fabricados) prueba el recorrido de tokens, no el LDEC. Ninguna prueba demuestra compatibilidad física. Hashes: `bootloader.bin` `eb420385…a327f`, BossFirm `b70a89a0…`, `nflasha3` oficial/integrado, `av-cam` (§11); todos los hashes y recuentos por imagen del corpus están en `r16-tpzl-corpus.json`.

## 14. Hipótesis revisadas

| H | Estado tras R16 |
|---|---|
| H3 TPZL/LDEC | **Sigue siendo la mejor sustentada**, ahora con un discriminante concreto: estructura 1×64 KiB frente a 16×4 KiB (y residuo 256). Sin prueba de rechazo. Bloques > 128 sectores: **debilitada como causa** (129 sectores funcionan en la cámara). |
| H4 RAMCFG | cerrada; `c01f7752` no carga archivos |
| H1 BOS / H2 Backup / H5 proceso | sin cambios (sin evidencia física) |
| H6 código personalizado | sin ruta a −302 |

## 15. Decisión y trazabilidad

**C — Inconsistencia del paquete demostrada:** la estructura de segmentos de los bloques 0/48/57 del TPZL 3.25 difiere de la de **todo** el corpus de Sony y coincide con un parámetro del trabajo (`size>>12`) que el ARM7 escribe en hardware; R15 no la había identificado. No se elige A: no hay condición que *rechace* el bloque. No se elige B: sí aparece una diferencia verificable. Restricciones respetadas: sin artefactos instalables ni payloads (los scripts solo analizan).

## 16. Respuestas

**Q1.** SÍ para la cadena de software (Loader3 `c01fdd8e`→MuMin→ARM7 `0x1338`→LDEC `0xf2903000`); NO para el silicio. **Q2.** SÍ hasta `c01fccd2`/ARM7 `0x3f4` (el campo se copia, no se lee); falta el LDEC y un desensamblado ARM7 completo. **Q3.** NO. **Q4.** NO (129 sectores funcionan; no hay límite de 64 KiB hallado). **Q5.** PARCIAL: lote 0x80 y capacidad ≥ 256 KiB verificados; semántica de registros no. **Q6.** SÍ por software (todo error → −302); NO la existencia de un fallo LDEC real. **Q7.** SÍ una diferencia (1×64 KiB frente a 16×4 KiB, uniforme en Sony); NO una violación demostrada. **Q8.** SÍ. **Q9.** SÍ (89 + 22 = 111). **Q10.** SÍ (§12): deriva de `triage.json` desde R7, corregida. **Q11.** Sustentada: H3 (por el discriminante); debilitado el argumento «>64 KiB»; descartada H4; H1/H2/H5 sin cambios. **Q12.** Ver §17.

## 17. Recomendación para R17

Offline y decisiva: **desensamblar y trazar completo el ARM7** (flujo de datos desde `[0x3f54]`, `0x81c/0x784/0x8ac`, ISR `0x4d8`) buscando (a) cualquier lector de trabajo+8, (b) cómo se usa trabajo+0xc (segmentos) y si el número de terminadores se contrasta con él, (c) drenado del tulist al envolver. Complemento: ¿hay algún TPZL de Sony con un bloque de un solo segmento de 64 KiB (otras generaciones, `nflasha*` de α7 II, firmware de lentes)? Si existe, C pierde fuerza. Sin hardware no se puede cerrar más.

Límites: no se analizó el cuerpo de Loader3 fuera del prefijo de 43 páginas; el desensamblado ARM7 cubre solo funciones citadas; el texto del aviso de residuo no es legible; el estado físico de la NAND y lo escrito realmente (C) siguen sin evidencia.
