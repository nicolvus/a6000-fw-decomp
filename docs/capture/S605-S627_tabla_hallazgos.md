# Auditoría de la validación S605–S627

**Fecha:** 23-10-2026. **VEREDICTO sobre la entrega de OpenCode: CAMBIOS.**

Este informe corrige [la validación anterior, commit 9e1a4055](https://github.com/nicolvus/a6000-fw-decomp/commit/9e1a4055).
Sus 263 pruebas pasan, pero no acreditan todas sus conclusiones. Las nuevas regresiones
reprodujeron siete fallos antes de corregir datos y estados.

| Afirmación o hallazgo | Decisión | Evidencia y corrección |
|---|---|---|
| Existencia de cadenas en 22 fichas | ACEPTO con correcciones | Son **94 trazas**, no 23 cadenas. Se comparan bytes exactos y NUL contra A6000 fw3.21. |
| “Byte por byte” en la entrega original | RECHAZO | 13 textos omitían saltos de línea o espacios finales. `rstrip()` ocultaba las diferencias. JSON corregidos y normalización eliminada. |
| Direcciones gemelas S606 | RECHAZO original; ACEPTO corregidas | Las siete `twin_vaddr` eran falsas. Se recuperaron coincidencias únicas y se comprobaron deltas y núcleos. |
| Longitudes de prefijo | RECHAZO original; ACEPTO corregidas | Cinco campos adicionales incorrectos: S606 gemelo 7 B; S608 núcleo 4 B y compuesto 18 B; S611 núcleo 10 B y compuesto 26 B. |
| Esquemas fuera de `text/vaddr` | ACEPTO cobertura corregida | Se verifican `twin_text/twin_vaddr/delta`, `core_text`, longitudes y cantidad de trazas. Los recuentos `differential` y otras afirmaciones quedan explícitamente NO_VERIFICADO. |
| “Logger global es código porque no es cero/FF” | RECHAZO del método | Ese test también aceptaba una cadena ASCII. Se conserva la lectura de bytes sin elevarla a identidad funcional. Hay instrucciones verificadas, descritas abajo. |
| Logger dual y equivalencias funcional/de código | ACEPTO dejarlas pendientes | **NO_VERIFICADO** para las 23 fichas. Falta evidencia específica de cargas, llamadas, flujo y comparación entre modelos. No se han demostrado falsos. |
| “Línea del obturador negativa VERIFICADO” | RECHAZO | Cero palabras clave, o una lista vacía, no excluye una ruta funcional. Las 23 fichas pasan a **NO_VERIFICADO**. |
| S618 como módulo independiente | RECHAZO como clasificación documental | No tiene trazas propias; remite a S617. Esto no demuestra ausencia de código independiente ni identidad funcional. |
| “Todo funciona: 263/263 PASS” | RECHAZO como validación completa | Los 263 tests sí pasan, pero **21/23 verificadores individuales fallaban** por longitudes obsoletas. Corregidos; ahora pasan los 23. |

## Evidencia concreta

A6000 fw3.21 `av-cam.bin`, base `0x43541000`. Los tres binarios estaban
disponibles localmente; no había que obtenerlos. Rutas, tamaños y SHA-256 quedan
en [resultados reproducibles](../../analysis/s6xx_verification_results.json).

- S607 `0x43caeb3d`: el texto termina en `req[%d]\\n\\0`, no en `req[%d]\\0`.
  Otras omisiones: S607 (4), S609 (5), S616 (4): 13 en total.
- S606, gemelas correctas:
  `0x43cfdb44`, `0x43cfdb88`, `0x43cfdbda`, `0x43cfdc36`,
  `0x43cfdc7f`, `0x43cfdcbc`, `0x43cfdcf8`.
  Deltas desde las principales: **38, 34, 52, 44, 33, 32, 32 B**.
  La primera dirección antigua, `0x43cfdb9c`, apuntaba a `mer(): %d`, no a la gemela.
- S608 y S611: **11 núcleos** comprobados como sufijos NUL de las cadenas A6000.
  Las coincidencias A7S/A6300 constan con direcciones por núcleo; una coincidencia
  textual no es equivalencia funcional ni prueba un literal autónomo.
- `0x43902718`, offset `0x3c1718`: bytes `0fb4 0021 30b5 a3b0` decodifican
  como Thumb `push {r0,r1,r2,r3}; movs r1,#0; push {r4,r5,lr}; sub sp,#140`.
  Verificado con Capstone y LLVM `llvm-mc --disassemble --triple=thumbv7`.
  Esto sustenta instrucciones en esa dirección; no acredita dos emisiones por módulo.
- Evidencia REA histórica consultada:
  `analysis/rea-independent/out/av-cam-session-evidence-bundle.json.gz`,
  registro `ev_08b4ea6919648bcf2d3d1e6713bd8cd70bc6f6b96c71f2f14e6c259b3a18599f`,
  `analyze_function(0x437de9f0)`: `0x437dea2e: bl 0x43902718`.
  Los bytes reales son `23f173fe`, confirmados como BL Thumb hacia ese destino.
  Es evidencia de una llamada en otra función, **no de logger dual S605–S627**.
  REA MCP no tenía un documento activo en esta revisión; se reutilizó la exportación
  antes de contrastar bytes y decodificación.

## Cobertura y límites

Cada JSON incluye estado para trazas, gemelas, núcleos, metadatos, logger,
equivalencias, obturador, esquema `differential` y otros campos.
`logger_dual=null` significa desconocido. La etiqueta histórica
`shutter_line=NEGATIVO ACOTADO` no acredita ausencia funcional.

Los recuentos `token_count`, `related_strings_count`, `dgi_jpeg_symbols`,
las interpretaciones de nombres y los sitios/funciones emisoras sin referencias
siguen **NO_VERIFICADO**. No se reconstruyó un criterio de selección que los
convirtiera en mediciones reproducibles. Los 23 informes retiran afirmaciones de
código preexistente renombrado y de ausencia de relación con el obturador.
S51 no cambia; sin ejecución de firmware, cámara ni flasheo.

## Reproducción

Desde la raíz del repositorio:

```bash
.venv/bin/python analysis/verify_s6xx.py
.venv/bin/python analysis/verify_s6xx.py --json
.venv/bin/python -m pytest -q tests/test_s60[5-9]_*.py tests/test_s61[0-9]_*.py tests/test_s62[0-7]_*.py tests/test_s6xx*.py
```

El verificador es de solo lectura, usa rutas ancladas al proyecto y falla ante
diferencias de bytes, deltas, núcleos o metadatos. Los tests de mutación comprueban
que detecta espacios omitidos, gemelas incorrectas, deltas corruptos, núcleos
alterados, rangos inválidos, NUL ausente y falsos positivos de código sobre ASCII.
El actualizador recalcula desde firmware, sin confiar en resultados guardados
obsoletos. Los antiguos scripts `fix_s6xx_*.py` son migraciones históricas y no
forman parte del procedimiento de validación.

Validación final: **275 tests y 92 subtests PASS; 23/23 verificadores individuales PASS**.
Ruff: cero avisos nuevos en los 28 archivos Python afectados (54 previos, conservados).
Ruff y mypy sin avisos en el verificador común, el actualizador y las dos suites nuevas/corregidas.
