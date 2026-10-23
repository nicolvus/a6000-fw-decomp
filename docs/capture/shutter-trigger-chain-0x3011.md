# Cadena disparador → 0x3011 → CaptureStart (línea C2, Claude; parcial)

Exports: `analysis/ghidra/liro-h3011.json`, `liro-h3011b.json`, `liro-camuser.json`, `liro-camuser-handlers.json`.
Análisis adicional: `analysis/rea-independent/out/C2_CHAIN_ANALYSIS.md` (22-10-2026).
Desensamblado estático: `analysis/rea-independent/out/c2_dispatcher_0x43807f4c.txt`, `c2_handlers_0x43808100.txt`, `c2_handlers2_0x43808400.txt`, `relmgr_emitter_0x4379d838.txt`, `camuser_send_0x4379eba0.txt`, `capture_start_install_0x43809ed8.txt`.

## VERIFICADO (C): RelMgr emisor de 0x3011

RelMgr `0x4379d838` → `0x4379e6a8` → `0x4379eba0` envía tipo 2, id `0x3011`, correlación e índice de disparador a la cola `0x40193` (origen `0x30001`).

`0x3011` NO se compara en ningún código con `cmp`/`movw` salvo el emisor (`0x4379eba8`) y trazas (`0x4381c6a8` CapIdTblMgr, `0x4394ad1c` RcResize): el despacho es por tabla (id, estado).

Tabla en `0x43ffdd30` (filas de 16 B: `{función_guarda, id_mensaje, clase_estado, id_siguiente}`; estados 0, 0x20, 1, 2, 0x59). Para `0x3011` en estado 2 la fila es `{0x437fd0e1, 0x3011, 2, 0x3010}`; la «función» `0x437fd0e0` solo devuelve el puntero `0x43bf3626` (byte `02`). Otras filas (`0x437fce40`, `0x437fd5c0`, `0x437fd53c`, `0x437fda8c`) devuelven punteros a registros constantes `0x43bf3xxx` según flags de contexto (`+0x34→+0xa/+0xb`, `0x43af0d4c`, `0x437fe50c`).

INFERENCIA: esa tabla es de **arbitraje/permisos**: dado (mensaje, modo de función) devuelve el registro de condiciones que permiten o bloquean la petición (coherente con «remote capture cancel due to camuser's release lock» y `IsNeedForceS1ON`). No contiene la acción.

`Camera::Function::CamUser` (`wrapper/CamUser.cpp`, `sendMessageToCamUser`) es parte del *CAM_FUNC_MGR* de LIRO; su vtable (`0x43fcd468`) solo tiene destructores: la lógica no es un método virtual de CamUser.

## VERIFICADO (estático, capstone): Dispatcher de dominio C2 `0x43807f4c`

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

**VERIFICADO:** El dispatcher `0x43807f4c` (Thumb `0x43807f4d`) está referenciado como puntero de función en una tabla/vtable en `0x43fcd3e0` (file offset `0xa8c3e0`, entrada 16 de la tabla base `0x43fcd3a0`). No se encontró ninguna referencia literal a la dirección de la tabla `0x43fcd3a0` ni al Thumb `0x43fcd3a1`, por lo que el puntero de vtable se establece en runtime.

**El llamador del dispatcher `0x43807f4c` NO se ha encontrado estáticamente:**
- No hay BL directo a `0x43807f4c` desde ninguna dirección
- No hay literal de la dirección en el binario
- `procedure_callers(0x43807f4c)` devuelve vacío en REA
- La tabla vtable en `0x43fcd3a0` no tiene referencias directas como literal

## VERIFICADO: Puente C2 `0x43807d80`

`0x43807d80` es el puente del dominio C2 al dominio local `0x100-0x207`. Llama a:
- `0x4383a84e`, `0x43543004`, `0x4383aca4`, `0x4383b44c`, `0x4383aca0`, `0x4383b1c0`
- `0x4383aa04`, `0x4383b50c`, `0x4383aca0`, `0x4383b1b6`
- `0x4383bb1c`, `0x4383a602`, `0x4383a9b6`, `0x4383b486`, `0x4383b3c2`, `0x4383b41c`, `0x4383b3ba`

## VERIFICADO: Entrada C2 hoja `0x438082ce`

```
0x438082ce: bl  #0x43807d80   ; llama al puente
0x438082d2: b   #0x43808406   ; salta a handler común
```

Es hoja (no tiene llamadas entrantes BL). No hay referencia a `0x3011` ni `0x40193` en este cuerpo.

## VERIFICADO: Instalador de CaptureStart `0x43809ed8

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

Llama a: `0x437de2fc`, `0x43ada220`, `0x439018b0`, `0x43b0172c`, `0x43ae85d4`.

**No hay BL directo a `0x43809ed8` desde fuera (no hay xrefs directos).** Es llamado probablemente vía tabla de etapas de captura.

## VERIFICADO: Handler msg 0x104 `0x43808122`

Llama a: `0x43b01616`, `0x43b0160e`, `0x43809bf8`, `0x43b01382`, `0x43b01710`, `0x43b015ce`, `0x43b02414`, `0x43b017be`, `0x43b01832`.

## VERIFICADO: C2 callback CaptureStart `0x437df640`

Es el callback de inicio de captura instalado por `0x43809ed8`. No hay relación directa con `0x3011` ni `0x40193` en su cuerpo.

## NO VERIFICADO / BLOQUEADO estáticamente: Receptor de cola `0x40193`

- No existe el literal `0x40193` (word de 4 bytes LE) en `av-cam.bin`
- No existe la cadena ASCII `"40193"` en el binario
- No hay instrucciones `movw`/`movt` que construyan `0x40193` (verificado: búsqueda de `F240 9301` y `F2C0 4000` dio 0 resultados)
- No hay `BL` a `osal_rcv_msg` (0x43561260) desde fuera de la propia función OSAL
- Las BL a `osal_rcv_msg` encontradas (2 sitios en 0x43561902, 0x43561eb0) están dentro de la propia función OSAL
- `trace_native_values` y `trace_call_path` de REA no encontraron camino desde `0x4379eba0` hasta `0x43809ed8`

**Conclusión:** El receptor de la cola `0x40193` usa un mecanismo completamente indirecto (registro dinámico de callback de buzón, ID de buzón compuesto, o tabla de buzones no accesible estáticamente). **Requiere trazado dinámico (prueba física P1 autorizada) o REA con `trace_native_values` desde el punto de envío en RelMgr.**

## Siguientes pasos para C2

1. Encontrar llamador indirecto de `0x43807f4c` (vía tabla de saltos o puntero de función en runtime)
2. Encontrar función que registra la cola receptora `0x40193`
3. Rastrear desde `0x4380db04` (mensajes 0x104/0x141) hacia atrás
4. Prueba física P1 (autorización requerida)

## Efecto en S51

S51 sigue A=NO, B=NO, C=NO. La cadena C2 no demuestra una ruta de exposición totalmente electrónica.
