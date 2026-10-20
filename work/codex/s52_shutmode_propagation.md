# S52/R2 — propagación de clase y ShutMode

## B1 — resultado

**NO VERIFICADO como cadena completa.** La ampliación agotó el escaneo de materializaciones PC-relativas para el bloque de política y el patrón de despacho virtual; no apareció una transferencia demostrable desde los destinos de clase al argumento de `SetExposure`.

| tramo | instrucciones verificadas | resultado |
|---|---|---|
| tipo Silent → banco | `0x43862f18 ldr r3,[r6,#0x76c]`; `0x43862f1c str r3,[r7,#0x404]` | tipo se copia al banco |
| tipo 2 → clase 0 | `0x438649f0 ldr.w r2,[r7,#0x404]`; `cmp #2`; `0x438649f8/49fa` materializan `0x43f06bc8` (PC de `add`=`0x438649fe`); `0x43864a48 str r1,[r2,#0x5c]` con `r1=0` | VERIFICADO |
| corrección de la pista | `0x43f06d5c..98` resulta de sumar las literales a su propia dirección, no al PC de cada `add`; el escáner recupera la familia `0x43f06c2c` en `0x438643de..0x43864d0e` | las direcciones exactas requieren PC correcto por instrucción |
| lector de `+0x5c` | `ldst_imm_scan.py` no puede tipar registros base; referencias reconstruidas pertenecen a la política | frontera: no hay lector tipado demostrado |
| argumento del sensor | IMX235 `0x436f4198 ldrb.w r6,[r10,#9]`; IMX210 `0x436d6fb6 ldrb.w r9,[r1,#9]` | VERIFICADO |

La reserva A7S `0x437b8948` escribe solo `+0,+4,+5,+6`; no prueba `param+9`. Tampoco es válido inferirlo por semejanza con A6000.

## Llamadores virtuales `+0x28`

El patrón A6000 está verificado en `0x436d6320..4a`: `ldr r0,[r0]`; `ldr r3,[r0]`; `ldr r3,[r3,#0x28]`; `blx r3`. La vtable IMX210 `0x43fcc090+0x28 = 0x436d6f6d`; la IMX235 contiene `0x436f4169` en `0x43fce050+0x28`.

El barrido global de `ldr *,[#0x28]; blx` produce muchas clases polimórficas (`s52/a7s-class-pcrel-and-vtable.txt`, `s52/a6000-vtable.txt`). Sin tipado de receptor no permite declarar cuáles llevan C_ImagerCtrl_IMX235. La frontera para «todos los llamadores» es la resolución dinámica del objeto antes del `blx`.

## B3 — A6000

El único llamador tipado recuperado llega al slot `+0x28`, pero la ruta normal de foto no demuestra construir `param+9=0`. Vídeo/LV seleccionan modos de lectura, no un valor probado para este byte; no hay evidencia para vídeo, LV, AF, ráfaga, bracketing o servicio.

| hipótesis | estado | evidencia / frontera |
|---|---|---|
| H52-3: clase 0 A7S alcanza `param+9=0` | INFERENCIA baja | extremos verificados; falta copia/demultiplexado |
| H52-4: clase 0 inhibe segunda cortina | NO VERIFICADO | no hay consumidor de clase hacia actuador |
