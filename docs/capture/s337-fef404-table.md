# S337 — `0x43fef404` no es una tabla de tiempos (carril B)

22-10-2026. Carril B. Sesión S337. **Solo lectura estática; sin firmware en ejecución, sin cámara, sin flasheo.**

## Pregunta

S329 marcó `0x43fef404` como el único candidato estricto del barrido (un `u16[69]` con valores 1..78 en la región de tablas de modo). ¿Es una tabla de tiempos?

## Veredicto

| Afirmación | Clasificación | Evidencia |
|---|---|---|
| `0x43fef404` es una tabla de **69 entradas de 4 B** `{u16 código, u16 0x000d}` | **VERIFICADO** | 69 pares con el segundo campo siempre `0x000d`; termina en `0x43fef518` |
| **No** es un `u16[69]` de tiempos: la vista `u16` mezcla códigos y el valor constante `0x000d` | **VERIFICADO** | 34 apariciones de `0x000d` en la vista de 69 `u16`; el «array» de S329 cruzaba la estructura |
| Va precedida de **169** palabras de 32 bits `0x43f9c622` (punteros a la zona `0x43f9c6xx`) | **VERIFICADO** | Ristra contigua antes de la tabla |
| **No tiene consumidor estático**: 0 literales de `0x43fef404` en el blob | **VERIFICADO (negativo acotado)** | Búsqueda de bytes |
| Códigos de la tabla: `0x01`..`0x64` (69 valores) | **VERIFICADO** | Campo 1 de cada entrada |
| Que los códigos sean ids de registro (coinciden 69 entradas con las 69 filas de la matriz) | **INFERENCIA (baja)** | Coincidencia numérica; sin consumidor que lo demuestre |

**S51 no cambia (A = NO, B = NO, C = NO).**

## Detalle

```
0x43fef3f0  c622 43f9 c622 43f9 c622 43f9 c622 43f9   ; ristra 0x43f9c622
0x43fef400  c622 43f9 0046 000d 004e 000d 000f 000d   ; fin de ristra + inicio
0x43fef410  002e 000d 002f 000d 0031 000d 0014 000d
...
0x43fef510  0061 000d 0062 000d 0063 000d 003f 000d
```

Entradas: `{0x0046, 0x000d}`, `{0x004e, 0x000d}`, `{0x000f, 0x000d}`, … hasta 69 pares.

## Corrección

- **S329**: el «único candidato estricto» del barrido es un **falso positivo** producido por una ventana de 69 `u16` que cruzaba dos estructuras. No es una tabla de tiempos; la conclusión de S329 (no hay tabla de tiempos por modo) no cambia.

## Límites

- Una lista vacía de referencias no prueba ausencia de uso indirecto: el consumidor podría llegar por un puntero calculado.
- No se asigna significado al campo `0x000d` ni a los códigos.
- S51 (A/B/C) no cambia.

## Reproducción

```bash
.venv/bin/python analysis/s337_fef404_table/build_fef404_table.py
.venv/bin/python analysis/s337_fef404_table/verify_fef404_table.py  # 12 comprobaciones
.venv/bin/python -m unittest tests.test_s337_fef404_table            # 7 tests
```

Artefactos: `analysis/s337_fef404_table/fef404_table.json`, `build_fef404_table.py`, `verify_fef404_table.py`, `tests/test_s337_fef404_table.py`.
