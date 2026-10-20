# S60 Sol — emisor de los parámetros temporales IMX210

20-10-2026. A6000 `av-cam.bin`, base `0x43541000`, SHA-256
`b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9`.
Solo instrucciones, Capstone y Unicorn offline. Los marcadores de la emulación son
**sintéticos**. No hubo cámara, flasheo ni parche.

## Resultado

**VERIFICADO:** el emisor inmediato del caso 4 es `0x43b00fe6` (rol 1,
`obj+0xd60`, 0x54 B); el del caso 10 largo es `0x43b00f62` (rol 1,
`obj+0x6c0`, 0x5e0 B). Ambos pasan por `0x43806400` a la cola
`0x8003030f`. El receptor `0x43806e38` espera en `0x3030f`, llama a
`0x438069f0` en `0x43806e54` y libera el mensaje. El bit 31 entre IDs
**no está resuelto**: por ello el vínculo entre envío y recepción es
**PARCIAL**, aunque constructores y consumidores locales sí están probados.
El despachador responde al **caso 3** con el mensaje 4 y al **caso 9** con
el mensaje 10; son intercambios de solicitud y respuesta, no envíos
espontáneos demostrados.

**VERIFICADO en el objeto del emisor, bajo la guarda de publicación:**
`0x43b00dd4` copia primero `obj+d64 → obj+db4` (80 B), luego, si
`obj+568=1`, reemplaza `obj+d64 ← obj+e04` (80 B) y copia
`obj+d60 → obj+c4c` (0x54 B). Así, los mensajes posteriores transportan
el valor de `obj+e04`: caso 4 en `payload+4`; caso 10 largo en
`payload+0x590`. El escritor último de los **valores efectivos de**
`obj+e04` no quedó localizado. El constructor `0x43b00b48` lo pone a cero;
el ensayo con 80 bytes inyectados no demuestra que exista una toma con esos
valores.

## Evidencia y clasificación

En todos los renglones, binario y SHA son los de la cabecera. La prueba
reproducible es `python3 -m unittest tests.test_s60_sol -v`; el detalle de
instrucciones está en `analysis/s60/sol/{dispatcher,payload-manager,queue-send,tv-source}.asm`
y los resultados de ejecución en `probe-results.json`.

