# S66 (subtarea B) — Formato de los ficheros `/lens/VX*_lensfile.bin` y tabla de nombres en `av-cam.bin`

**Alcance:** reconstruir (solo estático, contra bytes reales) el formato binario de los 18
ficheros `VX*_lensfile.bin` de A6000 fw3.21, la tabla de nombres en `av-cam.bin` y el
código de lookup/parser, comparando con A6300 2.01 y A7S 3.20.

**Estado de los hechos:** VERIFICADO = comprobado contra bytes/instrucciones del blob
(Capstone `analysis/s58/tdis.py` con caché `analysis/s66/.cache`, verificación cruzada de
literales PC-relativas y del contenido de las tablas). INFERENCIA = lectura razonada.
NO_VERIFICADO = pendiente.

Artefactos: `analysis/s66/parse_lensfiles.py` (parser de los ficheros),
`analysis/s66/emit_lensfile_json.py` (emisor, regenerable),
`analysis/s66/lensfile_format.json` (datos completos: tablas, slots, sha256, tamaños).

---

## 1. Formato del fichero (VERIFICADO)

Cada fichero es una secuencia contigua **HDR(16 B) + ED + CS + LC + trailer(4 B)**. La
cadena de secciones acaba exactamente en `filesize - 4` en los **57/57** ficheros
(18 A6000 + 39 A6300), por lo que el trailer de 4 bytes es fijo al final.

```
0x00  u16  magic 'LF' (0x464c LE)        # comparado con literal 0x464c en 0x43907c7c
0x02  u16  header_len = 0x10             # consumido por el parser
0x04  u32  payload_size = filesize - 0x10 # coincide en los 57 ficheros
0x08  u32  0xB en 16/18 ficheros; VX9111=0xE, VX9116=0xC (semántica NO_VERIFICADA)
0x0c  u16  lens_id (0x9101..0x9129; coincide con el nombre del fichero)
0x0e  u16  0
```

Cada sección (seguidas sin hueco, en el orden ED → CS → LC):

```
+0x00 u16  magic: 'ED'=0x4445, 'CS'=0x5343, 'LC'=0x434c
+0x02 u16  hdr_len = 8
+0x04 u32  payload_len
+0x08      payload (payload_len bytes)
```

| Sección | Payload general | Tamaño (A6000) |
|---|---|---|
| ED | tabla de u16 (INFERENCIA: datos ópticos por lente) | `0x77c`–`0x32a4` (A6000) |
| CS | tabla de u16 (INFERENCIA: corrección/sombreado) | `0x38`–`0xc0` (A6000) |
| LC | 12 B fijos = 6 × u16 en **todos** los ficheros | `0xc` |

Trailer: 4 bytes (u32 final del fichero). **Algoritmo NO_VERIFICADO** — crc32/adler32/
suma/FNV-1a descartados empíricamente en la exploración previa (no coinciden).

Los «identificadores» per-lente son `lens_id@0x0c` y el trailer; **VX9103 y VX9123
difieren SOLO** en `lens_id@0x0c` (un byte: `0x03` vs `0x23`) y en un byte del trailer
(ev. checksum dependiente del id) — los datos ED+CS+LC son idénticos (INFERENCIA: misma
denominación óptica para dos variantes de nombre).

### Inventario A6000 fw3.21 (`0800_appli/lens/`, 18 ficheros)

| Fichero | bytes | lens_id | ED | CS | LC | sha256[8] |
|---|---|---|---|---|---|---|
| VX9101 | 6180 | 0x9101 | 0x1740 | 0xac | 0xc | f03bd985 |
| VX9102 | 4984 | 0x9102 | 0x12cc | 0x74 | 0xc | d8a6fdb1 |
| VX9103 | 13212 | 0x9103 | 0x32a4 | 0xc0 | 0xc | 1f842ae1 |
| VX9104 | 2064 | 0x9104 | 0x77c | 0x5c | 0xc | 428bbf78 |
| VX9105 | 2600 | 0x9105 | 0x998 | 0x58 | 0xc | afaf63fd |
| VX9106 | 3020 | 0x9106 | 0xb3c | 0x58 | 0xc | 0a842639 |
| VX9107 | 5504 | 0x9107 | 0x14b4 | 0x94 | 0xc | dde4edd2 |
| VX9108 | 2140 | 0x9108 | 0x7bc | 0x68 | 0xc | 544125b2 |
| VX9109 | 6660 | 0x9109 | 0x1914 | 0xb8 | 0xc | f698adf2 |
| VX9110 | 2160 | 0x9110 | 0x800 | 0x38 | 0xc | e33024b8 |
| VX9111 | 5956 | 0x9111 | 0x1674 | 0x98 | 0xc | 46323b86 |
| VX9113 | 9028 | 0x9113 | 0x227c | 0x90 | 0xc | 631fb3e4 |
| VX9114 | 2164 | 0x9114 | 0x800 | 0x3c | 0xc | 612de5de |
| VX9115 | 2576 | 0x9115 | 0x998 | 0x40 | 0xc | 06e88955 |
| VX9116 | 12200 | 0x9116 | 0x2eb0 | 0xc0 | 0xc | 8b774bca |
| VX9123 | 13212 | 0x9123 | 0x32a4 | 0xc0 | 0xc | 3f4e19ef |
| VX9124 | 2584 | 0x9124 | 0x998 | 0x48 | 0xc | 9070d6a3 |
| VX9129 | 11908 | 0x9129 | 0x2d90 | 0xbc | 0xc | 423e2bc9 |

