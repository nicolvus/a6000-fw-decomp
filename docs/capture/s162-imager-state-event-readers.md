# S162 — dos helpers leen `state+0x1c` y notifican a otros destinos

S162 clasifica los xrefs del estado en `0x438d933e` y `0x438d9378`. **VERIFICADO
localmente:** ambos cargan el objeto `0x43f72d02` desde GOT y leen el halfword
`state+0x1c`; luego usan ese valor al llamar a `FUN_438d9288` y guardan el
resultado en `0x43f7c702` o `0x43f7c704`. Ninguno escribe el objeto de estado ni
los gates `+3/+6` en su cuerpo.

| Procedimiento | Xref | Campo leído | Store posterior |
|---|---|---|---|
| `FUN_438d9318` (`0x438d9318..0x438d9355`) | `0x438d933e` | `ldrh r0,[r3,#0x1c]` → `0x43f72d1e`; si cero, usa 3 | `strh` a `0x43f7c702` (`0x438d9350`) |
| `FUN_438d936c` (`0x438d936c..0x438d938d`) | `0x438d9378` | `ldrh r0,[r3,#0x1c]` → `0x43f72d1e`; si cero, usa 3 | `strh` a `0x43f7c704` (`0x438d938a`) |

En ambos, el edge de `ldr r3,[r4,r3]` hacia `0x43f72d02` es `PARAM` (puntero
cargado); la lectura real sucede en `ldrh` a `+0x1c`. El campo está a cero en
el blob, no necesariamente en runtime. Evidence del procedimiento/lecturas y
stores se registra en `analysis/s162_imager_state_event_readers/event_readers.json`.

La función `FUN_438d9288` parece producir una notificación/mensaje OSAL (**INFERENCIA**); no se afirma efecto de sensor. Hay un lector adicional en `0x438d93aa` no cubierto aquí y otros xrefs de la base permanecen abiertos. Sin runtime, cámara o flasheo; S51 no cambia.

```sh
python3 analysis/s162_imager_state_event_readers/verify_state_event_readers.py
python3 -m unittest tests.test_s162_imager_state_event_readers -v
```
