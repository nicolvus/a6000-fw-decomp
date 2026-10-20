# S57-A — Semántica del registro ID1 (dirección 0x0001) del IMX210 (20-10-2026)

**Pregunta:** ¿qué controla ID1? **Resultado:** ID1 es un registro de **función combinada**: tiene bits fijados por el modo de lectura (SetMode), por el selector `ShutMode` de SetExposure y un bit de *strobe* (SSB). No se puede asignar un nombre eléctrico a ningún bit sin datasheet. Código: `analysis/s57/{emu57,id1_grid,bitops}.py`; pruebas `tests/test_s57_imx210_exposure.py::{Id1Writers,Id1Emulation,AdjustCmdFlags}`; evidencia `analysis/s57-evidence-matrix.json` (S57-01…09).

## 1. Los dos registros sombra
La lista síncrona de 119 punteros (`0x43fe995c`) contiene ID1 dos veces: **A = `0x4401ca2c`** (índice 1) y **B = `0x4401c734`** (índice 2). El dato es el byte `+2`. A se transmite antes que B. Valor inicial de ambos: `0x40` (columna `init` de la matriz de modos). `0x436d7c08` copia A en B en cada `Execute`, de modo que **B nunca guarda un valor propio**: solo difiere de A por el bit 3 cuando hay pulso (ver [SSB](s57-ssb-pulse-analysis.md)).

## 2. Escritores (VERIFICADO: Capstone + REA + emulación del código real)
| Escritor | Direcciones | Qué hace en ID1 | Condición |
|---|---|---|---|
| carga de columna de SetMode `0x436d6570` (slot `0x43fcc130` de la vtable derivada) | matriz `0x43fe9b74`, fila reg 0x01 → A | A ← columna del modo | cada cambio de modo |
| SetExposure `0x436d6f6c` | `0x436d70d2–0x436d7132` | bits 2,7,4,6 de A según ShutMode | cada SetExposure |
| trigger `0x436d7c08` | `0x436d7c16–0x436d7c46` | B←A; bit 3 (pulso) | cada Execute |
| ajuste `0x436d7cf0` | `0x436d7d0e–0x436d7d3a` | borra bits 2,7,4 de A y B | `[O+0x279]≠0` y drive_mode `0x0b` |

No hay más escritores en `0x436d5000–0x436daa00` (`analysis/s57/bitops.json`: 52 registros con operaciones de bit; ID1 solo en estas funciones). SetRead (`0x436d7e08`), SetMode de 2.ª tabla (`0x77b0`: 0 filas) y los registros de Execute no tocan ID1. Nadie lee ID1 salvo `0x436d7c08` y el recorrido de envío.

## 3. Tabla por bit
Base de SetMode (bits 0 y 2): `0x44` en `0x0b/0x2f`; `0x40` en `0x01,0x12,0x03,0x0a`; `0x41` en `0x05,0x10,0x07,0x0f,0x18,0x1a,0x19`.

| Bit | Escritores | Valores posteriores | Relación con ShutMode / drive_mode / StartExposure | Estado |
|---|---|---|---|---|
| 0 | solo SetMode (matriz) | 1 en `0x05,0x10,0x07,0x0f,0x18,0x1a,0x19`; 0 en el resto | independiente de ShutMode (verificado en 13 modos × 5 ShutMode); depende del drive_mode | correlaciona con el grupo «vídeo»/`0x0f` (nombre = HIPÓTESIS S50) |
| 1 | nadie | 0 | — | sin uso |
| 2 | SetMode (1 en `0x0b/0x2f`) → **sobrescrito** por SetExposure → borrado por `0x436d7cf0` | 1 si ShutMode∈{1,2,3}; 0 si {0,4} | tras SetExposure el valor final **no depende del drive_mode** | selector de ShutMode |
| 3 | solo `0x436d7c08` | 1 solo en A durante el pulso; 0 en el resto | lo pide `0x43ad9116` en cada flujo de exposición | strobe (SSB) |
| 4 | SetExposure; `0x436d7cf0` | 1 si ShutMode∈{2,3} | — | selector de ShutMode |
| 5 | nadie | 0 | — | sin uso |
| 6 | SetExposure (inicial `0x40`) | 1 si ShutMode∈{0,1,3,4}; 0 si 2 | — | selector de ShutMode |
| 7 | SetExposure; `0x436d7cf0` | 1 si ShutMode∈{1,2,3,4}; 0 si 0 | — | selector de ShutMode |