---

## 2. Tabla de nombres en `av-cam.bin` A6000 (VERIFICADO)

| Elemento | Valor |
|---|---|
| Tabla base | VA **0x43C22BF2** = fileoff **0x6E1BF2** (base de carga 0x43541000, verificada por sesiones previas) |
| Entradas | 18 (límite del bucle: `cmp r2, #0x12` en `0x43907be6`) |
| Stride | `0x42` (66 B) |
| Layout | `[u16 key][64 bytes NUL-padded con '/lens/VX91xx_lensfile.bin']` |
| Claves | `0x8011, 0x8012, … 0x802d` (18 valores NO consecutivos: faltan `0x801c`, `0x8021–0x8026`, `0x8029–0x802c`) |

**Función de lookup `0x43907bc4`** (única que referencia la tabla; llamada desde
`0x43b2a846` con `bl`). Desensamblado verificado (Capstone/tdis):

```
43907bc4 cmp r0, #1             ; contrato del llamador: r0 != 1 ➜ devuelve 0
43907bc8 bne #0x43907bee        ; (si no, devuelve 0)
43907bca subs r0, #1
43907bcc mov r2, r0
43907bce ldr r3, [pc, #0x24]    ; lit ➜ tabla
43907bd0 add r3, pc             ; r3 = 0x43541000+0x6E1BF2 = 0x43C22BF2
43907bd2 ldrh r4, [r3, r0]      ; r0 = 0x42*(k): clave del slot k
43907bd4 cmp r4, r1             ; comparación con el id pedido
43907bd6 bne #0x43907be2
43907bd8 movs r0, #0x42
43907bda mla r3, r0, r2, r3     ; r3 = base + 0x42*k
43907bde adds r0, r3, #2        ; devuelve &path[k] (offset +2)
43907be0 pop {r4, pc}
43907be2 adds r2, #1            ; incremento del índice de slots
43907be4 adds r0, #0x42         ; siguiente clave (stride)
43907be6 cmp r2, #0x12          ; límite = 18 slots
```

**Cadena de llamadores** (reconstruida Capstone en la subtarea; el enlace
`0x43b2a846 → bl 0x43907bc4` se re-verificó en este informe):
`0x43907BC4 ← 0x43B2A7E2/0x43B2A846 ← 0x43904FB0 ← 0x43B2CACC ← 0x43902FBC ←
0x43721B34 ← 0x436E1328`. El resultado del lookup (puntero a `'/lens/VX91xx...'`)
se almacena en `r5+8` (`str r0, [r5, #8]`, `0x43b2a84a`) y un resultado 0 indica
«no encontrado».

---

## 3. Parser/cargador en `av-cam.bin` (VERIFICADO)

**Función principal de parseo `0x43907c7c`**: máquina de estados con `tbh` sobre
`[r0]` (5 casos). Copia los primeros 12 bytes de la cabecera a `r4+0xc`
(`movs r2, #0xc; blx 0x439c5320`), compara el magic `0x464c` (`0x43907ce0`),
comprueba `header_len@0x02` (`ldrh` sobre `r4+0xe`, `cbz` → error) y usa
`u32@4` (`r4+0x10`, `cbnz` → estado 1). Pasa a
**setup de la sección ED `0x43907f54`** (`bl` en `0x43907d98`), llama al **lector TLV
`0x43b2bf88`** (`bl` en `0x43907dae`) y sirve errores con logs (`0x439041ec`,
formato/prefijo `Lens`), entre ellos el literal en `0x43c9ae7e` vía `0x43721624`.