| ID | Estado / confianza | Dirección, evidencia y resultado | Método y límite |
|---|---|---|---|
| S60-01 | VERIFICADO / alta | `0x43806e38..5c`: recibe ID `0x3030f`, despacha en `0x43806e54` y libera. Tabla TBH `0x43806a04`: caso 4→`0x43806c24`, caso 10→`0x43806d02`. | Capstone, bytes TBH y `test_binary_and_dispatch_targets`. No prueba entrega desde el emisor remoto. |
| S60-02 | VERIFICADO / alta | `0x43806c58..68`: caso 4 y rol `obj+568=2` llama `0x43b00d94(obj,payload+4)`; 80 B terminan en `obj+d64`. | Instrucciones y ejecución del helper original `test_case_four_payload_and_receiver`; se inyectó mensaje. |
| S60-03 | VERIFICADO / alta | `0x43806d24..70`: caso 10 y rol 2 copia 0x560 B desde `payload+8` a `obj+8`, 28 B desde `payload+0x570` a `obj+0x698`, y 80 B desde `payload+0x590` a `obj+d64`; responde con `0x43806590`. | Bytes/Capstone; helper final ejecutado en `test_case_ten_payload_and_receiver`. El despachador completo y OSAL no se emularon. |
| S60-04 | VERIFICADO / alta | `0x43806bfc..0x43806c12`: caso 3 llama `0x43b00fe6` con rol 1; `0x43806cdc..f2`: caso 9 llama `0x43b00f62` con rol 1. Preparan respectivamente tipo 4 en `obj+d60`, 0x54 B, y tipo 10 en `obj+6c0`, 0x5e0 B. Ambos llaman `0x43806400`; `0x43806408/4a/58`: destino `0x8003030f`, procedencia `0x3030f`, memcpy original y envío OSAL indirecto. | REA, bytes/Capstone y Unicorn con interceptación **solo** del servicio OSAL; `test_direct_calls_link_request_reply_and_receiver`, `test_case_four_payload_and_receiver`, `test_case_ten_payload_and_receiver`. ID de retorno y entrega real no demostrados. |
| S60-05 | VERIFICADO / alta para offsets | `payload+0x20 = (payload+4)+0x1c`; `payload+0x5ac = (payload+0x590)+0x1c`. Esos 24 B llegan a `obj+dd0..de7` si se ejecuta la publicación rol 2. En el emisor largo, `obj+6c0+0x590 = obj+c50`. | Aritmética de direcciones, bytes y Unicorn (`published_4_dd0`, `published_10_dd0`). Los 24 B no son por sí mismos duración física. |
| S60-06 | VERIFICADO / alta para el orden; PARCIAL / media para origen último | `0x43b00dd4..0x43b00e1a`, rol 1: `d64→db4` antes de `e04→d64` y `d60→c4c`. Constructor `0x43b00c3e..48` borra `e04..e53`. Emisión posterior: caso 4 usa `d64`; caso 10 usa `c50`, ambos derivados de `e04` en ese orden. | Unicorn `test_publish_then_stage_next_value`, marcadores distintos y sin stubs internos. No se identificó productor efectivo de `e04` ni se probó orden de eventos en cámara. |
| S60-07 | PARCIAL / media | `0x43792f54..80` invoca la publicación en la ruta VD cuando `obj+57c≠0`; `0x43b00da0` copia 80 B a `obj+db4`, cuyo interior `+dd0` lee `0x43ae84c0`/`0x437aa65c`. El rol 1/2 selecciona las copias posteriores. | Bytes S59 confirmados con Unicorn S60 para ambos mensajes. La publicación es estado/configuración, no evento eléctrico ni confirmación mecánica. |
| S60-08 | PARCIAL / media | Tv tiene una procedencia **separada** de M: `0x4383dfb6..0x4383e01a` toma cuatro u16 de `AEOUT3+0xfc+2i`, salvo ruta condicional que usa `input+0x164`; convierte con `0x4382fa94` y pasa el resultado a `0x4383d4d0`. Antes `0x4383def4/df16` selecciona/copia bancos mediante `0x4383d3c0`; `0x4383b458` puede sustituir u16 mediante globales no nulos bajo condiciones adicionales. | REA, Capstone `tv-source.asm` y revisión del flujo S58. Queda sin demostrar el escritor original de los Tv y qué rama ocurre en foto 0x0b/0x2f. |
| S60-09 | NO VERIFICADO / baja | `P+0x4c0 → X+0x5c` en `0x4383d18c`; `0x43844a2a` y `0x438451be` copian **desde `+0x4c4`**, por lo que no identifican escritor de `P+0x4c0`. `0x43866cfc` escribe un `+0x4c0` de otro objeto (`0x43eb121c`), no del P AE `0x43eaee84`. | Bytes y corrección S59-G4. Fuente, unidad y valores alcanzables de clk siguen abiertos; `0xde3` es fallback de software, no reloj medido. |
| S60-10 | PARCIAL / media | N: `0x437aa65c` copia `(*param_2)+a8 → X8+3c` y `0x43843e94` a `P+22c`. svr: byte consumido de `M+16`, procedente del u16 `X8+14e` con truncamiento. VdNum: `0x437aab3c..52` da `max(0,raw−0x3000)` hasta `0xcfff` local, luego el productor puede verlo como signed16; el host trata N=0, estado 9 y bit15 (`0x438110be..12a`). | Instrucciones y pruebas S59, sin repetir campañas S58/S59. No hay dominio conjunto por modo; nunca se debe tomar un valor sintético como alcanzable. |
| S60-11 | NO VERIFICADO / baja | Para modos fotográficos `0x0b` y `0x2f` no hay aquí traza de una toma que vincule simultáneamente `(M,Tv,clk,N,svr,VdNum,flags)` con el envío ni con el bus IMX210. Los emisores locales se guardan por rol, no por esos dos números de modo. | Revisión de `0x43b00fe6`/`0x43b00f62` y `0x438069f0`. No descarta guardas aguas arriba; estados sintéticos de `probe-results.json` quedan fuera del conjunto demostrado alcanzable. |

