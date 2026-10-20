# `ObjStillRecorderMediaMgr` y el campo `+0x2C` (sesión 12)

ELF de `libObj.so` fw 3.21 (VA Ghidra = ELF + 0x10000). Solo estático.

## 1. Qué es `+0x2C` (VERIFICADO)

Es **`mediaSelectMode`**, no un modo de «imagen externa». El volcador de `MediaMgr` (ELF `0x911084`, `tbb` en `0x9110a0`) imprime:

| Valor | Cadena | Máscara de slots (sesión 11) |
|---|---|---|
| 0 | `Normal` | `{0,5,6}` = 0x61 |
| 1 | `Multi` | `{1,3}` = 0x0a |
| 2 | `Relay` | — |
| 3 | `Sort` | `{1,3}` = 0x0a |
| 4 | **`None`** | `{4}` = 0x10 |
| 5 | `NormalTmp` | `{0,5,6}` |
| 6 | `Record` | `{0,5,6}` |

(`+0x48` imprime `m_priImageType`: All/None/Jpeg/Raw/Mpo.)

Conclusión: el «modo 4» de `MediaMgr` significa **ningún medio/destino seleccionado**; por eso `Execute` solo libera (sin `WriteStill`). No tiene relación con `this+0x128 = 4` del mensaje `0x1027` (otro campo, ya descartado como entrada de imagen).

## 2. Quién lo escribe

- Getter: ELF `0x9063ac` (`ldr r0,[r0,#0x2c]`). Lo lee `Execute` (`==4` → `0x90f8c8`, libera; si no, exige que un getter de slot `+0x34`/`+0x40` sea ≠ 0, entonces `RecordStill`).
- Setter: ELF `0x917076` (`str r1,[r0,#0x2c]`). Llamadores directos: solo `0x9174f8` y `0x917628`, ambos en `0x917460` (`IssueCommandSync`, manejo de `MSGID_SET_RECORDING_MODE_CMD` / `MSGID_SET_IMAGE_SIZE_CMD`): guarda el modo, pone **6 (`Record`)** y restaura (`0x9174f8` con el valor guardado). VERIFICADO.
- Constructor: valor por defecto 4 (sesión 11). NO re-verificado en esta sesión.
- NO VERIFICADO: qué orden concreta lleva el modo desde `None` hasta `Normal/Multi/Relay/Sort`; la cadena `MSGID_SET_RECORDING_MODE_CMD` (ELF `0x91750c`) apunta a que lo fija el comando «set recording mode», no la captura.

## 3. Precondiciones para que `Execute` llegue a `WriteStill` (VERIFICADO en código; cumplimiento real: NO VERIFICADO)

1. `mediaSelectMode != 4` (None).
2. Al menos un slot válido (`+0x34` o `+0x40` ≠ 0).
3. `0x910e1c`/`0x9104a4` (resolución de medio por mensaje) sin error; `0x90f698` (Ghidra `0x91f698`) obtiene `StillInfo` del Pool.
4. `EncodeStill` y la reserva de áreas sin error.

No se propone escribir el campo: sería saltarse la lógica de selección de medio (formateo, capacidad, multi-slot).