Los literales PC-relativos citados arriba se verificaron resolviendo cada
`ldr [pc,…]` + `add r3, pc` contra los bytes reales del blob; la base
0x43C22BF2 coincide con contenido (claves `0x8011..0x802d` y paths).

---

## 4. Comparación con A6300 2.01 (VERIFICADO, fileoff; base de carga NO_VERIFICADA)

**El formato del fichero se repite** y los **18 ficheros A6000 son byte a
byte idénticos** a sus homónimos en A6300 (sha256 iguales). Además A6300 incluye 21
ficheros más (VX8903…VX9202) → 39 ficheros. **Nota sobre el campo:** `payload = filesize
- 0x10` también en A6300 (validado fichero a fichero).

**Tabla(s) de nombres en `av-cam.bin` A6300**, verificado con Capstone (bases como
fileoff; el pool es PIC y su VA de carga NO_VERIFICADO):

| Sub-tabla | Base/fileoff | Slots | Claves | Bucle |
|---|---|---|---|---|
| A | `0x7C826A` | 18 | `0x8011..0x802d` (paths VX9101..VX9129) | `0x44c10e`–`0x44c11e`, límite `cmp r2, #0x12` |
| (fijo) | `0x7C870E` | 1 | clave `0xFFFF` (`0x44c122`: `movw r3, #0xffff; cmp r1, r3`) | path `'/lens/fixed_lensfile.bin'` en `0x7C8710` (**fichero ABSENTE** en el dir `lens/` de A6300) |
| B | `0x7C8750` | 22 | `0x20..0x46` (paths VX8903…VX9202) | `0x44c130`–`0x44c14a`, límite `cmp r2, #0x16` |

Total de slots referenciables = **41** (18 + fixed + 22). El único path duplicado es
`VX8905` (claves `0x35` y `0x45`). El patrón del bucle es el MISMO (cmp r4,r1 →
`mla r0, r0, r2, r3` → `adds r0, #2`), solo cambia el límite de recuento.

Claves de A6300: en la tabla A son idénticas a las de A6000 (`0x8011..0x802d`); en la
tabla B van de `0x20` a `0x46`. La **semántica de las claves NO_VERIFICADA**.

**A7S 3.20: ABSENTE.** 0 hits de `'/lens/'`, `'lensfile'`, `'VX9'` y del patrón
`(movs r0,#0x42; mla … r2,r3)` en su `av-cam.bin`; su firmware tampoco contiene un
directorio `lens/`. Es una función exclusiva del subsistema de montura E de A6000/A6300.

---

## 5. Semántica de los datos (INFERENCIA / NO_VERIFICADO)

- Los payloads de ED y CS son tablas de u16; el tamaño de ED se correlaciona
  aproximadamente con la "lente más compleja" (VX9103/VX9123 ≈ 4×VX9104). La
  semántica de cada palabra **NO_VERIFICADA** (candidatos plausibles: datos ópticos,
  sombreado, correcciones internas por distancia focal).
- `u32@8` varía (0xB, VX9111=0xE, VX9116=0xC): **NO_VERIFICADO** (sugerido como
  versión o número de bloques).
- Claves `0x8011..` vs `0x9101..`: 2 espacios de nombres distintos (clave de tabla vs
  id del fichero); NO mapeados explícitamente por código visible.
- El trailer (4 B) cambia con el contenido; su algoritmo **NO_VERIFICADO**.
- EN S66-D ya se identificó `Camera::Lens::ODL::Load` (`0x43721b9c`, con
  `AsyncSend`/`AsyncRecieve`) como consumidor de estos ficheros desde fuera del
  bloque: ver `analysis/s66/lens_power_attach.md`.

## 6. Pendiente (NO_VERIFICADO)

1. Semántica de ED/CS/LC (mapear offsets → campos ópticos).
2. Algoritmo del trailer de 4 bytes.
3. Base de carga/VA de `av-cam.bin` A6300 (las direcciones de su lógica de lookup son
   fileoff sobre el blob: el pool es PIC y el VA de carga NO_VERIFICADO).
4. Origen de las claves `0x8011..` (ev. id del lente montado consumido por
   `Camera::Lens::ODL::Load`).

---

Regenerar datos: `.venv/bin/python analysis/s66/emit_lensfile_json.py` (lee los
ficheros originales y vuelca todas las tablas en `lensfile_format.json`).
