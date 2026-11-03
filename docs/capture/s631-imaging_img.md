# S631 — `[IMAGING_IMG]`: evidencia de cadenas y rutas de guarda

**03-11-2026.** Cierra la etiqueta `[IMAGING_IMG]` y amplía la primera versión con llamadores y estructura de `Image`, la última pendiente de la familia IMAGING del censo S178. La presencia de texto y de cargas de dirección no demuestra la semántica de `Image` ni relación con la captura electrónica.

Datos: [imaging_img.json](../../analysis/s631_imaging_img/imaging_img.json). Verificador: `analysis/s631_imaging_img/verify_imaging_img.py` (lee `av-cam.bin`, base `0x43541000`, A6000 fw3.21; desensambla Thumb con capstone). Prueba: [test_s631_imaging_img.py](../../tests/test_s631_imaging_img.py).

## Evidencia comprobada

7 cadenas, todas con el prefijo `[IMAGING_IMG]: `, y 12 pares `ldr rX,[pc,#imm]` + `add rX,pc` que resuelven exactamente a ellas (coinciden con las 12 referencias PIC de [pendientes_auditados.json](../../analysis/s178_census/pendientes_auditados.json)).

| Cadena | Dirección | Cargas |
|---|---|---|
| `Image::Clone Image NULL %d` | `0x43cb4355` | 1 |
| `Image::Clone ImageParam NULL %d` | `0x43cb43a1` | 1 |
| `Image::Branch Image NULL %d` | `0x43cb43d0` | 1 |
| `Image::Branch ImageParam NULL %d` | `0x43cb43fb` | 1 |
| `Image::Create Image NULL %d` | `0x43cb442b` | 1 |
| `Image::Create ImageParam NULL %d` | `0x43cb4456` | 1 |
| `Image NULL log end` | `0x43cb437f` | 6 |

Tres funciones Thumb (cada una abre con `push.w` y contiene 4 de las 12 cargas): `0x4381ba9c` (Clone), `0x4381bbf0` (Branch) y `0x4381bd4c` (Create). En `Clone` (`0x4381ba9c`) el resultado de la llamada a `0x43b0473e` decide: si es distinto de cero (`cbnz`) se copian campos; si es cero se escribe la traza `Image NULL`, se repite con `log end` y se sale. El patrón de `Branch` y `Create` (mismas cadenas con otro verbo) no se desensambló entero. La traza se emite por dos rutas estáticas: el envoltorio `0x4381b9d0` y `0x43902718` (la misma pareja que usa [S611](s611-imaging_rsrc.md)). El `%d` es un contador que en `Clone` limita la traza a 5 emisiones (`cmp r3,#4` / `bhi`); en `Branch` y `Create` no se comprobó.

## Llamadores (VERIFICADO_ESTATICO)

Barrido de todo `av-cam.bin` (11 427 236 B) buscando `bl` Thumb-2 a las tres funciones: **43 sitios** (Clone 10, Branch 26, Create 7) con inicio de función localizado en 35 (30 funciones: 10 + 15 + 5); en 8 sitios de `Branch` (`0x43551b64`, `0x43552210`, `0x435522d0`, `0x43552482`, `0x435542d6`, `0x4355447a`, `0x435561f0`, `0x435563ae`) no se halló un `push {…lr}` en los 6000 B previos. Detalle por sitio en `callers` de [imaging_img.json](../../analysis/s631_imaging_img/imaging_img.json). No se buscaron llamadas indirectas; ningún puntero literal a las funciones aparece en el binario (alineado a 4 B, con y sin bit Thumb).

Etiquetas de las cadenas que cargan las funciones llamadoras (inicio de función hallado hacia atrás por `push {…lr}`; heurístico):

| Función | Etiquetas en los llamadores |
|---|---|
| Clone | `[IMAGING_CAP]` (9), `[IMAGING]` (5), `[CAM_SCALAR]` (1) |
| Branch | `[CAMERA_MAIN_SYNC]` (9), `[IMAGING_CAP]` (5), `[GOLFSHOT]` (4), `[IMAGING]` (1); 5 sitios localizados sin cadena etiquetada y 8 sin función localizada |
| Create | `[CAM_SCALAR]` (3), `[IMAGING_CAP]` (2), `[CAMERA_MAIN_SYNC]` (1) |

## Qué es `Image` (estructural, no semántico)

