# Análisis de la cadena C2 (disparador → 0x3011 → CaptureStart)

## Resumen ejecutivo

La cadena C2 está parcialmente mapeada estáticamente. El receptor de la cola de mensajes `0x40193` **no se ha podido localizar estáticamente** porque:
1. No existe el literal `0x40193` (word de 4 bytes LE) en `av-cam.bin`
2. No existe la cadena ASCII `"40193"` en el binario
3. No hay instrucciones `movw`/`movt` que construyan `0x40193`
4. No hay `BL` directo a `osal_rcv_msg` (0x43561260) desde fuera de la propia función
5. El dispatcher `0x43807f4c` no tiene `BL` directo ni literal de referencia — es llamado indirectamente (vía tabla de saltos o puntero de función)

## Dispatcher de dominio C2: 0x43807f4c

**VERIFICADO** (desensamblado con capstone):

El dispatcher compara el ID de mensaje (r3 = valor en [r1]) con los siguientes saltos:

| ID mensaje | Destino | Notas |
|------------|---------|-------|
| 0x100 | 0x438082ce | C2 entry hoja → bl 0x43807d80 → b 0x43808406 |
| 0x101 | 0x438082d4 | |
| 0x102 | 0x43808024 | |
| 0x103 | 0x438080aa | |
| 0x104 | 0x43808122 | Handler msg 0x104 |
| 0x201 | 0x438083b4 | |
| 0x202 | 0x4380840a | |
| 0x206 | 0x43808552 | |
| 0x8300 | 0x4380836e | |
| 0x8202 | 0x43808564 | |
| 0x8203 | 0x4380856e | |
| 0x8304 | 0x43808182 | |
| 0x8305 | 0x438081ec | |

**VERIFICADO** (nuevo): El dispatcher `0x43807f4c` (Thumb `0x43807f4d`) está referenciado como puntero de función en una tabla/vtable en `0x43fcd3e0` (file offset `0xa8c3e0`). La tabla en `0x43fcd3a0` contiene múltiples punteros de función en el rango `0x4380xxxx` y `0x43b0xxxx`/`0x43b1xxxx`. No se encontró ninguna referencia literal a la dirección de la tabla `0x43fcd3a0` ni al Thumb `0x43fcd3a1`, por lo que el puntero de vtable se establece en runtime. El llamador del dispatcher sigue sin localizarse estáticamente.

## Puente C2: 0x43807d80

**VERIFICADO** (desensamblado con capstone):

`0x43807d80` es el puente del dominio C2 al dominio local `0x100-0x207`. Llama a:
- `0x4383a84e`, `0x43543004`, `0x4383aca4`, `0x4383b44c`, `0x4383aca0`, `0x4383b1c0`
- `0x4383aa04`, `0x4383b50c`, `0x4383aca0`, `0x4383b1b6`
- `0x4383bb1c`, `0x4383a602`, `0x4383a9b6`, `0x4383b486`, `0x4383b3c2`, `0x4383b41c`, `0x4383b3ba`

## Entrada C2 hoja: 0x438082ce

**VERIFICADO**:
```
0x438082ce: bl  #0x43807d80   ; llama al puente
0x438082d2: b   #0x43808406   ; salta a handler común
```

**Estado:** Es hoja (no tiene llamadas entrantes BL). No hay referencia a `0x3011` ni `0x40193` en este cuerpo.

## Instalador de CaptureStart: 0x43809ed8

**VERIFICADO** (desensamblado con capstone):

```
0x43809ed8: push.w {r4, r5, r6, r7, lr}
0x43809eda: sub   sp, #0x1c
0x43809edc: mov   r4, r1
0x43809ede: mov   r5, r0
0x43809ee0: bl    #0x437de2fc
0x43809ee4: ldr   r6, [pc, #0x34]
...
0x43809efc: bl    #0x439018b0
0x43809f04: bl    #0x43b0172c
0x43809f10: bl    #0x43ae85d4
```

Llama a: `0x437de2fc`, `0x43ada220`, `0x439018b0`, `0x43b0172c`, `0x43ae85d4`

**Estado:** No hay `BL` directo a `0x43809ed8` desde fuera (no hay xrefs directos). Es llamado probablemente vía tabla de etapas de captura.

## Handler msg 0x104: 0x43808122

**VERIFICADO** (desensamblado con capstone):

Llama a: `0x43b01616`, `0x43b0160e`, `0x43809bf8`, `0x43b01382`, `0x43b01710`, `0x43b015ce`, `0x43b02414`, `0x43b017be`, `0x43b01832`

## C2 callback CaptureStart: 0x437df640

**VERIFICADO** (desde investigaciones previas):
- Es el callback de inicio de captura instalado por `0x43809ed8`
- No hay relación directa con `0x3011` ni `0x40193` en su cuerpo

## RelMgr emisor de 0x3011: 0x4379d838 → 0x4379e6a8 → 0x4379eba0

**VERIFICADO** (desde investigaciones previas S19):
- Envía tipo 2, id `0x3011`, correlación e índice de disparador a cola `0x40193` (origen `0x30001`)
- `0x3011` no se compara en ningún código con `cmp`/`movw` salvo el emisor y trazas
- El despacho es por tabla (id, estado) en `0x43ffdd30`

## Tabla de arbitraje C2: 0x43ffdd30

**VERIFICADO** (desde investigaciones previas S19):
- Filas de 16 B: `{función_guarda, id_mensaje, clase_estado, id_siguiente}`
- Para `0x3011` en estado 2: `{0x437fd0e1, 0x3011, 2, 0x3010}`
- Es una tabla de **arbitraje/permisos**, no contiene la acción de captura

## Receptor de cola 0x40193

**NO VERIFICADO / BLOQUEADO estáticamente:**

- No hay literal `0x40193` en el binario
- No hay `BL` a `osal_rcv_msg` desde fuera de la función OSAL
- Los nombres de funciones OSAL aparecen como strings (depuración/símbolos): `osal_rcv_msg`, `osal_snd_msg`, `osal_alloc_msgq_id`, `osal_free_msgq_id`, `osal_reg_sync_msg_queue_cb`, etc.
- `osal_alloc_msgq_id` está en `0x43ca8e74`, `osal_free_msgq_id` en `0x43ca8ecf`
- No hay `BL` directo a `osal_alloc_msgq_id`

**Conclusión:** El receptor usa un mecanismo indirecto (ID de buzón compuesto, tabla de buzones, o registro dinámico vía callback). Requiere trazado dinámico o REA con análisis de flujo de valores.

## Archivos desensamblados (capstone)

- `analysis/rea-independent/out/c2_dispatcher_0x43807f4c.txt` (284 instrucciones)
- `analysis/rea-independent/out/c2_handlers_0x43808100.txt` (451 instrucciones)
- `analysis/rea-independent/out/c2_handlers2_0x43808400.txt` (360 instrucciones)
- `analysis/rea-independent/out/relmgr_emitter_0x4379d838.txt` (1274 instrucciones)
- `analysis/rea-independent/out/camuser_send_0x4379eba0.txt` (860 instrucciones)
- `analysis/rea-independent/out/capture_start_install_0x43809ed8.txt` (55 instrucciones)

## Siguientes pasos para C2

1. Encontrar llamador indirecto de `0x43807f4c` (vía tabla de saltos o puntero de función)
2. Encontrar función que registra la cola receptora `0x40193`
3. Rastrear desde `0x4380db04` (mensajes 0x104/0x141) hacia atrás
4. Considerar trazado dinámico (prueba física P1 autorizada)
