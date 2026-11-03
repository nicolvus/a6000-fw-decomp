# S631 — `[IMAGING_IMG]`: evidencia de cadenas y rutas de guarda

**03-11-2026.** Cierra la etiqueta `[IMAGING_IMG]`, la última pendiente de la familia IMAGING del censo S178. La presencia de texto y de cargas de dirección no demuestra la semántica de `Image` ni relación con la captura electrónica.

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

## Afirmaciones pendientes

| Afirmación | Estado |
|---|---|
| Significado de `Image`/`ImageParam` y de los campos copiados | NO_VERIFICADO: sin tipos ni cuerpo completo. |
| Llamadores de las tres funciones | NO_VERIFICADO: no se rastrearon. |
| Relación con la captura electrónica / obturador | NO_VERIFICADO: el texto no la excluye ni la prueba. S51 no cambia. |
| Ejecución real de las trazas en cámara | NO_VERIFICADO. |

## Reproducción

```bash
.venv/bin/python analysis/s631_imaging_img/verify_imaging_img.py
.venv/bin/python -m pytest -q tests/test_s631_imaging_img.py
```
