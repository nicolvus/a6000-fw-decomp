# G22-OYENTE — quién recibe el reparto del bit 8 (26-11-2026)

Medidas del invitado para `docs/gui/g22-reproduccion-dispatch.md` §8. Cada fichero es un extracto literal del
`shim.log` del perfil indicado, en `analysis/gui/g22/harness/live/<perfil>/shim.log` (no versionado).

| Fichero | Perfil | Qué demuestra |
|---|---|---|
| `oyentes-oyente1.txt` | `oyente1` (`DESTKEYV=1 OYD=1 WAITLOG=3000 WLALL=1`) | El reparto del bit 8 (`libObj+0x10e8ec`) tiene **8 oyentes** (`oyentes=8`) y ninguno es una vista: `LookManager`, `SvcCaution`, `TestcmdManager`, `HighlightManagerCustom`, `InputService`, `CameraProfileService`, `TopologyManager`, `Database::HndlMgr`. Cada línea lleva clave del mapa, puntero, vtable, ranura `+8` y RTTI. |
| `arranque-oyente1.txt` | `oyente1` | Registro de los dos interruptores: `DESTKEYV: libObj+0x113076 04 22 -> 0c 22` y `OYD: trampa en libObj+0x10e914`. |
| `eqtrace-dest12-oyente6.txt` | `oyente6` | Con `DESTKEYV=1` los tres eventos de una pulsación se publican con `dest=12` (`0x0c`), `clase=1`, `notify=0`. |
| `dispatch-bit8-oyente8.txt` | `oyente8` (`TRACEFN=7eee68` + `TRACEDEREF=d1:4:3`) | La tecla **entra** en la rama `dest & 8`: la palabra `+8` del `Event` es `0x0000010c` y el código es `0x150100f2`/`0x150100f1`/`0x15070010`/`0x150701a0`. |
| `multicast-recibe-tecla-oyente8.txt` | `oyente8` | El reparto **entrega** la tecla a los 8 oyentes: `OYENTE n=256 … codigo=0x15070010 dest=0xc clase=0x1 oyentes=8`. |
| `geteventid-devuelve-oyente8.txt` | `oyente8` (`TRACELIB=viewUnified2.so` + `TRACEFN2=1994e8`) | `ViewBase::GetEventId` devuelve los ids de la vista (`0x2a`, `8`, `2`, con base `0x1306c000`) pero **devuelve el código sin traducir** para la tecla (`0x150100f2`) y sus sintéticos (`0x15070010`, `0x150701a0`). |
| `antes.png`, `despues.png` | `oyente1` | Pulsar Reproducción **no cambia la pantalla**: idénticos byte a byte (12 861 B, 0 píxeles distintos). Estado del arnés en ese momento: `2 fotogramas · 2 listas · opacos 0,0046` (G22-CUELGUE). |

Notas de método:

- `OYD=1` es el único interruptor nuevo que hizo falta: trampa **repetible** en `libObj+0x10e914` con emulación de
  `ldr r3,[r0]` en el manejador (no toca la instrucción siguiente, a diferencia de `TRACEREP`).
- `TRACEDEREF` desreferencia **siempre**: solo se usó con registros que son punteros (`d1:4:3` en la rama del bit 8,
  donde `r1` es el `Event*`, y `0:14:1` en `GetEventId`, donde `r0` es la vista). Ponerlo en `1106b8`, `f59f0` o `1994e8`
  mata el hilo.
- Los cinco arranques en frío de la sesión (`oyente1`…`oyente8`) se quedaron en el cuelgue conocido **G22-CUELGUE**
  (`2 fotogramas · 2 listas · opacos 0,0046`): el bucle `AppSystem::Main` despacha hasta ≈130 s y luego se para. Aun así
  la ruta de la tecla se mide, porque las trampas y el reparto siguen activos mientras dura el despacho.
