# S403 · E15/E12 — el buzón `0x0110027c` es la cola de `kikilog`

Estado: **cerrado** (E15, E12). Script: [e15_kikilog.py](../../analysis/s403_pendientes/e15_kikilog.py) → [e15_kikilog.json](../../analysis/s403_pendientes/e15_kikilog.json); prueba `tests/test_s403_e15_kikilog.py`.

## Hallazgo
- La palabra `0x0110027c` aparece como literal en pools de cuatro binarios, siempre en pares `osal_valloc_msg_wait` (reserva de 20 B) + `osal_snd_msg`:
  `av-cam.bin` (13 palabras, 13 pares), `libObj.so` (42 referencias), `upm.ko` (51) y `kikilog.ko` (8).
- El receptor está en **`kikilog.ko`** (módulo del kernel Linux, con símbolos): `kikilog_main_thread` llama a `osal_rcv_msg_tmo`, copia el
  mensaje de 20 B y llama a `record_log`. El id consta en una estructura de `.data` (`+0x7d04` del archivo), no como literal de código,
  por eso la búsqueda por literal no lo encontraba. `exit_kikilog` envía a la cola un mensaje de parada.
- Formato del mensaje (de `record_log` y de los emisores): `u16[0]` = tipo (12 bits altos del id de registro), `u16[2]`+`u16[4]` = código de 20 bits,
  `u16[6]`+`u16[8]` = banderas, `+10` = 8 B opcionales. `record_log` actúa según las banderas: `0x1` combilog, `0x2` evr, `0x10`/`0x20` userlog/acm
  (`&0x22 == 0x22` → `record_acm`), `0x100`/`0x200` retención de estado, `0x10000`/`0x20000` temporizador, `0x2000` reenvío a `notify_thread_qid`.
- Los 13 emisores de av-cam: 5 con tipo `3` y banderas `0x22` (entre ellos `0x437b0390`), 1 con tipo `0xd`, 3 con tipo `0x113` y banderas `0x3122`,
  y 4 que solo copian un mensaje ya formado.

## Consecuencia para S51
El mensaje de `0x437b0390` que emite `0x4384031c` en modo 1 (o 3 con bandera) es un **registro de diagnóstico** (tipo 3, banderas `0x22`, sin
`0x2000`): no se reenvía a otra cola y no llega a `SetMode/SetExposure/SetRead`. El límite de S51 («no se siguieron los receptores de los mensajes
que emite `0x437b0390`») queda levantado para ese mensaje. No cambia la decisión A/B/C=NO.

## Límites
- `kikilog_main_thread` se verificó por relocaciones del módulo y por el desensamblado de `record_log`; no se siguió cada función que éste llama.
- Que `0x7d04` sea la estructura de arranque del hilo se deduce de su forma (id + `0x110`); no se ejecutó nada.
- La pregunta «entradas indirectas de `CURTAINMODE`» no se resuelve aquí; pasa a E16.
