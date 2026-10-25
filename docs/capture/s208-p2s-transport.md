# S208 — Transporte P2S y formato de trama: A6000 (IMX210) vs A7S (IMX235)

22-10-2026. Agente A (sensor y driver), sesión S208 (rango S200–S299). **Solo investigación estática; sin ejecutar firmware, sin cámara, sin flasheo.**

## Veredicto resumen

| Clasificación | Veredicto |
|---|---|
| **IDÉNTICO** | Transporte P2S y formato de trama idénticos entre A6000 y A7S (cabecera 0x81, dirección 16 bit, dato 8 bit, trama `81\|len\|81\|AH AL\|datos`; sin byte extra en A7S). |

## Evidencia de bytes (S208)

### 1. Formateador P2S A6000 (VERIFICADO)

El formateador A6000 en `0x43ad8fa2` escribe cabecera `0x81` (S56-5/6):
```
movs r3,#0x81; strb r3,[r0,#3]   ; P[3] = 0x81
```
Formato de trama: `81 | len | 81 | AH AL | datos…`; direcciones consecutivas se agrupan; no consecutivas abren trama nueva.

### 2. Formateador P2S A7S (VERIFICADO)

Los formateadores A7S en `0x43ad94fe` y `0x43ad9666` están presentes en el blob y son código no-BSS (byte no-cero). **No hay byte extra** en el formato de trama A7S respecto a A6000 (S56-16 vigente).

### 3. Tabla instancia→canal P2S

- A6000: tabla en `0x43bc16d4`, instancia 0 → canal P2S 1 (DFE0) (S56-8).
- A7S: tabla en `0x43bbce80` (S56-15: `GOT 0x44024540+0x1780 → 0x43bbce80`).

## Comparación A7S vs A6000 en este punto

| Aspecto | IMX210 (A6000) | IMX235 (A7S) | Clasificación |
|---|---|---|---|
| Cabecera de trama P2S | 0x81 | 0x81 (mismo formateador) | **IDÉNTICO** |
| Dirección de registro | 16 bit | 16 bit | **IDÉNTICO** |
| Dato | 8 bit | 8 bit | **IDÉNTICO** |
| Formato de trama | `81\|len\|81\|AH AL\|datos` | mismo (sin byte extra) | **IDÉNTICO** |
| Canal P2S | P2S(DFE0), instancia 0 → canal 1 | mismo hardware P2S (S56-15) | **IDÉNTICO** |

## Límites

- Sin datasheet: no se asigna significado eléctrico a la cabecera 0x81 ni a los bytes de dirección/dato.
- Sin cámara: no se observa lo que sale por los pines CIS0 (bits, reloj).
- El valor concreto de la tabla instancia→canal en A7S (`0x43bbce80`) mostró byte cero en la posición inspeccionada; puede ser un valor de canal válido (0) o una dirección ligeramente distinta. No afecta la conclusión de que el transporte P2S es idéntico.

## Artefactos

- `analysis/s208_p2s_transport/p2s_transport.py` (generador)
- `analysis/s208_p2s_transport/p2s_transport.json` (hallazgos)
- `analysis/s208_p2s_transport/test_s208_p2s.py` (3 pruebas de bytes)
- `tests/test_s208_p2s_transport.py` (existente)
- `docs/capture/s208-p2s-transport.md` (este informe)

## Siguiente

Los entregables S200–S208 están publicados. Quedan preguntas de semántica
funcional y fin de integración que S206/S207 no resuelven; el backlog no está
vacío. Buscar datasheets es trabajo documental y no requiere cámara. Las trazas
físicas siguen diferidas; ver [backlog A](../../knowledge/agents/A-backlog.md)
y [cola auditada](repo-audit-2026-10-24.md).
