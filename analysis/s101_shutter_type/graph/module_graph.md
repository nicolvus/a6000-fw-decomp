# S72 — grafo de dependencias entre módulos y siglas (21-10-2026)

Método: `module_graph.py` busca, en cada cadena de traza `[A] …`, nombres de otros módulos de `module_map.json` como palabra completa (excluye palabras comunes que también son prefijo: `ERR`, `INFO`, `DEBUG`, `PARAM`…). **Es un grafo de menciones en trazas, no de llamadas**: INFERENCIA, no VERIFICADO.

348 módulos, 340 aristas (`module_graph.json`).

## Aristas más fuertes

| origen | destino | cadenas |
|---|---|---|
| CAMERA_MAIN_SYNC | GOLFSHOT | 59 |
| CDIAG | CTRLCORE | 49 |
| ADF | SAN | 45 |
| CAMERA_SA | APL | 42 |
| ACCY | REMOTE | 32 |
| ADF | SYSND | 28 |
| CDIAG | CTRLHDREC | 27 |
| CDIAG | CTRLSDREC | 27 |
| CDIAG | CTRLHDDEC | 26 |
| CDIAG | CTRLSDDEC | 26 |
| CAMERA_MAIN_TC | APL | 26 |
| CAM_FUNC_MGR | LRB | 26 |
| SFRA | RATECONTROL | 26 |
| ADF | ADJ | 25 |
| CDIAG | DEC | 23 |
| CAMERA_MAIN_YC | NULL | 23 |
| CDIAG | CTRLJPGENCDEC | 22 |
| CDIAG | CTRLJPGDEC | 21 |
| CDIAG | CTRLJPGENC | 21 |
| CDIAG | CTRLIF | 19 |
| TRK | EDTSA | 19 |
| CAMERA_MAIN_TC | DDT | 18 |
| SFRA | OPTION | 18 |
| ACCY | HELLO | 17 |
| TRK | NULL | 17 |

## Concentradores

- Más aristas salientes: CAMERA_MAIN_SYNC (48), ADF (27), ERR (20), IMAGING_CAP (20), CDIAG (19), ACCY (17), TRK (12), SDF (12)
- Más aristas entrantes: NULL (22), WRN (13), CMD (10), INIT (9), STOP (9), SIZE (9), DATA (8), OUT (7)

## Lectura

- `CDIAG` (diagnóstico) cita todos los módulos `CTRL*` (JPEG/SD/HD): es el único que los toca de forma transversal.
- `CAMERA_MAIN_SYNC → GOLFSHOT` (59) y `CAMERA_SA/MAIN_TC → APL` confirman S34/S88: la sincronía de cuadro conoce el disparo por sonido y el APL.
- `ADF → SAN/SYSND/ADJ` encaja con S81/S91/S100 (ADF = framework de arranque con submódulos).

## Siglas (`siglas.py`)

Búsqueda de frases cuyas iniciales coincidan con cada sigla en las cadenas de `av-cam.bin`: **sin expansiones creíbles** (ADF, IDT, VDF, VEF, SFRS/SFRA, WSX, ACCY, AUGI, SAD, APL, ZIT, FDT, VAT, PRC, VAE, VOT…); los aciertos son coincidencias de iniciales sin sentido. Las siglas **no se pueden deducir de los binarios**; hace falta documentación de Sony. Cerrado como no resoluble.
