# S53 — Darwin A7S 3.20 vs A6000 3.21: comparación funcional (19-10-2026)

Base ROM `0x4200`. Equivalencias establecidas por estructura de código idéntica (secuencia de llamadas, constantes,
offsets de S) y bytes; diferencias comprobadas por bytes en `tests/test_s53_darwin_caif.py`. Control positivo: A6300 2.01.
Detalle: [reconstrucción](s53-darwin-caif-reconstruction.md), [cortinas](s53-curtain-actuator-control.md).

## Matriz obligatoria

| Función | Darwin A7S | Darwin A6000 | Equivalencia | Evidencia |
|---|---|---|---|---|
| Recepción CAIF | MFS5 CSIO, mss-async `0x122a6`, ID `0x0c` (`0x28bc8`, rx `0x2000321c`, 22 B) | MFS5, `0x12172`, ID `0x0c` (`0x27c78`, rx `0x2000344c`, 22 B) | **igual** | bytes tabla; esquema A6000 P36–P38 = MSS_*_DWN |
| Parser del paquete | `0x18396` (S=`0x200034a0`) | `0x17f8c` (S=`0x200036d8`) | igual **salvo bit Silent** | pseudocódigo + bytes |
| Bit Silent `+0x12 & 0x20` | `S+0xd0.b5`; clase→2; predicado `0x19a86`/`0x216c2` | **no se lee** (solo bits 0 y 3) | **distinto (falta en A6000)** | `0x18460..0x18488` vs `0x18052` |
| Modo 2 (`+0x0d` b6-7) | `S+0x3d` entero; solo bit 0 consumido | íd. | igual (no interpretado) | barrido + pseudocódigo; ausencia NO probada |
| Control 1ª cortina (P4D) | `0x2172c(no_silent)` | `0x20cb2()` | distinto (sin argumento Silent) | bytes (`mov r4,r0`/`cmp r4,#0`) |
| Control 2ª cortina (P4E) | `0x21786(no_silent)` | `0x20d00()` | distinto | bytes |
| Máquina de estados (fases ADC `S+0x153`) | igual; arranque `0x2116e`/`0x21282` condicionado a no Silent | `0x20734`/`0x2083c` sin condición Silent | estructura igual, puerta Silent ausente | pseudocódigo |

Otras equivalencias: despacho IRQ `0x67fa`/`0x6808`; escritor bit-band `0x5200`/`0x51c0` (bytes idénticos);
selector de tipo de mecanismo `0x216e8`/`0x20c74` (S52); primitivas de exposición A7S `0x19d34/0x19d52/0x19d6a/0x19e00`
↔ A6000 `0x198bc/0x198d6/0x198ee/0x19978` (A6000 sin argumento `no_silent`); diferidos `0x214dc/0x214fa` ↔ `0x20a8a/0x20aa4`.

## Preguntas

| # | Respuesta | Estado |
|---|---|---|
| P1 receptor CAIF igual | Sí: mismo canal MFS5, misma entrada ID `0x0c` de 22 B, mismo copiador | VERIFICADO (bytes) |
| P2 mismo formato | Sí: 22 B, mismos offsets consumidos (`+0x00..+0x15`) | VERIFICADO; identidad CAIF ev1↔ID `0x0c` INFERENCIA fuerte |
| P3 A6000 interpreta `+0x12&0x20` | **No.** El parser lo descarta y no hay otro lector de `S+0xd0` b5 | VERIFICADO en la cobertura indicada |
| P4 A6000 admite modo 2 de `+0x0d` | Ni A6000 ni A7S consumen los bits 6-7 en el código analizado; no es el discriminante Darwin | PARCIAL (búsqueda negativa) |
| P5 ramas Silent internas | A7S sí (§ cortinas); A6000 no | VERIFICADO |
| P6 control de cortinas físicamente equivalente | Sí: mismas salidas PDOR y misma secuencia mecánica | VERIFICADO código; pines A7S INFERENCIA |
| P7 lógica latente en A6000 | Solo la rama «sin mecanismo» de `0x20d26/0x20e0e/0x20e98`, accesible con **tipo de mecanismo 0** (byte de configuración `0x1b080(0)&7`), no por el paquete; tipo 0 también desactiva P4D/P4E en todo el controlador | VERIFICADO estructura; efecto global de tipo 0 NO VERIFICADO |
| P8 origen de la diferencia | **Firmware** (instrucciones añadidas en A7S y A6300; mismo MCU, mismas salidas) | VERIFICADO para el código; hardware de cortina no comparado |
| P9 influencia del tipo 1/2/3 | El tipo condiciona cada escritura (P4D solo 1/2; P4E 1/2/3) y reescribe la clase tras el `+2` Silent; el predicado Silent es independiente del tipo | VERIFICADO |
| P10 validaciones de modelo | Ninguna en la ruta Silent A7S: solo depende de `pkt[+0x12]` b5 | VERIFICADO en la ruta; búsqueda global de comprobaciones de modelo NO hecha |

## Hipótesis S53

| H | Estado | A favor | En contra / límite | Confianza | Próxima comprobación |
|---|---|---|---|---|---|
| H53-1 A7S identifica Silent por `+0x12` b5 | **VERIFICADO** | `0x18460`; predicado `0x19a86`; control A6300 | — | alta | — |
| H53-2 A7S usa modo 2 de `+0x0d` | **NO SOPORTADA** | — | solo bit 0 de `S+0x3d` consumido | media | lectores indirectos de `S+0x3d` |
| H53-3 combinación de campos | **PARCIAL** | bit 5 decide; clase →2 y tipo de mecanismo modulan | modo 2 sin consumidor | media | — |
| H53-4 A6000 parser compatible con indicadores | **REFUTADA** (formato compatible, semántica no) | mismo parser | descarta el bit 5 | alta | — |
| H53-5 A6000 control de cortinas equivalente | **VERIFICADO** (mecánico) | mismas funciones/salidas | sin puerta Silent | alta | — |
| H53-6 A6000 carece de una rama necesaria | **VERIFICADO** | 3 bloques ausentes (parser, escritores, diferidos/ADC) | — | alta | — |
| H53-7 diferencias = variante de mecanismo | **REFUTADA** para la diferencia Silent | el tipo 1/2/3 es igual; la diferencia es el bit del paquete | tipo 4 (A6300) no analizado | alta | — |
| H53-8 Darwin actúa independiente de la lectura del sensor | **VERIFICADO** (código) | Darwin solo ve el paquete; ningún dato de sensor | sincronía física con IMX NO VERIFICADO | media | — |
