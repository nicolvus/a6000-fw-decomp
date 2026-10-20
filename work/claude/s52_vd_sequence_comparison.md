# S52 A4 — motor VD y temporización de exposición: A7S 3.20 frente a A6000 3.21 (acotado)

19-10-2026, Agente A (Claude). Estático. Las tareas VD son asíncronas (colas/eventos): el orden de instrucciones no es
cronología. Alcance deliberadamente acotado (prioridad A3/A1).

## Equivalencias localizadas (por referencia PIC a la cadena de log)

| Elemento | A6000 (S31/S32) | A7S (ref. a cadena) | Estado |
|---|---|---|---|
| `VD_Pre` | `0x43792a0c` | función `0x437b65a0` (ref. «VD_Pre S» en `0x437b65be`) | VERIFICADO ref.; límites por prólogo |
| `VD_Sequence` | `0x4379155c` | ref. «VD_Seq S» en `0x437b524a` | VERIFICADO ref. |
| `VD_Drive` | `0x4378f410` | ref. «VD_Drive S» en `0x437b33f0` | VERIFICADO ref. |
| `EC_VD_Post` | `0x4378f848` | ref. «EC_VD_Post S» en `0x437b37a4` | VERIFICADO ref. |
| `int_LM_Send1st_Handler` | `0x43792750` | ref. en `0x437b631e` | VERIFICADO ref. |
| `[CAMERA_MAIN_SYNC]` | prefijo en 444 cadenas | **sin prefijo** (32 cadenas VD) | difiere solo en log |
| `DFECore` | cadenas de error | RTTI `N6Camera7DFECore…` | presentes ambos |

## Diferencia Silent en el motor VD

**VERIFICADO:** `VD_Pre` A7S (`0x437b6f6c..6f7e`) lee el ajuste `[*0x43ea70a0]+0x250`, llama al conversor
`0x4379ec04` con `cap=NULL` y guarda el tipo Silent en **`0x43ea92d8+0x7e8 = 0x43eaaac0`**. La A6000 no tiene el
conversor. Lectores de `0x43eaaac0`: ninguno hallado (REA xrefs vacío; barrido PIC de las 83 referencias a la base
sin acceso `+0x7e8` salvo el propio store) → **NO VERIFICADO** su uso.

No se halló en `VD_Drive/VD_Sequence/VD_Post` A7S acceso a `captura+0x748/+0x78c` ni a las copias de clase
(`0x43f04c8c`, `0x43faba61`) — búsqueda por offset/PIC, no exhaustiva.

## Temporización de exposición en la secuencia de captura (no VD) — relevante para «fin de exposición»

| Hecho | Evidencia | Estado |
|---|---|---|
| La secuencia arma un temporizador software `0x43b1e4d4(0, tiempo, callback)` | `0x438b6af4`, `0x438b8010…` | VERIFICADO |
| Callbacks: `0x43b1d649` pone bandera `0x100000` (grupo 0x13); `0x43b1d66d` pone `0x2000`; `0x43b1d691` → `0x438bea3c` pone `0x4000` **y envía CAIF 3** (salvo `[GOT]+0x62`) | instrucciones | VERIFICADO |
| `0x438be5f8` espera **respuesta CAIF 3** si CA activa (`+0x757`), o la bandera `0x100000` del temporizador si no | `0x438be5fa..628` | VERIFICADO |
| En `0x108` (`0x438b7fce`): normal → tiempo calculado + callback `0x43b1d649`; con `+0x748==1` → `0xffffffff` + callback `0x43b1d5b1` (ops del imager si `+0x743`) | A7S y A6000 `0x438c8ac8` (misma forma con `+0x740`) | VERIFICADO; código **compartido** |

**INFERENCIA:** el fin de exposición mecánico se sincroniza con respuestas CAIF o con temporizadores software que
disparan el evento CAIF 3 (tag `0x12` → helper GPIO). En Silent, la A7S omite esperar esas respuestas en `0xc8` y en
ReadExecuteBase (ver `s52_curtain_control_trace.md` S3/S5). Qué termina la integración del IMX235 en Silent
(ShutMode 0 + modo `0x4e/0x4f`): **NO VERIFICADO** (requiere semántica de registros del sensor).

## Frontera

Falta: callbacks registrados en las listas de `VD_Drive/VD_Post` A7S (llamadas indirectas), receptor del mensaje
de `0x43eaaac0`, y la tarea CA A7S (tag `0x12`). Ninguna requiere ejecutar firmware; requieren resolver tablas de
callbacks Thumb que REA no recupera.
