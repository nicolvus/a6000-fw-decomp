# Seguimiento estático de `G+0x784` (tipo de obturador) en `av-cam.bin` — 26-10-2026

Motivo: T020 demostró que forzar `G+0x784`=2 no cambia el obturador. Se busca dónde se consume el valor.
Método: barrido de bytes de `av-cam.bin` (base `0x43541000`) por `ldr/str.w [rN,#0x784]` + desensamblado con capstone (Thumb). Las coincidencias con `rn=r15` son cargas de literal, descartadas.

## Accesos reales a `G+0x784` (VERIFICADO por bytes)
| Dirección | Tipo | Nota |
|---|---|---|
| `0x4378fb94` | escritura (a 0) | init de G, junto a `+0x780`, `+0x788` |
| `0x43793182/96`, `0x437931b6`, `0x4379323a/70/82/96` | escrituras | selector (`0x4379316a`) y ramas |
| `0x4378f5bc`, `0x4378f5c8` | lectura | pasa `G+0x784` (r0) y `G+0x778` (r1) a `0x4378dfdc`; en la rama alternativa (`+0x780`≠0 y `[..]≠0x807`) usa otra copia |
| `0x43737228` | lectura | suma `+0x784 + +0x780` en un cálculo de parámetros de otro objeto (r4) |
| `0x43ab8a78` | falso positivo | llamada por vtable (offset 0x784 de una tabla), no es G |

## Consumidor: `0x4378dfdc(tipo, arg)` (VERIFICADO)
- Compara `tipo` con el anterior; si cambia, desarma el modo previo y arma el nuevo.
- tipo 1 → `0x4359f174(3)` → `0x4359fd90`; tipo 2 → `0x4359eed0(3,0)` → `0x4359f4f8`; tipo 0 → desarma (`0x4359f12c`/`0x4359ee78` según el anterior).
- Registra eventos `0x2012`–`0x2016` (`0x43901a8c`) y guarda el resultado en variables globales; luego consulta `0x4359ecc0` y `0x4378dda0`.
- `0x4359fd90`/`0x4359f4f8`/`0x4359f5f4` operan sobre una tabla de 10 entradas (8 B) de un gestor de recursos/temporizadores (`0x435611b8`, `0x4359f87c`): no construyen ninguna orden CAIF ni escriben MMIO del obturador.

## Conclusión (INFERENCIA, con límite)
El tipo 2 llega hasta un gestor de recursos del módulo `0x4359xxxx` que se arma/desarma por tipo (1 y 2 usan rutas distintas, 0 las desarma). En ese tramo no aparece ninguna decisión que cambie el obturador físico, coherente con T020. La orden hacia Darwin no se arma en este camino; el siguiente paso sería identificar quién consume la "variable global" que guarda `0x4378dfdc` (y `0x4378dda0`) y dónde se arma la orden de captura. NO_VERIFICADO que el bit `0x20` se pierda aquí o en Darwin.

## Ampliación (E22, segunda pasada)
- Las globales que fija `0x4378dfdc` (`0x43e991cc..dc`, `0x43f9a424`) solo se referencian dentro del clúster `0x4378dd00..0x4378e2a0` (barrido PIC `ldr`+`add pc` de todo `av-cam.bin`; VERIFICADO). No salen del módulo.
- `0x4378dda0(i)` (tabla de 11 palabras) y `0x4378de88` (mapa 0..5 → 0..10) convierten el modo en índices; `0x4378df70` los inicializa (llamada desde `0x43787fa2`).
- `0x4378e1a4` rellena un registro (campos `+0x8..+0x40`) y llama a `0x4378df14` con el modo, que devuelve constantes por tipo: tipo 0 → `0x412b55`, `0xbbb`, `0x8257`; tipo 1 → `0x4e2000`, `0xe10`, `0x9c40`; tipo 2 → `0x51762b`, `0xeaa`, `0xa2ec`. Son parámetros de temporización distintos para el tipo 2 (INFERENCIA: lectura/tiempos del sensor; significado físico NO_VERIFICADO). El registro se rellena desde el manejador `0x43791c08` (`G+0x560`).
- Consumidores del registro: NO identificados (los offsets `+0x578/+0x580/+0x584` aparecen en muchas estructuras y el barrido no discrimina).
- Conclusión: el tipo 2 cambia constantes de temporización internas de `av-cam`, pero no se halló emisión de orden CAIF. Cierre parcial; seguir exige REA (`trace_native_values`) sobre el registro `G+0x560`.

## Tercera pasada (E22): el registro no pasa a otro módulo
- `0x4378e1a4` calcula cocientes (`0x4355faf0` = división) de las tres constantes por tipo y las guarda en `+0x1c/+0x22/+0x28/+0x2c` del registro. Es un registro de relojes/tiempos, no una orden.
- Las funciones vecinas que tocan `+0x57c/+0x584/+0x588/+0x784` (`0x43736800..`, `0x43737228..`) operan sobre una tabla de temporización por modo con cientos de campos (medias `(a+b)>>1` y diferencias `a-(b>>1)`): es otro objeto distinto de G. El `+0x784` leído en `0x43737228` NO es el tipo de obturador (coincidencia de offset; corrige la tabla de la primera pasada).
- Consumidores del registro de relojes del tipo 2: no hallados con barrido de bytes. Se abrió una sesión REA de `av-cam.bin` y se cerró sin consultas: las ramas relevantes son Thumb sembradas a mano que REA no cubre (ver `docs/STATE.md`).
- Estado: E22 se cierra con límite. El tipo 2 solo alcanza el gestor `0x4359xxxx` y constantes de reloj internas; sin camino hallado hacia CAIF/Darwin.
