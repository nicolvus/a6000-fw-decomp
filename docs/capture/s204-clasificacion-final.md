# S204 — Clasificación final: A7S (IMX235) vs A6000 (IMX210) — obturador electrónico

22-10-2026. Agente A (sensor y driver), sesión S204 (rango S200–S299). Síntesis de S200–S202.

## Cuadro de clasificación final

| Subsistema / campo | Clasificación | Qué tiene la A7S (IMX235) | Qué tiene la A6000 (IMX210) | Estado en A6000 |
|---|---|---|---|---|
| Modos de lectura | DISTINTO | 34 modos, incl. `0x4e`/`0x4f` Silent (índices 29, 30) | 13 modos; `SetMode` rechaza `0x4e`/`0x4f` | Ausente |
| Selector de modo / drive mode | DISTINTO | `0x43826d58(modo,sub,tipo)`: `tipo==2`→`0x4e`/`0x4f` | `SetMode` carga columna de matriz por modo | Ausente (no hay `tipo`) |
| CheckSet* LiroSeq (obturador) | IDÉNTICO | 0/0 (S169 vigente) | 0/0 (S169 vigente) | Ausente (como la A7S) |
| Mensaje a Liro (…ForLiro) | IDÉNTICO | Rechazado; sin `SetShutterTypeForLiro` | Rechazado; sin `SetShutterTypeForLiro` | Ausente (como la A7S) |
| Registros de tiempo | DISTINTO | Columnas estáticas por modo de lectura | svd/shd/spl en ID3–ID8 (sombra) | Diferente esquema |
| Fórmula svd | DISTINTO | No recuperada | `svd = n·svr_num − 1` (0x4381106c) | No aplica |
| Espejo condicional 0x144–0x149 | DISTINTO | No equivalente recuperado | Sí, si `[G+0x7f]≠0xFF` | No aplica |
| Tiempo de lectura (24 MP) | DISTINTO | No recuperado | ≈ 4176 líneas ≈ 66,8 ms (cálculo) | No aplica |
| Fin de integración | IDÉNTICO | No hay comando de "fin de integración" | No hay reescritura al terminar | NO_VERIFICADO (ambos) |
| Transporte P2S / CISIF | IDÉNTICO | Mismo hardware P2S (DFE0) | Mismo hardware P2S (DFE0) | Idéntico |
| Strobe SSB | DISTINTO | Bit `0x10` byte +4 de registro (`[O+0x3d7]`) | Bit 3 del dato ID1, dos veces (1,0) | Diferente |
| ShutMode | DISTINTO | ShutMode 2 no soportado; codificación distinta | ShutMode 0–4; en captura solo 0 y 1 | Diferente |

**Resumen:** 4 idénticos, 7 distintos, 0 ausentes-en-A6000 como categoría propia (las ausencias son funcionales: modos silenciosos y selector `tipo`).

## Vía de Silent de la A7S (respuesta a S169)

La A7S implementa el obturador silencioso **por drive mode + tabla de timings**, no por `CheckSet*` de LiroSeq (0/0) ni por mensaje `…ForLiro` a Liro (rechazado). Por bytes:

- Selector `0x43826d58`: `tipo == 2` (Silent) → `sub==0` devuelve `0x4e`, `sub==1` devuelve `0x4f`.
- Los modos `0x4e`/`0x4f` son columnas 29 y 30 de la matriz de 34 modos (`0x43fee370`).
- Sus filas de registro difieren mínimamente de `0x4c`/`0x4d` (1 registro cada una: `0x000c` y `0x000a`).

## Veredicto sobre qué falta en la A6000

La A6000/IMX210 **no implementa** en firmware:
1. Modos de lectura dedicados a Silent (no hay `0x4e`/`0x4f` ni equivalente; `SetMode` los rechaza).
2. Un selector de drive-mode equivalente al `tipo==2` de la A7S.
3. Una operación de fin de integración identificada (idem A7S: NO_VERIFICADO en ambos).

Esto **no demuestra incapacidad del hardware** (S51: A=NO, B=NO, C=NO se mantiene). Confirmar o refutar la capacidad de obturador electrónico a resolución completa en la A6000 requiere datasheet IMX210 o traza pasiva CIS0+XPI+VD (pruebas físicas P0–P2/P7 de `physical-test-plan.md`, pendientes de autorización).

## Artefactos del ciclo S200–S204

- `docs/capture/s201-imx210-imx235-registers.md` — tabla por subsistema (11 filas).
- `docs/capture/s202-imx210-imx235-timing.md` — tiempos de lectura/exposición.
- `docs/capture/s204-clasificacion-final.md` — este documento (síntesis).
- `analysis/s201_imx210_imx235_registers/compare.json` — tabla estructurada.
- `analysis/s202_imx210_imx235_timing/timing.json` — tiempos estructurados.
- `tests/test_s201_imx210_imx235_registers.py` (6 tests), `tests/test_s202_imx210_imx235_timing.py` (4 tests), `analysis/s200_imx210_imx235_register_compare/test_s200_register_compare.py` (7 tests).

## Cierre de ciclo

Todos los ítems del backlog del Agente A están hechos (S200–S204). No se abre una sesión por cada xref/cadena: la comparación se cerró por subsistema con tabla. No hay ítems derivados que requieran cámara; el único derivado pendiente es la prueba física (fuera de alcance sin autorización).

S51 sin cambios: **A=NO, B=NO, C=NO.**
