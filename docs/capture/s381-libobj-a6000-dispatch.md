# S381 — Despacho de mensajes en libObj.so A6000 fw3.21

## Corrección de auditoría — 23-10-2026

El mapeo histórico sumaba `base + índice × 16`, pero el PLT contiene cuerpos ARM de 12 B y veneers Thumb opcionales de 4 B. `r_offset` de `.rel.plt` señala GOT, no PLT. Se retiran las direcciones y los negativos de llamadas obtenidos con ese método.

`analysis/s380_libobj_map/elf_plt.py` resuelve el destino GOT desde las instrucciones ARM `add ip,pc,#imm; add ip,ip,#imm; ldr pc,[ip,#imm]!`, lo enlaza con la relocación y reconoce `bx pc; nop` como entrada Thumb al mismo cuerpo. Regresión: `tests/test_libobj_plt.py`.

| Import | Entrada ARM | Entrada Thumb adicional |
|---|---|---|
| MWF ObjMsgQueue::Enqueue | `0xdb7c8` | No detectada |
| UFW MsgReceiver::RcvMsg | `0xdcdbc` | No detectada |
| osal_reg_sync_msg_queue_cb | `0xdcd00` | `0xdccfc` |
| osal_reg_msg_queue_cb | `0xdd068` | `0xdd064` |
| MWF ObjPin::Send | `0xdeb30` | No detectada |
| MWF EventWrapper::SendAndRecv | `0xdfc0c` | No detectada |

El barrido Thumb de `.text`, con `scripts/elf_thumb_callers.py`, recupera **83 candidatos BL/BLX** a `0xdcd00` y **53** a `0xdd068`. Ejemplos: `0xffb1a` → `0xdcd00`; `0x10f83e` → `0xdd068`. Son referencias estáticas candidatas; la alcanzabilidad requiere recuperar funciones y flujo.

## RecordImage (antigua etiqueta RecordStill::Execute)

Dos sitios BL a `0x90b248`: `0x90de2e` y `0x91634e`, dentro de `0x90d7e8..0x90e148` y `0x9162d0..0x91647c`. Ver [S382](s382-recordstill-callers.md) y [contratos](recordstill-contract-audit-2026-10-23.md). Los 25 punteros Thumb `0x90d7e9` son `call_fn` de una tabla `StateMgr::_FuncEntry`; `StateMgr::CallFunc` los consume mediante `blx r3` en `libmprctrl.so:0x1cef2`, tras comparar estado e ID de mensaje. La activación runtime sigue NO_VERIFICADO. Una consulta vacía o la falta de literales pares no prueban ausencia de despacho. Los negativos históricos sobre MOVW #0x3500/#0x3002 usaban encodings incorrectos y quedan retirados.

## Pendiente

El callback OSAL Linux de `0x40193` sigue NO_VERIFICADO. [El trazado posterior](queue-40193-flow-2026-10-23.md) sí verifica literales LDR, cuatro emisores, receptor LIRO e inicializador `0x4379e93c` que instala su puntero en descriptor `0x43ea048c`. Pendientes: consumidor de arranque de ese descriptor y enlace Linux↔LIRO. Las xrefs al registrador OSAL no demuestran sus argumentos; el análisis estático sigue abierto.

## Reproducción

Regenerar `map.json` y `key_symbols.json` con sus scripts homónimos; `dispatch_analysis.py` usa el resolutor PLT y el decodificador Thumb compartido. Los originales y las bases Ghidra permanecen intactos.
