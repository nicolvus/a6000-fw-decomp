# S207 — Fin de integración / segunda cortina electrónica: A7S (IMX235) vs IMX210 (A6000)

22-10-2026. Agente A (sensor y driver), sesión S207 (rango S200–S299). **Solo investigación estática; sin ejecutar firmware, sin cámara, sin flasheo.**

## Veredicto resumen

| Preguesta | Estado | Veredicto |
|---|---|---|
| ¿A7S/IMX235 tiene registro de fin de integración que falte al IMX210? | **NO** | Ninguno encontrado en matriz ni código (S57-D D.6 vigente). |
| ¿A7S/IMX235 tiene mecanismo de segunda cortina electrónica? | **NO** | Sin cadenas de segunda cortina/final de integración en av-cam.bin A7S. |
| ¿IMX210 tiene equivalente? | **NO** | Tampoco lo tiene (paralelismo). |
| Clasificación | **IDÉNTICO** | Ambos carecen de operación de fin de integración identificada (NO_VERIFICADO si el sensor la hace internamente). |

## Evidencia de bytes (S207)

### 1. Cadenas de fin de integración / segunda cortina (VERIFICADO)

Barrido de bytes en av-cam.bin de ambos modelos. No aparecen como cadenas C (seguidas de 0x00):

| Cadena | A7S fw3.20 | A6000 fw3.21 |
|---|---|---|
| `second curtain` | ausente | ausente |
| `2nd curtain` | ausente | ausente |
| `shutter close` | ausente | ausente |
| `integration end` | ausente | ausente |
| `end of integration` | ausente | ausente |
| `finish integration` | ausente | ausente |
| `curtain close` | ausente | ausente |

Secuencias cortas de 3 bytes (`eoi`, `eos`, `curtain`) aparecen por coincidencia en código ejecutable de **ambos** modelos (falso positivo, no son cadenas C legibles).

### 2. Matriz IMX235 sin registro de fin de integración (VERIFICADO)

La matriz IMX235 (`0x43fee598`) tiene 35 registros, direcciones `0x0000`–`0x00CF`. Ninguna dirección ni columna está dedicada a "fin de integración" o "segunda cortina" (S57-D D.6 vigente). Los modos Silent `0x4e`/`0x4f` difieren de `0x4c`/`0x4d` solo en 1 registro cada uno (`0x000c` y `0x000a`), sin comando de fin de integración.

### 3. ExposureTimerEnd! no reescribe registros (S57-F, vigente)

`ExposureTimerEnd!` (`0x438c893a`) no reescribe ningún registro del sensor ni emite SSB/Execute. El firmware no gestiona el fin de integración por registros.

## Comparación A7S vs A6000 en este punto

| Aspecto | IMX235 (A7S) | IMX210 (A6000) | Clasificación |
|---|---|---|---|
| Registro de fin de integración | ausente | ausente | **IDÉNTICO** |
| Mecanismo de segunda cortina electrónica | ausente | ausente | **IDÉNTICO** |
| Cadenas de fin de integración en firmware | ausentes | ausentes | **IDÉNTICO** |
| Operación de fin de integración identificada | NO (ambos) | NO (ambos) | **IDÉNTICO (NO_VERIFICADO si el sensor la hace internamente)** |

## Límites

- Sin datasheet IMX210/IMX235: no se puede confirmar ni refutar que el sensor cierre la integración internamente por temporización programada al inicio (hipótesis H57-9).
- Sin cámara: no se observa el fin real de integración ni la señal XPI/CIS0_SCK/SI.
- Una consulta vacía de REA no prueba ausencia: la ausencia de cadenas y registros se confirmó con barrido de bytes, no solo con falta de xrefs.

## Artefactos

- `analysis/s207_imx235_end_of_integration/full_eoi.py` (generador)
- `analysis/s207_imx235_end_of_integration/full_eoi.json` (hallazgos)
- `analysis/s207_imx235_end_of_integration/test_s207_eoi.py` (3 pruebas de bytes)
- `tests/test_s207_imx235_end_of_integration.py` (a crear)
- `docs/capture/s207-imx235-end-of-integration.md` (este informe)

## Siguiente (S208)

Comparación del transporte P2S y formato de trama A6000 vs A7S (confirmar bytes: cabecera 0x81, longitud, dirección 16 bit, dato 8 bit; sin byte extra A7S según S56-16).