## Qué se puede afirmar del estado temporal

El ensayo ejecuta el código original de publicación, preparación y copia de
los dos mensajes. Para separar valores, inyecta una secuencia en `obj+d64` y
otra en `obj+e04`; comprueba que `obj+dd0` recibe primero la secuencia antigua
en rol 1, mientras ambos mensajes transportan la nueva, y que una publicación
posterior en rol 2 expone esta última en `obj+dd0`. Es una prueba de orden y
alias de memoria. No establece que los dos roles participen de la misma toma
ni que OSAL enrute `0x8003030f` hacia `0x3030f`.

**Estados alcanzables:** solo está demostrada la existencia de rutas de código
condicionadas por rol 1/2 y por `obj+57c`; el conjunto de tuplas temporales
efectivas para 0x0b o 0x2f sigue **NO VERIFICADO**. Una duración calculada o
copiada no acredita inicio ni fin de integración. Tampoco se deduce un evento
eléctrico del IMX210, una respuesta del host ni movimiento/supresión de la
segunda cortina. Fin electrónico de integración: **NO VERIFICADO**. S51 queda
**A=NO, B=NO, C=NO**.

## Reproducción

```sh
PYTHONDONTWRITEBYTECODE=1 python3 analysis/s60/sol/trace_payload.py
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_s60_sol -v
```

Ejecución de esta sesión: **6 tests, OK** (`analysis/s60/sol/tests-run.log`),
sonda en `probe-results.json`. El servicio de envío OSAL se intercepta;
las funciones de copia y construcción internas se ejecutan sin stubs.

REA: una sesión útil con `session_daemon.py`/`q.py`, 490,2 s de análisis
inicial. Las consultas originales están en `rea-results.jsonl` y
`rea-follow.jsonl`: confirma la tabla de casos, los llamadores internos de
`0x43b00fe6` y `0x43b00f62`, el envío `0x43806400`, la selección Tv en
`0x4383d3c0` y el único llamador registrado de `0x4383d704`
(`0x437b5e70`). La consulta de `0x43b00dd4` devolvió «no existe
procedimiento»: es una entrada Thumb no reconocida por REA, verificada con
bytes/Capstone/Unicorn; **no** es ausencia de función. La consulta de
llamadores de `0x438069f0` volvió vacía, aunque el BL Thumb directo de
`0x43806e54` está en bytes: ese vacío tampoco demuestra ausencia. La traza de valores
de `0x4383d704` quedó truncada (60 nodos visibles de un máximo de 120),
sin resolver origen último de Tv. El primer arranque local no pudo publicar
el socket Unix por el sandbox; la sesión útil se abrió por Context Mode,
respondió `{"bye":true}` al cierre y no dejó procesos REA. REA y el Ghidra
histórico comparten motor; los bytes y Unicorn sustentan el hallazgo decisivo.

Se ejecutó `knowledge-maintenance` sobre una copia temporal de SQLite para
respetar el alcance exclusivo de entregables: dos reconstrucciones con
2814 relaciones cada una (`knowledge-maintenance.log`); el índice compartido
queda sin actualizar. Ruff y mypy sobre los Python entregados: sin avisos
(`ruff.log`, `mypy.log`).

No se editaron firmware, Ghidra, informes anteriores ni archivos ajenos a los
entregables; no hubo `git add`, commit ni push.
