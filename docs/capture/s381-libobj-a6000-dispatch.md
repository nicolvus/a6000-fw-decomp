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

## RecordStill::Execute

Dos sitios BL a `0x90b248`: `0x90de2e` y `0x91634e`. Ver [S382](s382-recordstill-callers.md). Ni la falta de literales de puntero ni una consulta vacía demuestran despacho indirecto. Los negativos históricos sobre MOVW #0x3500/#0x3002 usaban encodings incorrectos y quedan retirados.

## Pendiente

El registro concreto de la cola `0x40193` sigue NO_VERIFICADO: hay referencias estáticas al registrador para investigar. No se declara agotada esa vía ni se exige cámara para continuar. Las funciones de los objetos, la tabla de despacho y la identidad de sus argumentos requieren análisis de flujo; los nombres de imports por sí solos no cierran esos contratos.

## Reproducción

Regenerar `map.json` y `key_symbols.json` con sus scripts homónimos; `dispatch_analysis.py` usa el resolutor PLT y el decodificador Thumb compartido. Los originales y las bases Ghidra permanecen intactos.