ShutMode → (bit2,bit7,bit4,bit6): 0→(0,0,0,1)=`0x40`; 1→(1,1,0,1)=`0xC4`; 2→(1,1,1,0)=`0x94`; 3→(1,1,1,1)=`0xD4`; 4→(0,1,0,1)=`0xC0` (con bit0 de SetMode: `+1`).
Rejilla completa: 13 modos × 5 ShutMode × SSB sí/no = 130 casos, **idénticos con memoria rellena a `0x00` y a `0xA5`** (`analysis/s57/id1_grid.json`).

## 4. Qué produce cada ShutMode en la captura real (VERIFICADO)
`ShutMode` = byte `arg+9` = `cap+0x655`. Constantes halladas: **0** (`0x438c79e2` arranque de captura; `0x438c82bc` StartExposure en estado 2/3) y **1** (`0x438c87f0`, `ExposureTimerStart!(first)`); camino CAMERA_MAIN_SYNC `0x4381106c`: ShutMode = `([obj+0x1fc]==9)`; copia en `0x4389cc28`. **No se encontró ninguna constante 2, 3 ni 4** en el barrido de `strb [rX,#0x655]` de todo el binario (la lectura «escrituras de 4» de `imager-exposure-p2s.md` no se reproduce con este barrido; puede existir por otra forma de almacenamiento: NO VERIFICADO).

## 5. Ruta de ajuste (AdjustCmd) — no es fotografía normal
`[O+0x277/0x278/0x279/0x27c]` los fija el manejador `0x43a12d9c` (comando `0x91`) mediante las fachadas `0x43ad9194/91a0/91ac/91b8` según una *categoría* de la tabla de comandos de ajuste (20 B/entrada; predicados `0x43b7a86a` cat 4→`+0x278`, `0x43b7a88a` cat 7→`+0x27c`, `0x43b7a8aa` cat 8→`+0x279`; `+0x277` para cat 1 y 7; cadena «`[CAM_IMAGER]: AdjustCmd Select error`»). Efectos emulados en `Execute`:
* `+0x279` con drive `0x0b`: bits 2,7,4 de A y B → 0 (ShutMode 2 → `0x00`), ID3…8 → 0, `ID0x73=0x39`, `ID0x12f=0x0E`.
* `+0x27c` con drive `0x0b`: `ID0x65=0x4C`, `ID0x73=0x39`, `ID0xDC=0x87`. `+0x277`: `ID0x73=0x39`.
INFERENCIA: son configuraciones de servicio/calibración (se activan por comandos de ajuste, S49); la tabla de comandos no se resolvió, así que no se sabe qué categoría usa cada ajuste. No hay evidencia de que alguna sea un obturador electrónico.

## 6. Clasificación (A.4)
ID1 **controla funciones combinadas**: (1) parte del modo de lectura (bits 0 y 2 desde la matriz de SetMode), (2) cuatro bits que reparten los cinco estados de ShutMode (selector del método de obturación/exposición del *firmware*), (3) un bit de strobe. **No clasificable con la evidencia:** qué hace cada bit en el sensor (lectura, integración o sincronización). El selector `ShutMode` toca ID1 pero no los registros de temporización 3–8 (S56): sugiere que ID1 elige *cómo* se aplica la temporización, no *cuánto* dura.

## 7. Límites
Sin datasheet del IMX210 ni traza eléctrica. La emulación ejecuta el código real de SetMode/SetExposure/Execute con stubs (llamadas fuera de `0x436d5000–0x436daa00`, `0x43ad8c00–0x43ad9700` devuelven 0; banderas OSAL/IRQ simuladas) y **no** modela el sensor. REA reconoce `0x436d7c08` y `0x436d7cf0` (coincide) pero no `SetExposure` (Thumb): ahí la verificación es Capstone + emulación; REA y Ghidra comparten motor.