- Las tres funciones obtienen el objeto con `0x43b0473e`: extrae el primer nodo de una **lista libre** (`ldr r5,[r4]` → `[r4]=[r5]`, contador `[r4+8]` decrementa) entre las llamadas `0x43560e1c`/`0x43560e38` con argumento `0x11`; `0x43b04760` lo devuelve. El nombre de ese bloqueo no se verificó. Por tanto, **`Image NULL` = pool agotado**, y el contador `%d` limita la traza a 5 emisiones.
- Layout del objeto en las copias de `Clone`: `+0x00` puntero (propietario), `+0x04` palabra, `+0x08…0x1b` 20 B (bloque 1), `+0x1c` palabra, `+0x20` halfword, `+0x22`/`+0x23` bytes, `+0x24…0x37` 20 B (bloque 2, `ImageParam`), `+0x38`/`+0x3c` palabras → objeto de al menos 0x40 B.
- `Create`/`Branch` rellenan el mismo layout desde un descriptor mayor (en `Branch` se leen `+0x14`, `+0x40`, `+0x44`) y llaman a `0x437965ac` con el campo `+0x14` (valor 4 se trata aparte). `Clone` copia de otro `Image`; `Branch` crea uno nuevo a partir de un `Image` y un descriptor; `Create` lo crea desde un descriptor.
- El significado de los campos (anchura, alto, formato…) no está identificado.

## Relación con el obturador

Los llamadores están en la zona de captura still (`[IMAGING_CAP]`, cuya `ResourceStack` gestiona acquire/release durante la captura, [S107](s107-camcore-resources.md)), en `[CAMERA_MAIN_SYNC]`/`[GOLFSHOT]` y en `[CAM_SCALAR]` (el handle `YCC_FULL`, [S604](s604-lens-yc-imaging-raw.md)). Eso sitúa `Image` en el camino de datos de la captura, **no** en el control del obturador: ninguna de las tres funciones toca registros del sensor ni de obturación, solo gestiona objetos de un pool. Conclusión: sin relación directa demostrada con el obturador electrónico; S51 no cambia.

## Cierre CAM-01 (03-11-2026, medido en bytes)

- **Llamadas indirectas** a `0x4381ba9c`, `0x4381bbf0`, `0x4381bd4c` y a `0x437965ac`: 0 por literal de 32 bits (con y sin bit Thumb), `ldr`+`add pc` en la misma función y `movw`+`movt` (`analysis/camera_closure/closure2.py`). Solo llamadas directas: 10, 26 y 7 (= 43, coincide con el barrido anterior) y 5 a `0x437965ac` (`0x437e5552`, `0x437e555e`, `0x4381bc96`, `0x4381bdec`, `0x43b04722`).
- **Sitios de `Branch` sin función localizada** (la función es la primera `push {…lr}` hacia atrás en 0x2000 B; es heurística y estas funciones son grandes):
  - `0x43551b64`: función `0x435503b0`, etiquetas cargadas hasta el sitio: `[CAMERA_MAIN_SYNC]`, `[IMAGING]`
  - `0x43552210`: función `0x435503b0`, etiquetas cargadas hasta el sitio: `[CAMERA_MAIN_SYNC]`, `[IMAGING]`
  - `0x435522d0`: función `0x435503b0`, etiquetas cargadas hasta el sitio: `[CAMERA_MAIN_SYNC]`, `[IMAGING]`
  - `0x43552482`: sin `push {…lr}` en 0x2000 B previos
  - `0x435542d6`: función `0x435525c0`, etiquetas cargadas hasta el sitio: `[CAMERA_MAIN_SYNC]`, `[IMAGING]`
  - `0x4355447a`: función `0x435525c0`, etiquetas cargadas hasta el sitio: `[CAMERA_MAIN_SYNC]`, `[IMAGING]`
  - `0x435561f0`: función `0x43554590`, etiquetas cargadas hasta el sitio: `[CAMERA_MAIN_SYNC]`, `[IMAGING]`
  - `0x435563ae`: función `0x43554590`, etiquetas cargadas hasta el sitio: `[CAMERA_MAIN_SYNC]`, `[IMAGING]`
- **Semántica de los campos de `Image`/`ImageParam` y de `0x437965ac`** y **ejecución real de las trazas en cámara**: no son afirmaciones de este informe (el layout es estructural; no se ejecutó firmware ni se usó cámara).

## Reproducción

```bash
.venv/bin/python analysis/s631_imaging_img/verify_imaging_img.py
.venv/bin/python -m pytest -q tests/test_s631_imaging_img.py
```
